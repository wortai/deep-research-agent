import logging

from ..llm_client import GeminiLLMClient

logger = logging.getLogger(__name__)


def generate_section_heading(
    gap_query: str,
    llm_client: GeminiLLMClient,
    performance_metrics: dict
) -> str:
    """Generate a professional section heading for a gap query using LLM."""
    try:
        prompt = f"""You are an expert at creating professional report section headings. Create a clear, informative section heading for the following research gap.

RESEARCH GAP:
{gap_query}

INSTRUCTIONS:
1. Create a professional section heading that clearly describes what this section will cover
2. The heading should be specific and descriptive
3. Use proper title case formatting
4. Keep it between 3-8 words
5. Make it suitable for a research report or academic paper
6. Focus on the key topic or area being addressed

EXAMPLES:
- Input: "Need more information about renewable energy storage costs"
- Output: "Renewable Energy Storage Economics"

- Input: "What are the latest trends in AI chatbot training"
- Output: "Current AI Chatbot Training Methodologies"

Generate ONLY the section heading, nothing else:"""

        response = llm_client.generate(prompt, context="section_heading", model_type="analysis")
        performance_metrics["llm_calls"] += 1
        
        # Clean and format the response
        heading = response.strip().strip('"').strip("'")
        
        # Ensure proper title case
        heading = ' '.join(word.capitalize() for word in heading.split())
        
        logger.info(f"Generated section heading: {heading}")
        return heading
        
    except Exception as e:
        logger.error(f"Failed to generate section heading: {e}")
        # Fallback to a cleaned version of the gap query
        fallback = ' '.join(word.capitalize() for word in gap_query.split()[:6])
        return fallback