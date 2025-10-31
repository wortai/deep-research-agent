"""
LangGraph orchestration for Researcher (Solver) and Reviewer workflow.

This module provides a complete pipeline that:
1. Takes a list of initial queries
2. Runs Research-Review cycles in parallel with configurable workers
3. Tracks analytics (LLM calls, Q&A pairs)
4. Dumps results to a comprehensive output file
"""

import asyncio
import json
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Annotated
import operator
from pathlib import Path
from collections import defaultdict

from langgraph.graph import StateGraph, END
from researcher.solution_tree.main import Solver
from reviewer.reviewer import Reviewer


# =============================================================================
# STATE DEFINITION
# =============================================================================

class ResearcherReviewerState(TypedDict):
    """State for parallel Researcher-Reviewer workflow."""

    # Input
    plan: List[str]  # List of queries in the research plan to execute in parallel

    # Researcher outputs (thread-safe via Annotated merge)
    solver_answers: Dict[str, Dict[str, str]]  # {query: {sub_q: answer}}
    solver_gaps: Dict[str, List[str]]  # {query: [gap_questions]}

    # Reviewer outputs
    enriched_content: Dict[str, Dict[str, str]]  # {query: enriched_answers}

    # Analytics (thread-safe accumulation)
    total_llm_calls: Annotated[int, operator.add]  # Cumulative LLM calls
    total_qa_pairs: Annotated[int, operator.add]  # Total Q&A pairs
    llm_calls_per_query: Dict[str, int]  # {query: num_calls}
    qa_pairs_per_query: Dict[str, int]  # {query: num_pairs}

    # Workflow control
    status: str  # "processing" | "complete"


# =============================================================================
# PARALLEL RESEARCH-REVIEW WORKER
# =============================================================================

async def process_single_query(
    query: str,
    query_idx: int,
    total_queries: int
) -> Dict[str, Any]:
    """
    Process a single query through Research -> Review pipeline.

    Returns a dict with all results and analytics for this query.
    """
    print(f"\n{'='*80}")
    print(f"[Worker {query_idx + 1}/{total_queries}] STARTING: {query}")
    print(f"{'='*80}\n")

    # ========== RESEARCH PHASE ==========
    print(f"[Worker {query_idx + 1}] RESEARCHING...")

    solver = Solver(
        query=query,
        num_web_queries=3,
        num_vector_queries=3,
        max_web_results=3,
        collection_name="research-documents",
        batch_size=100,
        num_gaps_per_node=2
    )

    gaps, answer = await solver.resolve()

    # Research analytics
    research_llm_calls = 3  # web + vector + analysis
    research_qa_pairs = len(answer)

    print(f"[Worker {query_idx + 1}] RESEARCH COMPLETE")
    print(f"  - Q&A pairs: {research_qa_pairs}")
    print(f"  - Gaps: {len(gaps)}")

    # ========== REVIEW PHASE ==========
    print(f"[Worker {query_idx + 1}] REVIEWING...")

    reviewer = Reviewer(
        num_review_queries=3,
        collection_name="research-documents"
    )

    enriched = await reviewer.review_and_enrich(
        original_query=query,
        content=answer
    )

    # Review analytics
    review_llm_calls = 1 + (3 * 3)  # generation + 3 queries * 3 calls each
    review_qa_pairs = len(enriched) - len(answer)

    total_llm_calls = research_llm_calls + review_llm_calls
    total_qa_pairs = research_qa_pairs + review_qa_pairs

    print(f"[Worker {query_idx + 1}] REVIEW COMPLETE")
    print(f"  - New Q&A pairs: {review_qa_pairs}")
    print(f"  - Total Q&A pairs: {total_qa_pairs}")
    print(f"  - Total LLM calls: {total_llm_calls}")
    print(f"{'='*80}\n")

    return {
        "query": query,
        "solver_answer": answer,
        "solver_gaps": gaps,
        "enriched_content": enriched,
        "llm_calls": total_llm_calls,
        "qa_pairs": total_qa_pairs
    }


async def parallel_process_node(state: ResearcherReviewerState) -> ResearcherReviewerState:
    """
    Process all queries in the plan in parallel with configurable concurrency.
    """
    plan = state["plan"]

    print(f"\n{'='*80}")
    print(f"PARALLEL PROCESSING: {len(plan)} queries in plan")
    print(f"{'='*80}\n")

    # Create tasks for all queries in the plan
    tasks = [
        process_single_query(query, idx, len(plan))
        for idx, query in enumerate(plan)
    ]

    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)

    # Aggregate results into state
    for result in results:
        query = result["query"]
        state["solver_answers"][query] = result["solver_answer"]
        state["solver_gaps"][query] = result["solver_gaps"]
        state["enriched_content"][query] = result["enriched_content"]
        state["llm_calls_per_query"][query] = result["llm_calls"]
        state["qa_pairs_per_query"][query] = result["qa_pairs"]

        # Accumulate totals
        state["total_llm_calls"] += result["llm_calls"]
        state["total_qa_pairs"] += result["qa_pairs"]

    state["status"] = "complete"
    return state


