"""
Gap Question Generator Module

A modular system for generating and resolving gap queries through 
web research and vector store operations.
"""

from .main import GapQuestionGenerator
from .models import (
    GapQuery,
    QnAResult,
    CompletionCheckResult,
    ExecutionResults,
    StopCondition
)
from .vector_queries import VectorQueryGenerator
from .research import ResearchManager
from .answer_generator import AnswerGenerator
from .completeness_checker import CompletenessChecker
from .llm_client import GeminiLLMClient
from .monitoring import ExecutionMonitor, DetailedQueryData

__version__ = "1.0.0"
__author__ = "Gap Question Generator Team"

__all__ = [
    "GapQuestionGenerator",
    "GapQuery",
    "QnAResult", 
    "CompletionCheckResult",
    "ExecutionResults",
    "StopCondition",
    "VectorQueryGenerator",
    "ResearchManager", 
    "AnswerGenerator",
    "CompletenessChecker",
    "GeminiLLMClient",
    "ExecutionMonitor",
    "DetailedQueryData"
]