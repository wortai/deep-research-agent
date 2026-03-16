
from typing import Dict, Any
from datetime import datetime
from langchain_core.output_parsers import JsonOutputParser
from llms.llms import LlmsHouse
from graphs.states.subgraph_state import AgentGraphState
from router.router_prompt import INTENT_CLASSIFICATION_PROMPT
from memory.memory_facade import MemoryFacade
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentRouter:
    """
    Classifies user intent, generates response-improvement guidance,
    and flags messages for long-term memory storage.

    Routing target is always normalized from search_mode.
    LTM evaluation happens inline — dedup is handled at insert time
    by LongTermMemory.store_memory().
    """

    def __init__(self):
        """Initialize with LLM for context-aware classification."""
        self.llm = LlmsHouse.grok_model(
            model_name="grok-4-1-fast-reasoning",
            temperature=0.9,
        )
        self.parser = JsonOutputParser()
        self.chain = self.llm | self.parser

    @staticmethod
    def _normalize_search_mode(search_mode: str) -> str:
        """Normalizes frontend mode variants to graph-supported values."""
        normalized = (search_mode or "").strip().lower()
        if normalized in {"websearch", "web"}:
            return "websearch"
        if normalized in {"extremesearch", "extreme_search", "extreme"}:
            return "extremesearch"
        if normalized == "edit":
            return "edit"
        return "deepsearch"

    def _format_chat_history(self, chat_messages: list) -> str:
        """Format chat_messages for prompt context."""
        if not chat_messages:
            return "No previous conversation."

        lines = []
        for msg in chat_messages[-10:]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def _format_reports_summary(self, reports: list) -> str:
        """Create a summary of available reports for the router."""
        if not reports:
            return "No reports generated yet."

        summary = f"There are {len(reports)} reports available in this thread:\n"
        for i, r in enumerate(reports, 1):
            summary += f"- Report {i}: {r.get('query', 'Unknown Topic')}\n"
        return summary

    @staticmethod
    def _sanitize_improvement(instruction: str) -> str:
        """Ensures a stable fallback text for Improve_in_response."""
        cleaned = (instruction or "").strip()
        if not cleaned:
            return "No need to improve in response, we are doing good."
        return cleaned

    async def _process_ltm_action(self, result: Dict, state: AgentGraphState) -> None:
        """
        Stores a long-term memory or profile update when the LLM
        flags the user's message as containing durable information.

        Both "profile" and "memory" actions go through the same
        store_user_memory path — inline dedup handles merging
        with existing similar entries automatically.
        """
        ltm_action = (result.get("ltm_action") or "none").strip().lower()
        ltm_content = (result.get("ltm_content") or "").strip()

        if ltm_action == "none" or not ltm_content:
            return

        user_id = state.get("user_id", "00000000-0000-0000-0000-000000000000")

        facade = MemoryFacade()
        await facade.initialize()

        if ltm_action == "profile":
            await facade.store_user_memory(
                user_id=user_id,
                content=ltm_content,
                memory_type="profile",
            )
            logger.info(f"[IntentRouter] Stored profile: {ltm_content[:50]}…")

        elif ltm_action == "memory":
            ltm_type = (result.get("ltm_type") or "fact").strip().lower()
            await facade.store_user_memory(
                user_id=user_id,
                content=ltm_content,
                memory_type=ltm_type,
            )
            logger.info(f"[IntentRouter] Stored {ltm_type}: {ltm_content[:50]}…")

    async def route(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Produce router reasoning, route by search_mode, and evaluate
        the user's message for long-term memory storage.

        Args:
            state: Current state with user_query, chat_messages, reports, search_mode.

        Returns:
            State update with search_mode, router_thinking, improve_in_response,
            and chat_messages.
        """
        user_query = state.get("user_query", "")
        search_mode = self._normalize_search_mode(state.get("search_mode", "deepsearch"))
        chat_messages = state.get("chat_messages", [])
        reports = state.get("reports", [])

        if not user_query:
            logger.warning("[IntentRouter] No user query provided")
            return {
                "search_mode": search_mode,
                "current_phase": "routing",
                "router_thinking": "No query provided.",
                "improve_in_response": "No need to improve in response, we are doing good.",
            }

        prompt = INTENT_CLASSIFICATION_PROMPT.format(
            user_query=user_query,
            reports_summary=self._format_reports_summary(reports),
            chat_history=self._format_chat_history(chat_messages),
        )

        try:
            result = await self.chain.ainvoke(prompt)
            print(result)
            reasoning = (result.get("reasoning") or "I will proceed with the selected search mode.").strip()
            improve_in_response = self._sanitize_improvement(result.get("Improve_in_response", ""))

            logger.info(f"[IntentRouter] Routed by search_mode: {search_mode}")

            await self._process_ltm_action(result, state)

            routing_msg = self._build_routing_message(search_mode, reasoning, improve_in_response)

            return {
                "search_mode": search_mode,
                "current_phase": "routing",
                "router_thinking": reasoning,
                "improve_in_response": improve_in_response,
                "chat_messages": [routing_msg],
            }

        except Exception as e:
            logger.error(f"[IntentRouter] Classification failed: {e}")
            return {
                "search_mode": search_mode,
                "current_phase": "routing",
                "router_thinking": f"Fallback routing due to error: {e}",
                "improve_in_response": "No need to improve in response, we are doing good.",
            }

    @staticmethod
    def _build_routing_message(
        mode: str,
        reasoning: str,
        improve_in_response: str,
    ) -> Dict[str, Any]:
        """Creates a compact system message recording the routing decision."""
        return {
            "message_id": str(uuid.uuid4()),
            "role": "system",
            "content": (
                f"[Routed as: {mode}] {reasoning}\n"
            ),
            "timestamp": datetime.now().isoformat(),
            "metadata": {"message_type": "routing", "mode": mode},
        }


async def router_node(state: AgentGraphState) -> Dict[str, Any]:
    """LangGraph node wrapper for IntentRouter."""
    router = IntentRouter()
    return await router.route(state)
