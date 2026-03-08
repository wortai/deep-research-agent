"""
Intent types for router classification.

Defines all possible intents that the router node can classify,
including search modes from frontend and detected intents from context.
"""

from enum import Enum


class SearchMode(str, Enum):
    """Search modes provided by frontend."""
    
    WEBSEARCH = "websearch"
    DEEPSEARCH = "deepsearch"
    EXTREMESEARCH = "extremesearch"


class IntentType(str, Enum):
    """
    All possible intents for routing.
    
    Search modes come from frontend, others are detected
    by router from chat history context.
    """
    
    WEBSEARCH = "websearch"
    DEEPSEARCH = "deepsearch"
    EXTREMESEARCH = "extremesearch"
    
    FOLLOW_UP = "follow_up"
    EDIT = "edit"
    CLARIFICATION = "clarification"
    OFF_TOPIC = "off_topic"


def is_research_mode(intent: IntentType) -> bool:
    """Check if intent requires research workflow."""
    return intent in (IntentType.WEBSEARCH, IntentType.DEEPSEARCH, IntentType.EXTREMESEARCH)


def requires_full_report(intent: IntentType) -> bool:
    """Check if intent requires full report generation."""
    return intent in (IntentType.DEEPSEARCH, IntentType.EXTREMESEARCH)
