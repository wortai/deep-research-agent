import asyncio
import logging
from typing import List, Dict, Any, Optional
from .collector import DataCollector
from .store_update import VectorStoreUpdater
from ...vectore_store import VectorStoreManager

logger = logging.getLogger(__name__)

class QueryProcessor:
    """Main entry point for query processing workflow."""
    
    def __init__(self, vector_store_manager: Optional[VectorStoreManager] = None, max_results: int = 5):
        """
        Initialize QueryProcessor with vector store manager.
        
        Args:
            vector_store_manager: Pre-initialized VectorStoreManager instance
            max_results: Maximum number of web search results
        """
        self.collector = DataCollector(max_results=max_results)
        if vector_store_manager:
            self.store_updater = VectorStoreUpdater(vector_store_manager=vector_store_manager)
        else:
            self.store_updater = None
    
    async def process_query(
        self, 
        query: str, # Query to search the web
        max_web_results: Optional[int] = None,
        vector_search_queries: Optional[List[str]] = None # Queries to search the vector store
    ) -> List[Dict[str, Any]]:
        """
        Main workflow: collect data, update vector store, and search.
        
        Args:
            query (str): The initial web search query
            max_web_results (int, optional): Maximum number of web search results
            vector_search_queries (List[str], optional): Custom search queries for vector store
            
        Returns:
            List[Dict[str, Any]]: List of search results with source and content
            
        Raises:
            Exception: If any step in the workflow fails
        """
        try:
            logger.info(f"Starting query processing workflow for: '{query}'")
            
            # Step 1: Collect data
            scraped_data = await self.collector.collect_data(query, max_web_results)
            
            if not scraped_data:
                logger.warning("No data collected, cannot proceed with workflow")
                return []
            
            # Step 2: Update vector store (if available)
            if self.store_updater:
                update_success = self.store_updater.update_vector_store(scraped_data)
                
                if not update_success:
                    logger.error("Failed to update vector store")
                    return []
                
                # Step 3: Generate search queries if not provided
                if vector_search_queries is None:
                    vector_search_queries = [
                        f"What are the key findings about {query}?",
                        f"facts related to {query}",
                    ]
                    logger.info("Using default vector search queries")
                else:
                    logger.info(f"Using provided vector search queries: {vector_search_queries}")
                
                # Step 4: Search vector store
                results = self.store_updater.search_vector_store(vector_search_queries)
                
                logger.info(f"Query processing workflow completed. Found {len(results)} results")
                return results
            else:
                logger.warning("No vector store manager provided, returning raw scraped data")
                return scraped_data
            
        except Exception as e:
            logger.error(f"Error in query processing workflow: {e}")
            raise Exception(f"Query processing failed: {str(e)}")
    
    async def collect_only(self, query: str, max_web_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Collect data only without updating vector store.
        
        Args:
            query (str): The search query
            max_web_results (int, optional): Maximum number of web search results
            
        Returns:
            List[Dict[str, Any]]: List of scraped data
        """
        return await self.collector.collect_data(query, max_web_results)
    
    def search_only(self, vector_search_queries: List[str], k: int = 8) -> List[Dict[str, Any]]:
        """
        Search vector store only without collecting new data.
        
        Args:
            vector_search_queries (List[str]): List of search queries for vector store
            k (int): Number of top results to return
            
        Returns:
            List[Dict[str, Any]]: List of search results
        """
        if self.store_updater:
            return self.store_updater.search_vector_store(vector_search_queries, k)
        else:
            logger.warning("No vector store manager available for search")
            return []