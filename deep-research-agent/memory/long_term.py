"""
Long-term memory backed by Qdrant.

Stores durable user insights (facts, preferences, episodic events,
procedural patterns, tone/style) with hybrid retrieval:
  1. Dense embedding (OpenAI text-embedding-3-small)
  2. CrossEncoder reranking for precision

Inline dedup: before inserting a new memory, searches for similar
existing ones and asks an LLM to merge or create new.

Collection: wort-long-term-memory (multitenancy on user-id).
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from memory.output_model import (
    MemoryItem, ScoredMemory, InlineDedup,
    ConsolidationAnalysis, MEMORY_TYPES,
)

load_dotenv()
logger = logging.getLogger(__name__)

COLLECTION_NAME = "wort-long-term-memory"
DENSE_VECTOR_NAME = "dense-vector"
DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.75


class LongTermMemory:
    """
    Manages durable, cross-session user memories via Qdrant.

    Storage: Qdrant with dense (OpenAI) vectors.
    Retrieval: dense search → optional CrossEncoder reranking.
    Dedup: before every insert, searches for overlapping memories
    and uses an LLM to merge if appropriate.
    """

    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        reranker_enabled: bool = True,
    ):
        self._qdrant_url = qdrant_url or os.getenv("QDRANT_URL")
        self._qdrant_api_key = qdrant_api_key or os.getenv("QDRANT_API_KEY")
        self._reranker_enabled = reranker_enabled

        self._client = None
        self._embedder = None
        self._reranker = None

    async def initialize(self) -> None:
        """Opens Qdrant connection, loads embedder and reranker."""
        self._initialize_client()
        self._initialize_embedder()
        self._initialize_reranker()

    async def shutdown(self) -> None:
        """Closes underlying Qdrant connection."""
        if self._client:
            self._client.close()
            logger.info("LongTermMemory: Qdrant client closed")

    # ------------------------------------------------------------------
    #  STORE (with inline dedup)
    # ------------------------------------------------------------------

    async def store_memory(
        self,
        user_id: str,
        memory_type: str,
        content: str,
        source_thread: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Stores a memory after checking for similar existing ones.
        If overlapping memories are found, asks an LLM to merge
        or insert as new. Returns the stored/merged memory ID.
        """
        if memory_type not in MEMORY_TYPES:
            raise ValueError(f"memory_type must be one of {MEMORY_TYPES}, got '{memory_type}'")

        if not self._client or not self._embedder:
            logger.warning("LongTermMemory: not initialized, memory not persisted")
            return ""

        similar = await self.search(
            user_id, content, memory_types=[memory_type], limit=10, rerank=False,
        )
        high_similarity = [m for m in similar if m.semantic_score >= SIMILARITY_THRESHOLD]

        if high_similarity:
            merged_id = await self._try_inline_merge(
                user_id, content, memory_type, high_similarity, source_thread, metadata,
            )
            if merged_id:
                return merged_id

        return await self._insert_point(user_id, content, memory_type, source_thread, metadata)

    async def store_batch(
        self,
        user_id: str,
        items: List[Dict[str, Any]],
        source_thread: str = "",
    ) -> List[str]:
        """Stores multiple memories with inline dedup per item."""
        ids: List[str] = []
        for entry in items:
            mid = await self.store_memory(
                user_id=user_id,
                memory_type=entry.get("memory_type", "fact"),
                content=entry.get("content", ""),
                source_thread=source_thread,
                metadata=entry.get("metadata"),
            )
            ids.append(mid)
        return ids

    # ------------------------------------------------------------------
    #  SEARCH
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
        Retrieves memories via dense vector search with optional
        memory-type filtering and CrossEncoder reranking.
        """
        if not self._client or not self._embedder:
            return []

        from qdrant_client.models import Filter, FieldCondition, MatchValue

        must_conditions = [FieldCondition(key="user-id", match=MatchValue(value=user_id))]
        if memory_types and len(memory_types) == 1:
            must_conditions.append(
                FieldCondition(key="memory_type", match=MatchValue(value=memory_types[0]))
            )

        oversample = 20 if rerank else limit
        dense_vector = self._embed_dense(query)

        results = self._client.query_points(
            collection_name=COLLECTION_NAME,
            query=dense_vector,
            using=DENSE_VECTOR_NAME,
            query_filter=Filter(must=must_conditions),
            limit=oversample,
            with_payload=True,
        )

        candidates = self._results_to_scored(results.points)

        if memory_types and len(memory_types) > 1:
            candidates = [c for c in candidates if c.memory_type in memory_types]

        if rerank and self._reranker_enabled and self._reranker and len(candidates) > 1:
            candidates = self._rerank(query, candidates)

        return candidates[:limit]

    # ------------------------------------------------------------------
    #  GET / DELETE
    # ------------------------------------------------------------------

    async def get_all(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[ScoredMemory]:
        """Lists all memories for a user, optionally filtered by type."""
        if not self._client:
            return []

        from qdrant_client.models import Filter, FieldCondition, MatchValue

        must_conditions = [FieldCondition(key="user-id", match=MatchValue(value=user_id))]
        if memory_type:
            must_conditions.append(
                FieldCondition(key="memory_type", match=MatchValue(value=memory_type))
            )

        results, _ = self._client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(must=must_conditions),
            limit=limit,
            with_payload=True,
        )

        return [
            ScoredMemory(
                memory_id=str(pt.id),
                content=pt.payload.get("content", ""),
                memory_type=pt.payload.get("memory_type", "fact"),
                created_at=pt.payload.get("created_at", ""),
                metadata=pt.payload.get("metadata", {}),
            )
            for pt in results
        ]

    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Deletes a single memory point by ID."""
        if not self._client:
            return False

        from qdrant_client.models import PointIdsList

        self._client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=PointIdsList(points=[memory_id]),
        )
        logger.info(f"Deleted memory {memory_id[:8]}…")
        return True

    # ------------------------------------------------------------------
    #  CONSOLIDATION (LLM-driven batch cleanup)
    # ------------------------------------------------------------------

    async def consolidate(self, user_id: str, llm: Any = None) -> Dict[str, int]:
        """
        Batch cleanup of all memories using LLM-driven dedup.
        Newer timestamps take priority over older ones.

        Returns: {"merged": N, "deleted": N, "kept": N}.
        """
        memories = await self.get_all(user_id)
        if len(memories) < 5:
            return {"merged": 0, "deleted": 0, "kept": len(memories)}

        if llm is None:
            from llms.llms import LlmsHouse
            llm = LlmsHouse.google_model("gemini-2.0-flash")

        from Prompts.memory_prompts import get_memory_consolidation_prompt

        numbered = "\n".join(
            f"{i + 1}. [{m.memory_type}] (created: {m.created_at}) {m.content}"
            for i, m in enumerate(memories)
        )

        prompt = get_memory_consolidation_prompt(numbered)

        try:
            response = await llm.ainvoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            analysis = ConsolidationAnalysis.model_validate_json(self._strip_code_fences(raw))
            return await self._apply_consolidation(user_id, memories, analysis)

        except Exception as exc:
            logger.error(f"Consolidation failed: {exc}")
            return {"merged": 0, "deleted": 0, "kept": len(memories)}

    async def _apply_consolidation(
        self,
        user_id: str,
        memories: List[ScoredMemory],
        analysis: ConsolidationAnalysis,
    ) -> Dict[str, int]:
        """Executes the merge/delete/keep actions from the LLM analysis."""
        merged_count, deleted_count = 0, 0

        for group in analysis.merge:
            if len(group.indices) >= 2 and group.merged_content:
                source_type = memories[group.indices[0] - 1].memory_type
                await self._insert_point(user_id, group.merged_content, source_type)
                merged_count += 1
                for idx in group.indices:
                    if 0 < idx <= len(memories):
                        await self.delete_memory(user_id, memories[idx - 1].memory_id)
                        deleted_count += 1

        for idx in analysis.delete:
            if 0 < idx <= len(memories):
                await self.delete_memory(user_id, memories[idx - 1].memory_id)
                deleted_count += 1

        kept = len(analysis.keep)
        logger.info(
            f"Consolidation for {user_id}: merged={merged_count}, "
            f"deleted={deleted_count}, kept={kept}"
        )
        return {"merged": merged_count, "deleted": deleted_count, "kept": kept}

    # ------------------------------------------------------------------
    #  USER PROFILE
    # ------------------------------------------------------------------

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves all profile-type memories as a combined profile dict."""
        if not self._client:
            return None

        from qdrant_client.models import Filter, FieldCondition, MatchValue

        results, _ = self._client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(must=[
                FieldCondition(key="user-id", match=MatchValue(value=user_id)),
                FieldCondition(key="memory_type", match=MatchValue(value="profile")),
            ]),
            limit=10,
            with_payload=True,
        )

        if not results:
            return None

        profile_entries = [pt.payload.get("content", "") for pt in results]
        return {"profile_facts": profile_entries}

    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> None:
        """
        Stores a profile update as a memory with memory_type='profile'.
        Inline dedup will merge it with existing profile entries if similar.
        """
        content = ", ".join(f"{k}: {v}" for k, v in updates.items())
        await self.store_memory(user_id, "profile", content)

    # ------------------------------------------------------------------
    #  PRIVATE — Inline dedup
    # ------------------------------------------------------------------

    async def _try_inline_merge(
        self,
        user_id: str,
        new_content: str,
        memory_type: str,
        similar_memories: List[ScoredMemory],
        source_thread: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Asks LLM if the new memory should merge with similar existing ones.
        Returns the merged memory ID if merged, None if the LLM says "new".
        """
        from llms.llms import LlmsHouse
        from Prompts.memory_prompts import get_inline_dedup_prompt

        llm = LlmsHouse.google_model("gemini-2.0-flash")

        existing_formatted = "\n".join(
            f"ID: {m.memory_id} | Type: {m.memory_type} | Created: {m.created_at} | Content: {m.content}"
            for m in similar_memories
        )

        prompt = get_inline_dedup_prompt(new_content, existing_formatted)

        try:
            response = await llm.ainvoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            decision = InlineDedup.model_validate_json(self._strip_code_fences(raw))

            if decision.action == "merge" and decision.merged_content:
                for old_id in decision.replace_ids:
                    await self.delete_memory(user_id, old_id)

                merged_id = await self._insert_point(
                    user_id, decision.merged_content, memory_type, source_thread, metadata,
                )
                logger.info(
                    f"Inline merged {len(decision.replace_ids)} memories → {merged_id[:8]}…"
                )
                return merged_id

            return None

        except Exception as exc:
            logger.warning(f"Inline dedup failed ({exc}), inserting as new")
            return None

    async def _insert_point(
        self,
        user_id: str,
        content: str,
        memory_type: str,
        source_thread: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Raw insert of a single point into Qdrant without dedup checks."""
        memory_id = str(uuid.uuid4())
        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            source_thread=source_thread,
            metadata=metadata or {},
        )

        dense_vector = self._embed_dense(content)

        from qdrant_client.models import PointStruct

        point = PointStruct(
            id=memory_id,
            vector={DENSE_VECTOR_NAME: dense_vector},
            payload={
                "user-id": user_id,
                "content": item.content,
                "memory_type": item.memory_type,
                "source_thread": item.source_thread,
                "created_at": item.created_at,
                "metadata": item.metadata,
            },
        )

        self._client.upsert(COLLECTION_NAME, points=[point])
        logger.info(f"Stored {memory_type} memory for user {user_id} (id={memory_id[:8]}…)")
        return memory_id

    # ------------------------------------------------------------------
    #  PRIVATE — Initialization
    # ------------------------------------------------------------------

    def _initialize_client(self) -> None:
        if not self._qdrant_url:
            logger.info("LongTermMemory: no QDRANT_URL; store unavailable")
            return

        try:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(
                url=self._qdrant_url,
                api_key=self._qdrant_api_key,
            )
            logger.info("LongTermMemory initialized with Qdrant")
        except Exception as exc:
            logger.warning(f"Failed to connect to Qdrant: {exc}")
            self._client = None

    def _initialize_embedder(self) -> None:
        try:
            from langchain_openai import OpenAIEmbeddings
            self._embedder = OpenAIEmbeddings(model="text-embedding-3-small")
        except Exception as exc:
            logger.warning(f"OpenAI embeddings unavailable: {exc}")
            self._embedder = None

    def _initialize_reranker(self) -> None:
        if not self._reranker_enabled:
            return
        try:
            from sentence_transformers import CrossEncoder
            self._reranker = CrossEncoder(DEFAULT_RERANKER_MODEL)
            logger.info(f"CrossEncoder reranker loaded: {DEFAULT_RERANKER_MODEL}")
        except Exception as exc:
            logger.warning(f"CrossEncoder unavailable ({exc}); reranking disabled")
            self._reranker = None
            self._reranker_enabled = False

    # ------------------------------------------------------------------
    #  PRIVATE — Embedding & Reranking
    # ------------------------------------------------------------------

    def _embed_dense(self, text: str) -> List[float]:
        """Generates dense embedding via OpenAI."""
        return self._embedder.embed_query(text)

    def _rerank(self, query: str, candidates: List[ScoredMemory]) -> List[ScoredMemory]:
        pairs = [(query, c.content) for c in candidates]
        scores = self._reranker.predict(pairs)
        for i, candidate in enumerate(candidates):
            candidate.rerank_score = float(scores[i])
        candidates.sort(key=lambda m: m.rerank_score, reverse=True)
        return candidates

    @staticmethod
    def _results_to_scored(points: list) -> List[ScoredMemory]:
        return [
            ScoredMemory(
                memory_id=str(pt.id),
                content=pt.payload.get("content", ""),
                memory_type=pt.payload.get("memory_type", "fact"),
                semantic_score=pt.score if hasattr(pt, "score") else 0.0,
                created_at=pt.payload.get("created_at", ""),
                metadata=pt.payload.get("metadata", {}),
            )
            for pt in points
        ]

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
