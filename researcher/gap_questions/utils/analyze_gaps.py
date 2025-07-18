import json
import logging
from typing import List

from ..llm_client import GeminiLLMClient
from ..prompts import create_gap_analysis_prompt
from ...vectore_store import VectorStoreManager

logger = logging.getLogger(__name__)


def analyze_gaps(
    query: str,
    llm_client: GeminiLLMClient,
    vector_store_manager: VectorStoreManager,
    performance_metrics: dict,
    max_gaps: int = 5
) -> List[str]:
    """Analyze gaps in content to identify missing information."""
    try:
        # Get content from vector store
        vector_content = _get_vector_store_content(query, vector_store_manager)
        if not vector_content:
            return []
        
        # Generate gaps using LLM
        prompt = create_gap_analysis_prompt(query, vector_content)
        response = llm_client.generate(prompt, context="gap_analysis", model_type="analysis")
        performance_metrics["llm_calls"] += 1
        
        # Parse result
        gaps = _parse_gaps_response(response)[:max_gaps]
        
        return gaps
        
    except Exception as e:
        logger.error(f"Failed to analyze gaps: {e}")
        return []


def _get_vector_store_content(query: str, vector_store_manager: VectorStoreManager, k: int = 10) -> str:
    """Get content from vector store for gap analysis."""
    try:
        results = vector_store_manager.similarity_search(query, k=k)
        content = "\n\n".join([doc.page_content[:500] for doc in results])
        return content
    except Exception as e:
        logger.error(f"Failed to get vector store content: {e}")
        return ""


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