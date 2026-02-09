"""
Module for orchestrating the research process with progress streaming.

Emits frontend events via LangGraph get_stream_writer for real-time
progress tracking of research nodes.
"""

import logging
import asyncio
from collections import deque
from typing import List, Optional, Dict, Any

from researcher.solution_tree.research_node import Node
from researcher.solution_tree.query_sol_ans import Solver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_tree(node: Node, prefix: str = "", is_last: bool = True):
    """Prints a visual representation of the research tree."""
    print(prefix + ("└── " if is_last else "├── ") + node.query)
    child_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        print_tree(child, child_prefix, is_last_child)


def _estimate_total_nodes(max_depth: int, num_gaps_per_node: int) -> int:
    """Estimate total nodes in research tree for progress tracking."""
    return sum(num_gaps_per_node ** d for d in range(max_depth + 1))


def _emit_event(writer, event_type: str, phase: str, payload: dict, progress: dict = None):
    """Emit event to stream writer if available."""
    if writer is None:
        return
    
    from datetime import datetime
    
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
    except Exception as e:
        logger.debug(f"Could not emit event: {e}")


async def execute_research_tree(
    initial_query: str, 
    max_depth: int = 2, 
    num_gaps_per_node: int = 2
) -> Dict[str, Any]:
    """
    Builds and resolves a tree of research queries using a breadth-first approach.
    
    Emits progress events via get_stream_writer for frontend progress bars.
    
    Args:
        initial_query (str): The initial research query (root).
        max_depth (int): Maximum depth of the research tree.
        num_gaps_per_node (int): Number of gaps to identify per node.
        
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
        "phase_started",
        "researching",
        {"query": initial_query, "max_depth": max_depth},
        {"completed": 0, "total": estimated_total}
    )
    
    root_node = Node(query=initial_query)
    queue = deque([root_node])
    
    all_answers = []
    all_gaps = {}
    nodes_processed = 0

    while queue:
        current_node = queue.popleft()
        
        _emit_event(
            writer,
            "research_node_started",
            "researching",
            {
                "query": current_node.query[:100],
                "depth": current_node.depth,
                "node_id": f"node_{nodes_processed}"
            },
            {"completed": nodes_processed, "total": estimated_total}
        )

        logger.info(f"Resolving Node at Depth {current_node.depth}: '{current_node.query}'")
        
        nodes_processed += 1

        if current_node.depth >= max_depth:
            logger.info("Max depth reached for this branch.")
            _emit_event(
                writer,
                "research_node_completed",
                "researching",
                {"query": current_node.query[:100], "status": "max_depth_reached"},
                {"completed": nodes_processed, "total": estimated_total}
            )
            continue

        try:
            solver = Solver(query=current_node.query, num_gaps_per_node=num_gaps_per_node)
            gaps, answer = await solver.resolve()
            
            current_node.answer = answer
            
            for q, a in answer.items():
                all_answers.append({
                    "query": q,
                    "answer": a,
                    "parent_query": current_node.query,
                    "depth": current_node.depth
                })
            
            all_gaps[current_node.query] = gaps
            
            logger.info(f"Query resolved. Found {len(gaps)} new child nodes (gaps).")
            
            _emit_event(
                writer,
                "research_node_completed",
                "researching",
                {
                    "query": current_node.query[:100],
                    "answers_count": len(answer),
                    "gaps_found": len(gaps),
                    "status": "resolved"
                },
                {"completed": nodes_processed, "total": estimated_total}
            )

            for gap_query in gaps:
                child_node = Node(
                    query=gap_query, 
                    depth=current_node.depth + 1, 
                    parent=current_node
                )
                current_node.children.append(child_node)
                queue.append(child_node)

        except Exception as e:
            logger.error(f"An error occurred while resolving '{current_node.query}': {e}")
            _emit_event(
                writer,
                "error",
                "researching",
                {"query": current_node.query[:100], "error": str(e)[:200]}
            )
            
    _emit_event(
        writer,
        "phase_completed",
        "researching",
        {"total_answers": len(all_answers), "total_nodes": nodes_processed},
        {"completed": nodes_processed, "total": nodes_processed}
    )
    
    logger.info("Research tree resolution is complete.")
    
    return {
        "tree_root": root_node,
        "all_answers": all_answers,
        "all_gaps": all_gaps,
        "total_nodes_processed": nodes_processed
    }
 