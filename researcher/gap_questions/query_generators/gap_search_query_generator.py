"""
Gap Search Query Generator

Generates web search queries based on identified gaps in research.
"""

import logging
import json
from typing import List
from ..llm_client import GeminiLLMClient
from ..prompts import create_gap_search_query_prompt

logger = logging.getLogger(__name__)

class GapSearchQueryGenerator:
    """Generates web search queries to fill identified research gaps."""
    
    def __init__(self):
        """Initialize with LLM client."""
        self.llm_client = GeminiLLMClient()
    
    def generate_gap_search_queries(self, gap: str, max_queries: int = 3) -> List[str]:
        """
        Generate web search queries to address specific research gaps.
        
        Args:
            gap (str): The identified gap that needs to be addressed
            max_queries (int): Maximum number of queries to generate
            
        Returns:
            List[str]: List of web search queries
        """
        try:
            if not gap or not gap.strip():
                logger.warning("Empty gap provided")
                return []
                
            logger.info(f"Generating gap search queries for: {gap[:50]}...")
            
            # Create prompt for gap search query generation
            prompt = create_gap_search_query_prompt(gap, max_queries)
            
            # Generate queries using LLM
            response = self.llm_client.generate(prompt, context="gap_search_generation")
            
            # Parse response
            queries = self._parse_queries_response(response, max_queries)
            
            logger.info(f"Generated {len(queries)} gap search queries")
            return queries
            
        except Exception as e:
            logger.error(f"Failed to generate gap search queries: {e}")
            return []
    

    def _parse_queries_response(self, response: str, max_queries: int) -> List[str]:
        """Parse LLM response to extract queries."""
        try:
            # Find JSON array in response
            response_clean = response.strip()
            start_idx = response_clean.find('[')
            end_idx = response_clean.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON array found in response")
                return []
            
            json_str = response_clean[start_idx:end_idx]
            queries = json.loads(json_str)
            
            if isinstance(queries, list):
                # Clean and validate queries
                cleaned_queries = []
                for query in queries[:max_queries]:
                    if isinstance(query, str) and query.strip():
                        clean_query = query.strip().strip('"\'')
                        if 3 <= len(clean_query) <= 100:  # Web search queries should be shorter
                            cleaned_queries.append(clean_query)
                
                return cleaned_queries
            else:
                logger.warning("Response not in expected list format")
                return []
                
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return []
        except Exception as e:
            logger.error(f"Error parsing queries response: {e}")
            return []