import json
import logging
from typing import List, Tuple, Dict, Any

from ..llm_client import GeminiLLMClient
from ..prompts import create_gap_analysis_prompt
from ..query_generators.vector_search_query_generator import VectorSearchQueryGenerator
from ...vectore_store import VectorStoreManager

logger = logging.getLogger(__name__)


def analyze_gaps(
    query: str,
    llm_client: GeminiLLMClient,
    vector_store_manager: VectorStoreManager,
    performance_metrics: dict,
    max_gaps: int = 5
) -> Tuple[List[str], List[Tuple[str, str, List[str]]]]:
    """Analyze gaps in content to identify missing information.
    
    Returns:
        Tuple containing:
        - List of gaps found
        - List of (vector_search_query, document_content, urls) tuples for raw_research_results
    """
    try:
        # Initialize vector search query generator
        vector_search_generator = VectorSearchQueryGenerator()
        
        # Generate optimized vector search queries for the plan query
        search_queries = vector_search_generator.generate_vector_search_queries(
            gap=query, max_queries=5 # Increased from 3 to 5 for more comprehensive search
        )
        
        # Get content from vector store using optimized queries
        if not search_queries:
            # Fallback to direct query if no optimized queries generated
            logger.warning("No optimized queries generated, falling back to direct search")
            results = vector_store_manager.similarity_search(query, k=3)  # Increased from 10 to 15
        else:
            # Search using all generated queries and combine results
            all_results = []
            results_per_query = max(1, 15 // len(search_queries))  # Increased base from 10 to 15
            
            for search_query in search_queries:
                query_results = vector_store_manager.similarity_search(search_query, k=results_per_query)
                all_results.extend(query_results)
            
            # Remove duplicates and limit to 10 results
            seen_content = set()
            unique_results = []
            for result in all_results:
                if result.page_content not in seen_content:
                    seen_content.add(result.page_content)
                    unique_results.append(result)
                    if len(unique_results) >= 15:
                        break
            
            results = unique_results
        
        # Prepare data for raw_research_results
        research_results = []
        
        # Extract content from vector store results and prepare for raw_research_results
        vector_content = ""
        for i, search_query in enumerate(search_queries):
            # Get results for this specific query
            query_results = vector_store_manager.similarity_search(search_query, k=3)
            
            # Extract content and URLs for this query
            query_content = ""
            query_urls = []
            for doc in query_results:
                query_content += doc.page_content[:400] + "\n\n"
                # Extract URL from metadata if available
                if hasattr(doc, 'metadata') and doc.metadata.get('source'):
                    query_urls.append(doc.metadata.get('source'))
            
            # Add to research results
            if query_content.strip():
                research_results.append((search_query, query_content.strip(), query_urls))
                vector_content += query_content
        
        # If no search queries were generated, use direct query
        if not search_queries:
            direct_content = ""
            direct_urls = []
            for doc in results:
                direct_content += doc.page_content[:400] + "\n\n"
                if hasattr(doc, 'metadata') and doc.metadata.get('source'):
                    direct_urls.append(doc.metadata.get('source'))
            
            if direct_content.strip():
                research_results.append((query, direct_content.strip(), direct_urls))
                vector_content = direct_content
        
        logger.info(f"Retrieved {len(results)} documents for gap analysis")
        
        if not vector_content:
            return [], []
        
        # Generate gaps using LLM
        prompt = create_gap_analysis_prompt(query, vector_content)
        response = llm_client.generate(prompt, context="gap_analysis", model_type="analysis")
        performance_metrics["llm_calls"] += 1
        
        # Parse result
        gaps = _parse_gaps_response(response)[:max_gaps]
        
        return gaps, research_results
        
    except Exception as e:
        logger.error(f"Failed to analyze gaps: {e}")
        return [], []


def _parse_gaps_response(response: str) -> List[str]:
    """Parse gaps from LLM response."""
    try:
        response_clean = response.strip()
        start_idx = response_clean.find('[')
        end_idx = response_clean.rfind(']') + 1
        
        if start_idx == -1 or end_idx == 0:
            return []
        
        json_str = response_clean[start_idx:end_idx]
        gaps = json.loads(json_str)
        
        if isinstance(gaps, list):
            return [gap.strip() for gap in gaps if isinstance(gap, str) and gap.strip()]
        return []
        
    except Exception as e:
        logger.error(f"Failed to parse gaps response: {e}")
        return []
