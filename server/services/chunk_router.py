"""
Chunk routing for LangGraph stream events.

Processes the three stream modes (updates, custom, messages) from the
LangGraph astream and routes each to the appropriate WebSocket message
type. Also triggers event persistence through EventPersister.
"""

import json
import logging
from typing import Any, Dict, Optional

from graphs.events.frontend_events import EventType
from redis_streams import RedisClient
from server.services.event_persister import EventPersister

logger = logging.getLogger(__name__)


class ChunkRouter:
    """
    Routes LangGraph stream chunks to Redis Streams and persistence.

    Handles three stream modes:
    - 'updates': Node state changes (reports, router thinking, responses, interrupts)
    - 'custom': Agent/writer progress, response tokens, errors
    - 'messages': Raw LLM tokens with filtering for noise reduction

    All data flows through Redis via _safe_send. Response persistence
    is handled by _on_response_update when response_node fires.
    """

    def __init__(self, persister: EventPersister):
        self._persister = persister
        self._thread_id: Optional[str] = None
        self._planner_json_started = False

    def set_thread_id(self, thread_id: str) -> None:
        """Sets the active thread_id for persistence context."""
        self._thread_id = thread_id

    def reset_turn(self) -> None:
        """Resets stream-specific state for a new turn."""
        self._planner_json_started = False

    async def _safe_send(self, data: dict) -> None:
        """Sends data to the Redis stream for the current thread."""
        if self._thread_id:
            await RedisClient.get_instance().xadd(
                f"wort:stream:{self._thread_id}", data
            )

    async def route(self, chunk: Any) -> bool:
        """
        Routes a single stream chunk to the appropriate handler.

        With subgraphs=True and multiple stream_mode, LangGraph yields
        (namespace, (mode, data)) 2-tuples. We detect the nested tuple
        and unpack accordingly.

        Returns:
            True if an interrupt was encountered, False otherwise.
        """
        namespace = ()
        mode = ""
        payload = {}

        if isinstance(chunk, tuple):
            if len(chunk) == 2:
                first, second = chunk
                if (
                    isinstance(first, tuple)
                    and isinstance(second, tuple)
                    and len(second) == 2
                ):
                    namespace = first
                    mode, payload = second
                elif isinstance(first, str):
                    mode, payload = first, second
                else:
                    logger.info(
                        f"[ChunkRouter] Unrecognized 2-tuple: first={type(first)}, second={type(second)}"
                    )
            elif len(chunk) == 3:
                namespace, mode, payload = chunk

        if mode == "custom":
            await self._handle_custom_event(payload)
        elif mode == "updates":
            return await self._handle_update_event(namespace, payload)
        elif mode == "messages":
            await self._handle_message_token(namespace, payload)

        return False

    # -------------------------------------------------------------------------
    # Custom events (agent progress, writer progress, response tokens)
    # -------------------------------------------------------------------------

    async def _handle_custom_event(self, data: Dict[str, Any]) -> None:
        """Routes custom events emitted by nodes via adispatch."""
        if data is None or not isinstance(data, dict):
            return

        event_type = data.get("event_type")

        if event_type == EventType.AGENT_PROGRESS.value:
            await self._on_agent_progress(data)

        elif event_type == EventType.RESPONSE_TOKEN.value:
            token = data.get("payload", {}).get("token", "")
            if token:
                await self._safe_send({"type": "token", "content": token})

        elif event_type == EventType.ERROR.value:
            await self._safe_send(
                {
                    "type": "error",
                    "message": data.get("payload", {}).get("message", "Unknown error"),
                }
            )

        elif event_type == EventType.WRITER_PROGRESS.value:
            await self._on_writer_progress(data)

        elif event_type == EventType.TOOL_EXECUTION.value:
            await self._on_tool_execution(data)

        elif event_type == EventType.CLARIFICATION_STARTED.value:
            payload = data.get("payload", {})
            await self._safe_send(
                {
                    "type": "clarification_progress",
                    "data": {
                        "message": payload.get(
                            "message", "Preparing clarification questions..."
                        ),
                        "loop_number": payload.get("loop_number", 1),
                        "timestamp": data.get("timestamp"),
                    },
                }
            )

        elif event_type == EventType.SKILL_SELECTION_COMPLETED.value:
            payload = data.get("payload", {})
            await self._safe_send(
                {
                    "type": "skill_selection",
                    "data": {
                        "skills": payload.get("skills", []),
                        "skill_labels": payload.get("skill_labels", []),
                        "reasoning": payload.get("reasoning", ""),
                        "timestamp": data.get("timestamp"),
                    },
                }
            )

        elif data.get("type") == "report":
            await self._safe_send(
                {
                    "type": "report",
                    "data": data.get("data", {}),
                }
            )

    # -------------------------------------------------------------------------
    # State update events (report, router, response, interrupt)
    # -------------------------------------------------------------------------

    async def _handle_update_event(self, namespace: Any, data: Dict[str, Any]) -> bool:
        """
        Routes node state updates to WebSocket and persists meaningful events.

        Only processes top-level node updates (namespace is empty).

        Returns:
            True if an interrupt was encountered, False otherwise.
        """
        if namespace:
            return False

        if data is None or not isinstance(data, dict):
            return False

        for node_name, node_state in data.items():
            if node_state is None or not isinstance(node_state, dict):
                continue

            if node_name == "writer_node":
                await self._on_writer_update(node_state)
            elif node_name == "router_node":
                await self._on_router_update(node_state)
            elif node_name == "editor_node":
                await self._on_editor_update(node_state)
            elif node_name == "response_node" and "final_response" in node_state:
                await self._on_response_update(node_state)

        if "__interrupt__" in data:
            return await self._on_interrupt(data["__interrupt__"])

        return False

    # -------------------------------------------------------------------------
    # Custom event helpers
    # -------------------------------------------------------------------------

    async def _on_agent_progress(self, data: Dict[str, Any]) -> None:
        """Handles agent progress events with persistence on completion."""
        payload = data.get("payload", {})
        progress_data = {
            "query_num": payload.get("query_num", data.get("agent_id", "0")),
            "query": payload.get("query", ""),
            "phase": payload.get("phase", data.get("phase", "")),
            "percentage": payload.get("percentage", data.get("percentage", 0)),
            "current_step": payload.get("current_step", ""),
            "metadata": payload.get("metadata"),
            "timestamp": data.get("timestamp"),
        }

        await self._safe_send({"type": "agent_progress", "data": progress_data})

        if progress_data["phase"] == "completed" and self._thread_id:
            await self._persister.persist_event(
                self._thread_id,
                "agent_progress",
                content=progress_data.get("query", ""),
                metadata=progress_data,
            )

    async def _on_writer_progress(self, data: Dict[str, Any]) -> None:
        """Handles writer progress events with persistence on completion."""
        payload = data.get("payload", {})
        writer_data = {
            "percentage": payload.get("percentage", 0),
            "current_step": payload.get("current_step", ""),
            "phase": payload.get("phase", "writing"),
            "metadata": payload.get("metadata"),
            "timestamp": data.get("timestamp"),
        }

        await self._safe_send({"type": "writer_progress", "data": writer_data})

        meta = writer_data.get("metadata") or {}
        if (
            writer_data["percentage"] == 100
            and self._thread_id
            and meta.get("mode") != "edit"
        ):
            await self._persister.persist_event(
                self._thread_id,
                "writer_progress",
                content=writer_data.get("current_step", "Writer complete"),
                metadata=writer_data,
            )

    async def _on_tool_execution(self, data: Dict[str, Any]) -> None:
        """Handles tool execution events with persistence on completion."""
        payload = data.get("payload", {})
        await self._safe_send(
            {
                "type": "log",
                "data": {
                    "message": payload.get("description", ""),
                    "event_type": "tool_execution",
                    "tool_name": payload.get("tool_name", ""),
                    "status": payload.get("status", "running"),
                    "timestamp": data.get("timestamp"),
                },
            }
        )

        if self._thread_id and payload.get("status") == "completed":
            await self._persister.persist_event(
                self._thread_id,
                "tool_execution",
                content=payload.get("description", ""),
                metadata={
                    "tool_name": payload.get("tool_name", ""),
                    "status": "completed",
                },
            )

    # -------------------------------------------------------------------------
    # Update event helpers
    # -------------------------------------------------------------------------

    async def _on_writer_update(self, node_state: Dict[str, Any]) -> None:
        """Sends report to frontend and persists writer completion events."""
        reports = node_state.get("reports")
        if reports and isinstance(reports, list) and len(reports) > 0:
            report_data = reports[0]
            body_sections = report_data.get("body_sections", [])
            if body_sections:
                sorted_sections = sorted(
                    body_sections,
                    key=lambda s: s.get("section_order", 0),
                )
                await self._safe_send(
                    {
                        "type": "report",
                        "data": {
                            "reports": [
                                {
                                    **report_data,
                                    "body_sections": sorted_sections,
                                }
                            ],
                        },
                    }
                )
                await self._persister.persist_event(
                    self._thread_id,
                    "report_ready",
                    metadata={"has_report": True},
                )
                await self._persister.persist_event(
                    self._thread_id,
                    "writer_summary",
                    content="Report generated",
                    metadata={"status": "completed"},
                )
                await self._persister.mark_report_ready(self._thread_id)
            return

        body_sections = node_state.get("report_body_sections")
        if not body_sections:
            return

        sorted_sections = sorted(
            body_sections,
            key=lambda s: s.get("section_order", 0),
        )
        await self._safe_send(
            {
                "type": "report",
                "data": {
                    "reports": [
                        {
                            "run_id": node_state.get("current_run_id", ""),
                            "query": node_state.get("user_query", ""),
                            "body_sections": sorted_sections,
                            "table_of_contents": node_state.get(
                                "report_table_of_contents", ""
                            ),
                            "abstract": node_state.get("report_abstract", ""),
                            "introduction": node_state.get("report_introduction", ""),
                            "conclusion": node_state.get("report_conclusion", ""),
                        }
                    ],
                },
            }
        )

        await self._persister.persist_event(
            self._thread_id,
            "report_ready",
            metadata={"has_report": True},
        )
        await self._persister.persist_event(
            self._thread_id,
            "writer_summary",
            content="Report generated",
            metadata={"status": "completed"},
        )
        await self._persister.mark_report_ready(self._thread_id)

    async def _on_router_update(self, node_state: Dict[str, Any]) -> None:
        """Sends router reasoning to frontend and persists intent classification."""
        reasoning = node_state.get("router_thinking")
        intent = node_state.get("intent_type", "")
        if not reasoning:
            return

        await self._safe_send(
            {
                "type": "log",
                "data": {
                    "message": f"Router Logic: {reasoning}",
                    "event_type": "router_log",
                },
            }
        )

        await self._persister.persist_event(
            self._thread_id,
            "router_thinking",
            content=reasoning,
            metadata={"intent_type": intent},
        )
        if intent:
            await self._persister.update_intent(self._thread_id, intent)

    async def _on_editor_update(self, node_state: Dict[str, Any]) -> None:
        """Sends targeted report section update to frontend."""
        update = node_state.get("report_section_update")
        if not update:
            logger.info(
                "[ChunkRouter] editor_node update missing report_section_update"
            )
            return

        logger.info(
            f"[ChunkRouter] Sending report_section_update section_id={update.get('section_id')} run_id={update.get('run_id')}"
        )
        await self._safe_send(
            {
                "type": "report_section_update",
                "data": update,
            }
        )

        if self._thread_id:
            await self._persister.persist_event(
                self._thread_id,
                "report_section_update",
                content=str(
                    update.get("chapter_heading") or update.get("section_id") or ""
                ),
                metadata={
                    "section_id": update.get("section_id"),
                    "section_order": update.get("section_order"),
                },
            )

    async def _on_response_update(self, node_state: Dict[str, Any]) -> None:
        """Sends final response to frontend and marks session completed."""
        final_response = node_state.get("final_response")
        if not final_response:
            return

        await self._safe_send(
            {
                "type": "final_response",
                "data": final_response,
            }
        )

        await self._persister.persist_event(
            self._thread_id,
            "assistant_response",
            content=final_response,
        )
        await self._persister.mark_completed(self._thread_id)

    async def _on_interrupt(self, interrupts: Any) -> bool:
        """Sends interrupt to frontend, distinguishing clarification from plan review."""
        if not interrupts:
            return False

        interrupt_value = interrupts[0].value
        interrupt_type = interrupt_value.get("type", "plan_review")

        if interrupt_type == "clarification":
            await self._safe_send(
                {
                    "type": "interrupt",
                    "interrupt_type": "clarification",
                    "questions": interrupt_value.get("questions", []),
                    "loop_number": interrupt_value.get("loop_number", 1),
                }
            )
        else:
            plan_display = interrupt_value.get("plan_display", "")
            await self._safe_send(
                {
                    "type": "interrupt",
                    "interrupt_type": "plan_review",
                    "plan": plan_display,
                }
            )

        await self._persister.persist_event(
            self._thread_id,
            interrupt_type,
            content=json.dumps(interrupt_value, default=str),
            metadata={"interrupt_type": interrupt_type},
        )
        return True

    # -------------------------------------------------------------------------
    # LLM message tokens (with noise filtering)
    # -------------------------------------------------------------------------

    async def _handle_message_token(self, namespace: Any, payload: Any) -> None:
        """Filters and forwards LLM tokens to the frontend."""
        if (
            payload is None
            or not isinstance(payload, (tuple, list))
            or len(payload) < 2
        ):
            return

        msg_chunk, metadata = payload[0], payload[1]
        if metadata is None or not isinstance(metadata, dict):
            metadata = {}

        msg_type = getattr(msg_chunk, "type", "")
        node_name = metadata.get("langgraph_node", "")
        content = getattr(msg_chunk, "content", "")

        if not msg_type.lower().startswith("ai"):
            logger.info(f"[ChunkRouter] DROPPED msg: type={msg_type}, node={node_name}")
            return

        silenced_nodes = {
            "memory_node",
            "router_node",
            "writer_node",
            "parallel_research_node",
            "parallel_solver_node",
            "human_review_node",
            "clarification_node",
            "skill_selection_node",
            "report_style_node",
            "websearch_agent",
            "editor_node",
            "response_node",
            "model",
        }
        if node_name in silenced_nodes:
            return

        if namespace:
            return

        if node_name == "planner_node":
            token = msg_chunk.content if hasattr(msg_chunk, "content") else ""
            if token:
                if self._planner_json_started:
                    return

                scan = token if isinstance(token, str) else str(token)
                if "```json" in scan or "{" in scan:
                    self._planner_json_started = True
                    return

                await self._safe_send({"type": "token", "content": token})
            return

        if content:
            await self._safe_send({"type": "token", "content": content})
        else:
            logger.info(f"[ChunkRouter] EMPTY content from {node_name}")
