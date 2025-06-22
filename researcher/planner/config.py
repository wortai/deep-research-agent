"""
Configuration settings and constants for the Deep Search Planner Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the Deep Search Planner Agent"""
    
    # API Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    DEFAULT_MODEL_NAME = "gemini-1.5-pro"
    
    # Planning Configuration
    DEFAULT_MAX_QUESTIONS = 3
    DEFAULT_MAX_ITERATIONS = 3
    DEFAULT_TOP_N_PLANS = 2
    MAX_QUESTIONS_LIMIT = 10
    
    # Quality Scoring Weights
    METRIC_WEIGHTS = {
        'completeness': 0.25,
        'clarity_specificity': 0.20,
        'logical_flow_cohesion': 0.20,
        'feasibility_realism': 0.15,
        'keyword_relevance_breadth': 0.20
    }
    
    # Default Questions for Fallback
    DEFAULT_SIMPLE_QUESTIONS = [
        "What time period should this research cover?",
        "Which region or country should be the main focus?",
        "What is the target audience for this research?",
        "Should this focus on current trends or future predictions?",
        "What industry sector is most important?",
        "What is the primary goal of this research?",
        "Which aspect should be prioritized?",
        "What level of detail is needed?",
        "Are there any specific constraints to consider?",
        "What type of sources are most valuable?"
    ]
    
    @classmethod
    def validate_api_key(cls) -> bool:
        """Validate that API key is available"""
        return bool(cls.GOOGLE_API_KEY)
    
    @classmethod
    def get_api_key(cls) -> str:
        """Get API key with validation"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "API key must be provided either as parameter or GOOGLE_API_KEY environment variable"
            )
        return cls.GOOGLE_API_KEY


# Constants
REQUIRED_PLAN_KEYS = ['search_steps', 'key_areas', 'information_sources', 'search_strategies', 'success_metrics']
EVALUATION_KEYS = ['overall_assessment', 'strengths', 'weaknesses_and_recommendations', 
                  'areas_for_potential_further_clarification', 'generated_questions']