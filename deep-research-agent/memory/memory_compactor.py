"""
Memory compactor for chat_messages state channel.

Runs at the start of each graph invocation to keep chat_messages
within a token budget (20K context window). Summarizes the oldest
~5K tokens of messages into one system message (whole messages only;
we never cut a message mid-content) and keeps the rest as recent
context. Uses the custom _context_reset reducer to replace the list.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from llms.llms import LlmsHouse
from graphs.states.subgraph_state import AgentGraphState
from Prompts.prompt import get_conversation_summary_prompt

logger = logging.getLogger(__name__)


# Token budget: compact when over this; summarize a prefix of ~this many tokens
CONTEXT_WINDOW_MAX_TOKENS = 20_000
SUMMARIZE_TARGET_TOKENS = 5_000
CHARS_PER_TOKEN = 4


class MemoryCompactor:
    """
    Compacts chat_messages by token count: when total exceeds the context
    window (20K tokens), summarizes the oldest ~5K tokens (whole messages
    only) and replaces that prefix with a single summary message.
    """

    def __init__(self):
        self._llm = LlmsHouse.google_model("gemini-2.0-flash")

    async def compact_if_needed(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Compacts when total tokens exceed CONTEXT_WINDOW_MAX_TOKENS.

        Splits messages into "old" (prefix totaling ~SUMMARIZE_TARGET_TOKENS,
        whole messages only) and "recent" (rest). Replaces old with one summary
        message. Returns empty dict when no compaction needed.
        """
        chat_messages = state.get("chat_messages", [])

        if not self._needs_compaction(chat_messages):
            return {}

        old, recent = self._split_old_and_recent(chat_messages)
        if not old:
            return {}

        existing_summary = self._extract_existing_summary(old)
        non_summary_old = [
            m for m in old
            if not self._is_summary_message(m)
        ]
        if not non_summary_old:
            # Only summary messages in "old"; replace with just recent
            return {
                "chat_messages": [
                    {"_context_reset": True},
                    *recent,
                ]
            }

        summary_text = await self._summarize(existing_summary, non_summary_old)

        summary_msg = {
            "message_id": str(uuid.uuid4()),
            "role": "system",
            "content": summary_text,
            "timestamp": datetime.now().isoformat(),
            "message_type": "summary",
            "metadata": {
                "message_type": "summary",
                "covers_until": old[-1].get("timestamp", "") if old else "",
                "compacted_count": len(non_summary_old),
            },
        }

        logger.info(
            f"[MemoryCompactor] Compacted {len(old)} messages (~{self._total_tokens(old)} tokens) "
            f"into summary, keeping {len(recent)} recent"
        )

        return {
            "chat_messages": [
                {"_context_reset": True},
                summary_msg,
                *recent,
            ]
        }

    # ------------------------------------------------------------------
    # Token and split logic
    # ------------------------------------------------------------------

    def _needs_compaction(self, messages: List[Dict]) -> bool:
        """True when total estimated tokens exceed the context window."""
        if not messages:
            return False
        return self._total_tokens(messages) > CONTEXT_WINDOW_MAX_TOKENS

    def _estimate_tokens(self, message: Dict) -> int:
        """
        Token estimate from message content only.

        chat_messages in our state store all displayable text in the "content"
        field (see subgraph_state.ChatMessage and create_message usage).
        len() on a str is O(1) in Python.
        """
        content = message.get("content", "")
        return len(content) // CHARS_PER_TOKEN + 4

    def _total_tokens(self, messages: List[Dict]) -> int:
        return sum(self._estimate_tokens(m) for m in messages)

    def _split_old_and_recent(
        self, messages: List[Dict]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Splits messages into (old, recent). "Old" is the longest prefix
        whose total tokens are at least SUMMARIZE_TARGET_TOKENS, using
        whole messages only (we never cut a message). If a single
        message exceeds 5K tokens, we still include it whole in "old".
        """
        if not messages:
            return [], []

        cumulative = 0
        split_index = 0
        for i, msg in enumerate(messages):
            cumulative += self._estimate_tokens(msg)
            if cumulative >= SUMMARIZE_TARGET_TOKENS:
                split_index = i + 1
                break
        else:
            # All messages together are under 5K; summarize all but last one
            # so we always keep at least one "recent" if there's more than one
            if len(messages) <= 1:
                return [], messages
            split_index = len(messages) - 1

        return messages[:split_index], messages[split_index:]

    def _is_summary_message(self, message: Dict) -> bool:
        """True if message is a prior compaction summary."""
        return message.get("metadata", {}).get("message_type") == "summary"

    def _extract_existing_summary(self, messages: List[Dict]) -> str:
        """Pulls content from a prior summary message if one exists."""
        for msg in messages:
            if self._is_summary_message(msg):
                return msg.get("content", "")
        return ""

    # ------------------------------------------------------------------
    # Summarization with <summary> tag and imported prompt
    # ------------------------------------------------------------------

    async def _summarize(
        self, existing_summary: str, messages: List[Dict]
    ) -> str:
        """
        Uses the prompt from Prompts.prompt to summarize. Stores the model
        response as-is (including <summary></summary> tags) so downstream
        models see the summary block clearly in context.
        """
        parts: List[str] = []
        for msg in messages:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            msg_type = msg.get("metadata", {}).get("message_type", "")
            label = f" ({msg_type})" if msg_type and msg_type != "text" else ""
            parts.append(f"{role}{label}: {content}")

        conversation_text = "\n".join(parts)
        prompt = get_conversation_summary_prompt(conversation_text, previous_summary=existing_summary)

        try:
            response = await self._llm.ainvoke(prompt)
            summary = response.content if hasattr(response, "content") else str(response)
            logger.info(f"[MemoryCompactor] Generated summary ({len(summary)} chars)")
            return summary.strip()
        except Exception as e:
            logger.error(f"[MemoryCompactor] Summarization failed: {e}")
            if existing_summary:
                return existing_summary
            return "Previous conversation context unavailable."


async def memory_node(state: AgentGraphState) -> Dict[str, Any]:
    """LangGraph node entry point — compacts chat_messages if over budget."""
    compactor = MemoryCompactor()
    return await compactor.compact_if_needed(state)
