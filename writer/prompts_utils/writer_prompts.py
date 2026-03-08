"""
Prompt generators for two-phase research report creation.

Phase 1: generate_outline_prompt() — produces instructions for LLM to create
         table_of_contents, report_outline, abstract, introduction, conclusion.
Phase 2: generate_chapter_prompt() — produces instructions for LLM to write
         one complete chapter/subchapter ready to be added to report_body.
"""

import os
import asyncio
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from llms import LlmsHouse

class DesignSkillSelection(BaseModel):
    """Structured output for deciding which design skill to use."""
    selected_skill_filename: str = Field(
        description="The exact filename of the best matching design skill markdown file (e.g. 'academic.md'). Must be one of the explicitly provided available libraries."
    )

class CssGenerationResult(BaseModel):
    """Structured output for the generated CSS code."""
    css_code: str = Field(
        description="The raw, final CSS code strictly scoped to .dynamic-report-style. Should contain NO markdown blocks."
    )


async def generate_outline_prompt(
    user_query: str,
    planner_queries: List[Dict[str, Any]],
    sections: List[Dict[str, Any]],
    report_style_skill: str = ""
) -> str:
    """
    First LLM call: generates optimized prompt for report outline creation.
    
    Receives full sections with section_ids. Produces instructions for
    table_of_contents, report_outline, abstract, introduction, conclusion.
    Incorporates report_style_skill to determine structural conventions.
    
    Args:
        user_query: Original user research question.
        planner_queries: List of PlannerQuery dicts with query_num and query fields.
        sections: List of section dicts with section_content and section_id fields.
        report_style_skill: LLM-generated style directive for report formatting.
        
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

{'=' * 60}
REPORT STYLE DIRECTIVE (HIGHEST PRIORITY)
{'=' * 60}
{report_style_skill if report_style_skill else 'No specific style directive provided. Use standard academic report format.'}

The style directive above MUST be followed when deciding:
- Whether to use chapters vs flat sections
- How deep the heading hierarchy goes
- What format each section takes (narrative paragraphs, numbered Q&A, tables, bullet lists)
- Whether to include abstract/introduction/conclusion or skip them
- The overall tone and presentation

IMPORTANT: The table_of_contents structure should REFLECT the report type from the style directive.
For example:
- A practice sheet should have topic-based sections with numbered questions
- A cheat sheet should have condensed flat sections with tables
- An academic paper should have chapters with sub-chapters
- A financial briefing should have executive summary, analysis sections, risk assessment
{'=' * 60}

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
    sections_for_chapter: List[Dict[str, Any]],
    report_style_skill: str = "") -> str:


    toc_formatted = "FULL REPORT TABLE OF CONTENTS:\n"
    for main_chapter, subchapters in table_of_contents.items():
        toc_formatted += f"  {main_chapter}\n"
        for sub in subchapters:
            toc_formatted += f"    {sub}\n"
    
    sections_formatted = ""
    for idx, section in enumerate(sections_for_chapter):
        content = section.get('section_content', '')
        sections_formatted += f"\n=== RESEARCH SECTION {idx + 1} ===\n{content}\n"
    
    prompt = f"""You are an expert academic research writer. Write ONE complete, publication-ready chapter of a research report — requiring zero post-editing.

{'=' * 60}
THIS IS THE REPORT STYLE DIRECTIVE
{'=' * 60}
{report_style_skill if report_style_skill else 'Use standard academic report formatting with professional tone.'}
{'=' * 60}

{'=' * 60}
TABLE OF CONTENTS (for context only — do NOT write other chapters)
{'=' * 60}
{toc_formatted}
{'=' * 60}

{'=' * 60}
YOUR ASSIGNMENT: Write ONLY this chapter → "{chapter_heading}"
{'=' * 60}

