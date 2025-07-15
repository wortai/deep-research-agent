"""
Research and vector store operations module
"""

import asyncio
import logging
from typing import List, Dict
from datetime import datetime


class ResearchManager:
    """Handles research workflow and vector store operations"""
    
    def __init__(self, vector_store_manager, web_search_class, monitor=None):
        self.vector_store_manager = vector_store_manager
        self.web_search_class = web_search_class
        self.monitor = monitor
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def research_and_store(self, query: str, vector_queries: List[str], 
                                max_web_results: int = 5) -> List[Dict]:
        """
        Integrated research workflow: web search, vector store, and similarity search.
        """
        step_start = datetime.now()
        
        if self.monitor:
            self.monitor.log_step("research_and_store", "started", {
                "query": query, 
                "max_web_results": max_web_results,
                "vector_queries_count": len(vector_queries)
            })
        
        extracted_data = []
        
        try:
            # Step 1: Web Search and Data Extraction (only if web results requested)
            if max_web_results > 0:
                self.logger.info(f"Performing web search for: {query}")
                web_search = self.web_search_class(query=query, max_results=max_web_results)
                scraped_data = await web_search.initiate_research()
                
                if scraped_data:
                    self.logger.info(f"Successfully scraped data from {len(scraped_data)} URLs")
                    # Load new data into vector store
                    self.vector_store_manager.load(scraped_data)
                    self.logger.info("New data loaded into vector store")
                else:
                    self.logger.warning("No data scraped from web search")
            
            # Step 2: Vector Store Similarity Search
            self.logger.info("Performing vector store similarity search")
            
            # Search vector store for each query
            for search_query in vector_queries:
                self.logger.info(f"Searching vector store for: '{search_query}'")
                
                search_results = self.vector_store_manager.similarity_search(
                    query=search_query, 
                    k=4  # Top 4 results per query
                )
                
                if search_results:
                    self.logger.info(f"Found {len(search_results)} relevant documents")
                    for doc in search_results:
                        extracted_data.append({
                            "source": doc.metadata.get('source', 'vector_store'),
                            "content": doc.page_content
                        })
                else:
                    self.logger.info("No relevant documents found for this query")
            
            # Remove duplicates based on content similarity
            extracted_data = self._deduplicate_results(extracted_data)
            
            if self.monitor:
                self.monitor.complete_step("research_and_store", step_start, {
                    "results_found": len(extracted_data),
                    "web_results": max_web_results if max_web_results > 0 else 0
                })
            
            return extracted_data
            
        except Exception as e:
            if self.monitor:
                self.monitor.log_step("research_and_store", "error", {"query": query}, str(e))
            self.logger.error(f"Research workflow failed: {e}")
            return []

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on content similarity"""
        if not results:
            return []
        
        unique_results = []
        seen_content = set()
        
        for result in results:
            content = result.get('content', '')
            # Use first 200 chars as deduplication key
            content_key = content[:200].strip().lower()
            
            if content_key and content_key not in seen_content:
                unique_results.append(result)
                seen_content.add(content_key)
        
        return unique_results