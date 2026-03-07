"""
Long-term memory system for cross-session user knowledge.

Stores durable user insights (facts, preferences, episodic events,
procedural patterns, tone/style) in PostgreSQL via LangGraph's
AsyncPostgresStore with OpenAI embeddings for semantic retrieval.

Retrieval pipeline:
  1. Semantic search via pgvector (dense embeddings)
  2. CrossEncoder reranking for precision
  3. Optional memory-type filtering

User-scoped by namespace: each user's memories live under
(user_id, "memories") so a single store table serves all users
with full isolation.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field
from Prompts.prompt import get_memory_consolidation_prompt

logger = logging.getLogger(__name__)

MemoryType = Literal["fact", "preference", "episodic", "procedural", "style"]

MEMORY_TYPES: List[str] = ["fact", "preference", "episodic", "procedural", "style"]

DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536
SEMANTIC_SEARCH_OVERSAMPLE = 20
CONSOLIDATION_BATCH_LIMIT = 50


class MemoryItem(BaseModel):
    """Schema for a single long-term memory entry stored in the value JSONB."""

    content: str
    memory_type: MemoryType = "fact"
    source_thread: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    access_count: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScoredMemory(BaseModel):
    """A memory item annotated with retrieval and reranking scores."""

    memory_id: str
    content: str
    memory_type: str
    confidence: float = 1.0
    semantic_score: float = 0.0
    rerank_score: float = 0.0
    created_at: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LongTermMemory:
    """
    Manages durable, cross-session user memories.

    Storage: LangGraph AsyncPostgresStore (pgvector for embeddings).
    Retrieval: dense semantic search → CrossEncoder reranking.
    Scoping: namespace tuple (user_id, "memories") isolates per user.
    """

    MEMORY_TYPES = MEMORY_TYPES

    def __init__(
        self,
        db_uri: Optional[str] = None,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        reranker_model: str = DEFAULT_RERANKER_MODEL,
        reranker_enabled: bool = True,
    ):
        self._db_uri = db_uri or self._load_db_uri()
        self._embedding_model = embedding_model
        self._reranker_model = reranker_model
        self._reranker_enabled = reranker_enabled

        self._store = None
        self._store_cm = None
        self._reranker = None
        self._fallback: Dict[str, Dict[str, Dict]] = {}

    async def initialize(self) -> None:
        """Opens the AsyncPostgresStore connection and loads the reranker."""
        await self._initialize_store()
        self._initialize_reranker()

    async def shutdown(self) -> None:
        """Gracefully closes underlying connections."""
        if self._store and hasattr(self._store, "pool"):
            await self._store.pool.close()
            logger.info("LongTermMemory store pool closed")

    # ------------------------------------------------------------------
    #  STORE
    # ------------------------------------------------------------------

    async def store_memory(
        self,
        user_id: str,
        memory_type: MemoryType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        source_thread: str = "",
        confidence: float = 1.0,
    ) -> str:
        """
        Persists a single memory for the user. Returns the generated memory_id.
        """
        self._validate_memory_type(memory_type)

        memory_id = str(uuid.uuid4())
        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            source_thread=source_thread,
            confidence=confidence,
            metadata=metadata or {},
        )

        if self._store:
            try:
                await self._store.aput(
                    self._namespace(user_id),
                    memory_id,
                    item.model_dump(),
                )
                logger.info(
                    f"Stored {memory_type} memory for user {user_id} "
                    f"(id={memory_id[:8]}…)"
                )
            except Exception as exc:
                logger.error(f"Failed to store memory: {exc}")
                self._put_fallback(user_id, memory_id, item.model_dump())
        else:
            self._put_fallback(user_id, memory_id, item.model_dump())

        return memory_id

    async def store_batch(
        self,
        user_id: str,
        items: List[Dict[str, Any]],
        source_thread: str = "",
    ) -> List[str]:
        """
        Stores multiple memories in one pass.

        Each dict in *items* must have at least "content" and "memory_type".
        Returns list of generated memory_ids.
        """
        ids: List[str] = []
        for entry in items:
            mid = await self.store_memory(
                user_id=user_id,
                memory_type=entry.get("memory_type", "fact"),
                content=entry.get("content", ""),
                metadata=entry.get("metadata"),
                source_thread=source_thread,
                confidence=entry.get("confidence", 1.0),
            )
            ids.append(mid)
        return ids

    # ------------------------------------------------------------------
    #  RETRIEVE
    # ------------------------------------------------------------------

    async def search(
        self,
        user_id: str,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 5,
        rerank: bool = True,
    ) -> List[ScoredMemory]:
        """
        Retrieves memories relevant to *query* using the full pipeline:
          1. Semantic (dense) search via pgvector
          2. Memory-type filtering
          3. CrossEncoder reranking (when enabled)

        Returns up to *limit* ScoredMemory items sorted by rerank_score.
        """
        if not self._store:
            return self._search_fallback(user_id, query, memory_types, limit)

        try:
            oversample = SEMANTIC_SEARCH_OVERSAMPLE if rerank else limit
            filter_dict = self._build_type_filter(memory_types)

            raw_results = await self._store.asearch(
                self._namespace(user_id),
                query=query,
                filter=filter_dict,
                limit=oversample,
            )

            candidates = self._results_to_scored(raw_results)

            if memory_types and len(memory_types) > 1:
                candidates = [c for c in candidates if c.memory_type in memory_types]

            if rerank and self._reranker_enabled and self._reranker and len(candidates) > 1:
                candidates = self._rerank(query, candidates)

            return candidates[:limit]

        except Exception as exc:
            logger.error(f"Memory search failed: {exc}")
            return []

    async def get_by_id(self, user_id: str, memory_id: str) -> Optional[ScoredMemory]:
        """Fetches a single memory by its ID."""
        if not self._store:
            data = self._fallback.get(user_id, {}).get(memory_id)
            if data:
                return self._dict_to_scored(memory_id, data)
            return None

        try:
            item = await self._store.aget(self._namespace(user_id), memory_id)
            if item:
                return self._dict_to_scored(item.key, item.value)
        except Exception as exc:
            logger.error(f"Failed to get memory {memory_id}: {exc}")
        return None

    async def get_all(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[ScoredMemory]:
        """Lists all memories for a user, optionally filtered by type."""
        if not self._store:
            return self._list_fallback(user_id, memory_type, limit)

        try:
            filter_dict = {"memory_type": memory_type} if memory_type else None
            results = await self._store.asearch(
                self._namespace(user_id),
                filter=filter_dict,
                limit=limit,
            )
            return self._results_to_scored(results)
        except Exception as exc:
            logger.error(f"Failed to list memories: {exc}")
            return []

    # ------------------------------------------------------------------
    #  UPDATE / DELETE
    # ------------------------------------------------------------------

    async def update_memory(
        self,
        user_id: str,
        memory_id: str,
        content: Optional[str] = None,
        metadata_updates: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None,
    ) -> bool:
        """
        Partially updates an existing memory. Only provided fields are changed.
        Re-embeds automatically because aput replaces the value JSONB.
        """
        if not self._store:
            return self._update_fallback(user_id, memory_id, content, metadata_updates, confidence)

        try:
            existing = await self._store.aget(self._namespace(user_id), memory_id)
            if not existing:
                return False

            data = existing.value
            if content is not None:
                data["content"] = content
            if metadata_updates:
                data.setdefault("metadata", {}).update(metadata_updates)
            if confidence is not None:
                data["confidence"] = confidence
            data["updated_at"] = datetime.now().isoformat()

            await self._store.aput(self._namespace(user_id), memory_id, data)
            logger.info(f"Updated memory {memory_id[:8]}…")
            return True
        except Exception as exc:
            logger.error(f"Failed to update memory: {exc}")
            return False

    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Deletes a single memory."""
        if not self._store:
            return self._delete_fallback(user_id, memory_id)

        try:
            await self._store.adelete(self._namespace(user_id), memory_id)
            logger.info(f"Deleted memory {memory_id[:8]}…")
            return True
        except Exception as exc:
            logger.error(f"Failed to delete memory: {exc}")
            return False

    async def clear_user_memories(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
    ) -> int:
        """Removes all memories for a user, optionally scoped to a type."""
        memories = await self.get_all(user_id, memory_type)
        deleted = 0
        for mem in memories:
            if await self.delete_memory(user_id, mem.memory_id):
                deleted += 1
        logger.info(f"Cleared {deleted} memories for user {user_id}")
        return deleted

    # ------------------------------------------------------------------
    #  CONSOLIDATION (LLM-driven deduplication / merge)
    # ------------------------------------------------------------------

    async def consolidate(
        self,
        user_id: str,
        llm: Any = None,
    ) -> Dict[str, int]:
        """
        Uses an LLM to identify and merge duplicate or overlapping memories.

        Returns a summary dict: {"merged": N, "deleted": N, "kept": N}.
        """
        memories = await self.get_all(user_id, limit=CONSOLIDATION_BATCH_LIMIT)
        if len(memories) < 5:
            return {"merged": 0, "deleted": 0, "kept": len(memories)}

        if llm is None:
            from llms.llms import LlmsHouse
            llm = LlmsHouse.google_model("gemini-2.0-flash")

        numbered = "\n".join(
            f"{i + 1}. [{m.memory_type}] {m.content}"
            for i, m in enumerate(memories)
        )

        prompt = get_memory_consolidation_prompt(numbered)

        try:
            response = await llm.ainvoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            raw = self._strip_code_fences(raw)

            import json
            analysis = json.loads(raw)

            merged_count, deleted_count = 0, 0

            for group in analysis.get("merge", []):
                indices = group.get("indices", [])
                merged_text = group.get("merged_content", "")
                if len(indices) >= 2 and merged_text:
                    source_type = memories[indices[0] - 1].memory_type
                    await self.store_memory(user_id, source_type, merged_text)
                    merged_count += 1
                    for idx in indices:
                        if 0 < idx <= len(memories):
                            await self.delete_memory(user_id, memories[idx - 1].memory_id)
                            deleted_count += 1

            for idx in analysis.get("delete", []):
                if 0 < idx <= len(memories):
                    await self.delete_memory(user_id, memories[idx - 1].memory_id)
                    deleted_count += 1

            kept = len(analysis.get("keep", []))
            logger.info(
                f"Consolidation for {user_id}: merged={merged_count}, "
                f"deleted={deleted_count}, kept={kept}"
            )
            return {"merged": merged_count, "deleted": deleted_count, "kept": kept}

        except Exception as exc:
            logger.error(f"Consolidation failed: {exc}")
            return {"merged": 0, "deleted": 0, "kept": len(memories)}

    # ------------------------------------------------------------------
    #  USER PROFILE (convenience namespace)
    # ------------------------------------------------------------------

    async def store_user_profile(self, user_id: str, profile: Dict[str, Any]) -> None:
        """Stores or replaces the user profile under a dedicated namespace."""
        data = {
            "content": str(profile),
            "profile": profile,
            "updated_at": datetime.now().isoformat(),
        }
        if self._store:
            try:
                await self._store.aput((user_id, "profile"), "user_profile", data)
            except Exception as exc:
                logger.error(f"Failed to store profile: {exc}")
        else:
            self._fallback.setdefault(user_id, {})["__profile__"] = data

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the user profile if it exists."""
        if self._store:
            try:
                item = await self._store.aget((user_id, "profile"), "user_profile")
                if item:
                    return item.value.get("profile", item.value)
            except Exception as exc:
                logger.error(f"Failed to get profile: {exc}")
                return None
        else:
            entry = self._fallback.get(user_id, {}).get("__profile__")
            if entry:
                return entry.get("profile")
        return None

    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> None:
        """Merges *updates* into the existing user profile."""
        current = await self.get_user_profile(user_id) or {}
        current.update(updates)
        await self.store_user_profile(user_id, current)

    # ==================================================================
    #  PRIVATE — Initialization
    # ==================================================================

    @staticmethod
    def _load_db_uri() -> Optional[str]:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("DATABASE_URL")

    async def _initialize_store(self) -> None:
        if not self._db_uri:
            logger.info("LongTermMemory running in fallback (in-memory) mode")
            return

        try:
            from langgraph.store.postgres import AsyncPostgresStore
            from langchain_openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(model=self._embedding_model)

            self._store_cm = AsyncPostgresStore.from_conn_string(
                self._db_uri,
                index={
                    "embed": embeddings,
                    "dims": EMBEDDING_DIMS,
                    "fields": ["content"],
                },
            )
            self._store = await self._store_cm.__aenter__()

            if hasattr(self._store, "setup"):
                await self._store.setup()

            logger.info("LongTermMemory initialized with AsyncPostgresStore")
        except Exception as exc:
            logger.warning(f"Failed to connect to PostgreSQL store: {exc}. Using fallback.")
            self._store = None

    def _initialize_reranker(self) -> None:
        if not self._reranker_enabled:
            return
        try:
            from sentence_transformers import CrossEncoder
            self._reranker = CrossEncoder(self._reranker_model)
            logger.info(f"CrossEncoder reranker loaded: {self._reranker_model}")
        except Exception as exc:
            logger.warning(f"CrossEncoder unavailable ({exc}); reranking disabled")
            self._reranker = None
            self._reranker_enabled = False

    # ==================================================================
    #  PRIVATE — Namespace & Validation
    # ==================================================================

    @staticmethod
    def _namespace(user_id: str) -> Tuple[str, str]:
        return (user_id, "memories")

    @staticmethod
    def _validate_memory_type(memory_type: str) -> None:
        if memory_type not in MEMORY_TYPES:
            raise ValueError(
                f"memory_type must be one of {MEMORY_TYPES}, got '{memory_type}'"
            )

    @staticmethod
    def _build_type_filter(memory_types: Optional[List[str]]) -> Optional[Dict[str, Any]]:
        """
        AsyncPostgresStore supports $eq/$ne/$gt/$gte/$lt/$lte but not $in.
        For a single type we can filter server-side; for multiple types
        we skip the filter and do client-side post-filtering.
        """
        if not memory_types or len(memory_types) != 1:
            return None
        return {"memory_type": memory_types[0]}

    # ==================================================================
    #  PRIVATE — Reranking
    # ==================================================================

    def _rerank(self, query: str, candidates: List[ScoredMemory]) -> List[ScoredMemory]:
        pairs = [(query, c.content) for c in candidates]
        scores = self._reranker.predict(pairs)

        for i, candidate in enumerate(candidates):
            candidate.rerank_score = float(scores[i])

        candidates.sort(key=lambda m: m.rerank_score, reverse=True)
        return candidates

    # ==================================================================
    #  PRIVATE — Result Mapping
    # ==================================================================

    @staticmethod
    def _results_to_scored(results: List) -> List[ScoredMemory]:
        scored: List[ScoredMemory] = []
        for item in results:
            val = item.value
            scored.append(
                ScoredMemory(
                    memory_id=item.key,
                    content=val.get("content", ""),
                    memory_type=val.get("memory_type", "fact"),
                    confidence=val.get("confidence", 1.0),
                    semantic_score=getattr(item, "score", 0.0) or 0.0,
                    rerank_score=0.0,
                    created_at=val.get("created_at", ""),
                    metadata=val.get("metadata", {}),
                )
            )
        return scored

    @staticmethod
    def _dict_to_scored(memory_id: str, data: Dict) -> ScoredMemory:
        return ScoredMemory(
            memory_id=memory_id,
            content=data.get("content", ""),
            memory_type=data.get("memory_type", "fact"),
            confidence=data.get("confidence", 1.0),
            semantic_score=0.0,
            rerank_score=0.0,
            created_at=data.get("created_at", ""),
            metadata=data.get("metadata", {}),
        )

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```", 1)[1]
            if text.startswith("json"):
                text = text[4:]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        return text.strip()

    # ==================================================================
    #  PRIVATE — In-memory fallback (dev / test only)
    # ==================================================================

    def _put_fallback(self, user_id: str, memory_id: str, data: Dict) -> None:
        self._fallback.setdefault(user_id, {})[memory_id] = data

    def _search_fallback(
        self,
        user_id: str,
        query: str,
        memory_types: Optional[List[str]],
        limit: int,
    ) -> List[ScoredMemory]:
        query_lower = query.lower()
        matches: List[ScoredMemory] = []
        for key, val in self._fallback.get(user_id, {}).items():
            if key.startswith("__"):
                continue
            if memory_types and val.get("memory_type") not in memory_types:
                continue
            if query_lower in val.get("content", "").lower():
                matches.append(self._dict_to_scored(key, val))
        return matches[:limit]

    def _list_fallback(
        self,
        user_id: str,
        memory_type: Optional[str],
        limit: int,
    ) -> List[ScoredMemory]:
        results: List[ScoredMemory] = []
        for key, val in self._fallback.get(user_id, {}).items():
            if key.startswith("__"):
                continue
            if memory_type and val.get("memory_type") != memory_type:
                continue
            results.append(self._dict_to_scored(key, val))
        return results[:limit]

    def _update_fallback(
        self,
        user_id: str,
        memory_id: str,
        content: Optional[str],
        metadata_updates: Optional[Dict[str, Any]],
        confidence: Optional[float],
    ) -> bool:
        data = self._fallback.get(user_id, {}).get(memory_id)
        if not data:
            return False
        if content is not None:
            data["content"] = content
        if metadata_updates:
            data.setdefault("metadata", {}).update(metadata_updates)
        if confidence is not None:
            data["confidence"] = confidence
        data["updated_at"] = datetime.now().isoformat()
        return True

    def _delete_fallback(self, user_id: str, memory_id: str) -> bool:
        if user_id in self._fallback and memory_id in self._fallback[user_id]:
            del self._fallback[user_id][memory_id]
            return True
        return False
