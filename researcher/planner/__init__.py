"""
Deep Search Planner Agent - A sophisticated search planning system using AI
"""

from researcher.planner.planner import DeepSearchPlannerAgent
from researcher.planner.models import SearchPlan, PlanData, PlanEvaluation
from researcher.planner.config import Config

__version__ = "1.0.0"
__author__ = "Deep Search Planner Team"
__description__ = "AI-powered search planning agent with iterative refinement"

# Main exports
__all__ = [
    "DeepSearchPlannerAgent",
    "SearchPlan", 
    "PlanData",
    "PlanEvaluation",
    "Config"
]

# Convenience function for quick start
def create_planner(api_key=None, model_name=None):
    """
    Convenience function to create and initialize a planner
    
    Args:
        api_key: Google AI API key (optional)
        model_name: Gemini model name (optional)
        
    Returns:
        DeepSearchPlannerAgent: Initialized planner instance
    """
    planner = DeepSearchPlannerAgent(api_key=api_key, model_name=model_name)
    if planner.load_gemini_model():
        return planner
    else:
        raise RuntimeError("Failed to initialize planner. Check your API key and configuration.")