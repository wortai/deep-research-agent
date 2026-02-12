"""
Researcher-Reviewer SubGraph with loop functionality.

This subgraph processes a single query through research-review cycles:
1. Research (with web search) - initial deep research
2. Review (generate reviews) - identify gaps
3. Resolve (with web search) - answer review questions using web search
4. Loop back to Review until no more reviews

Parent graph invokes this subgraph in parallel (one per query from planner).
Emits progress events via StreamWriter for real-time tracking.
"""

import logging
import uuid
from typing import Dict, Any
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.types import StreamWriter

from graphs.states.subgraph_state import ResearchReviewData
from researcher.solution_tree.research_orchestrator import execute_research_tree
from researcher.solution_tree.query_sol_ans import Solver
from reviewer.reviewer import Reviewer
from streaming.stream_event import emit_node_progress

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def researcher_node(state: ResearchReviewData, writer: StreamWriter) -> Dict[str, Any]:
    """
    Initial research node that performs deep research with web search.
    
    Uses execute_research_tree to perform BFS research on the query,
    populating raw_research_results with List[RawResearchResult].
    Emits progress events via StreamWriter for real-time tracking.
    """
    query = state["query"]
    query_num = state.get("query_num", 0)
    logger.info(f"[researcher_node] Starting research for: {query}")
    
    emit_node_progress(writer, "researcher", query_num, "started", 10, {"query": query[:50]})
    
    research_results = await execute_research_tree(
        initial_query=query,
        max_depth=2,
        num_gaps_per_node=2
    )
    
    all_answers = research_results["all_answers"]
    
    logger.info(f"[researcher_node] Research complete: {len(all_answers)} research results")
    emit_node_progress(writer, "researcher", query_num, "completed", 40, {"results_count": len(all_answers)})
    
    return {
        "raw_research_results": all_answers,
        "iteration_count": 0,
        "logs": [{
            "message_id": str(uuid.uuid4()),
            "role": "system",
            "content": f"Researcher #{query_num} completed initial research. Found {len(all_answers)} results.",
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": "log",
            "metadata": {"query_num": query_num, "step": "researcher"}
        }]
    }


MAX_ITERATIONS = 1

async def reviewer_node(state: ResearchReviewData, writer: StreamWriter) -> Dict[str, Any]:
    """
    Review node that generates synthesis questions.
    
    Analyzes raw_research_results and generates review queries
    that identify gaps needing further exploration.
    Emits progress events via StreamWriter for real-time tracking.
    """
    query = state["query"]
    query_num = state.get("query_num", 0)
    research_results = state["raw_research_results"]
    iteration = state.get("iteration_count", 0)
    
    emit_node_progress(writer, "reviewer", query_num, "started", 50)
    
    if iteration >= MAX_ITERATIONS:
        logger.info(f"[reviewer_node] Max iterations ({MAX_ITERATIONS}) reached. Stopping reviews.")
        emit_node_progress(writer, "reviewer", query_num, "completed", 100, {"status": "max_iterations"})
        return {
            "current_reviews": [],
            "review_feedback": [],
            "iteration_count": iteration
        }
    
    logger.info(f"[reviewer_node] Iteration {iteration}: Generating reviews...")
    
    reviewer = Reviewer(num_review_queries=3)
    reviews = reviewer.generate_reviews(query, research_results)
    
    logger.info(f"[reviewer_node] Generated {len(reviews)} reviews and the main query is {state['query']}")
    emit_node_progress(writer, "reviewer", query_num, "completed", 70, {"reviews_count": len(reviews)})
    
    return {
        "current_reviews": reviews,
        "review_feedback": reviews,
        "iteration_count": iteration + 1,
        "logs": [{
            "message_id": str(uuid.uuid4()),
            "role": "system",
            "content": f"Reviewer #{query_num} generated {len(reviews)} follow-up questions.",
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": "log",
            "metadata": {"query_num": query_num, "step": "reviewer"}
        }]
    }


async def resolve_node(state: ResearchReviewData, writer: StreamWriter) -> Dict[str, Any]:
    """
    Resolve node that answers review questions using web search.
    
    Takes current_reviews and resolves each using web search.
    Results are appended to raw_research_results as List[RawResearchResult].
    Emits progress events via StreamWriter for real-time tracking.
    """
    current_reviews = state.get("current_reviews", [])
    query_num = state.get("query_num", 0)
    
    emit_node_progress(writer, "resolver", query_num, "started", 75)
    logger.info(f"[resolve_node] Resolving {len(current_reviews)} reviews...")
    
    new_results = []
    review_query = ", ".join(current_reviews)
    solver = Solver(
        query=review_query,
        num_web_queries=1,
        max_web_results=2,
        num_gaps_per_node=0
    )
    
    _, answer = await solver.resolve()
    
    # Handle case where LLM returns string instead of dict
    if isinstance(answer, dict):
        for q, a in answer.items():
            new_results.append({
                "query": q,
                "answer": a,
                "parent_query": review_query,
                "depth": 0,
                "section_id": str(uuid.uuid4())
            })
    elif isinstance(answer, str) and answer:
        new_results.append({
            "query": review_query,
            "answer": answer,
            "parent_query": review_query,
            "depth": 0,
            "section_id": str(uuid.uuid4())
        })

    logger.info(f"[resolve_node] Added {len(new_results)} new research results")
    emit_node_progress(writer, "resolver", query_num, "completed", 90, {"results_count": len(new_results)})

    return {
        "raw_research_results": new_results,
        "logs": [{
            "message_id": str(uuid.uuid4()),
            "role": "system", 
            "content": f"Resolver #{query_num} answered {len(new_results)} questions.",
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": "log",
            "metadata": {"query_num": query_num, "step": "resolver"}
        }]
    }


def should_continue(state: ResearchReviewData) -> str:
    """
    Conditional edge function to determine if loop should continue.
    
    Returns:
        "resolve_node" if there are reviews to process
        END if no more reviews (research is complete)
    """
    current_reviews = state.get("current_reviews", [])
    
    if current_reviews:
        logger.info(f"[should_continue] {len(current_reviews)} reviews pending -> continue")
        return "resolve_node"
    else:
        logger.info("[should_continue] No reviews -> END")
        return END


def build_researcher_reviewer_subgraph() -> StateGraph:
    """
    Build the Researcher-Reviewer loop subgraph.
    
    Flow: researcher_node -> reviewer_node -> (conditional) -> resolve_node -> reviewer_node -> ...
    Loop continues until reviewer_node returns empty current_reviews.
    
    Returns:
        Compiled StateGraph ready to be invoked.
    """
    workflow = StateGraph(ResearchReviewData)
    
    workflow.add_node("researcher_node", researcher_node)
    workflow.add_node("reviewer_node", reviewer_node)
    workflow.add_node("resolve_node", resolve_node)
    
    workflow.set_entry_point("researcher_node")
    workflow.add_edge("researcher_node", "reviewer_node")
    
    workflow.add_conditional_edges(
        "reviewer_node",
        should_continue,
        {
            "resolve_node": "resolve_node",
            END: END
        }
    )
    
    workflow.add_edge("resolve_node", "reviewer_node")
    return workflow.compile()