{'=' * 60}
RESEARCH SOURCE MATERIAL FOR THIS CHAPTER
{'=' * 60}
{sections_formatted}
{'=' * 60}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP-BY-STEP INSTRUCTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Follow these steps IN ORDER before writing:

STEP 1 — READ: Read ALL research sections completely before writing a single word.
STEP 2 — PLAN: Identify the logical sub-groupings within this chapter.
STEP 3 — SYNTHESIZE: Merge overlapping content; each fact appears exactly once.
STEP 4 — WRITE: Produce the complete chapter following all rules below.
STEP 5 — CHECK: Verify every `*`, `**`, `` ` ``, and `>` opens AND closes cleanly.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. HEADING STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Main chapter   (e.g. "1. Topic")    → `# 1. Topic`
- Subchapter     (e.g. "1.1 Topic")   → `## 1.1 Topic`
- Section inside → `###` wherever 3+ related paragraphs need grouping

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. CONTENT SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ DO: Rewrite every sentence — synthesize and connect across source sections.
✅ DO: Preserve every fact, number, statistic, and technical detail exactly.
✅ DO: Add smooth transitions between topics.
❌ DO NOT: Copy-paste any source text verbatim.
❌ DO NOT: Invent any fact, figure, or URL not present in the source material.
❌ DO NOT: Include internal identifiers — strip all section_id, [REF], [SOURCE] tags.
❌ DO NOT: Reference other chapters or write content that belongs elsewhere.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. FORMATTING — RULES + EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Choose the format that best matches the content type:

──────────────────────────────────────────
BOLD  →  key terms, definitions, critical values only
──────────────────────────────────────────
✅ CORRECT:
  **Transformer architecture** relies on self-attention to process tokens in parallel.
  Costs fell by **87% between 2015 and 2023**, driven by manufacturing scale.

❌ WRONG:
  **The model was trained on large datasets and showed strong results.**   ← whole sentence bolded
  Results were **very** **good** and **highly** **significant**.           ← decorative overuse

──────────────────────────────────────────
ITALIC  →  first mention of a technical term; subtle emphasis
──────────────────────────────────────────
✅ CORRECT:
  The system uses *backpropagation*, a gradient-descent optimization technique.
  This approach yields *statistically significant* improvements over the baseline.

❌ WRONG:
  *The entire paragraph is italicized for stylistic reasons.*
  The method is *fast* and *accurate* and *reliable* and *scalable*.   ← stacked, meaningless

──────────────────────────────────────────
BLOCKQUOTE  →  one key finding or critical takeaway per major section
──────────────────────────────────────────
✅ CORRECT:
  > Models fine-tuned on domain-specific corpora outperformed general baselines by 34% on average.

❌ WRONG:
  > This section discusses machine learning.                 ← generic summary, not a finding
  > As mentioned above, performance improved.                ← vague redundancy
  > The results were interesting.                            ← not a notable takeaway

LIMIT: At most ONE blockquote per major section. Never quote ordinary sentences.

──────────────────────────────────────────
CODE BLOCKS  →  multi-line code, configs, algorithms only
──────────────────────────────────────────
✅ CORRECT:
  ```python
  def train(model, data, epochs=10):
      for epoch in range(epochs):
          loss = model.step(data)
  ```

❌ WRONG:
  ```
  The accuracy was 94.2%
  ```                        ← plain text is not code; use prose instead

ALWAYS include a language tag: ```python / ```bash / ```json / ```yaml

──────────────────────────────────────────
TABLES  →  comparisons, specs, benchmarks, feature matrices
──────────────────────────────────────────
✅ CORRECT:
  | Model       | Accuracy | Latency (ms) | Params |
  |-------------|----------|--------------|--------|
  | BERT-base   | 91.2%    | 45           | 110M   |
  | RoBERTa     | 93.8%    | 52           | 125M   |

❌ WRONG:
  - BERT: 91.2%, 45ms    ← bullet list when a table is clearly better
  Model, Accuracy, Size  ← comma list, not markdown table syntax

