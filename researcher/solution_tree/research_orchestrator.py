"""
Module for orchestrating the research process with progress streaming.

Emits frontend events via LangGraph get_stream_writer for real-time
progress tracking of research nodes.
"""

import logging
import asyncio
from collections import deque
from typing import List, Optional, Dict, Any
import uuid

from researcher.solution_tree.research_node import Node
from researcher.solution_tree.query_sol_ans import Solver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def _estimate_total_nodes(max_depth: int, num_gaps_per_node: int) -> int:
    """Estimate total nodes in research tree for progress tracking."""
    return sum(num_gaps_per_node ** d for d in range(max_depth + 1))


def _emit_event(writer, phase: str, payload: dict, progress: dict = None):
    """
    Emit agent_progress event to stream writer for frontend tracking.

    Uses consistent 'agent_progress' event_type so stream_service.py
    handles orchestrator events identically to subgraph-level emissions.

    Args:
        writer: LangGraph stream writer callable.
        phase: Current phase string (e.g. 'researching').
        payload: Event data with query, current_step, percentage, etc.
        progress: Optional dict with completed/total counts.
    """
    if writer is None:
        return
    
    from datetime import datetime
    
    event = {
        "event_type": "agent_progress",
        "phase": phase,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat()
    }
    if progress:
        event["progress"] = progress
    
    try:
        writer(event)
    except Exception as e:
        logger.debug(f"Could not emit event: {e}")


async def execute_research_tree(
    initial_query: str, 
    max_depth: int = 2, 
    num_gaps_per_node: int = 2,
    query_num: int = 0,
    clarification_context: list = None
) -> Dict[str, Any]:
    """
    Builds and resolves a tree of research queries using a breadth-first approach.
    
    Emits progress events via get_stream_writer for frontend progress bars.
    Each event includes query_num so the frontend routes it to the
    correct agent card (one subgraph invocation = one agent).
    
    Args:
        initial_query: The initial research query (root).
        max_depth: Maximum depth of the research tree.
        num_gaps_per_node: Number of gaps to identify per node.
        query_num: Planner query index this tree belongs to.
        
    Returns:
        Dict[str, Any]: Dictionary with tree_root, all_answers (List[RawResearchResult]), 
            all_gaps, total_nodes_processed.
    """
    try:
        from langgraph.config import get_stream_writer
        writer = get_stream_writer()
    except Exception:
        writer = None
        logger.debug("Stream writer not available, progress events disabled")
    
    estimated_total = _estimate_total_nodes(max_depth, num_gaps_per_node)
    
    _emit_event(
        writer,
        "researching",
        {
            "query_num": query_num,
            "query": initial_query,
            "current_step": f"Starting research tree (depth {max_depth})",
            "percentage": 0
        },
        {"completed": 0, "total": estimated_total}
    )
    
    root_node = Node(query=initial_query)
    queue = deque([root_node])
    
    all_answers = []
    all_gaps = {}
    nodes_processed = 0

    while queue:
        # Group all nodes at the same depth for parallel processing
        current_depth = queue[0].depth
        same_depth_nodes = []
        while queue and queue[0].depth == current_depth:
            same_depth_nodes.append(queue.popleft())
        
        async def process_single_node(node: Node, node_index: int) -> Dict[str, Any]:
            """
            Process a single research node.
            
            Resolves the query using Solver and returns results for aggregation.
            Handles max_depth check and error cases.
            
            Args:
                node: The research node to process.
                node_index: Index for tracking progress.
                
            Returns:
                Dict with node, gaps, answer, and success status.
            """
            nonlocal nodes_processed
            local_node_id = nodes_processed + node_index
            
            _emit_event(
                writer,
                "researching",
                {
                    "query_num": query_num,
                    "query": node.query[:100],
                    "current_step": f"Searching: {node.query[:80]}",
                    "depth": node.depth,
                    "percentage": int((local_node_id / max(estimated_total, 1)) * 100)
                },
                {"completed": local_node_id, "total": estimated_total}
            )
            
            # logger.info(f"Resolving Node at Depth {node.depth}: '{node.query}'")
            
            if node.depth >= max_depth:
                # logger.info("Max depth reached for this branch.")
                _emit_event(
                    writer,
                    "researching",
                    {
                        "query_num": query_num,
                        "query": node.query[:100],
                        "current_step": "Max depth reached",
                        "percentage": int(((local_node_id + 1) / max(estimated_total, 1)) * 100)
                    },
                    {"completed": local_node_id + 1, "total": estimated_total}
                )
                return {"node": node, "gaps": [], "answer": {}, "success": True, "max_depth": True}
            
            try:
                at_last_runnable_depth = node.depth >= max_depth - 1
                solver = Solver(
                    query=node.query,
                    num_gaps_per_node=0 if at_last_runnable_depth else num_gaps_per_node,
                    clarification_context=clarification_context or []
                )
                gaps, answer = await solver.resolve()
                
                _emit_event(
                    writer,
                    "researching",
                    {
                        "query_num": query_num,
                        "query": node.query[:100],
                        "current_step": f"Resolved ({len(answer)} answers, {len(gaps)} gaps)",
                        "percentage": int(((local_node_id + 1) / max(estimated_total, 1)) * 100)
                    },
                    {"completed": local_node_id + 1, "total": estimated_total}
                )
                
                return {"node": node, "gaps": gaps, "answer": answer, "success": True, "max_depth": False}
                
            except Exception as e:
                logger.error(f"An error occurred while resolving '{node.query}': {e}")
                _emit_event(
                    writer,
                    "researching",
                    {
                        "query_num": query_num,
                        "query": node.query[:100],
                        "current_step": f"Error: {str(e)[:100]}",
                        "percentage": int(((local_node_id + 1) / max(estimated_total, 1)) * 100)
                    }
                )
                return {"node": node, "gaps": [], "answer": {}, "success": False, "max_depth": False}
        
        # Process all sibling nodes in parallel
        results = await asyncio.gather(*[
            process_single_node(node, idx) for idx, node in enumerate(same_depth_nodes)
        ])
        
        # Aggregate results from parallel execution
        for result in results:
            nodes_processed += 1
            node = result["node"]
            
            if result["max_depth"]:
                continue
                
            if result["success"]:
                node.answer = result["answer"]
                
                for q, a in result["answer"].items():
                    all_answers.append({
                        "query": q,
                        "answer": a,
                        "parent_query": node.query,
                        "depth": node.depth,
                        "section_id": str(uuid.uuid4())
                    })
                
                all_gaps[node.query] = result["gaps"]
                
                for gap_query in result["gaps"]:
                    if node.depth + 1 < max_depth:
                        child_node = Node(
                            query=gap_query, 
                            depth=node.depth + 1, 
                            parent=node
                        )
                        node.children.append(child_node)
                        queue.append(child_node)
            
    _emit_event(
        writer,
        "researching",
        {
            "query_num": query_num,
            "current_step": f"Research complete ({len(all_answers)} answers, {nodes_processed} nodes)",
            "percentage": 100
        },
        {"completed": nodes_processed, "total": nodes_processed}
    )
    
    # logger.info("Research tree resolution is complete.")
    
    return {
        "tree_root": root_node,
        "all_answers": all_answers,
        "all_gaps": all_gaps,
        "total_nodes_processed": nodes_processed
    }
 