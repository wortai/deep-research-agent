"""
Prompt templates for the Gap Questions module.

This module contains all prompt templates used throughout the gap questions
generation and search query generation system.
"""

from typing import List

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

def create_section_heading_prompt(gap_query: str) -> str:
    """
    Create prompt for generating professional section headings.
    
    Args:
        gap_query (str): The research gap query
        
    Returns:
        str: Formatted prompt for section heading generation
    """
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
    
    return prompt

def create_section_content_prompt(gap_query: str, combined_content: str) -> str:
    """
    Create prompt for generating comprehensive section content summaries.
    
    Args:
        gap_query (str): The research gap query
        combined_content (str): Combined research content from multiple sources
        
    Returns:
        str: Formatted prompt for section content generation
    """
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
    
    return prompt

def create_gap_search_query_prompt(gap: str, max_queries: int) -> str:
    """
    Create prompt for generating web search queries to fill research gaps.
    
    Args:
        gap (str): The identified gap that needs to be addressed
        max_queries (int): Maximum number of queries to generate
        
    Returns:
        str: Formatted prompt for gap search query generation
    """
    prompt = f"""You are an expert research assistant. Your task is to generate effective web search queries that will help fill a specific gap in research knowledge.

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
    
    return prompt

def create_vector_search_query_prompt(gap: str, max_queries: int) -> str:
    """
    Create prompt for generating vector search queries optimized for finding content to fill gaps.
    
    Args:
        gap (str): The identified gap that needs to be addressed
        max_queries (int): Maximum number of queries to generate
        
    Returns:
        str: Formatted prompt for vector search query generation
    """
    prompt = f"""You are an expert at generating vector search queries. Your task is to create effective queries for searching a vector database to find information that addresses a specific gap.

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
    
    return prompt

def create_sections_from_research_prompt(raw_research_results: List[tuple]) -> str:
    """
    Create prompt for generating sections from raw research results.
    
    Args:
        raw_research_results: List of (vector_search_query, document_content, urls) tuples
        
    Returns:
        str: Formatted prompt for section generation
    """
    # Format the research results for the prompt
    formatted_results = []
    for i, (query, content, urls) in enumerate(raw_research_results, 1):
        url_list = ", ".join(urls) if urls else "No URLs available"
        formatted_results.append(f"""
Research Result {i}:
Vector Search Query: {query}
Content: {content[:500]}...
URLs: {url_list}
""")
    
    research_content = "\n".join(formatted_results)
    
    prompt = f"""You are an expert research analyst. Your task is to analyze the provided research results and create well-structured sections for a research report.

RESEARCH RESULTS:
{research_content}

INSTRUCTIONS:
1. Analyze all the research results and identify distinct topics/themes
2. Create 3-5 sections that best organize the information
3. Each section should have a clear, professional heading (3-8 words)
4. Each section should contain comprehensive content (200-300 words) that synthesizes information from relevant research results
5. Include source URLs for each section
6. Focus on creating coherent, valuable sections rather than just summarizing individual results
7. Ensure sections are distinct and don't overlap significantly

REQUIREMENTS:
- Generate sections only if there is meaningful content to include
- Use professional, academic tone
- Structure content with clear topic sentences and logical flow
- Include specific details and examples where available
- Organize information in a way that would be useful for a research report

FORMAT YOUR RESPONSE AS A JSON ARRAY:
[
  {{
    "section_heading": "Professional Section Title",
    "section_content": "Comprehensive content that synthesizes relevant research...",
    "section_urls": ["url1", "url2", "url3"]
  }},
  {{
    "section_heading": "Another Section Title",
    "section_content": "More comprehensive content...",
    "section_urls": ["url4", "url5"]
  }}
]

Generate the sections now:"""
    
    return prompt