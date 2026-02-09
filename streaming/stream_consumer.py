"""
Stream consumer for processing LangGraph stream output.

Parses stream chunks from astream() and dispatches events
to the terminal display for visualization.
"""

from typing import Any, Dict, Tuple, Optional
import logging

from streaming.terminal_display import TerminalDisplay

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamConsumer:
    """
    Consumes stream output from graph.astream() and updates display.
    
    Handles namespace parsing for subgraph identification,
    aggregates progress from parallel agents, and routes
    events to the terminal display.
    """
    
    def __init__(self, display: TerminalDisplay):
        """
        Initialize consumer with display target.
        
        Args:
            display: TerminalDisplay instance for output.
        """
        self._display = display
        self._agent_progress: Dict[int, int] = {}
    
    def process_chunk(
        self,
        namespace: Tuple[str, ...],
        mode: str,
        chunk: Any
    ) -> None:
        """
        Process a single stream chunk from astream().
        
        When using stream_mode=["updates", "custom"] with subgraphs=True,
        chunks arrive as (namespace, mode, data) tuples.
        
        Args:
            namespace: Tuple path identifying source node/subgraph.
            mode: Stream mode ("updates" or "custom").
            chunk: The actual data payload.
        """
        if mode == "custom":
            self._handle_custom_event(namespace, chunk)
        elif mode == "updates":
            self._handle_state_update(namespace, chunk)
    
    def _handle_custom_event(
        self,
        namespace: Tuple[str, ...],
        event: Dict[str, Any]
    ) -> None:
        """
        Handle custom streaming event from get_stream_writer or StreamWriter.
        
        Custom events include agent_progress, phase events, and
        subgraph node progress updates.
        """
        if not isinstance(event, dict):
            return
        
        event_type = event.get("event_type", "")
        
        if event_type == "agent_progress":
            self._handle_agent_progress(event)
        
        elif event_type == "subgraph_node_progress":
            self._handle_subgraph_node_progress(event)
        
        elif event_type == "phase_started":
            phase = event.get("phase", "unknown")
            self._display.set_phase(phase)
            
            if phase == "researching":
                payload = event.get("payload", {})
                total = payload.get("total_queries", 0)
                if total:
                    self._display.set_total_queries(total)
        
        elif event_type == "phase_completed":
            phase = event.get("phase", "")
            if phase == "researching":
                self._display.set_phase("writing")
    
    def _handle_agent_progress(self, event: Dict[str, Any]) -> None:
        """Update display with agent progress event."""
        payload = event.get("payload", {})
        query_num = payload.get("query_num", 0)
        query = payload.get("query", f"Query {query_num}")
        percentage = payload.get("percentage", 0)
        phase = payload.get("phase", "")
        current_step = payload.get("current_step", "")
        
        self._display.update_agent(
            query_num=query_num,
            query=query,
            percentage=percentage,
            phase=phase,
            current_step=current_step
        )
    
    def _handle_subgraph_node_progress(self, event: Dict[str, Any]) -> None:
        """Update display from subgraph node progress event."""
        agent_id = event.get("agent_id", "")
        percentage = event.get("percentage", 0)
        node_name = event.get("node_name", "")
        status = event.get("status", "")
        
        try:
            query_num = int(agent_id.replace("agent_", ""))
        except ValueError:
            return
        
        current_step = f"{node_name}: {status}"
        
        self._display.update_agent(
            query_num=query_num,
            query=f"Research Query {query_num + 1}",
            percentage=percentage,
            current_step=current_step
        )
    
    def _handle_state_update(
        self,
        namespace: Tuple[str, ...],
        chunk: Dict[str, Any]
    ) -> None:
        """
        Handle state update from updates stream mode.
        
        State updates show which nodes completed and their outputs.
        We use namespaces to identify subgraph context.
        """
        if "__interrupt__" in chunk:
            self._display.set_phase("human_review")
            return
        
        for node_name, node_output in chunk.items():
            if node_name == "router_node":
                self._display.set_phase("routing")
            
            elif node_name == "planner_node":
                self._display.set_phase("planning")
                queries = node_output.get("planner_query", [])
                if queries:
                    self._display.set_total_queries(len(queries))
            
            elif node_name == "parallel_research_node":
                self._display.set_phase("researching")
            
            elif node_name == "writer_node":
                self._display.set_phase("writing")
            
            elif node_name == "publisher_node":
                self._display.set_phase("publishing")
            
            elif node_name == "response_node":
                self._display.set_phase("responding")
        
        if namespace:
            self._infer_subgraph_progress(namespace, chunk)
    
    def _infer_subgraph_progress(
        self,
        namespace: Tuple[str, ...],
        chunk: Dict[str, Any]
    ) -> None:
        """
        Infer agent progress from subgraph namespace paths.
        
        When streaming with subgraphs=True, namespace tuples like
        ('parallel_research_node:abc123',) identify which subgraph
        emitted the update.
        """
        if not namespace:
            return
        
        for node_name in chunk.keys():
            if node_name == "researcher_node":
                self._update_from_namespace(namespace, 25)
            elif node_name == "reviewer_node":
                self._update_from_namespace(namespace, 75)
            elif node_name == "resolve_node":
                self._update_from_namespace(namespace, 50)
    
    def _update_from_namespace(
        self,
        namespace: Tuple[str, ...],
        percentage: int
    ) -> None:
        """Extract query_num from namespace and update display."""
        pass


def parse_subgraph_namespace(namespace: Tuple[str, ...]) -> Optional[int]:
    """
    Parse subgraph namespace to extract query index.
    
    Namespace format: ('parallel_research_node:task_id', ...)
    We track the order of unique task_ids to assign query_num.
    """
    return None