async def complete_node(state: ResearcherReviewerState) -> ResearcherReviewerState:
    """Final node - dump results to file."""
    print(f"\n{'='*80}")
    print("ALL QUERIES COMPLETE - Generating Output")
    print(f"{'='*80}\n")

    state["status"] = "complete"
    return state


# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================

def build_graph() -> StateGraph:
    """Build the parallel Researcher-Reviewer LangGraph."""

    workflow = StateGraph(ResearcherReviewerState)

    # Add nodes
    workflow.add_node("parallel_process", parallel_process_node)
    workflow.add_node("complete", complete_node)

    # Set entry point and edges
    workflow.set_entry_point("parallel_process")
    workflow.add_edge("parallel_process", "complete")
    workflow.add_edge("complete", END)

    return workflow.compile()


# =============================================================================
# RESULT DUMPING
# =============================================================================

def dump_results(state: ResearcherReviewerState, output_dir: str = "workflow_results"):
    """
    Dump comprehensive results to markdown and JSON files.

    Creates:
    - {output_dir}/{timestamp}_results.md - Human-readable results
    - {output_dir}/{timestamp}_analytics.json - Analytics data
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # =============================================================================
    # MARKDOWN OUTPUT
    # =============================================================================

    md_file = output_path / f"{timestamp}_results.md"

    with open(md_file, "w", encoding="utf-8") as f:
        # Header
        f.write("# Researcher-Reviewer Workflow Results\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Total Queries in Plan:** {len(state['plan'])}\n")
        f.write(f"- **Total LLM Calls:** {state['total_llm_calls']}\n")
        f.write(f"- **Total Q&A Pairs:** {state['total_qa_pairs']}\n")
        f.write(f"- **Avg LLM Calls/Query:** {state['total_llm_calls'] / len(state['plan']):.1f}\n")
        f.write(f"- **Avg Q&A Pairs/Query:** {state['total_qa_pairs'] / len(state['plan']):.1f}\n\n")

        # Per-query analytics
        f.write("## Query Analytics\n\n")
        f.write("| Query | LLM Calls | Q&A Pairs | Gaps Found |\n")
        f.write("|-------|-----------|-----------|------------|\n")

        for query in state["plan"]:
            llm_calls = state["llm_calls_per_query"].get(query, 0)
            qa_pairs = state["qa_pairs_per_query"].get(query, 0)
            gaps = len(state["solver_gaps"].get(query, []))
            f.write(f"| {query[:50]}... | {llm_calls} | {qa_pairs} | {gaps} |\n")

        f.write("\n")

        # Detailed results per query
        f.write("## Detailed Results\n\n")

        for idx, query in enumerate(state["plan"], 1):
            f.write(f"### Query {idx}: {query}\n\n")

            # Researcher Results
            f.write("#### Researcher Output\n\n")
            solver_answers = state["solver_answers"].get(query, {})

            for sub_q, answer in solver_answers.items():
                f.write(f"**Q:** {sub_q}\n\n")
                f.write(f"{answer}\n\n")
                f.write("---\n\n")

            # Gap Questions
            gaps = state["solver_gaps"].get(query, [])
            if gaps:
                f.write("**Identified Gaps:**\n\n")
                for gap in gaps:
                    f.write(f"- {gap}\n")
                f.write("\n")

            # Reviewer Results
            f.write("#### Reviewer Enrichment\n\n")
            enriched = state["enriched_content"].get(query, {})

            # Get only new answers (not in solver_answers)
            new_answers = {k: v for k, v in enriched.items() if k not in solver_answers}

            if new_answers:
                for sub_q, answer in new_answers.items():
                    f.write(f"**Q:** {sub_q}\n\n")
                    f.write(f"{answer}\n\n")
                    f.write("---\n\n")
            else:
                f.write("*No additional enrichment added*\n\n")

            f.write(f"\n{'='*80}\n\n")

    # =============================================================================
    # JSON OUTPUT
    # =============================================================================

    json_file = output_path / f"{timestamp}_analytics.json"

    analytics = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_queries_in_plan": len(state["plan"]),
            "total_llm_calls": state["total_llm_calls"],
            "total_qa_pairs": state["total_qa_pairs"],
            "avg_llm_calls_per_query": state["total_llm_calls"] / len(state["plan"]),
            "avg_qa_pairs_per_query": state["total_qa_pairs"] / len(state["plan"])
        },
        "plan": state["plan"],
        "query_results": []
    }

    for query in state["plan"]:
        query_data = {
            "query": query,
            "llm_calls": state["llm_calls_per_query"].get(query, 0),
            "qa_pairs": state["qa_pairs_per_query"].get(query, 0),
            "gaps_found": len(state["solver_gaps"].get(query, [])),
            "gaps": state["solver_gaps"].get(query, []),
            "researcher_qa_count": len(state["solver_answers"].get(query, {})),
            "reviewer_qa_count": len(state["enriched_content"].get(query, {})) - len(state["solver_answers"].get(query, {}))
        }
        analytics["query_results"].append(query_data)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=2)

    print(f"\n[RESULTS SAVED]")
    print(f"  - Markdown: {md_file}")
    print(f"  - Analytics: {json_file}")

    return md_file, json_file


# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def run_researcher_reviewer_workflow(
    plan: List[str],
    output_dir: str = "workflow_results",
    max_concurrent: int = 3
) -> ResearcherReviewerState:
    """
    Execute the complete Researcher-Reviewer workflow in parallel.

    Args:
        plan: List of queries in the research plan to execute in parallel
        output_dir: Directory to save results
        max_concurrent: Maximum concurrent Research-Review cycles (default: 3)

    Returns:
        Final state with all results and analytics
    """
    print(f"\n{'='*80}")
    print("PARALLEL RESEARCHER-REVIEWER WORKFLOW")
    print(f"{'='*80}")
    print(f"Queries in Plan: {len(plan)}")
    print(f"Max Concurrent Workers: {max_concurrent}")
    print(f"Output: {output_dir}/")
    print(f"{'='*80}\n")

    # Initialize state
    final_state: ResearcherReviewerState = {
        "plan": plan,
        "solver_answers": {},
        "solver_gaps": {},
        "enriched_content": {},
        "total_llm_calls": 0,
        "total_qa_pairs": 0,
        "llm_calls_per_query": {},
        "qa_pairs_per_query": {},
        "status": "processing"
    }

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)

    async def controlled_process(query: str, idx: int, total: int) -> Dict[str, Any]:
        """Process with semaphore control."""
        async with semaphore:
            return await process_single_query(query, idx, total)

    # Process with concurrency limit
    tasks = [
        controlled_process(query, idx, len(plan))
        for idx, query in enumerate(plan)
    ]

    results = await asyncio.gather(*tasks)

    # Aggregate results into state
    for result in results:
        query = result["query"]
        final_state["solver_answers"][query] = result["solver_answer"]
        final_state["solver_gaps"][query] = result["solver_gaps"]
        final_state["enriched_content"][query] = result["enriched_content"]
        final_state["llm_calls_per_query"][query] = result["llm_calls"]
        final_state["qa_pairs_per_query"][query] = result["qa_pairs"]
        final_state["total_llm_calls"] += result["llm_calls"]
        final_state["total_qa_pairs"] += result["qa_pairs"]

    final_state["status"] = "complete"

    # Dump results
    dump_results(final_state, output_dir)

    print(f"\n{'='*80}")
    print("WORKFLOW COMPLETE")
    print(f"{'='*80}")
    print(f"Total LLM Calls: {final_state['total_llm_calls']}")
    print(f"Total Q&A Pairs: {final_state['total_qa_pairs']}")
    print(f"{'='*80}\n")

    return final_state


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

async def main():
    """Example usage of the Researcher-Reviewer workflow."""

    # Define research plan - list of queries to execute in parallel
    research_plan = [
        "What are the limitations of traditional Convolutional Neural Networks (CNNs) that prompted researchers to look for a new architecture for vision tasks?",
        "How does a Vision Transformer (ViT) reframe an image processing problem into a sequence processing problem, similar to how Transformers handle text?"
    ]

    # Run workflow with 3 concurrent workers
    final_state = await run_researcher_reviewer_workflow(
        plan=research_plan,
        output_dir="workflow_results",
        max_concurrent=3
    )

    # Access results programmatically if needed
    for query in research_plan:
        print(f"\nQuery: {query}")
        print(f"  - Solver Q&A: {len(final_state['solver_answers'][query])}")
        print(f"  - Enriched Q&A: {len(final_state['enriched_content'][query])}")
        print(f"  - Gaps: {len(final_state['solver_gaps'][query])}")


if __name__ == "__main__":
    asyncio.run(main())
