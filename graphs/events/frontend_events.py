"""
Frontend event types for streaming progress to UI.

Defines event structures emitted via LangGraph's get_stream_writer()
for real-time progress tracking of research agents and workflow phases.
"""

from enum import Enum
from typing import TypedDict, Dict, Any, Optional
from datetime import datetime


class EventType(str, Enum):
    """Event types for frontend streaming."""
    
    PHASE_STARTED = "phase_started"
    PHASE_COMPLETED = "phase_completed"
    
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_PROGRESS = "agent_progress"
    
    RESEARCH_NODE_STARTED = "research_node_started"
    RESEARCH_NODE_COMPLETED = "research_node_completed"
    
    SUBGRAPH_STARTED = "subgraph_started"
    SUBGRAPH_PROGRESS = "subgraph_progress"
    SUBGRAPH_COMPLETED = "subgraph_completed"
    SUBGRAPH_NODE_PROGRESS = "subgraph_node_progress"
    
    PLAN_GENERATED = "plan_generated"
    PLAN_APPROVED = "plan_approved"
    PLANNER_PROGRESS = "planner_progress"
    
    CLARIFICATION_STARTED = "clarification_started"
    
    WRITER_PROGRESS = "writer_progress"
    PUBLISHER_PROGRESS = "publisher_progress"
    
    RESPONSE_TOKEN = "response_token"
    RESPONSE_COMPLETE = "response_complete"
    
    REPORT_SECTION_COMPLETED = "report_section_completed"
    REPORT_READY = "report_ready"
    
    ERROR = "error"
    TOOL_EXECUTION = "tool_execution"


class PhaseType(str, Enum):
    """Workflow phase identifiers."""
    
    ROUTING = "routing"
    PLANNING = "planning"
    CLARIFYING = "clarifying"
    HUMAN_REVIEW = "human_review"
    RESEARCHING = "researching"
    REVIEWING = "reviewing"
    WRITING = "writing"
    PUBLISHING = "publishing"
    RESPONDING = "responding"

# Alias for backward compatibility or clarity in agent contexts
AgentPhase = PhaseType


class AgentProgress:
    """Tracks progress of a specific research agent."""
    
    def __init__(
        self, 
        query_num: int, 
        query: str, 
        phase: AgentPhase, 
        percentage: int, 
        current_step: str = ""
    ):
        self.query_num = query_num
        self.query = query
        self.phase = phase
        self.percentage = percentage
        self.current_step = current_step

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_num": self.query_num,
            "query": self.query,
            "phase": self.phase,
            "percentage": self.percentage,
            "current_step": self.current_step
        }


class ProgressInfo(TypedDict, total=False):
    """Progress tracking for frontend progress bars."""
    
    completed: int
    total: int
    percentage: float


class FrontendEvent(TypedDict, total=False):
    """
    Event structure sent to frontend via streaming.
    
    Consumed by WebSocket/SSE handler for real-time UI updates.
    """
    
    event_type: EventType
    phase: PhaseType
    payload: Dict[str, Any]
    timestamp: str
    progress: ProgressInfo
    agent_id: str
    query_num: int


def create_event(
    event_type: EventType,
    phase: PhaseType,
    payload: Dict[str, Any] = None,
    progress: ProgressInfo = None,
    agent_id: str = None,
    query_num: int = None
) -> FrontendEvent:
    """
    Factory for creating FrontendEvent with timestamp.
    
    Args:
        event_type: Type of event being emitted.
        phase: Current workflow phase.
        payload: Event-specific data.z
        progress: Optional progress info for progress bars.
        agent_id: Optional identifier for specific agent.
        query_num: Optional query number for tracking.
        
    Returns:
        FrontendEvent ready for streaming.
    """
    event: FrontendEvent = {
        "event_type": event_type,
        "phase": phase,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload or {}
    }
    
    if progress:
        event["progress"] = progress
    if agent_id:
        event["agent_id"] = agent_id
    if query_num is not None:
        event["query_num"] = query_num
        
    return event
