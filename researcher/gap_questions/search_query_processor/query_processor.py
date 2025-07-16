import asyncio
import logging
from typing import List, Dict, Any, Optional
from .collector import DataCollector
from .store_update import VectorStoreUpdater
from ...vectore_store import VectorStoreManager

logger = logging.getLogger(__name__)

class QueryProcessor:
    """Main entry point for query processing workflow."""
    
    def __init__(self, vector_store_manager: Optional[VectorStoreManager] = None, 
                 max_results_per_query: int = 1):
        """
        Initialize QueryProcessor with vector store manager.
        
        Args:
            vector_store_manager: Pre-initialized VectorStoreManager instance
            max_results_per_query: Maximum number of web search results per query
        """
        self.max_results_per_query = max_results_per_query
        self.collector = DataCollector(max_results=max_results_per_query)
        if vector_store_manager:
            self.store_updater = VectorStoreUpdater(vector_store_manager=vector_store_manager)
        else:
            self.store_updater = None
    
    async def process_multiple_queries(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple web search queries, collect data, and store in vector DB in one shot.
        
        Args:
            queries (List[str]): List of web search queries
            
        Returns:
            List[Dict[str, Any]]: List of search results with source and content
            
        Raises:
            Exception: If any step in the workflow fails
        """
        try:
            logger.info(f"Processing {len(queries)} web search queries")
            
            # Step 1: Collect data from all queries (1 result per query by default)
            all_collected_data = []
            
            for query in queries:
                logger.info(f"Collecting data for query: '{query}'")
                scraped_data = await self.collector.collect_data(query, self.max_results_per_query)
                
                if scraped_data:
                    logger.info(f"Collected {len(scraped_data)} results for query: '{query}'")
                    all_collected_data.extend(scraped_data)
                else:
                    logger.warning(f"No data collected for query: '{query}'")
            
            if not all_collected_data:
                logger.warning("No data collected from any queries")
                return []
            
            logger.info(f"Total collected data: {len(all_collected_data)} items")
            
            # Step 2: Store all collected data in vector DB in one shot
            if self.store_updater:
                logger.info("Storing all collected data in vector store...")
                update_success = self.store_updater.update_vector_store(all_collected_data)
                
                if not update_success:
                    logger.error("Failed to update vector store")
                    return []
                
                logger.info("All data successfully stored in vector store")
                return all_collected_data
            else:
                logger.warning("No vector store manager provided, returning raw collected data")
                return all_collected_data
            
        except Exception as e:
            logger.error(f"Error in multi-query processing workflow: {e}")
            raise Exception(f"Multi-query processing failed: {str(e)}")
    
    async def process_query(self, query: str, max_web_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Process single web search query (wrapper for backward compatibility).
        
        Args:
            query (str): The web search query
            max_web_results (int, optional): Maximum number of web search results
            
        Returns:
            List[Dict[str, Any]]: List of search results with source and content
        """
        # Override max_results_per_query if specified
        if max_web_results:
            old_max = self.max_results_per_query
            self.max_results_per_query = max_web_results
            self.collector = DataCollector(max_results=max_web_results)
            
            result = await self.process_multiple_queries([query])
            
            # Restore original value
            self.max_results_per_query = old_max
            self.collector = DataCollector(max_results=old_max)
            return result
        else:
            return await self.process_multiple_queries([query])
    
    def search_only(self, vector_search_queries: List[str], k: int = 8) -> List[Dict[str, Any]]:
        """
        Search vector store only without collecting new data.
        
        Args:
            vector_search_queries (List[str]): List of search queries for vector store
            k (int): Number of top results to return per query
            
        Returns:
            List[Dict[str, Any]]: List of search results
        """
        if self.store_updater:
            return self.store_updater.search_vector_store(vector_search_queries, k)
        else:
            logger.warning("No vector store manager available for search")
            return []