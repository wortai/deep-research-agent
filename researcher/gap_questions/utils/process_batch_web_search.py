import logging
from typing import List, Dict, Any

from ..search_query_processor.query_processor import QueryProcessor

logger = logging.getLogger(__name__)


async def process_batch_web_search(
    queries: List[str],
    query_processor: QueryProcessor
) -> List[Dict[str, Any]]:
    """Process web search queries using the new simplified logic."""
    try:
        logger.info(f"Processing {len(queries)} web search queries in batch")
        
        # Use the new process_multiple_queries method
        # This will collect 1 result per query by default and store all in vector DB in one shot
        all_results = await query_processor.process_multiple_queries(queries)
        
        logger.info(f"Batch processing completed. Collected {len(all_results)} total results")
        return all_results
        
    except Exception as e:
        logger.error(f"Batch web search processing failed: {e}")
        return []