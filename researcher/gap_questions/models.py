"""
Data models for Gap Question Generator
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class StopCondition(Enum):
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    CONFIDENCE_THRESHOLD_MET = "confidence_threshold_met"
    MAX_DEPTH_REACHED = "max_depth_reached"
    QUEUE_EMPTY = "queue_empty"


@dataclass
class GapQuery:
    """Single gap query with tracking information"""
    query: str
    level: int
    parent_query: str
    answer: Optional[str] = None
    confidence_score: Optional[float] = None
    sources: List[str] = field(default_factory=list)
    created_at: Optional[str] = None


@dataclass
class QnAResult:
    """Question and Answer result"""
    gap_query: str
    answer: str
    confidence_score: float
    sources: List[str]
    level: int
    parent_query: str


@dataclass
class CompletionCheckResult:
    """Result of completeness check"""
    is_complete: bool
    confidence_score: float
    new_gap_queries: List[str]
    reasoning: str
    parent_limit_reached: bool = False  # New field to track parent limit


@dataclass
class ExecutionResults:
    """Final execution results"""
    gap_queries_with_answers: List[Dict]
    total_queries_processed: int
    max_level_reached: int
    final_confidence: float
    stop_condition: StopCondition
    execution_time: float