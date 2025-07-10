"""
Vector store query generation module
"""

import logging
from typing import List
from datetime import datetime


class VectorQueryGenerator:
    """Generates diverse search queries for vector store"""
    
    def __init__(self, llm_client, monitor=None):
        self.llm_client = llm_client
        self.monitor = monitor
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_queries(self, gap_query: str, user_query: str, max_queries: int = 3) -> List[str]:
        """Generate diverse search queries for vector store"""
        step_start = datetime.now()
        
        if self.monitor:
            self.monitor.log_step("generate_vector_queries", "started", {
                "gap_query": gap_query,
                "max_queries": max_queries
            })
        
        try:
            prompt = f"""Generate {max_queries} diverse search queries for a vector store.

GAP QUERY: {gap_query}
USER QUESTION: {user_query}

Create {max_queries} different ways to search for this information:
1. Different keywords and phrasings
2. Specific enough to find relevant documents
3. Cover different aspects of the topic

Return only queries, one per line:"""
            
            response = self.llm_client.generate(prompt, context="vector_query_generation")
            queries = [line.strip() for line in response.strip().split('\n') 
                      if line.strip() and len(line.strip()) > 10]
            
            final_queries = queries[:max_queries] or [gap_query]
            
            if self.monitor:
                self.monitor.complete_step("generate_vector_queries", step_start, {
                    "queries_generated": len(final_queries)
                })
            
            self.logger.info(f"Generated {len(final_queries)} vector queries for: {gap_query}")
            return final_queries
            
        except Exception as e:
            if self.monitor:
                self.monitor.log_step("generate_vector_queries", "error", {}, str(e))
            self.logger.error(f"Vector query generation failed: {e}")
            return [gap_query]