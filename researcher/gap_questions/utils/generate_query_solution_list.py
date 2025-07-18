import logging
from typing import List, Dict, Any

from ..query_generators.vector_search_query_generator import VectorSearchQueryGenerator
from ..search_query_processor.query_processor import QueryProcessor

logger = logging.getLogger(__name__)


def generate_query_solution_list(
    gaps: List[str],
    vector_search_generator: VectorSearchQueryGenerator,
    query_processor: QueryProcessor,
    max_gap_queries: int = 3
) -> List[Dict[str, Any]]:
    """Generate solutions for identified gaps using simplified search."""
    try:
        final_solutions = []
        
        logger.info(f"Processing {len(gaps)} gaps")
        
        # Collect all vector queries
        all_vector_queries = []
        gap_to_queries = {}
        
        for gap in gaps:
            vector_queries = vector_search_generator.generate_vector_search_queries(
                gap, max_queries=max_gap_queries
            )
            gap_to_queries[gap] = vector_queries
            all_vector_queries.extend(vector_queries)
        
        # Search all queries using simplified search_only method
        if all_vector_queries:
            logger.info(f"Searching {len(all_vector_queries)} vector queries")
            all_search_results = query_processor.search_only(all_vector_queries, k=3)
            
            # Group results by gap (simplified approach)
            for gap in gaps:
                gap_queries = gap_to_queries.get(gap, [])
                
                # For simplicity, take a portion of results for each gap
                # This is a simple distribution - could be made more sophisticated
                results_per_gap = len(all_search_results) // len(gaps) if gaps else 0
                gap_start_idx = gaps.index(gap) * results_per_gap
                gap_end_idx = gap_start_idx + results_per_gap
                
                gap_solutions = all_search_results[gap_start_idx:gap_end_idx] if all_search_results else []
                
                # Create solution
                solution_data = {
                    "gap": gap,
                    "vector_queries": gap_queries,
                    "solution": _curate_gap_solution(gap, gap_solutions),
                    "source_count": len(gap_solutions)
                }
                
                final_solutions.append(solution_data)
        
        logger.info(f"Processing completed for {len(gaps)} gaps")
        
        return final_solutions
        
    except Exception as e:
        logger.error(f"Failed to generate query solution list: {e}")
        return []


def _curate_gap_solution(gap: str, solutions: List[Dict[str, Any]]) -> str:
    """Curate a solution for a specific gap."""
    if not solutions:
        return f"No information found to address: {gap}"
    
    # Combine solutions into a coherent response
    content_parts = []
    for sol in solutions[:3]:  # Use top 3 solutions
        if sol.get("content"):
            content_parts.append(sol["content"][:200])
    
    return " ".join(content_parts) if content_parts else f"Limited information available for: {gap}"