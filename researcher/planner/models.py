"""
Data models and classes for the Deep Search Planner Agent
"""
from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class SearchPlan:
    """Represents a search plan with its components and metadata"""
    query: str
    enhanced_query: str
    plan_steps: List[str]
    decision_points: List[str]
    clarifying_questions: List[str]
    quality_score: float
    iteration: int
    timestamp: float


@dataclass
class PlanEvaluation:
    """Represents plan evaluation results"""
    overall_score: float
    metric_scores: Dict[str, float]
    evaluation_summary: str
    actionable_feedback: List[str]
    areas_for_clarification: List[str]
    decision_points: List[str]
    clarifying_questions: List[str]


@dataclass
class PlanData:
    """Represents structured plan data"""
    search_steps: List[str]
    key_areas: List[str]
    information_sources: List[str]
    search_strategies: List[str]
    success_metrics: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "search_steps": self.search_steps,
            "key_areas": self.key_areas,
            "information_sources": self.information_sources,
            "search_strategies": self.search_strategies,
            "success_metrics": self.success_metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanData':
        """Create from dictionary"""
        return cls(
            search_steps=data.get('search_steps', []),
            key_areas=data.get('key_areas', []),
            information_sources=data.get('information_sources', []),
            search_strategies=data.get('search_strategies', []),
            success_metrics=data.get('success_metrics', [])
        )