"""
Unified memory facade for Deep Research Agent.

Provides a single interface for both short-term (conversation)
and long-term (semantic) memory operations, coordinating
retrieval and storage across both systems.
"""

import os
import logging
from typing import List, Dict, Optional, Any

from dotenv import load_dotenv

from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from graphs.states.subgraph_state import MemoryContext

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryFacade:
    """
    Unified interface for all memory operations.
    
    Coordinates short-term (conversation history) and long-term
    (user facts, preferences) memory retrieval and storage.
    Provides context-building methods for the Planner and other nodes.
    """

    def __init__(
        self, 
        db_uri: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize memory facade with both memory systems.
        
        Args:
            db_uri: PostgreSQL connection string for persistence.
            embedding_model: Model for long-term memory embeddings.
        """
        self._db_uri = db_uri or os.getenv("DATABASE_URL")
        self._embedding_model = embedding_model
        self._short_term = ShortTermMemory(self._db_uri)
        self._long_term = LongTermMemory(self._db_uri, embedding_model)
        self._initialized = False

    async def initialize(self) -> None:
        """
        Initializes database connections for both memory systems.
        
        Must be called before using async methods.
        """
        if self._initialized:
            return
            
        await self._short_term.initialize()
        await self._long_term.initialize()
        self._initialized = True
        self._initialized = True
        logger.info("MemoryFacade fully initialized")

    async def shutdown(self) -> None:
        """Closes database connections."""
        if self._initialized:
            await self._short_term.shutdown()
            await self._long_term.shutdown()
            logger.info("MemoryFacade shut down")

    @property
    def short_term(self) -> ShortTermMemory:
        """Direct access to short-term memory for advanced operations."""
        return self._short_term

    @property
    def long_term(self) -> LongTermMemory:
        """Direct access to long-term memory for advanced operations."""
        return self._long_term

    @property
    def checkpointer(self):
        """Returns checkpointer for graph compilation."""
        return self._short_term.checkpointer

    async def get_context_for_planner(
        self, 
        thread_id: str, 
        user_id: str, 
        current_query: str,
        max_history_tokens: int = 2000
    ) -> MemoryContext:
        """
        Retrieves comprehensive memory context for the Planner.
        
        Combines relevant long-term memories with conversation summary
        to provide optimal context for plan generation.
        
        Args:
            thread_id: Current conversation thread.
            user_id: User identifier for long-term memory.
            current_query: The current user query for semantic search.
            max_history_tokens: Token limit for conversation history.
            
        Returns:
            MemoryContext with semantic_memories, user_profile, and summary.
        """
        if not self._initialized:
            await self.initialize()
            
        semantic_memories = await self._long_term.search_memories(
            user_id, 
            current_query, 
            limit=5
        )
        
        user_profile = await self._long_term.get_user_profile(user_id)
        
        conversation_history = await self._short_term.get_conversation_history(
            thread_id, 
            limit=50
        )
        
        conversation_summary = None
        if self._short_term.count_tokens(conversation_history) > max_history_tokens:
            conversation_summary = await self._short_term.summarize_conversation(
                conversation_history[:-4]
            )
        
        return MemoryContext(
            semantic_memories=[
                {"content": m.get("content", ""), "type": m.get("type", "fact")}
                for m in semantic_memories
            ],
            user_profile=user_profile,
            conversation_summary=conversation_summary
        )

    async def process_turn(
        self,
        thread_id: str,
        user_id: str,
        messages: List[Dict],
        extract_facts: bool = True
    ) -> None:
        """
        Post-turn processing to extract and store notable facts.
        
        Should be called after each conversation turn to learn
        from the interaction and store useful information.
        
        Args:
            thread_id: Current conversation thread.
            user_id: User identifier.
            messages: Recent messages from the turn.
            extract_facts: Whether to use LLM fact extraction.
        """
        if not self._initialized:
            await self.initialize()
            
        if not extract_facts or not messages:
            return
            
        try:
            facts = await self._short_term.extract_facts(messages)
            
            for fact in facts:
                fact_content = fact.get("fact", "")
                fact_type = fact.get("type", "fact")
                
                if fact_type not in LongTermMemory.MEMORY_TYPES:
                    fact_type = "fact"
                    
                if fact_content:
                    await self._long_term.store_memory(
                        user_id,
                        fact_type,
                        fact_content,
                        {"source_thread": thread_id}
                    )
                    
            logger.info(f"Processed turn: extracted {len(facts)} facts")
            
        except Exception as e:
            logger.error(f"Failed to process turn: {e}")

   
    async def add_chat_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
        tool_results: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Creates and returns a properly formatted chat message.
        
        The message should be added to state's chat_messages field.
        
        Args:
            thread_id: Current conversation thread.
            role: Message role (user, assistant, system, tool).
            content: Message text content.
            tool_calls: Optional tool calls from assistant.
            tool_results: Optional results from tool execution.
            metadata: Optional additional metadata.
            
        Returns:
            Formatted chat message dictionary.
        """
        return ShortTermMemory.create_message(
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
            metadata=metadata
        )

    async def get_conversation_state(self, thread_id: str) -> Optional[Dict]:
        """
        Retrieves full conversation state for a thread.
        
        Args:
            thread_id: Conversation thread identifier.
            
        Returns:
            State dictionary or None if not found.
        """
        if not self._initialized:
            await self.initialize()
            
        return await self._short_term.get_latest_state(thread_id)

    async def get_user_memories(
        self, 
        user_id: str,
        memory_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Gets all memories for a user.
        
        Args:
            user_id: User identifier.
            memory_type: Optional filter by type.
            
        Returns:
            List of memory dictionaries.
        """
        if not self._initialized:
            await self.initialize()
            
        return await self._long_term.get_all_memories(user_id, memory_type)

    async def store_user_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str = "fact",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Stores a memory for the user.
        
        Args:
            user_id: User identifier.
            content: Memory content text.
            memory_type: Type of memory (fact, preference, episodic, procedural).
            metadata: Optional additional metadata.
            
        Returns:
            Generated memory_id.
        """
        if not self._initialized:
            await self.initialize()
            
        return await self._long_term.store_memory(
            user_id, 
            memory_type, 
            content, 
            metadata
        )

    async def update_user_profile(
        self, 
        user_id: str, 
        updates: Dict
    ) -> None:
        """
        Updates user profile with new fields.
        
        Args:
            user_id: User identifier.
            updates: Fields to update in profile.
        """
        if not self._initialized:
            await self.initialize()
            
        await self._long_term.update_user_profile(user_id, updates)

    async def consolidate_user_memories(self, user_id: str) -> None:
        """
        Consolidates/merges similar memories for a user.
        
        Uses LLM to identify and merge duplicate or related memories.
        
        Args:
            user_id: User identifier.
        """
        if not self._initialized:
            await self.initialize()
            
        await self._long_term.consolidate_memories(user_id)

    def build_context_prompt(self, memory_context: MemoryContext) -> str:
        """
        Builds a formatted context string from MemoryContext.
        
        Formats memories and profile for inclusion in LLM prompts.
        
        Args:
            memory_context: Retrieved memory context.
            
        Returns:
            Formatted string for LLM context.
        """
        sections = []
        
        if memory_context.get("user_profile"):
            profile = memory_context["user_profile"]
            profile_text = ", ".join([f"{k}: {v}" for k, v in profile.items()])
            sections.append(f"User Profile: {profile_text}")
            
        if memory_context.get("semantic_memories"):
            memories = memory_context["semantic_memories"]
            if memories:
                memory_lines = [f"- {m.get('content', '')}" for m in memories]
                sections.append("Relevant User Facts:\n" + "\n".join(memory_lines))
                
        if memory_context.get("conversation_summary"):
            sections.append(f"Previous Context: {memory_context['conversation_summary']}")
            
        if not sections:
            return ""
            
        return "\n\n".join(sections)
