"""
Gap Search Query Generator

Generates web search queries based on identified gaps in research.
"""

import logging
import json
from typing import List
from ..llm_client import GeminiLLMClient

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
            prompt = self._create_gap_search_prompt(gap, max_queries)
            
            # Generate queries using LLM
            response = self.llm_client.generate(prompt, context="gap_search_generation")
            
            # Parse response
            queries = self._parse_queries_response(response, max_queries)
            
            logger.info(f"Generated {len(queries)} gap search queries")
            return queries
            
        except Exception as e:
            logger.error(f"Failed to generate gap search queries: {e}")
            return []
    
    def _create_gap_search_prompt(self, gap: str, max_queries: int) -> str:
        """Create prompt for gap search query generation."""
        return f"""You are an expert research assistant. Your task is to generate effective web search queries that will help fill a specific gap in research knowledge.

RESEARCH GAP:
{gap}

INSTRUCTIONS:
1. Generate {max_queries} distinct web search queries that would help gather information to address this gap
2. Make queries specific and actionable for web search engines
3. Use different search strategies (keywords, questions, specific terms)
4. Focus on finding recent, authoritative sources
5. Include relevant technical terms and alternative phrasings

REQUIREMENTS:
- Each query should be 3-8 words long
- Use quotation marks for exact phrases when beneficial
- Include year-specific queries if temporal relevance is important
- Prioritize queries that would return academic papers, reports, or expert analysis
- Avoid overly broad or vague terms

FORMAT YOUR RESPONSE AS A JSON LIST:
["query1", "query2", "query3", ...]

EXAMPLE INPUT: "Lack of data on electric vehicle adoption rates in rural areas"
EXAMPLE OUTPUT: ["electric vehicle adoption rural areas 2024", "EV uptake rural vs urban statistics", "rural electric vehicle infrastructure challenges", "electric car sales rural markets data"]

Generate the gap search queries now:"""

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