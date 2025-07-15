"""
Prompt templates for the Gap Questions module.

This module contains all prompt templates used throughout the gap questions
generation and search query generation system.
"""

def create_search_query_prompt(plan_bullet_point: str, max_queries: int) -> str:
    """
    Create an optimized prompt for generating web search queries from research plan bullet points.
    
    Args:
        plan_bullet_point (str): The research plan bullet point
        max_queries (int): Maximum number of queries to generate
        
    Returns:
        str: Formatted prompt for LLM
    """
    prompt = f"""You are an expert research assistant. Your task is to generate effective web search queries for a specific research objective.

RESEARCH OBJECTIVE:
{plan_bullet_point}

INSTRUCTIONS:
1. Generate {max_queries} distinct web search queries that would help gather comprehensive information about this research objective
2. Make queries specific, actionable, and likely to return relevant results
3. Use different angles/perspectives to cover the topic thoroughly
4. Include relevant keywords, technical terms, and alternative phrasings
5. Focus on recent, authoritative, and factual information sources
6. Avoid overly broad or vague terms

REQUIREMENTS:
- Each query should be 3-8 words long
- Use quotation marks for exact phrases when beneficial
- Include year-specific queries if temporal relevance is important
- Prioritize queries that would return academic papers, industry reports, or expert analysis

FORMAT YOUR RESPONSE AS A JSON LIST:
["query1", "query2", "query3", ...]

EXAMPLE INPUT: "Analyze the impact of AI on healthcare diagnostics"
EXAMPLE OUTPUT: ["AI healthcare diagnostics accuracy", "machine learning medical diagnosis 2024", "artificial intelligence radiology applications", "AI diagnostic tools clinical trials", "healthcare AI implementation challenges"]

Generate the search queries now:"""
    
    return prompt

# Additional prompt templates can be added here as the system grows
# For example:

def create_question_generation_prompt():
    """Prompt template for question generation (placeholder for future use)."""
    pass

def create_gap_analysis_prompt(query: str, vector_content: str) -> str:
    """
    Create prompt for analyzing gaps in research content.
    
    Args:
        query (str): The original research query
        vector_content (str): Content from vector store
        
    Returns:
        str: Formatted prompt for gap analysis
    """
    prompt = f"""You are an expert research analyst. Your task is to identify gaps in the available research content that prevent fully answering the given query.

ORIGINAL QUERY:
{query}

AVAILABLE CONTENT:
{vector_content}

INSTRUCTIONS:
1. Analyze the available content against the original query
2. Identify specific gaps or missing information needed to fully answer the query
3. Focus on factual gaps, missing data, or areas that need more exploration
4. Be specific about what type of information is missing
5. Prioritize the most critical gaps

REQUIREMENTS:
- Generate 1-3 specific gaps (not generic statements)
- Each gap should be 1-2 sentences describing what's missing
- Focus on actionable gaps that can be researched
- Avoid overly broad or vague gap descriptions

FORMAT YOUR RESPONSE AS A JSON LIST:
["gap1 description", "gap2 description", "gap3 description"]

EXAMPLE:
Query: "Impact of AI on healthcare"
Content: "AI improves diagnostic accuracy..."
Gaps: ["Missing data on AI implementation costs in healthcare systems", "Lack of information on patient privacy concerns with AI diagnostics"]

Analyze and identify the gaps now:"""
    
    return prompt