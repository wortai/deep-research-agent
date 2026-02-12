"""
Stream event emitter for LangGraph nodes.

Provides unified utilities for emitting structured progress events
using the StreamWriter pattern. Designed for WebSocket compatibility.
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from langgraph.types import StreamWriter


class EventType(str, Enum):
    """All streaming event types for frontend consumption."""
    
    AGENT_PROGRESS = "agent_progress"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    
    PHASE_STARTED = "phase_started"
    PHASE_COMPLETED = "phase_completed"
    
    SUBGRAPH_NODE_PROGRESS = "subgraph_node_progress"
    
    PLANNER_PROGRESS = "planner_progress"
    WRITER_PROGRESS = "writer_progress"
    PUBLISHER_PROGRESS = "publisher_progress"
    
    RESPONSE_TOKEN = "response_token"
    RESPONSE_COMPLETE = "response_complete"
    
    REPORT_READY = "report_ready"
    ERROR = "error"


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


class StreamEmitter:
    """
    Unified stream event emitter with WebSocket-ready output.
    
    Wraps StreamWriter with type-safe event emission and optional
    terminal display callback for development visibility.
    """
    
    def __init__(self, writer: Optional[StreamWriter] = None, terminal_callback: Optional[Callable] = None):
        """
        Initialize emitter with optional terminal callback.
        
        Args:
            writer: LangGraph StreamWriter for graph streaming.
            terminal_callback: Optional function to display events in terminal.
        """
        self._writer = writer
        self._terminal_callback = terminal_callback
    
    def _emit(self, event: Dict[str, Any]) -> None:
        """Core emit logic - sends to writer and terminal."""
        if self._terminal_callback:
            self._terminal_callback(event)
        
        if self._writer is None:
            return
        
        try:
            self._writer(event)
        except Exception:
            pass
    
    def _create_event(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Factory method for event creation with timestamp."""
        event = {
            "event_type": event_type.value,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        return event
    
    def emit_agent_progress(
        self,
        query_num: int,
        query: str,
        phase: AgentPhase,
        percentage: int,
        current_step: str = ""
    ) -> None:
        """Emit agent progress event for subgraph tracking."""
        progress = AgentProgress(
            query_num=query_num,
            query=query,
            phase=phase,
            percentage=percentage,
            current_step=current_step
        )
        
        event = self._create_event(
            EventType.AGENT_PROGRESS,
            progress.to_dict(),
            agent_id=f"agent_{query_num}"
        )
        self._emit(event)
    
    def emit_phase_event(
        self,
        event_type: EventType,
        phase: str,
        payload: Dict[str, Any],
        progress: Optional[Dict[str, int]] = None
    ) -> None:
        """Emit workflow phase event (started/completed)."""
        event = self._create_event(event_type, payload, phase=phase)
        if progress:
            event["progress"] = progress
        self._emit(event)
    
    def emit_node_progress(
        self,
        node_name: str,
        query_num: int,
        status: str,
        percentage: int,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Emit progress event for subgraph node execution."""
        event = self._create_event(
            EventType.SUBGRAPH_NODE_PROGRESS,
            details or {},
            node_name=node_name,
            agent_id=f"agent_{query_num}",
            status=status,
            percentage=percentage
        )
        self._emit(event)
    
    def emit_response_token(self, token: str, is_complete: bool = False) -> None:
        """Emit LLM response token for streaming chat responses."""
        event_type = EventType.RESPONSE_COMPLETE if is_complete else EventType.RESPONSE_TOKEN
        event = self._create_event(event_type, {"token": token})
        self._emit(event)
    
    def emit_report_ready(self, pdf_path: str, md_path: str = "") -> None:
        """Emit report ready event with file paths."""
        event = self._create_event(
            EventType.REPORT_READY,
            {"pdf_path": pdf_path, "md_path": md_path}
        )
        self._emit(event)


def get_emitter(writer: Optional[StreamWriter] = None, enable_terminal: bool = True) -> StreamEmitter:
    """
    Factory function for creating StreamEmitter with optional terminal output.
    
    Args:
        writer: LangGraph StreamWriter instance.
        enable_terminal: If True, prints events to terminal during dev.
        
    Returns:
        Configured StreamEmitter instance.
    """
    terminal_cb = None
    if enable_terminal:
        def terminal_cb(event: Dict[str, Any]):
            event_type = event.get("event_type", "unknown")
            if event_type == "response_token":
                print(event["payload"]["token"], end="", flush=True)
            elif event_type == "response_complete":
                print()
    
    return StreamEmitter(writer, terminal_cb)


# Legacy function wrappers for backward compatibility
def emit_agent_progress(
    writer: StreamWriter,
    query_num: int,
    query: str,
    phase: AgentPhase,
    percentage: int,
    current_step: str = ""
) -> None:
    """Legacy wrapper - use StreamEmitter.emit_agent_progress instead."""
    emitter = StreamEmitter(writer)
    emitter.emit_agent_progress(query_num, query, phase, percentage, current_step)


def emit_phase_event(
    writer: StreamWriter,
    event_type: str,
    phase: str,
    payload: Dict[str, Any],
    progress: Optional[Dict[str, int]] = None
) -> None:
    """Legacy wrapper - use StreamEmitter.emit_phase_event instead."""
    emitter = StreamEmitter(writer)
    emitter.emit_phase_event(EventType(event_type), phase, payload, progress)


def emit_node_progress(
    writer: StreamWriter,
    node_name: str,
    query_num: int,
    status: str,
    percentage: int,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """Legacy wrapper - use StreamEmitter.emit_node_progress instead."""
    emitter = StreamEmitter(writer)
    emitter.emit_node_progress(node_name, query_num, status, percentage, details)
