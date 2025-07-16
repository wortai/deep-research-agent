import asyncio
import logging
from typing import List, Dict, Any, Optional
from researcher.web_search import WebSearch

logger = logging.getLogger(__name__)

class DataCollector:
    """Handles data collection using web search functionality."""
    
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
    
    async def collect_data(self, query: str, max_web_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Collects data using web search.
        
        Args:
            query (str): The search query
            max_web_results (int, optional): Maximum number of web search results
            
        Returns:
            List[Dict[str, Any]]: List of scraped data with url and content
            
        Raises:
            Exception: If web search fails
        """
        try:
            # Validate query before proceeding
            if not query or not isinstance(query, str) or not query.strip():
                logger.error("Query must be a non-empty string")
                return []
            
            results_limit = max_web_results or self.max_results
            logger.info(f"Initiating web search for query: '{query.strip()}'")
            
            web_search = WebSearch(query=query, max_results=results_limit)
            scraped_data = await web_search.initiate_research()
            
            if not scraped_data:
                logger.warning("No data scraped from web search")
                return []
                
            logger.info(f"Successfully scraped data from {len(scraped_data)} URLs")
            return scraped_data
            
        except ValueError as e:
            logger.error(f"Invalid query provided: {e}")
            return []
        except Exception as e:
            logger.error(f"Error during data collection: {e}")
            raise Exception(f"Data collection failed: {str(e)}")