import logging
from typing import List, Dict, Any

from ..llm_client import GeminiLLMClient

logger = logging.getLogger(__name__)


def summarize_section_content(
    gap_query: str,
    research_data: List[Dict[str, Any]],
    llm_client: GeminiLLMClient,
    performance_metrics: dict
) -> str:
    """Generate a comprehensive summary of research data for a gap query using LLM."""
    try:
        if not research_data:
            return f"No research data available to address: {gap_query}"
        
        # Prepare the research content for summarization
        content_parts = []
        for i, data in enumerate(research_data[:5], 1):  # Use top 5 pieces of data
            content = data.get('content', '')
            if content:
                content_parts.append(f"Source {i}: {content[:600]}")  # 600 chars per source
        
        combined_content = "\n\n".join(content_parts)
        
        prompt = f"""You are an expert research analyst. Create a comprehensive summary that addresses the research gap using the provided data sources.

RESEARCH GAP TO ADDRESS:
{gap_query}

RESEARCH DATA:
{combined_content}

INSTRUCTIONS:
1. Create a well-structured summary that directly addresses the research gap
2. Synthesize information from multiple sources into a coherent narrative
3. Include key findings, statistics, trends, and insights
4. Write in a professional, academic tone
5. Aim for 200-300 words
6. Focus on answering or addressing the specific gap mentioned
7. Structure with clear topic sentences and logical flow
8. Include specific details and examples where available

FORMAT:
Write as a cohesive paragraph or series of paragraphs that could fit into a research report section.

Generate the comprehensive summary:"""

        response = llm_client.generate(prompt, context="section_content", model_type="analysis")
        performance_metrics["llm_calls"] += 1
        
        # Clean the response
        summary = response.strip()
        
        logger.info(f"Generated section content summary ({len(summary)} characters)")
        return summary
        
    except Exception as e:
        logger.error(f"Failed to generate section content summary: {e}")
        # Fallback to basic content combination
        fallback_parts = []
        for data in research_data[:3]:
            content = data.get('content', '')
            if content:
                fallback_parts.append(content[:200])
        
        fallback_summary = " ".join(fallback_parts) if fallback_parts else f"Limited information available for: {gap_query}"
        return fallback_summary