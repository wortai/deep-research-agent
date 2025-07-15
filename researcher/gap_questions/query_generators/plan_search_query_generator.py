"""
Search Query Generator for Research Plan Bullet Points

This module generates web search queries from research plan bullet points
using LLM to create targeted, effective search terms for research agents.
"""

import logging
import json
from typing import List, Optional
from ..llm_client import GeminiLLMClient
from ..prompts import create_search_query_prompt

logger = logging.getLogger(__name__)

class PlanSearchQueryGenerator:
    """Generates web search queries from research plan bullet points."""
    
    def __init__(self, llm_client: Optional[GeminiLLMClient] = None):
        """
        Initialize the search query generator.
        
        Args:
            llm_client (GeminiLLMClient, optional): LLM client instance
        """
        self.llm_client = llm_client or GeminiLLMClient()
    
    def generate_search_queries(self, plan_bullet_point: str, max_queries: int = 5) -> List[str]:
        """
        Generate web search queries from a research plan bullet point.
        
        Args:
            plan_bullet_point (str): A single bullet point from a research plan
            max_queries (int): Maximum number of search queries to generate
            
        Returns:
            List[str]: List of optimized web search queries
            
        Raises:
            ValueError: If plan_bullet_point is empty or invalid
            Exception: If LLM generation fails
        """
        try:
            # Input validation
            if not plan_bullet_point or not isinstance(plan_bullet_point, str):
                raise ValueError("Plan bullet point must be a non-empty string")
            
            plan_bullet_point = plan_bullet_point.strip()
            if not plan_bullet_point:
                raise ValueError("Plan bullet point cannot be empty or whitespace only")
            
            logger.info(f"Generating search queries for: '{plan_bullet_point[:100]}...'")
            
            # Create an efficient prompt for search query generation
            prompt = create_search_query_prompt(plan_bullet_point, max_queries)
            
            # Generate queries using LLM
            response = self.llm_client.generate(
                prompt=prompt,
                context="search_query_generation",
                model_type="generation"
            )
            
            # Parse and validate the response
            search_queries = self._parse_search_queries(response, max_queries)
            
            logger.info(f"Generated {len(search_queries)} search queries")
            return search_queries
            
        except ValueError as e:
            logger.error(f"Invalid input: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to generate search queries: {e}")
            raise Exception(f"Search query generation failed: {str(e)}")
    
    
    def _parse_search_queries(self, llm_response: str, max_queries: int) -> List[str]:
        """
        Parse and validate search queries from LLM response.
        
        Args:
            llm_response (str): Raw response from LLM
            max_queries (int): Maximum number of queries expected
            
        Returns:
            List[str]: Cleaned and validated search queries
        """
        try:
            # Try to parse as JSON first
            response_clean = llm_response.strip()
            
            # Find JSON array in response
            start_idx = response_clean.find('[')
            end_idx = response_clean.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON array found in LLM response, attempting manual parsing")
                return self._manual_parse_queries(response_clean, max_queries)
            
            json_str = response_clean[start_idx:end_idx]
            queries = json.loads(json_str)
            
            # Validate and clean queries
            if not isinstance(queries, list):
                raise ValueError("Response is not a list")
            
            cleaned_queries = []
            for query in queries[:max_queries]:
                if isinstance(query, str) and query.strip():
                    cleaned_query = query.strip()
                    # Remove excessive quotes and clean up
                    cleaned_query = cleaned_query.strip('"').strip("'")
                    if len(cleaned_query) > 0 and len(cleaned_query) <= 200:  # Reasonable length limit
                        cleaned_queries.append(cleaned_query)
            
            if not cleaned_queries:
                logger.warning("No valid queries found in LLM response")
                return []
            
            return cleaned_queries
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}, attempting manual parsing")
            return self._manual_parse_queries(llm_response, max_queries)
        except Exception as e:
            logger.error(f"Error parsing search queries: {e}")
            return []
    
    def _manual_parse_queries(self, response: str, max_queries: int) -> List[str]:
        """
        Manually parse search queries from response when JSON parsing fails.
        
        Args:
            response (str): Raw LLM response
            max_queries (int): Maximum number of queries to extract
            
        Returns:
            List[str]: Extracted search queries
        """
        try:
            lines = response.split('\n')
            queries = []
            
            for line in lines:
                line = line.strip()
                # Skip empty lines and obvious non-query content
                if not line or line.lower().startswith(('here', 'example', 'note:', 'format')):
                    continue
                
                # Remove common prefixes like numbers, bullets, quotes
                line = line.lstrip('0123456789.-*" ').strip('"\'')
                
                # Basic validation - should look like a search query
                if 3 <= len(line) <= 200 and not line.lower().startswith(('the ', 'this ', 'that ')):
                    queries.append(line)
                
                if len(queries) >= max_queries:
                    break
            
            return queries[:max_queries]
            
        except Exception as e:
            logger.error(f"Manual parsing failed: {e}")
            return []

# Convenience function for direct usage
def generate_search_queries_for_plan(plan_bullet_point: str, max_queries: int = 5) -> List[str]:
    """
    Convenience function to generate search queries from a plan bullet point.
    
    Args:
        plan_bullet_point (str): Research plan bullet point
        max_queries (int): Maximum number of queries to generate
        
    Returns:
        List[str]: Generated search queries
    """
    generator = PlanSearchQueryGenerator()
    return generator.generate_search_queries(plan_bullet_point, max_queries)

# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Test the function
    test_bullet_points = [
        "Analyze market penetration of electric vehicles in European markets",
        "Evaluate the effectiveness of remote work policies on employee productivity",
        "Research emerging trends in quantum computing applications for financial services"
    ]
    
    generator = PlanSearchQueryGenerator()
    
    for bullet_point in test_bullet_points:
        print(f"\nPlan: {bullet_point}")
        print("Generated Queries:")
        try:
            queries = generator.generate_search_queries(bullet_point, max_queries=4)
            for i, query in enumerate(queries, 1):
                print(f"  {i}. {query}")
        except Exception as e:
            print(f"  Error: {e}")