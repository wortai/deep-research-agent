"""
Stream event emitter for LangGraph nodes.

Provides utilities for emitting structured progress events from async nodes
using the StreamWriter pattern (required for async Python).
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from langgraph.types import StreamWriter


class AgentPhase(str, Enum):
    """Sub-phases within an agent's research cycle."""
    
    SEARCHING = "searching"
    RESOLVING = "resolving"
    REVIEWING = "reviewing"
    COMPLETE = "complete"


@dataclass
class AgentProgress:
    """
    Tracks progress of a single research agent (subgraph instance).
    
    Each parallel invocation of researcher_reviewer_subgraph creates
    one AgentProgress instance tracked by query_num.
    """
    
    query_num: int
    query: str
    phase: AgentPhase = AgentPhase.SEARCHING
    percentage: int = 0
    current_step: str = ""
    total_steps: int = 4
    completed_steps: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for streaming."""
        return {
            "query_num": self.query_num,
            "query": self.query[:60] + "..." if len(self.query) > 60 else self.query,
            "phase": self.phase.value,
            "percentage": self.percentage,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps
        }


def emit_agent_progress(
    writer: StreamWriter,
    query_num: int,
    query: str,
    phase: AgentPhase,
    percentage: int,
    current_step: str = ""
) -> None:
    """
    Emit agent progress event via StreamWriter.
    
    Designed for use within async subgraph nodes to report
    individual agent progress to the parent graph stream.
    
    Args:
        writer: LangGraph StreamWriter injected into async node.
        query_num: Index of the research query (0-indexed).
        query: The research query text.
        phase: Current phase within the agent lifecycle.
        percentage: Progress percentage (0-100).
        current_step: Description of current activity.
    """
    if writer is None:
        return
    
    progress = AgentProgress(
        query_num=query_num,
        query=query,
        phase=phase,
        percentage=percentage,
        current_step=current_step
    )
    
    event = {
        "event_type": "agent_progress",
        "agent_id": f"agent_{query_num}",
        "payload": progress.to_dict(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        writer(event)
    except Exception:
        pass


def emit_phase_event(
    writer: StreamWriter,
    event_type: str,
    phase: str,
    payload: Dict[str, Any],
    progress: Optional[Dict[str, int]] = None
) -> None:
    """
    Emit workflow phase event via StreamWriter.
    
    Used by main graph nodes to signal phase transitions
    (e.g., routing → planning → researching).
    
    Args:
        writer: LangGraph StreamWriter.
        event_type: Type of event (phase_started, phase_completed, etc.).
        phase: Current workflow phase name.
        payload: Event-specific data.
        progress: Optional dict with 'completed' and 'total' keys.
    """
    if writer is None:
        return
    
    event = {
        "event_type": event_type,
        "phase": phase,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if progress:
        event["progress"] = progress
    
    try:
        writer(event)
    except Exception:
        pass


def emit_node_progress(
    writer: StreamWriter,
    node_name: str,
    query_num: int,
    status: str,
    percentage: int,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Emit progress event for a specific subgraph node.
    
    Called at start/end of researcher_node, reviewer_node, resolve_node
    to track individual node execution within the subgraph.
    
    Args:
        writer: LangGraph StreamWriter.
        node_name: Name of the executing node.
        query_num: Index of research query.
        status: Current status (started, in_progress, completed).
        percentage: Overall agent progress percentage.
        details: Optional additional event data.
    """
    if writer is None:
        return
    
    event = {
        "event_type": "subgraph_node_progress",
        "node_name": node_name,
        "agent_id": f"agent_{query_num}",
        "status": status,
        "percentage": percentage,
        "payload": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        writer(event)
    except Exception:
        pass
