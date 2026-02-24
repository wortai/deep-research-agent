"""
Stream event emitter for LangGraph nodes.

Provides unified utilities for emitting structured progress events
using the StreamWriter pattern. Designed for WebSocket compatibility.
MOVED FROM: deep-research-agent/streaming/stream_event.py
"""

from typing import Dict, Any, Optional, Callable
from datetime import datetime
from langgraph.types import StreamWriter, Send
from graphs.events.frontend_events import EventType, AgentPhase, AgentProgress

class StreamEmitter:
    """
    Unified stream event emitter with WebSocket-ready output.
    
    Wraps StreamWriter with type-safe event emission.
    Use this within nodes to send "custom" data events to the frontend.
    """
    
    def __init__(self, writer: Optional[StreamWriter] = None, terminal_callback: Optional[Callable] = None):
        """
        Initialize emitter.
        
        Args:
            writer: LangGraph StreamWriter for graph streaming.
        """
        self._writer = writer
        self._terminal_callback = terminal_callback
    



    
    def _emit(self, event: Dict[str, Any]) -> None:
        """Core emit logic - sends to writer."""
        if self._terminal_callback:
            try:
                self._terminal_callback(event)
            except Exception:
                pass

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
        current_step: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emit unified agent progress event for frontend tracking.

        All subgraph progress (researcher, reviewer, resolver) flows through
        this single method to avoid duplicate event types.

        Args:
            query_num: Index of the planner query this agent handles.
            query: The research query text being processed.
            phase: Current workflow phase (RESEARCHING, REVIEWING, etc.).
            percentage: Progress percentage (0-100).
            current_step: Human-readable description of current activity.
            metadata: Optional extra data (results_count, etc.).
        """
        progress = AgentProgress(
            query_num=query_num,
            query=query,
            phase=phase,
            percentage=percentage,
            current_step=current_step
        )
        
        payload = progress.to_dict()
        if metadata:
            payload["metadata"] = metadata
        
        event = self._create_event(
            EventType.AGENT_PROGRESS,
            payload,
            agent_id=f"agent_{query_num}"
        )
        self._emit(event)
    




    def emit_report_ready(self, section_count: int) -> None:
        """
        Emit report ready signal after writer completes all sections.

        Carries section_count so the frontend knows structured report JSON
        is available in the state update. This is purely a notification —
        the actual report data is delivered via the 'updates' stream mode.

        Args:
            section_count: Total number of report body sections generated.
        """
        event = self._create_event(
            EventType.REPORT_READY,
            {"section_count": section_count}
        )
        self._emit(event)


    def emit_writer_progress(
        self,
        percentage: int,
        current_step: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emit writer-specific progress for the single synthesis agent.

        Unlike emit_agent_progress (keyed by query_num for parallel research),
        this emits a flat WRITER_PROGRESS event since only one writer exists.

        Args:
            percentage: Progress percentage (0-100).
            current_step: Human-readable description of current activity.
            metadata: Optional extra data (chapters_total, chapters_done, etc.).
        """
        payload = {
            "percentage": percentage,
            "current_step": current_step,
            "phase": "writing"
        }
        if metadata:
            payload["metadata"] = metadata
        event = self._create_event(EventType.WRITER_PROGRESS, payload)
        self._emit(event)

    def emit_token(self, token: str) -> None:
        """
        Emit a generic token event.
        Useful if 'messages' stream mode is not sufficient or for specific custom tokens.
        """
        event = self._create_event(
            EventType.RESPONSE_TOKEN,
            {"token": token}
        )
        self._emit(event)


def get_emitter(writer: Optional[StreamWriter] = None) -> StreamEmitter:
    """
    Factory function for creating StreamEmitter.
    
    Args:
        writer: LangGraph StreamWriter instance.
        
    Returns:
        Configured StreamEmitter instance.
    """
    # Optional: logic to detect environment and enable terminal callback if needed
    # For now, we assume terminal handling might be done via shared utils or disabled in prod
    return StreamEmitter(writer)
