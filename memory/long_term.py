"""
Long-term memory management for cross-thread user memories.

Provides PostgresStore-based persistence with semantic search,
multiple memory types, and CRUD operations for user facts,
preferences, and learned information.
"""

import os
import logging
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime
import uuid

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LongTermMemory:
    """
    Manages cross-thread user memories via PostgresStore.
    
    Supports multiple memory types:
    - Semantic (facts, knowledge about user)
    - Episodic (past interactions, experiences)
    - Procedural (user preferences, rules, patterns)
    
    Uses embeddings for semantic search across memories.
    """

    MEMORY_TYPES = ["fact", "preference", "episodic", "procedural"]

    def __init__(
        self, 
        db_uri: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize long-term memory with optional PostgreSQL persistence.
        
        Args:
            db_uri: PostgreSQL connection string. If None, uses in-memory storage.
            embedding_model: OpenAI embedding model name for semantic search.
        """
        self._db_uri = db_uri or os.getenv("DATABASE_URL")
        self._embedding_model = embedding_model
        self._store = None
        self._is_async = False
        self._memories: Dict[str, Dict[str, Dict]] = {}

    async def initialize(self) -> None:
        """
        Initializes the PostgresStore connection asynchronously.
        
        Must be called before using async methods when using PostgreSQL.
        """
        if self._db_uri:
            try:
                from langgraph.store.postgres import AsyncPostgresStore
                from langchain_openai import OpenAIEmbeddings
                
                embeddings = OpenAIEmbeddings(model=self._embedding_model)
                
                self._store = await AsyncPostgresStore.from_conn_string(
                    self._db_uri,
                    index={
                        "embed": embeddings,
                        "dims": 1536,
                        "fields": ["content"]
                    }
                )
                self._is_async = True
                
                # Should setup store if needed (create tables etc)
                # AsyncPostgresStore usually handles this or has a setup method
                if hasattr(self._store, 'setup'):
                     await self._store.setup()
                
                logger.info("LongTermMemory initialized with AsyncPostgresStore")
            except Exception as e:
                logger.warning(f"Failed to connect to PostgreSQL store: {e}. Using in-memory storage.")
                self._store = None
        else:
            logger.info("LongTermMemory initialized with in-memory storage")

    async def store_memory(
        self, 
        user_id: str, 
        memory_type: Literal["fact", "preference", "episodic", "procedural"],
        content: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Stores a memory item under the user's namespace.
        
        Args:
            user_id: User identifier for namespace.
            memory_type: Type of memory being stored.
            content: The memory content text.
            metadata: Optional additional metadata.
            
        Returns:
            Generated memory_id for the stored memory.
        """
        if memory_type not in self.MEMORY_TYPES:
            raise ValueError(f"memory_type must be one of {self.MEMORY_TYPES}")
            
        memory_id = str(uuid.uuid4())
        memory_data = {
            "content": content,
            "type": memory_type,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        if self._store:
            namespace = (user_id, "memories")
            try:
                await self._store.aput(namespace, memory_id, memory_data)
                logger.info(f"Stored {memory_type} memory for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to store memory: {e}")
                self._store_in_memory(user_id, memory_id, memory_data)
        else:
            self._store_in_memory(user_id, memory_id, memory_data)
            
        return memory_id

    async def store_user_profile(self, user_id: str, profile: Dict) -> None:
        """
        Stores or updates the user's profile/preferences.
        
        Args:
            user_id: User identifier.
            profile: Profile data dictionary.
        """
        profile_data = {
            "content": str(profile),
            "type": "profile",
            "profile": profile,
            "updated_at": datetime.now().isoformat()
        }
        
        if self._store:
            namespace = (user_id, "profile")
            try:
                await self._store.aput(namespace, "user_profile", profile_data)
                logger.info(f"Stored profile for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to store profile: {e}")
        else:
            if user_id not in self._memories:
                self._memories[user_id] = {}
            self._memories[user_id]["__profile__"] = profile_data

    async def search_memories(
        self, 
        user_id: str, 
        query: str, 
        memory_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Semantic search for relevant memories.
        
        Args:
            user_id: User identifier.
            query: Search query for semantic matching.
            memory_types: Optional filter by memory types.
            limit: Maximum results to return.
            
        Returns:
            List of matching memory dictionaries with scores.
        """
        if self._store:
            namespace = (user_id, "memories")
            try:
                results = await self._store.asearch(namespace, query=query, limit=limit)
                memories = []
                for item in results:
                    memory = item.value
                    memory["memory_id"] = item.key
                    memory["score"] = getattr(item, 'score', 1.0)
                    
                    if memory_types and memory.get("type") not in memory_types:
                        continue
                        
                    memories.append(memory)
                    
                return memories[:limit]
            except Exception as e:
                logger.error(f"Failed to search memories: {e}")
                return []
        else:
            return self._search_in_memory(user_id, query, memory_types, limit)

    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves user profile if exists.
        
        Args:
            user_id: User identifier.
            
        Returns:
            Profile dictionary or None.
        """
        if self._store:
            namespace = (user_id, "profile")
            try:
                result = await self._store.aget(namespace, "user_profile")
                if result:
                    return result.value.get("profile", result.value)
            except Exception as e:
                logger.error(f"Failed to get profile: {e}")
                return None
        else:
            if user_id in self._memories and "__profile__" in self._memories[user_id]:
                return self._memories[user_id]["__profile__"].get("profile")
                
        return None

    async def get_all_memories(
        self, 
        user_id: str, 
        memory_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Gets all memories for a user, optionally filtered.
        
        Args:
            user_id: User identifier.
            memory_type: Optional filter by type.
            
        Returns:
            List of memory dictionaries.
        """
        if self._store:
            namespace = (user_id, "memories")
            try:
                results = await self._store.asearch(namespace, limit=100)
                memories = []
                for item in results:
                    memory = item.value
                    memory["memory_id"] = item.key
                    
                    if memory_type and memory.get("type") != memory_type:
                        continue
                        
                    memories.append(memory)
                    
                return memories
            except Exception as e:
                logger.error(f"Failed to get memories: {e}")
                return []
        else:
            if user_id not in self._memories:
                return []
                
            memories = []
            for key, value in self._memories[user_id].items():
                if key.startswith("__"):
                    continue
                if memory_type and value.get("type") != memory_type:
                    continue
                memory = value.copy()
                memory["memory_id"] = key
                memories.append(memory)
                
            return memories

    async def update_memory(
        self, 
        user_id: str, 
        memory_id: str, 
        content: str
    ) -> bool:
        """
        Updates an existing memory's content.
        
        Args:
            user_id: User identifier.
            memory_id: ID of memory to update.
            content: New content text.
            
        Returns:
            True if update successful, False otherwise.
        """
        if self._store:
            namespace = (user_id, "memories")
            try:
                existing = await self._store.aget(namespace, memory_id)
                if existing:
                    updated_data = existing.value
                    updated_data["content"] = content
                    updated_data["updated_at"] = datetime.now().isoformat()
                    await self._store.aput(namespace, memory_id, updated_data)
                    logger.info(f"Updated memory {memory_id}")
                    return True
            except Exception as e:
                logger.error(f"Failed to update memory: {e}")
                return False
        else:
            if user_id in self._memories and memory_id in self._memories[user_id]:
                self._memories[user_id][memory_id]["content"] = content
                self._memories[user_id][memory_id]["updated_at"] = datetime.now().isoformat()
                return True
                
        return False

    async def update_user_profile(self, user_id: str, updates: Dict) -> None:
        """
        Partially updates user profile with new fields.
        
        Args:
            user_id: User identifier.
            updates: Dictionary of fields to update.
        """
        current_profile = await self.get_user_profile(user_id) or {}
        current_profile.update(updates)
        await self.store_user_profile(user_id, current_profile)

    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """
        Deletes a specific memory.
        
        Args:
            user_id: User identifier.
            memory_id: ID of memory to delete.
            
        Returns:
            True if deletion successful, False otherwise.
        """
        if self._store:
            namespace = (user_id, "memories")
            try:
                await self._store.adelete(namespace, memory_id)
                logger.info(f"Deleted memory {memory_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete memory: {e}")
                return False
        else:
            if user_id in self._memories and memory_id in self._memories[user_id]:
                del self._memories[user_id][memory_id]
                return True
                
        return False

    async def clear_user_memories(
        self, 
        user_id: str, 
        memory_type: Optional[str] = None
    ) -> int:
        """
        Clears all memories for user, optionally by type.
        
        Args:
            user_id: User identifier.
            memory_type: Optional type filter.
            
        Returns:
            Count of deleted memories.
        """
        memories = await self.get_all_memories(user_id, memory_type)
        deleted_count = 0
        
        for memory in memories:
            if await self.delete_memory(user_id, memory["memory_id"]):
                deleted_count += 1
                
        logger.info(f"Cleared {deleted_count} memories for user {user_id}")
        return deleted_count

    async def consolidate_memories(
        self, 
        user_id: str,
        llm: Any = None
    ) -> None:
        """
        Uses LLM to merge similar or duplicate memories.
        
        Reduces memory bloat by combining related facts.
        
        Args:
            user_id: User identifier.
            llm: LangChain LLM instance. Uses default if None.
        """
        memories = await self.get_all_memories(user_id)
        
        if len(memories) < 5:
            return
            
        if llm is None:
            from llms.llms import LlmsHouse
            llm = LlmsHouse.google_model("gemini-2.0-flash")
            
        memories_text = "\n".join([
            f"{i+1}. [{m['type']}] {m['content']}" 
            for i, m in enumerate(memories)
        ])
        
        prompt = f"""Review these memories and identify duplicates or memories that can be merged.
Return a JSON object with:
- "keep": list of memory numbers to keep unchanged
- "merge": list of objects with "indices" (numbers to merge) and "merged_content" (new text)
- "delete": list of memory numbers to delete (redundant/outdated)

Memories:
{memories_text}

Analysis (JSON):"""

        try:
            response = await llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            import json
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                    
            analysis = json.loads(content)
            
            for merge_group in analysis.get("merge", []):
                indices = merge_group.get("indices", [])
                merged_content = merge_group.get("merged_content", "")
                
                if len(indices) >= 2 and merged_content:
                    await self.store_memory(
                        user_id,
                        memories[indices[0] - 1].get("type", "fact"),
                        merged_content
                    )
                    
                    for idx in indices:
                        if 0 < idx <= len(memories):
                            await self.delete_memory(user_id, memories[idx - 1]["memory_id"])
                            
            for idx in analysis.get("delete", []):
                if 0 < idx <= len(memories):
                    await self.delete_memory(user_id, memories[idx - 1]["memory_id"])
                    
            logger.info(f"Consolidated memories for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to consolidate memories: {e}")

    def _store_in_memory(self, user_id: str, memory_id: str, data: Dict) -> None:
        """Stores memory in local dict when database unavailable."""
        if user_id not in self._memories:
            self._memories[user_id] = {}
        self._memories[user_id][memory_id] = data

    def _search_in_memory(
        self, 
        user_id: str, 
        query: str, 
        memory_types: Optional[List[str]], 
        limit: int
    ) -> List[Dict]:
        """Simple keyword search for in-memory storage."""
        if user_id not in self._memories:
            return []
            
        query_lower = query.lower()
        matches = []
        
        for key, value in self._memories[user_id].items():
            if key.startswith("__"):
                continue
                
            if memory_types and value.get("type") not in memory_types:
                continue
                
            content = value.get("content", "").lower()
            if query_lower in content:
                memory = value.copy()
                memory["memory_id"] = key
                memory["score"] = 1.0
                matches.append(memory)
                
        return matches[:limit]
