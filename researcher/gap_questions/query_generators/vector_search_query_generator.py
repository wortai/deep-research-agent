"""
Vector Search Query Generator

Generates optimized queries for vector store searches based on identified gaps.
"""

import logging
import json
from typing import List
from ..llm_client import GeminiLLMClient

logger = logging.getLogger(__name__)

class VectorSearchQueryGenerator:
    """Generates vector search queries optimized for gap analysis."""
    
    def __init__(self):
        """Initialize with LLM client."""
        self.llm_client = GeminiLLMClient()
    
    def generate_vector_search_queries(self, gap: str, max_queries: int = 3) -> List[str]:
        """
        Generate vector search queries optimized for finding content to fill specific gaps.
        
        Args:
            gap (str): The identified gap that needs to be addressed
            max_queries (int): Maximum number of queries to generate
            
        Returns:
            List[str]: List of optimized vector search queries
        """
        try:
            if not gap or not gap.strip():
                logger.warning("Empty gap provided")
                return []
                
            logger.info(f"Generating vector search queries for gap: {gap[:50]}...")
            
            # Create prompt for vector search query generation
            prompt = self._create_vector_search_prompt(gap, max_queries)
            
            # Generate queries using LLM
            response = self.llm_client.generate(prompt, context="vector_search_generation")
            
            # Parse response (expecting JSON list)
            queries = self._parse_queries_response(response, max_queries)
            
            logger.info(f"Generated {len(queries)} vector search queries")
            return queries
            
        except Exception as e:
            logger.error(f"Failed to generate vector search queries: {e}")
            return []
    
    def _create_vector_search_prompt(self, gap: str, max_queries: int) -> str:
        """Create prompt for vector search query generation."""
        return f"""You are an expert at generating vector search queries. Your task is to create effective queries for searching a vector database to find information that addresses a specific gap.

GAP TO ADDRESS:
{gap}

INSTRUCTIONS:
1. Generate {max_queries} distinct vector search queries that would help find information to fill this gap
2. Make queries specific and likely to find relevant stored content
3. Use different angles and phrasings to maximize coverage
4. Focus on factual, informative content
5. Include key terms and concepts related to the gap

REQUIREMENTS:
- Each query should be 5-15 words long
- Use natural language questions or statements
- Avoid overly broad or vague terms
- Focus on finding specific information, data, or explanations

FORMAT YOUR RESPONSE AS A JSON LIST:
["query1", "query2", "query3", ...]

EXAMPLE INPUT: "Need more information about renewable energy storage costs"
EXAMPLE OUTPUT: ["renewable energy storage costs comparison", "battery storage economics renewable energy", "cost analysis energy storage technologies", "renewable energy storage investment trends"]

Generate the vector search queries now:"""

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
                        if 3 <= len(clean_query) <= 200:
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