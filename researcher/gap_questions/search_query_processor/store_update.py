import logging
from typing import List, Dict, Any, Optional
from researcher.vectore_store import QdrantService, VectorStoreManager

logger = logging.getLogger(__name__)

class VectorStoreUpdater:
    """Handles vector store updates with collected data."""
    
    def __init__(self, vector_store_manager: VectorStoreManager):
        """
        Initialize with pre-configured vector store manager.
        
        Args:
            vector_store_manager: Already initialized VectorStoreManager instance
        """
        self.vector_store_manager = vector_store_manager
    
    def update_vector_store(self, scraped_data: List[Dict[str, Any]]) -> bool:
        """
        Updates vector store with scraped data.
        
        Args:
            scraped_data (List[Dict[str, Any]]): List of data with url and content
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            Exception: If vector store update fails
        """
        try:
            if not scraped_data:
                logger.warning("No data provided for vector store update")
                return False
            
            logger.info("Loading data into vector store...")
            self.vector_store_manager.load(scraped_data)
            logger.info("Data successfully loaded into vector store")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating vector store: {e}")
            raise Exception(f"Vector store update failed: {str(e)}")
    
    def search_vector_store(self, search_queries: List[str], k: int = 8) -> List[Dict[str, Any]]:
        """
        Searches vector store with provided queries.
        
        Args:
            search_queries (List[str]): List of search queries
            k (int): Number of top results to return
            
        Returns:
            List[Dict[str, Any]]: List of search results with source and content
            
        Raises:
            Exception: If vector store search fails
        """
        try:
            if not search_queries:
                logger.warning("No search queries provided")
                return []
            
            extract_data = []
            
            for search_query in search_queries:
                logger.info(f"Searching vector store for: '{search_query}'")
                
                vector_search_results = self.vector_store_manager.similarity_search(
                    query=search_query, k=k
                )
                
                if vector_search_results:
                    logger.info(f"Found {len(vector_search_results)} relevant documents")
                    for doc in vector_search_results:
                        extract_data.append({
                            "source": doc.metadata.get('source', 'N/A'),
                            "content": doc.page_content
                        })
                else:
                    logger.info("No relevant documents found for this query")
            
            return extract_data
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise Exception(f"Vector store search failed: {str(e)}")