──────────────────────────────────────────
BULLETS / NUMBERED LISTS
──────────────────────────────────────────
- Bullet list  → unordered features, findings, properties
- Numbered list → sequential steps, ranked items, procedures
❌ DO NOT convert naturally flowing prose into bullets — write paragraphs.

──────────────────────────────────────────
INLINE CODE  →  variable names, commands, file paths, short expressions
──────────────────────────────────────────
✅  Run `pip install transformers` to install the library.
❌  Run pip install transformers  ← missing backticks for a shell command

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. CITATION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every URL from the research MUST become an inline markdown link. No bare URLs. No footnote-style references. No `## Sources` section at the end.

✅ CORRECT — cite at paragraph end, group multiple sources:
  Battery costs dropped **90% since 2010** due to improved lithium-ion supply chains,
  according to [BloombergNEF](https://bloomberg.com/energy) and
  [MIT Technology Review](https://technologyreview.com/batteries).

❌ WRONG:
  Battery costs dropped 90%. [1]
  https://bloomberg.com/energy                    ← bare URL
  See source: [Click here](https://bloomberg.com) ← "click here" is not descriptive

Link text rules:
- Use the publication name or a clear short description — never "here", "source", or the raw URL
- If the source name is unknown, use the domain name: [bloomberg.com](https://bloomberg.com/...)
- Group multiple sources in one `according to [A](url) and [B](url)` phrase
- Skip any URL that is weak, tangential, or adds nothing to the claim

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. HARD RULES — NEVER VIOLATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CLEAN MARKDOWN ONLY — Every `*`, `**`, `` ` ``, and `>` must open and close
   correctly. Unclosed or stray symbols break rendering. Double-check before output.
2. NO INTERNAL IDs — Strip all section_id, Section N, [REF], [SOURCE] from output.
3. NO INVENTED CONTENT — Facts, data, and URLs must come from the source material only.
4. NO VERBATIM COPYING — Every sentence must be rewritten and synthesized.
5. NO REDUNDANCY — Each fact appears once; merge duplicates across source sections.
6. NO DECORATIVE FORMATTING — Bold, italic, and blockquotes signal importance, not style.
7. NO PREAMBLE — Begin your output directly with the chapter heading. No "Here is..." intro.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Start IMMEDIATELY with the heading. Example:

# 1. Introduction          ← or ## 2.1 Background — match {chapter_heading} exactly

[Chapter content...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUICK REFERENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Heading        → main chapter         **term**   → key term / critical value
## Heading       → subchapter           *term*     → first use of technical term
### Heading      → logical group        `code`     → inline commands / vars only
> blockquote     → one key finding      | Table |  → comparisons and specs
- bullet         → unordered items      1. step    → sequential steps only
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Now write the COMPLETE chapter "{chapter_heading}". The output is the final chapter — heading, subheadings, and all content included."""

    return prompt



def get_available_design_skills() -> Dict[str, str]:
    """
    Reads all markdown files in the design_skills directory.
    
    Returns:
        Dict mapping filename (e.g. 'academic.md') to its contents.
    """
    skills_dir = os.path.join(os.path.dirname(__file__), 'design_skills')
    skills = {}
    
    if not os.path.exists(skills_dir):
        return skills
        
    for filename in os.listdir(skills_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(skills_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    skills[filename] = f.read()
            except Exception:
                pass
                
    return skills


async def choose_design_skill_prompt(
    user_query: str,
    table_of_contents: Dict[str, List[str]],
    abstract: str,
    introduction: str,
    available_skills: Dict[str, str]
) -> str:
    """
    Generates a prompt asking the LLM to select the most appropriate design
    skill filename based on the report context.
    
    Returns:
        Prompt for the routing LLM call.
    """
    toc_formatted = "FULL REPORT TABLE OF CONTENTS:\n"
    for main_chapter, subchapters in table_of_contents.items():
        toc_formatted += f"  {main_chapter}\n"
        for sub in subchapters:
            toc_formatted += f"    {sub}\n"
            
    # Create descriptions of available skills based on their filenames and first lines
    skills_list = ""
    for filename, content in available_skills.items():
        first_line = content.split('\n')[0].replace('#', '').strip() if content else "Style rules"
        skills_list += f"- {filename}: {first_line}\n"

    prompt = f"""You are a master UI/UX Art Director. Your task is to analyze an upcoming research report and select the PERFECT CSS design style for it from our available libraries.

=====================================================================
REPORT DATA:
=====================================================================
USER QUERY: {user_query}

{toc_formatted}

ABSTRACT: 
{abstract}

INTRODUCTION:
{introduction}

=====================================================================
AVAILABLE DESIGN LIBRARIES:
=====================================================================
{skills_list}

YOUR TASK:
Based heavily on the User Query and the Table of Contents, which ONE of these design libraries is the absolute best fit? 
If none fit perfectly, or if it is a general report, select `general_fallback.md`.
"""
    return prompt


async def generate_scoped_css_prompt(
    user_query: str,
    table_of_contents: Dict[str, List[str]],
    selected_skill_name: str,
    selected_skill_rules: str,
    report_style_skill: str = ""
) -> str:
    """
    Generates the final prompt for creating a custom CSS design leveraging
    the rules defined in the chosen design skill file.
    
    Args:
        user_query: The user's original query.
        table_of_contents: The generated TOC.
        selected_skill_name: Filename of the chosen skill.
        selected_skill_rules: The markdown contents of the chosen skill.
        report_style_skill: LLM-generated style directive for content context.
        
    Returns:
        Prompt string for the CSS generation LLM call.
    """
    
    toc_formatted = "FULL REPORT TABLE OF CONTENTS:\n"
    for main_chapter, subchapters in table_of_contents.items():
        toc_formatted += f"  {main_chapter}\n"
        for sub in subchapters:
            toc_formatted += f"    {sub}\n"
            
    prompt = f"""You are an elite, world-class UI/UX Designer and CSS Expert. Your task is to generate a custom, stunning CSS stylesheet for a report. You have been assigned to use the `{selected_skill_name}` design system.

=====================================================================
REPORT STYLE CONTEXT
=====================================================================
{report_style_skill if report_style_skill else 'Standard academic report format.'}

Use this style context to understand what kind of content elements the report will contain, so your CSS can highlight the right structural patterns.

=====================================================================
REPORT TOPIC:
=====================================================================
USER QUERY: {user_query}

{toc_formatted}

=====================================================================
YOUR STRICT DESIGN GUIDELINES ({selected_skill_name}):
=====================================================================
Apply the visual rules, colors, typography, and vibes from the following design brief exactly:

{selected_skill_rules}

=====================================================================
TECHNICAL REQUIREMENTS (CRITICAL!):
=====================================================================
1. **STRICT SCOPING RULES**:
   - ALL CSS rules **MUST** be strictly scoped under the class `.dynamic-report-style`. 
   - For example:
     `.dynamic-report-style h1 {{ color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 8px; }}`
     `.dynamic-report-style blockquote {{ border-left: 4px solid #eaeaea; }}`
   - Do NOT write global CSS (e.g., `body {{ ... }}`). It MUST be scoped to `.dynamic-report-style`.

2. **COMPONENT COVERAGE**:
   - The report contains elements like `h1`, `h2`, `h3`, `p`, `blockquote`, `ul`, `ol`, `li`, `table`, `th`, `td`, `a`, `img`, `pre`, and `code`.
   - Ensure the classes cover these beautifully according to your design brief.
   - For links (`a`), add nice hover effects.
   - Make sure your tables look incredible and professional.

"""
    return prompt




async def main():
    """Module entry point for testing."""
    pass


if __name__ == "__main__":
    asyncio.run(main())
