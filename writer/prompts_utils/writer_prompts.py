"""
Prompt generators for two-phase research report creation.

Phase 1: generate_outline_prompt() — produces instructions for LLM to create
         table_of_contents, report_outline, abstract, introduction, conclusion.
Phase 2: generate_chapter_prompt() — produces instructions for LLM to write
         one complete chapter/subchapter ready to be added to report_body.
"""

import asyncio
from typing import List, Dict, Any
from llms import LlmsHouse


async def generate_outline_prompt(
    user_query: str,
    planner_queries: List[Dict[str, Any]],
    sections: List[Dict[str, Any]]
) -> str:
    """
    First LLM call: generates optimized prompt for report outline creation.
    
    Receives full sections with section_ids. Produces instructions for
    table_of_contents, report_outline, abstract, introduction, conclusion.
    
    Args:
        user_query: Original user research question.
        planner_queries: List of PlannerQuery dicts with query_num and query fields.
        sections: List of section dicts with section_content and section_id fields.
        
    Returns:
        Optimized prompt string for the outline LLM call.
    """
    
    planner_context = "PLANNER'S RESEARCH PLAN:\n" + "-" * 80 + "\n"
    for pq in planner_queries:
        planner_context += f"Query #{pq.get('query_num', 0)}: {pq.get('query', '')}\n"
    planner_context += "-" * 80 + "\n\n"
    
    sections_context = "RESEARCH SECTIONS AVAILABLE (preview):\n" + "=" * 80 + "\n\n"
    for idx, section in enumerate(sections):
        content = section.get('section_content', '')
        total_chars = len(content)
        if total_chars > 500:
            preview = content[:500]
            remaining = total_chars - 500
            preview += f"\n[... {remaining} more characters not shown, {total_chars} characters total in this section]"
        else:
            preview = content
        sections_context += f"--- Section {idx + 1} ---\n{preview}\n\n"
    sections_context += "=" * 80 + "\n\n"
    
    meta_prompt = f"""You are an expert in prompt engineering and academic research report writing. Your task is to generate an EXTREMELY DETAILED and COMPREHENSIVE prompt that will instruct an LLM to create a professional REPORT OUTLINE with abstract, introduction, and conclusion.

CONTEXT INFORMATION:
=====================

USER'S ORIGINAL QUERY:
{user_query}


This is the Plan we made to cover the topics:
{planner_context}

These are ALL research sections with their section_id. Each section contains research content 
gathered from web sources. The section_id uniquely identifies each section's content.
{sections_context}

YOUR TASK:
==========
Generate a highly detailed prompt that will guide an LLM to create a COMPLETE REPORT OUTLINE. The outline has FIVE outputs:


1. **TABLE OF CONTENTS** (structured object):
   - Keys are main chapter headings with numbering (e.g. "1. Neural Network Fundamentals", "2. Training Methods")
   - Values are arrays of subchapter headings with numbering (e.g. ["1.1 Architecture Overview", "1.2 Activation Functions"])
   - Must have logical flow: foundational concepts first, then advanced topics, then applications
   - Must directly address the user's query: "{user_query}"
   - Should cover ALL important topics from the planner's plan and research sections
   - Use descriptive, professional chapter titles
   - Include enough chapters to cover the topic comprehensively (5-10 main chapters typically)

2. **REPORT OUTLINE** (structured object):
   - Keys are ALL headings from table_of_contents (both main chapters AND subchapters)
   - Values are arrays of section_ids that contain the research content needed for that heading
   - Each section_id can appear in multiple headings if the content is relevant
   - Every section_id from the research MUST be assigned to at least one heading
   - Group related sections together under the most relevant heading

3. **ABSTRACT** (markdown string):
   - Professional abstract (150-300 words)
   - Cover: research objectives, methodology overview, key findings, main conclusions
   - Self-contained — can be read independently
   - Academic tone, concise and impactful

4. **INTRODUCTION** (markdown string):
   - Compelling opening that hooks the reader
   - Clear background and context for the research topic
   - Explicit research objectives tied to the user query
   - Scope and limitations of the report
   - Brief methodology mention
   - Roadmap: outline what each chapter covers

5. **CONCLUSION** (markdown string):
   - Synthesis of ALL findings across chapters
   - Directly answer the original research question
   - Key takeaways and actionable insights
   - Practical recommendations
   - Acknowledge limitations
   - Future research directions


YOUR PROMPT MUST INSTRUCT THE LLM TO:

1. **DETERMINE REPORT FORMAT** based on the user's query:
   - The user query "{user_query}" should drive what kind of report this is
   - If the query is about learning/education → use tutorial-style format with examples, code blocks, practice problems
   - If the query is about comparison → use comparison tables, pros/cons, benchmarks
   - If the query is about technology/tools → use technical deep-dive with architecture diagrams (described in markdown), specifications, use cases
   - If the query is about research/science → use academic format with methodology, results, analysis
   - If the query is about business/strategy → use executive format with market analysis, recommendations, ROI
   - If the query is about how-to/process → use step-by-step guides with numbered instructions, checklists
   - If the query is general overview → use encyclopedic format with definitions, history, current state, future outlook
   
2. **DESIGN TABLE OF CONTENTS STRUCTURE**:
   - Analyze the planner's queries to understand the research breakdown
   - Group related sections by topic similarity based on their content
   - Order chapters from foundational/introductory → core concepts → advanced/specialized → practical applications
   - Create descriptive chapter titles that directly relate to the user's query  
   - Balance chapter sizes — avoid chapters with too many or too few sections
   - Chapter numbering must be consistent (1, 1.1, 1.2, 1.3..., 2, 2.1, 2.2..., etc.)

3. **MAP SECTIONS TO CHAPTERS**:
   - Every section_id MUST be assigned to at least one chapter/subchapter
   - Group related sections under the most relevant heading
   - A section CAN appear under multiple headings if its content spans topics
   - Ensure no section is orphaned (left unassigned)

4. **CONTENT PRESENTATION FORMAT** (instruct based on content type):
   
   **Analytical & Comparative Content**:
   - Tables for feature comparisons, specification matrices, benchmark results
   - Side-by-side analysis with pros and cons
   - Data visualizations described in markdown (charts, graphs)
   
   **Educational & Tutorial Content**:
   - Step-by-step numbered instructions
   - Code blocks with language specification for examples and algorithms
   - Practice problems or exercises where appropriate
   - Key concept definitions in bold or callout format
   
   **Technical & Research Content**:
   - Architecture and flow descriptions (using indented lists or markdown diagrams)
   - Mathematical formulas and equations where relevant
   - Detailed specifications and parameters in tables
   - Methodology sections with clear process descriptions
   
   **Narrative & Explanatory Content**:
   - Narrative paragraphs for context, analysis, and explanations
   - Bullet points for key findings, lists, and enumerated items
   - Bold/italic for emphasis on key terms and definitions
   - Blockquotes for important takeaways or notable findings
   
   **Practical & Applied Content**:
   - Checklists for actionable items
   - Case studies with structured breakdown
   - Best practices in highlighted format
   - Real-world examples with source attribution

5. **QUALITY & TONE REQUIREMENTS**:
   - Professional academic writing — clear, accessible, evidence-based
   - Authoritative but not overly technical
   - Engaging and readable
   - Avoid unnecessary jargon — explain technical terms when first used
   - Evidence-based statements with source attribution
   - The tone should match the user's query intent (formal for research, practical for how-to, etc.)

6. **MARKDOWN FORMATTING STANDARDS**:
   - ALL content must be in valid markdown format
   - Chapter headings use `#`, subchapters use `##`, sub-subchapters use `###`
   - URLs must be preserved as markdown links: [descriptive text](url)
   - Tables must use proper markdown table syntax with headers
   - Code blocks must specify the language
   - Use **bold**, *italic*, and formatting consistently


CRITICAL REMINDERS:
- The outline drives the ENTIRE report structure — be thorough
- section_ids must match EXACTLY what appears in the section content above
- Every section_id must appear in at least one heading's array
- Chapter numbering must be consistent (1, 1.1, 1.2, 1.3..., 2, 2.1, etc.)
- The report must directly serve the user's query: "{user_query}"
- Abstract, Introduction, and Conclusion must be self-contained and professional
- The format/style of the report should be determined by the nature of the user's query

Generate the detailed prompt NOW. Be as specific and comprehensive as possible."""

    model = LlmsHouse().google_model('gemini-2.0-flash')
    response_prompt = await model.ainvoke(meta_prompt)
    return response_prompt.content




