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

def create_sections_from_gaps_prompt(gaps: List[str], raw_research_results: List[tuple]) -> str:
    """
    Create prompt for generating sections from gaps and their corresponding research results.
    
    Args:
        gaps: List of gap queries
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
    
    # Format the gaps
    gaps_list = "\n".join([f"{i}. {gap}" for i, gap in enumerate(gaps, 1)])
    
    prompt = f"""You are an expert research analyst. Your task is to create exactly {len(gaps)} sections for a research report, with each section addressing one specific gap using the available research results.

GAPS TO ADDRESS:
{gaps_list}

RESEARCH RESULTS:
{research_content}

INSTRUCTIONS:
1. Create EXACTLY {len(gaps)} sections - one for each gap listed above
2. Each section should address a specific gap using relevant research results
3. Transform each gap into a clear, professional section heading (like a title) that reflects the topic in a readable sentence format
4. Each section should contain comprehensive content (1000-1500 words) that directly addresses the gap
5. Include inline citations by placing relevant URLs immediately after sentences that reference specific information from those sources
6. Match research results to gaps based on topic relevance and content overlap
7. If a gap cannot be fully addressed, acknowledge the limitation but provide what information is available

REQUIREMENTS:
- Generate exactly {len(gaps)} sections, no more, no less
- Use professional, academic tone
- Structure content with clear topic sentences and logical flow
- Include specific details and examples where available
- Each section must directly address its corresponding gap
- Add inline citations in the format: "Statement based on research (URL)" throughout the content
- Place citations immediately after the sentence they support

FORMAT YOUR RESPONSE AS A JSON ARRAY WITH EXACTLY {len(gaps)} SECTIONS:
[
  {{
    "gap_addressed": "The original gap text being addressed",
    "section_heading": "Professional Title Sentence Based on the Gap",
    "section_content": "Comprehensive content that directly addresses the gap...",
    "section_urls": ["url1", "url2", "url3"]
  }},
  ...
]

EXAMPLE:
If gap is: "Need more data on AI model training costs"
Section heading should be: "AI Model Training Cost Analysis and Economics"
Section content should include: "Training large language models requires significant computational resources, with costs ranging from $100,000 to several million dollars (https://example.com/ai-training-costs). OpenAI's GPT-3 training reportedly cost approximately $4.6 million in compute resources (https://example.com/gpt3-costs)."

Generate exactly {len(gaps)} sections now:"""
    
    return prompt