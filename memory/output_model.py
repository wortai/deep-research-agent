from typing import Any, Dict, List, Literal
from datetime import datetime

from pydantic import BaseModel, Field

MemoryType = Literal["fact", "preference", "episodic", "procedural", "style"]
MEMORY_TYPES = ["fact", "preference", "episodic", "procedural", "style"]


class MemoryItem(BaseModel):
    """Schema for a single long-term memory entry stored as Qdrant payload."""

    content: str
    memory_type: MemoryType = "fact"
    source_thread: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScoredMemory(BaseModel):
    """A retrieved memory annotated with search and reranking scores."""

    memory_id: str
    content: str
    memory_type: str
    semantic_score: float = 0.0
    rerank_score: float = 0.0
    created_at: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MergeGroup(BaseModel):
    """A group of memory indices the LLM wants to merge into one."""

    indices: List[int]
    merged_content: str


class ConsolidationAnalysis(BaseModel):
    """Structured LLM output for memory consolidation decisions."""

    merge: List[MergeGroup] = Field(default_factory=list)
    delete: List[int] = Field(default_factory=list)
    keep: List[int] = Field(default_factory=list)


class InlineDedup(BaseModel):
    """LLM decision when a new memory overlaps with existing ones."""

    action: Literal["merge", "new"]
    merged_content: str = ""
    replace_ids: List[str] = Field(default_factory=list)
