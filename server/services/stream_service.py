"""
WebSocket streaming service for the WORT agent.

Thin orchestrator connecting the FastAPI WebSocket to the LangGraph
execution loop. Delegates chunk routing to ChunkRouter and event
persistence to EventPersister. Triggers long-term memory extraction
once a session completes.

Endpoint: /ws/chat/{thread_id}
"""

import asyncio
import json
import logging
import traceback
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import WebSocket, WebSocketDisconnect
from langgraph.types import Command

from graphs.deep_research_agent import DeepResearchAgent
from memory.memory_facade import MemoryFacade
from server.storage.session_store import SessionStore
from server.storage.event_store import EventStore
from server.services.event_persister import EventPersister
from server.services.chunk_router import ChunkRouter
from utils.cost_tracker import CostTracker
from redis_streams import RedisClient

logger = logging.getLogger(__name__)


class StreamService:
    """
    Connects a WebSocket client to the LangGraph execution loop.

    Lifecycle per session:
      1. Client sends 'start' -> build initial/update state -> invoke graph
      2. Client sends 'resume' -> resume after HITL interrupt
      3. Stream chunks are routed via ChunkRouter
      4. Events are persisted via EventPersister
    """

    def __init__(
        self,
        websocket: WebSocket,
        manager: Any,
        memory_facade: Optional[MemoryFacade],
        session_store: Optional[SessionStore] = None,
        event_store: Optional[EventStore] = None,
        websearch_limiter: Optional[Any] = None,
        deepsearch_limiter: Optional[Any] = None,
    ):
        self._websocket = websocket
        self._manager = manager
        self._memory_facade = memory_facade

        self._persister = EventPersister(session_store, event_store)
        self._chunk_router = ChunkRouter(self._persister)

        self._agent: Optional[DeepResearchAgent] = None
        self._thread_id: Optional[str] = None
        self._user_id: Optional[str] = None
        self._session_store = session_store

        self._websearch_limiter = websearch_limiter
        self._deepsearch_limiter = deepsearch_limiter
        self._active_threads: set = getattr(websocket.app.state, "active_threads", set())

        self._reader_task: Optional[asyncio.Task] = None
        self._graph_task: Optional[asyncio.Task] = None
        self._last_seen_id = "0"

    @staticmethod
    def _normalize_search_mode(search_mode: str) -> str:
        normalized = (search_mode or "").strip().lower()
        if normalized in {"websearch", "web"}:
            return "websearch"
        if normalized in {"extremesearch", "extreme_search", "extreme"}:
            return "extremesearch"
        if normalized == "edit":
            return "edit"
        return "deepsearch"

    @staticmethod
    def _extract_analysis_level(raw_mode: str) -> str:
        """Extracts the deep analysis intensity level from the raw frontend mode string."""
        normalized = (raw_mode or "").strip().lower()
        if normalized.endswith("_high"):
            return "high"
        if normalized.endswith("_mid"):
            return "mid"
        return "low"

    async def handle_websocket(self, thread_id: str, user_id: str) -> None:
        """Main loop receiving client messages and executing the graph.

        Args:
            thread_id: The conversation thread identifier.
            user_id: The authenticated user ID (verified by the WebSocket
                endpoint via JWT). Must not be client-supplied.
        """
        self._thread_id = thread_id
        self._user_id = user_id
        self._chunk_router.set_thread_id(thread_id)
        await self._manager.connect(self._websocket)

        self._reader_task = asyncio.create_task(self._redis_reader_loop())

        try:
            if not self._memory_facade:
                await self._manager.send_json(
                    {"type": "error", "message": "Memory system not initialized"},
                    self._websocket,
                )
                return

            while True:
                try:
                    data = await self._websocket.receive_json()
                except json.JSONDecodeError:
                    continue

                await self._process_message(data)

        except WebSocketDisconnect:
            self._manager.disconnect(self._websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
            self._manager.disconnect(self._websocket)
        finally:
            if self._reader_task:
                self._reader_task.cancel()

    async def _process_message(self, data: Dict[str, Any]) -> None:
        """Routes a client message to the appropriate handler and starts streaming."""
        if "last_seen_id" in data:
            self._last_seen_id = str(data["last_seen_id"])

        msg_type = data.get("type", "start")

        if msg_type == "join_stream":
            return

        if msg_type == "start":
            await self._check_rate_limit(data)

        self._chunk_router.reset_turn()
        if not self._agent:
            self._agent = DeepResearchAgent(memory=self._memory_facade)
        config = {"configurable": {"thread_id": self._thread_id}}

        if msg_type == "start":
            input_data = await self._handle_start(data)
        elif msg_type == "resume":
            await RedisClient.get_instance().delete_stream(
                f"wort:stream:{self._thread_id}"
            )
            input_data = await self._handle_resume(data)
        elif msg_type == "resume_error":
            can_resume = await self._handle_resume_error(data)
            if can_resume:
                await self._stream_graph(None, config, is_new_turn=False)
            else:
                await self._manager.send_json(
                    {
                        "type": "error",
                        "message": "No checkpoint found to resume from. Please start a new session.",
                    },
                    self._websocket,
                )
            return
        elif msg_type == "edit_section":
            input_data = await self._handle_edit_section(data)
        else:
            return

        if input_data:
            is_new_turn = msg_type == "start"
            await self._stream_graph(input_data, config, is_new_turn=is_new_turn)
        elif msg_type == "edit_section":
            await self._manager.send_json(
                {
                    "type": "error",
                    "message": "Invalid section edit: missing section id, chapter HTML, or feedback.",
                },
                self._websocket,
            )

    # -------------------------------------------------------------------------
    # Rate limiting
    # -------------------------------------------------------------------------

    async def _check_rate_limit(self, data: Dict[str, Any]) -> None:
        """Checks rate limits based on the search mode before processing a start message."""
        raw_mode = data.get("mode", "deepsearch")
        search_mode = self._normalize_search_mode(raw_mode)

        limiter = None
        if search_mode == "websearch":
            limiter = self._websearch_limiter
        else:
            limiter = self._deepsearch_limiter

        if limiter:
            await limiter.check(self._websocket, user_id=self._user_id)

    # -------------------------------------------------------------------------
    # Message handlers
    # -------------------------------------------------------------------------

    async def _handle_start(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Builds graph input state for a new 'start' message."""
        user_message = data.get("content")
        user_id = self._user_id  # Authenticated user_id from WebSocket JWT

        raw_mode = data.get("mode", "deepsearch")
        search_mode = self._normalize_search_mode(raw_mode)
        analysis_level = self._extract_analysis_level(raw_mode)
        api_keys = data.get("api_keys") or {}
        model_selections = data.get("model_selections") or {}

        if not user_message:
            return None

        config = {"configurable": {"thread_id": self._thread_id}}
        existing_state = await self._agent._graph.aget_state(config)

        # Guard: reject new queries while a previous run is still active
        if self._thread_id in self._active_threads:
            await self._manager.send_json(
                {
                    "type": "error",
                    "message": "A report is currently being generated. Please wait for it to complete before starting a new query.",
                    "thread_id": self._thread_id,
                },
                self._websocket,
            )
            # Reset frontend processing state so the UI doesn't get stuck
            await self._manager.send_json(
                {"type": "done", "thread_id": self._thread_id},
                self._websocket,
            )
            return None

        logger.info(
            f"[_handle_start] thread={self._thread_id}, "
            f"has_existing_state={bool(existing_state.values)}, "
            f"chat_msgs_count={len(existing_state.values.get('chat_messages', []))} "
            f"if existing_state.values else 0"
        )

        if existing_state.values:
            input_state = self._agent._create_update_state(
                user_query=user_message,
                search_mode=search_mode,
                analysis_level=analysis_level,
                thread_id=self._thread_id,
                user_id=user_id,
                api_keys=api_keys,
                model_selections=model_selections,
            )
        else:
            input_state = self._agent._create_initial_state(
                user_query=user_message,
                search_mode=search_mode,
                analysis_level=analysis_level,
                thread_id=self._thread_id,
                user_id=user_id,
                api_keys=api_keys,
                model_selections=model_selections,
            )

        context = await self._memory_facade.get_context_for_planner(
            thread_id=self._thread_id,
            user_id=user_id,
            current_query=user_message,
            search_mode=search_mode,
        )
        logger.info(
            f"[_handle_start] memory_context for thread={self._thread_id}: "
            f"semantic_memories={len(context.get('semantic_memories', []))}, "
            f"has_summary={context.get('conversation_summary') is not None}"
        )
        input_state["memory_context"] = context

        await self._persister.persist_session_start(
            self._thread_id,
            user_id,
            user_message,
            search_mode,
        )

        await self._manager.send_json(
            {"type": "status", "status": "processing", "thread_id": self._thread_id},
            self._websocket,
        )
        return input_state

    async def _handle_resume(self, data: Dict[str, Any]) -> Any:
        """Builds a Command(resume=value) for HITL interrupts."""
        resume_data = data.get("resume_data", {})
        resume_type = resume_data.get("type", "plan_review")

        if resume_type == "clarification":
            resume_value = {
                "answers": resume_data.get("answers", {}),
            }
            await self._persister.persist_event(
                self._thread_id,
                "clarification_answer",
                content=str(resume_value.get("answers", {})),
                metadata={"type": "clarification"},
            )
        else:
            resume_value = {
                "approved": resume_data.get("approved", True),
                "feedback": resume_data.get("feedback", ""),
            }
            await self._persister.persist_event(
                self._thread_id,
                "plan_feedback",
                content=resume_value.get("feedback", ""),
                metadata={"approved": resume_value["approved"]},
            )

        await self._manager.send_json(
            {"type": "status", "status": "resuming", "thread_id": self._thread_id},
            self._websocket,
        )
        return Command(resume=resume_value)

    async def _handle_edit_section(
        self, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Builds a minimal graph input for an in-place report section edit."""
        edit_data = data.get("edit_data") or {}
        section_id = edit_data.get("section_id")
        old_html = edit_data.get("old_html")
        feedback = (edit_data.get("feedback") or "").strip()
        edit_mode = (edit_data.get("edit_mode") or "visual").strip().lower()
        raw_order = edit_data.get("section_order")
        if isinstance(raw_order, int):
            edit_section_order: Optional[int] = raw_order
        elif isinstance(raw_order, float) and raw_order == int(raw_order):
            edit_section_order = int(raw_order)
        else:
            edit_section_order = None
        chapter_heading = (edit_data.get("chapter_heading") or "").strip()

        if not section_id or not old_html or not feedback:
            return None

        user_message = {
            "message_id": str(uuid.uuid4()),
            "role": "user",
            "content": feedback,
            "timestamp": datetime.now().isoformat(),
            "metadata": {"message_type": "edit", "section_id": str(section_id)},
        }

        edit_input = {
            "search_mode": "edit",
            "user_query": feedback,
            "chat_messages": [user_message],
            "edit_section_id": str(section_id),
            "edit_section_order": edit_section_order,
            "edit_chapter_heading": chapter_heading,
            "edit_old_html": old_html,
            "edit_feedback": feedback,
            "edit_mode": "research" if edit_mode == "research" else "visual",
            "edit_run_id": (edit_data.get("run_id") or "").strip(),
        }

        await self._persister.persist_event(
            self._thread_id,
            "edit_section_request",
            content=feedback,
            metadata={
                "section_id": str(section_id),
                "edit_mode": edit_input["edit_mode"],
            },
        )

        await self._manager.send_json(
            {"type": "status", "status": "processing", "thread_id": self._thread_id},
            self._websocket,
        )
        return edit_input

    async def _handle_resume_error(self, data: Dict[str, Any]) -> bool:
        """Resumes the graph after a runtime error by reusing the last checkpoint.

        Returns True if a checkpoint exists to resume from, False otherwise.
        The caller should pass None to astream() on True so LangGraph resumes
        from the last checkpoint instead of re-invoking from scratch.
        """
        config = {"configurable": {"thread_id": self._thread_id}}
        existing_state = await self._agent._graph.aget_state(config)

        if not existing_state.values:
            logger.warning(
                f"[_handle_resume_error] No existing state for thread={self._thread_id}"
            )
            return False

        await self._manager.send_json(
            {
                "type": "status",
                "status": "resuming_from_error",
                "thread_id": self._thread_id,
            },
            self._websocket,
        )

        return True

    # -------------------------------------------------------------------------
    # Graph streaming
    # -------------------------------------------------------------------------

    async def _stream_graph(
        self, input_data: Any, config: Dict[str, Any], is_new_turn: bool = True
    ) -> None:
        """Launches the graph execution in a background task."""
        if self._graph_task and not self._graph_task.done():
            logger.warning(
                f"[StreamService] Previous graph task still running for thread={self._thread_id}. "
                "Starting new task — stream output may interleave."
            )
        self._graph_task = asyncio.create_task(
            self._background_graph_task(input_data, config, is_new_turn)
        )

    async def _background_graph_task(
        self, input_data: Any, config: Dict[str, Any], is_new_turn: bool = True
    ) -> None:
        """Streams graph execution and routes each chunk via ChunkRouter into Redis Streams."""
        redis = RedisClient.get_instance()
        stream_name = f"wort:stream:{self._thread_id}"

        if is_new_turn:
            await redis.delete_stream(stream_name)

        # Mark this thread as actively running
        self._active_threads.add(self._thread_id)

        cost_tracker = CostTracker()
        if "callbacks" not in config:
            config["callbacks"] = []
        config["callbacks"].append(cost_tracker)

        try:
            interrupted = False
            async for chunk in self._agent._graph.astream(
                input_data,
                stream_mode=["updates", "custom", "messages"],
                subgraphs=True,
                config=config,
            ):
                try:
                    if await self._chunk_router.route(chunk):
                        interrupted = True
                except Exception as e:
                    logger.error(f"[ChunkRouter Routing error] {e}")

            if not interrupted:
                summary = cost_tracker.get_summary()

                logger.info(f"\n{cost_tracker.format_summary()}")

                if self._session_store and self._user_id:
                    try:
                        await self._session_store.update_usage(
                            session_id=self._thread_id,
                            user_id=self._user_id,
                            input_tokens=summary.get("input_tokens", 0),
                            output_tokens=summary.get("output_tokens", 0),
                            total_cost=summary.get("total_cost", 0.0),
                        )
                    except Exception as e:
                        logger.error(f"Failed to update session usage metrics: {e}")

                await redis.xadd(stream_name, {"__stream_end__": True})
                asyncio.create_task(self._delayed_delete_stream(stream_name, delay=10))

        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Streaming error: {e}\n{error_trace}")

            error_payload = {}
            if e.__class__.__name__ == "LLMCatchError":
                try:
                    error_payload = {
                        "llm_catch_error": json.dumps(e.to_dict()),
                        "traceback": error_trace,
                    }
                except AttributeError:
                    error_payload = {"error": f"{str(e)}\n\nTraceback:\n{error_trace}"}
            else:
                error_payload = {"error": f"{str(e)}\n\nTraceback:\n{error_trace}"}

            await redis.xadd(stream_name, error_payload)
            await redis.xadd(stream_name, {"__stream_end__": True})
            asyncio.create_task(self._delayed_delete_stream(stream_name, delay=10))
        finally:
            # Always clear the active flag so new queries can proceed
            self._active_threads.discard(self._thread_id)

    async def _delayed_delete_stream(self, stream_name: str, delay: int):
        """Allows enough time for trailing connected clients to receive the end signal."""
        await asyncio.sleep(delay)
        await RedisClient.get_instance().delete_stream(stream_name)

    # -------------------------------------------------------------------------
    # Redis reader
    # -------------------------------------------------------------------------

    async def _redis_reader_loop(self):
        """Continuously reads live tokens out of Redis Streams and pushes them over the WebSocket."""
        redis = RedisClient.get_instance()
        stream_name = f"wort:stream:{self._thread_id}"

        try:
            while True:
                if self._websocket.client_state.name == "DISCONNECTED":
                    break

                messages = await redis.xread_block(
                    stream_name, self._last_seen_id, block_ms=1000
                )
                if not messages:
                    continue

                for msg_id, data in messages:
                    if "__stream_end__" in data:
                        try:
                            await self._manager.send_json(
                                {"type": "done", "thread_id": self._thread_id},
                                self._websocket,
                            )
                        except Exception:
                            pass
                        self._last_seen_id = msg_id
                        continue

                    if "llm_catch_error" in data:
                        try:
                            error_obj = json.loads(data["llm_catch_error"])
                            error_obj["traceback"] = data.get("traceback", "")
                            await self._manager.send_json(
                                {"type": "llm_error", "error_data": error_obj},
                                self._websocket,
                            )
                        except Exception:
                            pass
                        self._last_seen_id = msg_id
                        continue

                    if "error" in data:
                        try:
                            await self._manager.send_json(
                                {"type": "error", "message": data["error"]},
                                self._websocket,
                            )
                        except Exception:
                            pass
                        self._last_seen_id = msg_id
                        continue

                    try:
                        if isinstance(data, dict):
                            data["_redis_id"] = msg_id
                        await self._manager.send_json(data, self._websocket)
                    except Exception as e:
                        logger.warning(
                            f"WebSocket closed trying to send stream chunk: {e}"
                        )
                        return

                    self._last_seen_id = msg_id
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[_redis_reader_loop error] {e}")