async def generate_chapter_prompt(
    chapter_heading: str,
    table_of_contents: Dict[str, List[str]],
    sections_for_chapter: List[Dict[str, Any]]
) -> str:
    """
    Generates prompt for writing one complete chapter/subchapter.
    
    Called once per chapter in the report_outline, then invoked in parallel.
    Uses only the relevant sections (filtered by section_id). The returned
    prompt instructs LLM to produce a complete, ready-to-add chapter with
    heading, subheadings, and all formatted content.
    
    Args:
        chapter_heading: The heading for this chapter (e.g. "1.1 Architecture Overview").
        table_of_contents: Full ToC dict for context on where this chapter fits.
        sections_for_chapter: List of section dicts (full content) for this chapter.
        
    Returns:
        Prompt string for the chapter generation LLM call.
    """
    
    toc_formatted = "FULL REPORT TABLE OF CONTENTS:\n"
    for main_chapter, subchapters in table_of_contents.items():
        toc_formatted += f"  {main_chapter}\n"
        for sub in subchapters:
            toc_formatted += f"    {sub}\n"
    
    sections_formatted = ""
    for idx, section in enumerate(sections_for_chapter):
        content = section.get('section_content', '')
        sections_formatted += f"\n=== RESEARCH SECTION {idx + 1} ===\n{content}\n"
    
    prompt = f"""You are an expert academic research writer. Your task is to write ONE COMPLETE chapter/subchapter of a research report. The output must be a FULLY FINISHED section — ready to be directly added to the final report with NO modifications needed.

=====================================================================
YOUR ASSIGNMENT: Write the complete chapter "{chapter_heading}"
=====================================================================

{toc_formatted}

You are writing ONLY: "{chapter_heading}"

=====================================================================
RESEARCH SOURCE MATERIAL (use these sections to write your chapter):
=====================================================================
{sections_formatted}
=====================================================================

CHAPTER WRITING REQUIREMENTS:
==============================

1. **HEADING STRUCTURE**: 
   - Start with the correct markdown heading for "{chapter_heading}"
   - Main chapters (e.g. "1. Topic") → use `# 1. Topic`
   - Subchapters (e.g. "1.1 Subtopic") → use `## 1.1 Subtopic`
   - Add sub-subheadings (`###`) within the chapter wherever logical grouping is needed
   - The chapter must feel complete with proper internal structure

2. **CONTENT SYNTHESIS**:
   - Read ALL provided research sections carefully
   - SYNTHESIZE and UNIFY the content into a cohesive, flowing narrative
   - DO NOT copy-paste sections verbatim — rewrite, connect, and enhance
   - Preserve ALL factual information, data points, statistics, and technical details
   - Preserve ALL URLs and embed them as markdown links: [descriptive text](url)
   - DO NOT invent any facts, data, or URLs not present in the source sections
   - DO NOT include any internal references like "section_id", "Section 1", or technical identifiers in your output
   - Eliminate redundancy while keeping every unique piece of information
   - Add smooth transitions between topics within the chapter
   
3. **FORMATTING & PRESENTATION**:
   - Use **tables** for comparisons, specifications, feature matrices, benchmark data
   - Use **bullet points** for key findings, feature lists, enumerated items
   - Use **numbered lists** for step-by-step processes, ranked items, sequential instructions
   - Use **code blocks** (with language tag) for algorithms, code examples, technical configs
   - Use **bold** for key terms, definitions, and important concepts
   - Use *italic* for emphasis and first mention of technical terms
   - Use **blockquotes** for notable findings or important takeaways
   - Use proper markdown table syntax with header rows and alignment
   - For content you think can be different use correct markdown format that represents the content best .
  - Don't Include any section_id, section number, or technical identifiers in your output
4. **COMPLETENESS**:
   - The chapter must be SELF-CONTAINED and complete
   - Include ALL relevant information from the source sections
   - Do NOT reference other chapters' content — write what belongs HERE
   - Do NOT add a table of contents, abstract, or conclusion within this chapter
   - The output IS the chapter — heading, content, everything included

5. **QUALITY**:
   - Professional academic tone — clear, accessible, evidence-based
   - Logical flow: overview → details → specifics → summary/transition
   - Technical accuracy with readable presentation
   - Proper attribution via embedded URL links

Write the COMPLETE chapter "{chapter_heading}" NOW. Include the heading, all subheadings, and all content. The output must be ready to directly insert into the final report."""

    return prompt


async def main():
    """Module entry point for testing."""
    pass


if __name__ == "__main__":
    asyncio.run(main())
