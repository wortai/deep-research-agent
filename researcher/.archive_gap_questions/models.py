"""
Data models for the Gap Question Generator system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any


class StopCondition(Enum):
    """Reasons for stopping the generation process"""
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    CONFIDENCE_THRESHOLD_MET = "confidence_threshold_met"
    QUEUE_EMPTY = "queue_empty"


@dataclass
class ProcessingStep:
    """Tracks individual processing steps"""
    step_name: str
    timestamp: str
    status: str
    details: Dict
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class CompletionCheckResult:
    """Results from checking query completeness"""
    is_complete: bool
    confidence_score: float
    missing_aspects: List[str]
    completeness_percentage: float


@dataclass
class DetailedQueryData:
    """Comprehensive data for each query processed"""
    gap_query: str
    vector_queries: List[str] = field(default_factory=list)
    llm_prompt: str = ""
    llm_response: str = ""
    urls_accessed: List[str] = field(default_factory=list)
    content_from_urls: List[Dict[str, str]] = field(default_factory=list)
    vector_search_results: List[Dict[str, str]] = field(default_factory=list)
    insights_extracted: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class OrchestratorState(dict):
    """State for LangGraph orchestration"""
    current_iteration: int
    should_continue: bool
    stop_condition: Optional[StopCondition]

