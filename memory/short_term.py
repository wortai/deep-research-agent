
"""
Short-term memory management for conversation history.

Provides PostgresSaver-based persistence with trimming, summarization,
and fact extraction capabilities for managing conversation context.
"""

import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.postgres.shallow import AsyncShallowPostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from psycopg_pool import AsyncConnectionPool

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    Manages thread-scoped conversation history via PostgresSaver.
    
    Provides retrieval, trimming, summarization, and fact extraction
    for maintaining optimal context window usage while preserving
    important conversation details.
    """

    def __init__(self, db_uri: Optional[str] = None):
        """
        Initialize short-term memory with optional PostgreSQL persistence.
        
        Args:
            db_uri: PostgreSQL connection string. If None, uses in-memory storage.
        """
        self._db_uri = db_uri or os.getenv("DATABASE_URL")
        self._checkpointer = None
        self._pool = None
        self._is_async = False
        
        if self._db_uri:
            try:
                # Initialize pool with open=False to allow async opening later
                # Add keepalives to prevent connection drops on remote DBs
                conn_kwargs = {
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 5
                }
                # Add automatic connection checking to prune dead connections
                self._pool = AsyncConnectionPool(
                    conninfo=self._db_uri, 
                    max_size=20, 
                    open=False, 
                    kwargs=conn_kwargs,
                    check=AsyncConnectionPool.check_connection
                )
                self._checkpointer = AsyncShallowPostgresSaver(self._pool)
                self._is_async = True
                logger.info("AsyncShallowPostgresSaver instantiated (pending initialization)")
            except Exception as e:
                logger.warning(f"Failed to configure PostgreSQL checkpointer: {e}. Using in-memory storage.")
                self._checkpointer = MemorySaver()
        else:
            self._checkpointer = MemorySaver()
            logger.info("ShortTermMemory initialized with MemorySaver (in-memory)")

    async def initialize(self) -> None:
        """
        Initializes the PostgresSaver connection asynchronously.
        
        Must be called before using async methods when using PostgreSQL.
        """
        if self._is_async and self._pool:
            try:
                await self._pool.open()
                
                # Setup tables/indexes using a dedicated autocommit connection.
                # This is required because 'CREATE INDEX CONCURRENTLY' cannot run inside a transaction properly
                # when facilitated by the pool's default behavior or AsyncPostgresSaver's setup logic.
                # Note: This connection is temporary and closed automatically after the block.
                if self._db_uri:
                    import psycopg
                    async with await psycopg.AsyncConnection.connect(self._db_uri, autocommit=True) as conn:
                        checkpointer = AsyncShallowPostgresSaver(conn)
                        await checkpointer.setup()

                logger.info("ShortTermMemory fully initialized with AsyncShallowPostgresSaver")
            except Exception as e:
                logger.error(f"Failed to initialize ShallowPostgresSaver: {e}")
                raise e

    async def shutdown(self) -> None:
        """Closes the connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("ShortTermMemory pool closed")

    @property
    def checkpointer(self):
        """Returns the underlying checkpointer for graph compilation."""
        if self._checkpointer is None:
            self._checkpointer = MemorySaver()
        return self._checkpointer

    async def get_conversation_history(
        self, 
        thread_id: str, 
        limit: int = 50
    ) -> List[Dict]:
        """
        Retrieves chat messages for the given thread.
        
        Args:
            thread_id: Conversation thread identifier.
            limit: Maximum number of messages to return.
            
        Returns:
            List of chat message dictionaries, most recent first.
        """
        if self._checkpointer is None:
            return []
            
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            if self._is_async:
                checkpoint = await self._checkpointer.aget_tuple(config)
            else:
                checkpoint = self._checkpointer.get_tuple(config)
                
            if checkpoint and checkpoint.checkpoint:
                messages = checkpoint.checkpoint.get("channel_values", {}).get("chat_messages", [])
                logger.info(
                    f"[ShortTermMemory] thread={thread_id}, "
                    f"retrieved {len(messages)} chat_messages, "
                    f"first_msg_id={messages[0].get('message_id', 'N/A') if messages else 'NONE'}"
                )
                return messages[-limit:] if len(messages) > limit else messages
            else:
                logger.info(f"[ShortTermMemory] thread={thread_id}, no checkpoint found")
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            
        return []

    async def get_latest_state(self, thread_id: str) -> Optional[Dict]:
        """
        Gets the most recent state snapshot for the thread.
        
        Args:
            thread_id: Conversation thread identifier.
            
        Returns:
            Full state dictionary or None if not found.
        """
        if self._checkpointer is None:
            return None
            
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            if self._is_async:
                checkpoint = await self._checkpointer.aget_tuple(config)
            else:
                checkpoint = self._checkpointer.get_tuple(config)
                
            if checkpoint and checkpoint.checkpoint:
                return checkpoint.checkpoint.get("channel_values", {})
        except Exception as e:
            logger.error(f"Failed to retrieve latest state: {e}")
            
        return None

    def trim_by_token_count(
        self, 
        messages: List[Dict], 
        max_tokens: int = 4000
    ) -> List[Dict]:
        """
        Trims messages to fit within token limit, keeping most recent.
        
        Uses approximate token counting (4 chars = 1 token) for speed.
        
        Args:
            messages: List of chat message dictionaries.
            max_tokens: Maximum allowed token count.
            
        Returns:
            Trimmed list of messages within token limit.
        """
        if not messages:
            return []
            
        total_tokens = self.count_tokens(messages)
        
        if total_tokens <= max_tokens:
            return messages
            
        trimmed = []
        current_tokens = 0
        
        for msg in reversed(messages):
            msg_tokens = self._estimate_message_tokens(msg)
            if current_tokens + msg_tokens <= max_tokens:
                trimmed.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
                
        logger.info(f"Trimmed {len(messages) - len(trimmed)} messages to fit token limit")
        return trimmed

    def trim_by_message_count(
        self, 
        messages: List[Dict], 
        max_messages: int = 20
    ) -> List[Dict]:
        """
        Keeps only the last N messages.
        
        Args:
            messages: List of chat message dictionaries.
            max_messages: Maximum number of messages to keep.
            
        Returns:
            List containing at most max_messages recent messages.
        """
        if len(messages) <= max_messages:
            return messages
            
        trimmed = messages[-max_messages:]
        logger.info(f"Trimmed to last {max_messages} messages")
        return trimmed

    def smart_trim(
        self, 
        messages: List[Dict], 
        max_tokens: int = 4000
    ) -> List[Dict]:
        """
        Smart trimming that preserves important context.
        
        Keeps:
        - System messages (always)
        - First user message (initial context)
        - Messages with tool calls (important actions)
        - Most recent messages (current context)
        
        Args:
            messages: List of chat message dictionaries.
            max_tokens: Maximum allowed token count.
            
        Returns:
            Trimmed messages preserving important context.
        """
        if not messages or self.count_tokens(messages) <= max_tokens:
            return messages
            
        system_msgs = [m for m in messages if m.get("role") == "system"]
        first_user = next((m for m in messages if m.get("role") == "user"), None)
        tool_msgs = [m for m in messages if m.get("tool_calls") or m.get("tool_results")]
        recent_msgs = messages[-6:] if len(messages) > 6 else messages
        
        important = []
        seen_ids = set()
        
        for msg_list in [system_msgs, [first_user] if first_user else [], tool_msgs, recent_msgs]:
            for msg in msg_list:
                if msg and msg.get("message_id") not in seen_ids:
                    important.append(msg)
                    seen_ids.add(msg.get("message_id"))
        
        important.sort(key=lambda m: messages.index(m) if m in messages else 0)
        
        if self.count_tokens(important) > max_tokens:
            return self.trim_by_token_count(important, max_tokens)
            
        return important

    async def summarize_conversation(
        self, 
        messages: List[Dict],
        llm: Any = None
    ) -> str:
        """
        Uses LLM to create concise summary of conversation.
        
        Args:
            messages: List of chat message dictionaries to summarize.
            llm: LangChain LLM instance. Uses default if None.
            
        Returns:
            Concise summary string.
        """
        if not messages:
            return ""
            
        if llm is None:
            from llms.llms import LlmsHouse
            llm = LlmsHouse.google_model("gemini-2.0-flash")
            
        conversation_text = self._format_messages_for_summary(messages)
        
        prompt = f"""Summarize the following conversation concisely.
Include key facts, decisions, user preferences, and important context.
Keep the summary under 200 words.

Conversation:
{conversation_text}

Summary:"""

        try:
            response = await llm.ainvoke(prompt)
            summary = response.content if hasattr(response, 'content') else str(response)
            logger.info(f"Generated conversation summary: {len(summary)} chars")
            return summary
        except Exception as e:
            logger.error(f"Failed to summarize conversation: {e}")
            return ""

    async def extract_facts(
        self, 
        messages: List[Dict],
        llm: Any = None
    ) -> List[Dict]:
        """
        Extracts key facts and decisions from conversation.
        
        Args:
            messages: List of chat message dictionaries.
            llm: LangChain LLM instance. Uses default if None.
            
        Returns:
            List of fact dictionaries with 'fact' and 'type' keys.
        """
        if not messages:
            return []
            
        if llm is None:
            from llms.llms import LlmsHouse
            llm = LlmsHouse.google_model("gemini-2.0-flash")
            
        conversation_text = self._format_messages_for_summary(messages[-10:])
        
        prompt = f"""Extract key facts from this conversation.
Return a JSON array of objects with "fact" and "type" keys.
Types: "preference", "decision", "context", "requirement"

Only extract concrete, useful facts. If nothing notable, return empty array.

Conversation:
{conversation_text}

Facts (JSON array):"""

        try:
            response = await llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            import json
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                    
            facts = json.loads(content)
            logger.info(f"Extracted {len(facts)} facts from conversation")
            return facts if isinstance(facts, list) else []
        except Exception as e:
            logger.error(f"Failed to extract facts: {e}")
            return []

    def count_tokens(self, messages: List[Dict]) -> int:
        """
        Estimates token count for messages.
        
        Uses 4 characters per token approximation for speed.
        
        Args:
            messages: List of chat message dictionaries.
            
        Returns:
            Estimated token count.
        """
        total_chars = sum(self._estimate_message_tokens(m) * 4 for m in messages)
        return total_chars // 4

    def _estimate_message_tokens(self, message: Dict) -> int:
        """Estimates tokens for a single message."""
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
        tool_results = message.get("tool_results", [])
        
        char_count = len(content)
        
        if tool_calls:
            char_count += len(str(tool_calls))
        if tool_results:
            char_count += len(str(tool_results))
            
        return char_count // 4 + 4

    def _format_messages_for_summary(self, messages: List[Dict]) -> str:
        """Formats messages into readable text for LLM."""
        lines = []
        for msg in messages:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")[:500]
            lines.append(f"{role}: {content}")
            
            if msg.get("tool_calls"):
                lines.append(f"  [Tool calls: {len(msg['tool_calls'])} calls]")
                
        return "\n".join(lines)

    @staticmethod
    def create_message(
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
        tool_results: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Factory method to create a properly formatted chat message.
        
        Args:
            role: Message role (user, assistant, system, tool).
            content: Message text content.
            tool_calls: Optional tool calls made by assistant.
            tool_results: Optional results from tool execution.
            metadata: Optional additional metadata.
            
        Returns:
            Chat message dictionary.
        """
        return {
            "message_id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tool_calls": tool_calls,
            "tool_results": tool_results,
            "metadata": metadata
        }
