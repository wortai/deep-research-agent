"""
Prompt generators for unified research report creation.

This module contains the first LLM call that generates an optimized 
prompt for unified report generation based on user query, planner's 
plan, and research sections.
"""

import asyncio
from typing import List, Dict, Any
from llms import LlmsHouse


async def generate_unified_report_prompt(
    user_query: str,
    planner_queries: List[Dict[str, Any]],
    sections: List[Dict[str, Any]]
) -> str:
    """
    First LLM call: generates optimized prompt for unified report creation.
    
    Takes user query, planner's plan, and research sections to produce detailed
    instructions for report generation covering hierarchy, focus areas, styling,
    and structure.
    
    Args:
        user_query: Original user research question
        planner_queries: List of PlannerQuery dicts with query_num and query fields
        sections: List of section dicts with section_content field (markdown with embedded headings)
        
    Returns:
        Optimized prompt string for second LLM call to generate unified report
    """
    
    # Format planner queries for context
    planner_context = "PLANNER'S RESEARCH PLAN:\n" + "-" * 80 + "\n"
    for pq in planner_queries:
        planner_context += f"Query #{pq.get('query_num', 0)}: {pq.get('query', '')}\n"
    planner_context += "-" * 80 + "\n\n"
    
    # Format sections with preview
    sections_context = "RESEARCH SECTIONS AVAILABLE (already in markdown with URLs):\n" + "=" * 80 + "\n\n"
    for idx, section in enumerate(sections):
        content = section.get('section_content', '')
        preview = content[:500] + ('...' if len(content) > 500 else '')
        sections_context += f"--- Section {idx + 1} ---\n{preview}\n\n"
    sections_context += "=" * 80 + "\n\n"
    
    meta_prompt = f"""You are an expert in prompt engineering and academic research report writing. Your task is to generate an EXTREMELY DETAILED and COMPREHENSIVE prompt that will instruct an LLM to create a professional unified research report.

CONTEXT INFORMATION:
=====================

USER'S ORIGINAL QUERY:
{user_query}


This is the Plan we made to cover the topics 
{planner_context}

This is the Preview of each sections so you get the idea of what type of sections we covering. Remember 
these sections are already in markdown format with URLs in the end of each section. 
{sections_context}

YOUR TASK:
==========
Generate a highly detailed prompt that will guide an LLM to create a unified, professional research report. Your prompt MUST include ALL of the following elements:

1. **REPORT STRUCTURE INSTRUCTIONS**:
   - Table of Contents with chapter/subchapter numbering (Chapter 1, 1.1, 1.2, Chapter 2, 2.1, 2.2, etc.)
   - Abstract (150-250 words)
   - Introduction with proper context and research objectives
   - Report Body organized by chapters and subchapters
   - Conclusion with synthesis and recommendations

2. **CONTENT HIERARCHY & ORGANIZATION**:
   - Explain which sections should be MERGED and why
   - Define the LOGICAL ORDER from foundational concepts to advanced analysis
   - Specify which topics deserve MORE FOCUS (main chapters) vs LESS FOCUS (subchapters)
   - Ensure progressive depth: start with basics, move to deeper analysis
   - Explain how to organize content to directly address the user's original query: "{user_query}"

3. **MARKDOWN FORMATTING REQUIREMENTS**:
   - ALL content must be in valid markdown format
   - Chapter headings use `#`, subchapters use `##`, sub-subchapters use `###`
   - Preserve URLs from original sections and place them next to relevant content as markdown links
   - Use appropriate formatting: **bold**, *italic*, tables, code blocks, bullet lists, numbered lists
   - Ensure consistent styling throughout

4. **CONTENT PRESENTATION TECHNIQUES**:
   - Specify when to use TABLES for comparisons or structured data
   - When to use BULLET POINTS for lists or key findings
   - When to use NARRATIVE paragraphs for explanations
   - When to use CHARTS/DIAGRAMS descriptions (in markdown format)
   - When to use SUB-PARAGRAPH techniques for detailed elaboration
   - When to use COMPARISON techniques for contrasting concepts

5. **QUALITY REQUIREMENTS FOR EACH SECTION**:
   
   **Table of Contents**:
   - Numbered hierarchically (1, 1.1, 1.2, 2, 2.1, etc.)
   - Include page/section references
   - Clear and descriptive chapter titles
   
   **Abstract**:
   - AMAZING synthesis of entire report
   - Cover: objectives, methodology overview, key findings, main conclusions
   - Professional academic tone
   - Self-contained (can be read independently)
   
   **Introduction**:
   - EXCEPTIONAL opening that hooks the reader
   - Clear background and context
   - Explicit research objectives tied to user query
   - Scope and limitations
   - Brief methodology mention
   - Roadmap of report structure
   
   **Report Body**:
   - Seamlessly UNIFY the provided sections without major content changes
   - Preserve factual accuracy, data, and URLs from original sections
   - Eliminate redundancy between sections
   - Create smooth transitions between chapters
   - Use appropriate presentation techniques based on content type
   - Include URLs and citations from original sections
   - Maintain logical flow from simple to complex topics
   
   **Conclusion**:
   - OUTSTANDING synthesis of all findings
   - Directly answer the original research question
   - Key takeaways and insights
   - Practical recommendations
   - Acknowledge limitations
   - Future research directions

6. **CONTENT FIDELITY RULES**:
   - DO NOT invent facts, data, or URLs not present in sections
   - DO preserve all factual information from sections
   - DO maintain all URLs and proper attribution
   - DO keep technical details and metrics accurate
   - DO unify and organize but NOT fundamentally rewrite content

7. **STYLE & TONE**:
   - Professional academic writing
   - Clear and accessible language
   - Avoid unnecessary jargon
   - Evidence-based statements
   - Authoritative but not overly technical
   - Engaging and readable

8. **SPECIAL INSTRUCTIONS BASED ON PLANNER'S PLAN**:
   - Analyze the planner's queries to understand the research structure
   - Ensure report addresses each planner query appropriately
   - Create chapters that align with the planner's logical breakdown
   - Maintain the investigative flow the planner intended

CRITICAL REMINDERS:
- The sections provided are already in markdown format with embedded headings
- Your job is to UNIFY, ORGANIZE, and ENHANCE presentation, not completely rewrite
- URLs must be preserved and included next to relevant content
- The final report should feel like a cohesive, professional document, not a collection of separate answers
- Focus on answering "{user_query}" comprehensively

Generate the detailed prompt NOW. Be as specific and comprehensive as possible. This prompt will be used to create a high-quality research report."""

    model = LlmsHouse().google_model('gemini-2.0-flash')
    response_prompt = await model.ainvoke(meta_prompt)
    return response_prompt.content


async def main():
    print("Unified report prompt generator module")


if __name__ == "__main__":
    asyncio.run(main())
