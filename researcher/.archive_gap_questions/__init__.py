"""
Gap Question Generator Package
"""

from researcher.gap_questions.generator import GapQuestionGenerator
from researcher.gap_questions.models import (
    StopCondition,
    ProcessingStep,
    CompletionCheckResult,
    DetailedQueryData,
    OrchestratorState
)
from researcher.gap_questions.monitoring import ExecutionMonitor
from researcher.gap_questions.llm_client import GeminiLLMClient
from researcher.web_search import WebSearch
from researcher.vector_store import QdrantService, VectorStoreManager
from researcher.gap_questions.utils import analyze_logs, create_visualization_report

__version__ = "1.0.0"
__all__ = [
    "GapQuestionGenerator",
    "ExecutionMonitor",
    "GeminiLLMClient",
    "analyze_logs",
    "create_visualization_report",
    "StopCondition",
    "ProcessingStep",
    "CompletionCheckResult",
    "DetailedQueryData",
    "OrchestratorState"
]