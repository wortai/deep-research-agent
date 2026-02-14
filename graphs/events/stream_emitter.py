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
        current_step: str = ""
    ) -> None:
        """
        Emit agent progress event for subgraph tracking.
        Used by the parallel researcher to update its progress bar.
        """
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
    
    def emit_subgraph_node_progress(
        self,
        node_name: str,
        query_num: int,
        status: str,
        percentage: int,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emit progress event for specific subgraph node execution.
        """
        event = self._create_event(
            EventType.SUBGRAPH_NODE_PROGRESS,
            details or {},
            node_name=node_name,
            agent_id=f"agent_{query_num}",
            status=status,
            percentage=percentage
        )
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
