"""
Prompt generators for two-phase research report creation.

Phase 1: generate_outline_prompt() — produces instructions for LLM to create
         table_of_contents, report_outline, abstract, introduction, conclusion.
Phase 2: generate_chapter_prompt() — produces instructions for LLM to write
         one complete chapter as self-contained HTML with inline styles.

Design flow: generate_design_instructions_prompt() produces a deep visual
style brief (colors, fonts, spacing, chart conventions) that is injected
into every chapter prompt for consistent aesthetics.
"""

import os
import re
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field
from llms import LlmsHouse

class DesignSkillSelection(BaseModel):
    """Structured output for deciding which design skill to use."""
    selected_skill_filename: str = Field(
        description="The exact filename of the best matching design skill markdown file (e.g. 'academic.md'). Must be one of the explicitly provided available libraries."
    )

class DesignInstructionsResult(BaseModel):
    """Structured output containing the visual style brief for HTML chapters."""
    design_instructions: str = Field(
        description="Comprehensive visual style instructions covering colors, fonts, spacing, chart conventions, table styles, and overall aesthetic. This is a detailed text brief, NOT CSS code."
    )


def generate_global_outline_prompt(
    user_query: str,
    planner_queries: List[Dict[str, Any]],
    sections: List[Dict[str, Any]],
) -> str:
    """
    Generates a single prompt for the LLM to design the full report outline
    (all chapters and subchapters) using a global view of all sections.

    To keep the prompt bounded, only the first ~20 lines of each section are
    included as content snippets. If this global attempt fails, the writer
    falls back to the per-chapter outline generation path.
    """
    # Planner context block
    planner_block = "PLANNER QUERIES (chapter intents):\n" + "-" * 80 + "\n"
    for pq in planner_queries:
        planner_block += f"Query #{pq.get('query_num', 0)}: {pq.get('query', '')}\n"
    planner_block += "-" * 80 + "\n\n"

    # Sections snapshot block
    sections_block = "ALL RESEARCH SECTIONS SNAPSHOT (first ~20 lines each):\n" + "=" * 80 + "\n\n"
    for idx, section in enumerate(sections):
        content = section.get("section_content", "") or ""
        section_id = section.get("section_id", f"sec-{idx+1}")
        # Take only the first ~20 lines to control prompt size
        lines = content.splitlines()
        head = "\n".join(lines[:20])
        sections_block += f"--- Section {idx + 1} [section_id: {section_id}] ---\n{head}\n\n"
    sections_block += "=" * 80 + "\n"

    prompt = f"""You are an expert research report architect. Your task is to design the COMPLETE outline for a multi-chapter research report from a global view of all research sections.

USER QUERY:
{user_query}

{planner_block}

{sections_block}

TASK:
Design the full report structure: top-level chapters and their subchapters, assigning each section_id to exactly one subchapter (avoid repetition unless absolutely necessary). The outline must:

- Cover all important content contained in the research section snapshots.
- Avoid redundant chapters or subchapters — no repetition of topics across the outline.
- Use a natural narrative flow from foundations → analysis → synthesis.
- Keep subchapter counts reasonable (typically 2–6 per chapter), merging very small or tightly related sections, and giving large, dense sections their own subchapter when warranted.
- Treat top-level chapter titles as concise overviews; subchapters carry the detailed angles.

Rules:
1. Propose a numbered sequence of chapters: "1. [Chapter Title]", "2. [Chapter Title]", etc. Each chapter title must clearly communicate its role in the report.
2. For each chapter, define 2–6 subchapters as needed: "1.1 [Subchapter Title]", "1.2 [Subchapter Title]", etc. Subchapter titles must be specific and non-generic.
3. Every section_id from the snapshot MUST be assigned to exactly one subchapter — do not omit any, and do not repeat except in rare, clearly necessary overlaps.
4. The chapter-level entry in the outline must be the union of its subchapters' section_ids.
5. Maintain a clean, progressive narrative across chapters — avoid jumping back and forth between topics.

OUTPUT FORMAT — respond with exactly this JSON object, no markdown fences, no extra text:
{{
  "table_of_contents": {{
    "1. [Chapter Title]": ["1.1 [Subchapter Title]", "1.2 [Subchapter Title]"],
    "2. [Chapter Title]": ["2.1 [Subchapter Title]"]
  }},
  "report_outline": {{
    "1. [Chapter Title]": ["section-id-a", "section-id-b"],
    "1.1 [Subchapter Title]": ["section-id-a"],
    "1.2 [Subchapter Title]": ["section-id-b"],
    "2. [Chapter Title]": ["section-id-c"],
    "2.1 [Subchapter Title]": ["section-id-c"]
  }}
}}
"""
    return prompt


async def generate_chapter_prompt(
    chapter_heading: str,
    table_of_contents: Dict[str, List[str]],
    sections_for_chapter: List[Dict[str, Any]],
    design_instructions: str = "",
    user_query: str = "",
    planner_queries: Optional[List[Dict[str, Any]]] = None,
) -> List:

    from langchain_core.messages import SystemMessage, HumanMessage

    system_prompt = """You produce one complete report chapter as a single HTML block. Output is inserted as-is. Your job: match report type, choose the best way to show this chapter and its subchapters (not always a table), keep layout inside bounds, and preserve full knowledge while explaining ideas clearly.

HOW TO DECIDE HOW TO SHOW THIS CHAPTER (in order)
1) Design instructions — They state report type and how data should be shown (prose-heavy vs tables vs charts vs lists vs Q&A, etc.). Treat them as the first authority.
2) Report type — Use the REPORT TYPES reference below. Each type has a default look and typical section content; your section should feel like that type.
3) This chapter’s content — Ask: Is this narrative, comparison, chronology, definitions, numbers, steps, or mixed? Then pick the best format:
   - Narrative / argument / story → prose (paragraphs, blockquotes). Do not force a table.
   - Comparison of a few items → prose or a compact list often clearer than a wide table.
   - Comparison of many items or repeated columns → table.
   - Trend over time / distribution → Charts.css or SVG. Not every number set needs a table.
   - Steps / procedure → numbered list or short paragraphs.
   - Definitions / terms → definition blocks or bold term + line, not necessarily a table.
   - Q&A / FAQ → question as heading, answer as paragraph; or <details> for reveal.
   - When content is long and you are clearly moving into a new chunk of focus (new major point, new scenario, new dataset), you may insert a lightweight page-break marker `<div data-page-break="true"></div>` before continuing, so the frontend can split the chapter into multiple visual pages.
Do not default to a table. Match format to content and to what the design instructions say this report type uses. Use a mix of visuals (Charts.css, SVG, KPI cards, callouts, timelines) and prose when the content justifies it, instead of repeating similar large tables. For every important visual, briefly explain in the surrounding text what it shows, why it is there, and how it helps the reader understand the idea more easily.

REPORT TYPES — WHAT EACH EXPECTS (use to recognize and match your report)
- General: Clean, balanced; prose + tables + charts as needed. Sections: overview, background, analysis, conclusion.
- Math: White, LaTeX-like; definitions in boxes, theorems, proofs, worked examples, graphs. Sections: definitions, theorems/proofs, examples, key formulas.
- Philosophy: Warm parchment, prose-first; blockquotes, thought experiments, dialectical structure. Sections: question, thinkers, arguments, objections, relevance.
- History: Archival cream, chronology; timelines, dates, primary quotes, maps. Sections: context, chronological narrative, causes, legacy.
- Literature: Narrow column, typography-first; excerpts, close reading, themes. Sections: work/author, synopsis, textual analysis, themes, legacy.
- Physics: Diagrams + equations; force diagrams, equations, examples, units. Sections: phenomenon, laws/equations, diagrams, examples, experiment.
- Finance: Numbers-first; KPIs, charts, dense tables, green/red. Sections: thesis, metrics, analysis, valuation, risk.
- Startup/Pitch: Bold metrics, growth charts, minimal prose; pitch-deck feel. Sections: problem, solution, traction, ask.
- Scientific: Methods, results, figures/tables, captions; evidence-led. Sections: intro, methods, results, discussion.
- News/Journalism: Lede first, inverted pyramid, quotes, datelines. Sections: lede, facts, voices, timeline, impact.
- Coding: Code blocks first-class; API tables, examples, architecture. Sections: what/why, setup, API/concepts, examples, best practices.
- Practice/Learning: Cheat sheets, problems, hidden solutions, tips. Sections: concepts, reference table, problems, solutions (e.g. <details>), mistakes/tips.
- Minimalist: Lots of whitespace; typography as data, few elements. Sections: one takeaway, key numbers, brief analysis.

LAYOUT — NEVER MESS UP
- One outer div only: width 100%, max-width 100%, box-sizing border-box, overflow hidden. All content inside it. The outer document viewer already constrains total width.
- Inner layout: single column (block stack). No multi-column or grid unless design instructions explicitly ask for it. Everything stacks vertically within the available width.
- Every inner block (paragraph, heading, table wrapper, chart wrapper, list, callout): use width 100% or max-width 100%, box-sizing border-box. No fixed pixel width larger than the container. No position absolute/fixed that escapes the div.
- Tables: wrap in <div style="width:100%; overflow-x:auto;"> so wide tables scroll instead of bursting out.
- Charts (Charts.css or SVG): same — wrapper width 100%, overflow-x auto. Let chart scale or scroll inside the column.
- Spacing: use margins/padding from design instructions consistently. Gaps between sections so nothing overlaps or feels cramped.
- Fonts and colors: only from design instructions. Same for every heading, paragraph, table, and chart in this section.

OUTPUT — ONE CONTAINING DIV
- Exactly one root: <div class="report-chapter" style="width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;"> ... </div>
- Inside: structure that fits the report type and this section — e.g. h2, then divs/sections with h3/h4, prose, lists, tables (wrapped), Charts.css, SVG, Q&A, callouts. All contained; nothing overlapping or overflowing.

UNDERSTANDING THE CORRECT CHAPTER
- You are writing one specific place in the report: the CHAPTER marked "YOU ARE HERE" in the table of contents. That is the only part you produce.
- Inside this chapter, you are responsible for both the top-level chapter title and all of its subchapters. The chapter title should give a crisp, high-level overview; each subchapter should then go in-depth on its specific angle so that, together, the chapter feels complete.
- Understand what value this chapter brings: it exists to answer a part of the user’s request and the planner’s plan. Your output must fully deliver that — the reader who finishes this chapter should feel that this piece of the report is complete and genuinely understandable.
- Use the research sections provided for this chapter only. They are the evidence for this chapter. Your job is to turn them into one coherent, complete chapter (with internal subheadings) that fulfills the exact chapter heading and its role in the TOC. Nothing essential from these sections should be missing; no filler that doesn’t serve the chapter’s purpose.

THIS CHAPTER ONLY
- Write only this chapter and its subchapters. TOC shows opening / middle / closing. Focus this chapter’s scope; don’t repeat earlier or preempt later. Keep flow.

CONTENT, EXPLANATION, AND KNOWLEDGE
- Preserve every fact, number, date, nuance from source. Synthesize in your own voice; no paste-by-blocks. No invented content. No section_id, [REF], [SOURCE]. Explain clearly; best format for clarity (prose, list, chart, or table as judged above). No half-explained ideas; dense but clear.
- Content quality matters as much as visuals. Never sacrifice explanation, narrative, or step-by-step reasoning just to use a visual. Whenever you introduce a chart, table, diagram, or other visual, add a short, plain-language explanation before or after it so a reader who is not visually oriented still fully understands the concept.

STRUCTURE RULES
- Hierarchy: h2 (chapter title once at the top), h3 (subchapters that align with the table of contents for this chapter), h4 (sub-sections inside a subchapter). Short labels only. Inline CSS only; no <style>, <link>, <html>, <head>, <body>, <!DOCTYPE>. Valid HTML; same element type → same styling.

HARD RULES
1. Start with <div class="report-chapter" style="width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;">. No text before or after the HTML.
2. Colors/fonts from design instructions only. No overlap or overflow.
3. No invented content. No internal IDs in output.
4. One full chapter (with its internal subchapters); clear, information-dense, and easy to understand."""

    # ── Build TOC block ──────────────────────────────────────────────────────
    toc_lines = ["FULL REPORT TABLE OF CONTENTS:"]
    chapter_list = list(table_of_contents.keys())
    for i, (main_chapter, subchapters) in enumerate(table_of_contents.items()):
        position_tag = ""
        if i == 0:
            position_tag = "  ← FIRST CHAPTER"
        elif i == len(chapter_list) - 1:
            position_tag = "  ← FINAL CHAPTER"
        is_current = chapter_heading.strip() in main_chapter.strip() or main_chapter.strip() in chapter_heading.strip()
        marker = "  >>>  YOU ARE HERE" if is_current else ""
        toc_lines.append(f"  {main_chapter}{position_tag}{marker}")
        for sub in subchapters:
            sub_is_current = chapter_heading.strip() in sub.strip() or sub.strip() in chapter_heading.strip()
            sub_marker = "  >>>  YOU ARE HERE" if sub_is_current else ""
            toc_lines.append(f"      {sub}{sub_marker}")
    toc_formatted = "\n".join(toc_lines)

    # ── Build sections block ─────────────────────────────────────────────────
    sections_formatted = ""
    for idx, section in enumerate(sections_for_chapter):
        content = section.get('section_content', '')
        sections_formatted += f"\n{'─' * 60}\nRESEARCH SECTION {idx + 1} OF {len(sections_for_chapter)}\n{'─' * 60}\n{content}\n"

    # ── User query and planner context (for section focus) ───────────────────
    user_planner_block = ""
    if user_query or (planner_queries and len(planner_queries) > 0):
        user_planner_block = "\n"
        if user_query:
            user_planner_block += f"USER QUERY (what the report is for):\n{user_query}\n\n"
        if planner_queries:
            planner_lines = "PLANNER QUERIES (what each part of the report is meant to cover):\n"
            for pq in planner_queries:
                planner_lines += f"  {pq.get('query_num', '')}. {pq.get('query', '')}\n"
            user_planner_block += planner_lines
        user_planner_block += "\nUse these to understand user intent and which part of the report you are writing. Your chapter must serve the query and the planner’s goal for this section.\n\n"

    default_design = "Clean professional: navy headings #1a365d, body #2d3748, bg white, accent #2c5282. Inline styles only."
    human_prompt = f"""DESIGN INSTRUCTIONS (report type + colors, fonts, layout — use everywhere; sections must fit cleanly inside the document viewer width without overflowing):
{design_instructions.strip() if design_instructions else default_design}
{user_planner_block}
TABLE OF CONTENTS (you are writing the section marked YOU ARE HERE):
{toc_formatted}ƒ

SECTION FOCUS — UNDERSTAND AND FULFILL THIS CHAPTER COMPLETELY
- You are writing exactly one chapter: "{chapter_heading}". It is the only place in the TOC marked "YOU ARE HERE". All other chapters are written separately; your output is only this one.
- Understand what value this section brings: it answers a specific part of the user’s request and the planner’s plan. Your chapter must feel complete and genuine — a reader who finishes it should have gotten the full story for this part of the report.
- The research sections below are the only source for this chapter. They were gathered to support this exact chapter. Your job: turn them into one coherent chapter that (1) fully fulfills the chapter heading and its role in the TOC, (2) leaves no important information from these sections out, (3) does not add filler or repeat what belongs in other chapters. If the sections contain it, it should appear in your chapter in the best form (prose, list, table, or chart). Perfect output = this chapter completely delivered using these sections.

RESEARCH SECTIONS FOR THIS CHAPTER ({len(sections_for_chapter)}):
{sections_formatted}

TASK: Write only this chapter: "{chapter_heading}"
- Decide how to show it: (1) design instructions say what report type and formats to use, (2) match that report type from the reference, (3) for this section’s content pick the best format — prose, list, chart, or table. Do not default to a table.
- One outer <div class="report-chapter" style="width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;"> containing everything. All inner content width 100% or wrapped with overflow-x auto; no overlap or overflow.
- Preserve all information; present clearly. No preamble or text after the closing </div>."""

    return [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]





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
    planner_queries: List[Dict[str, Any]],
    table_of_contents: Dict[str, List[str]],
    abstract: str,
    introduction: str,
    available_skills: Dict[str, str]
) -> str:
    """
    Generates a prompt for the LLM to select the single best design skill
    filename for this report. Returns the prompt string.
    """
    toc_formatted = "TABLE OF CONTENTS:\n"
    for main_chapter, subchapters in table_of_contents.items():
        toc_formatted += f"  {main_chapter}\n"
        for sub in subchapters:
            toc_formatted += f"    {sub}\n"

    planner_context = "PLANNER QUERIES (chapter intents):\n"
    for pq in planner_queries:
        planner_context += f"  {pq.get('query_num', 0)}. {pq.get('query', '')}\n"

    # Extract Identity & Scope (primary signal) and first line of Content Structure
    skills_list = ""
    for filename in sorted(available_skills.keys()):
        content = available_skills[filename]
        identity_match = re.search(r'## Identity & Scope\n(.*?)(?=\n\n##)', content, re.DOTALL)
        structure_match = re.search(r'## Content Structure & Narrative Flow\n(.*?)(?=\n\n##)', content, re.DOTALL)
        identity = identity_match.group(1).strip() if identity_match else "General report; no single domain."
        structure_blob = structure_match.group(1).strip() if structure_match else ""
        structure_first = structure_blob.split("\n")[0].strip() if structure_blob else "Standard sections."
        skills_list += f"--- {filename} ---\n{identity}\nStructure: {structure_first}\n\n"

    valid_filenames = ", ".join(sorted(available_skills.keys()))

    prompt = f"""Select exactly one design skill for this report. Output its filename only.

SELECTION RULE:
- Match the report's primary domain and content type to the skill's "Identity & Scope". Query + planner queries + TOC define the report.
- Strong match: topic and format align (e.g. theorems/proofs → math; KPIs/valuation → finance; chronology/primary sources → history; arguments/thinkers → philosophy; startups/pitch → startup_pitch).
- If no strong domain match, or mixed domains, or clearly general/broad topic → general_fallback.md.
- One skill. No hybrids.

REPORT SIGNALS:
QUERY: {user_query}

{planner_context}

{toc_formatted}

ABSTRACT: {abstract[:500] if abstract else "(none)"}

INTRODUCTION: {introduction[:500] if introduction else "(none)"}

SKILLS (Identity & Scope = when to use):
{skills_list}

VALID OUTPUTS (pick one): {valid_filenames}
"""
    return prompt



async def generate_design_instructions_prompt(
    user_query: str,
    planner_queries: List[Dict[str, Any]],
    table_of_contents: Dict[str, List[str]],
    selected_skill_name: str,
    selected_skill_rules: str
) -> str:

    toc_formatted = "FULL REPORT TABLE OF CONTENTS:\n"
    for main_chapter, subchapters in table_of_contents.items():
        toc_formatted += f"  {main_chapter}\n"
        for sub in subchapters:
            toc_formatted += f"    {sub}\n"

    planner_context = "PLANNER'S RESEARCH PLAN:\n" + "-" * 80 + "\n"
    for pq in planner_queries:
        planner_context += f"Query #{pq.get('query_num', 0)}: {pq.get('query', '')}\n"
    planner_context += "-" * 80 + "\n\n"

    prompt = f"""You are a senior Visual Art Director. Define the design identity for a research report. Your output is injected into chapter-writing prompts — chapter writers will use it as their sole visual reference.

=====================================================================
INPUTS
=====================================================================
USER QUERY: {user_query}

{planner_context}

{toc_formatted}

ROUTER-SELECTED SKILL — {selected_skill_name}:
A previous model analyzed the query, planner plan, and TOC and selected this skill as the best fit. Use it as strong inspiration. The skill lists visual patterns (Charts.css types, SVG diagram options, interactive elements) — choose the best combination for this report. Adapt or blend if the report spans multiple domains.

Skill rules (identity, structure, and visual toolkit) are a starting point, not a prison. Use them to:
- Anchor the report's visual feel (domain-appropriate typography, color temperature, density).
- Identify which VISUAL FORMS are primary for this report type (e.g. charts for finance, diagrams for physics, quotations for philosophy).
- Suggest domain-typical layouts and emphasis.

You are allowed to:
- Refine colors into a specific, coherent palette that best fits this particular report and user query, as long as it respects the skill’s color philosophy.
- Prioritize a subset of visual patterns for this report (e.g. favor Charts.css bar/line charts + KPI cards, but rarely use large dense tables).
- Introduce additional, reasonable HTML structures (timelines, callouts, two-column comparisons) when they clearly align with the skill’s intent.

Always favor designs that make the content easiest to understand, not just the most decorative.

SKILL REFERENCE:
{selected_skill_rules}

=====================================================================
WORK FLOW (follow in order — each step informs the next)
=====================================================================

PHASE 1 — ANALYZE REPORT TYPE
From user query, planner queries, and TOC: What does the user want? Single domain (math, finance, philosophy, history, etc.) or hybrid? Is it a cheat sheet, Q&A, narrative essay, data-heavy analysis, pitch deck, reference, comparison? Infer the report's primary purpose and audience. (Do not output this analysis — use it to drive all decisions below.)

PHASE 2 — HIGH-LEVEL DESIGN DECISIONS
Decide: What will OUR report look like?
- General presentation approach: prose-dense vs. visual-dense vs. balanced
- Visual mix: which Charts.css types, SVG diagrams, tables, lists, callouts, timelines
- Data presentation: how numbers, trends, and comparisons will appear (tables, charts, cards, inline)
- Emotional tone: clinical, warm, academic, editorial, minimal

PHASE 3 — STRUCTURE & FORMAT DEPTH
- Report structure: how chapters flow, what each section type conveys
- Format: cheat sheet (compact reference), Q&A (question-led), narrative (flowing prose), finance-dense (KPIs, dashboards), or hybrid
- Component logic: when to use tables vs. charts vs. prose vs. lists. Which visual patterns from the skill apply here?
- Interactive elements: `<details>` for collapsed content? When?

PHASE 4 — TYPOGRAPHY & COLOR
Use the skill's Typography & Color section as foundation. Output exact values:
- Fonts: heading + body (+ monospace if needed). Google Fonts or system stacks.
- Type scale: h2, h3, h4, body, caption — rem values.
- Line-height, weights.
- Palette: bg, body text, headings, 2–3 accents, semantic (pos/neg if relevant), chart sequence (5–6 hex).
- Component surfaces: table header, row alt, blockquote, insight box, code block — bg + border hex.
All colors must be consistent throughout. One palette — no ad-hoc additions.

PHASE 5 — GUARDRAILS (instructional, not rigid)
- Preserve all information. If content doesn't fit a template, invent a new format. Never truncate to fit.
- Consistent palette. we can color outside the defined system if it's necessary and you understand thaht with combination it will perfectly fit the report.
- Layout is guidance. Chapter writers adapt structure when content demands it.
- When uncertain, default to clarity over flair.

=====================================================================
OUTPUT FORMAT
=====================================================================
Write a design brief as plain text under these headers. Use bullets and exact values (hex, rem). No CSS code, no JSON, no markdown blocks. A chapter writer must be able to make every visual decision from this brief alone.

1. COLOR SYSTEM — bg, text hierarchy, accents, semantic, chart colors, component surfaces (all hex)
2. TYPOGRAPHY — fonts, scale, weights, line-height
3. SPACING — vertical rhythm, component padding, max content width
4. VISUAL MOOD — 2–4 sentences: what type of aesthectism we follow and small details that will make the report look and feel like the user wants it to be.
5. What Report will Look Like —  some sentences: what the report will look like and how it will be presented. what is the report type and How to present it , how user wants to percieve this report , what type of visuals will be using , and how should our structure and elements be used to present the report in the best way.
6. REPORT INTENT - some sentences: what is the report intent and what is the user trying to achieve with this report and want to learn or understand or read , whatever and What are the above ways we can achieve and how to show it in the best way.
7. VISUALS - Explaining the visuals and how to use them in the best way to achieve the report intent and user wants. and not restricing to tose visuals only giving LLM the ability to make it , but explain all things we can do using the skills we have and Additional things
8  What to avoid - Explaining things to avoid might not to present the report in a way that user doesn't want to , Explaining user intent and what might each sections should avoid , like general mistakes like overusing tables or charts or lists or etc or if suppose to use not using , and may be this report follow completely different visuals like hisotrical structure and not using it.s
"""
    return prompt

def generate_single_chapter_outline_prompt(
    chapter_num: int,
    total_chapters: int,
    query: str,
    sections: List[Dict[str, Any]],
    all_queries: List[Dict[str, Any]],

) -> str:
    """
    Generates a focused prompt for ONE chapter's outline.

    The model designs the chapter AND its subchapters together, so it can see
    how all research sections for this chapter relate, which visuals they may
    demand, and how to create a natural, non-repetitive flow within the chapter.
    """
    is_first = chapter_num == 1
    is_last = chapter_num == total_chapters

    position_note = ""
    if is_first:
        position_note = "This is the FIRST chapter. It should establish the foundation and context for everything that follows."
    elif is_last:
        position_note = "This is the FINAL chapter. It should synthesize the report and point toward key outcomes or future directions."
    else:
        position_note = f"This is chapter {chapter_num} of {total_chapters}. It builds upon earlier chapters and sets up those that follow."

    # Full report map for positional awareness
    all_queries_block = "FULL REPORT PLAN (all chapters):\n" + "-" * 60 + "\n"
    for pq in all_queries:
        num = pq.get("query_num", 0)
        marker = " ← YOUR CHAPTER" if num == chapter_num else ""
        all_queries_block += f"  Chapter {num}: {pq.get('query', '')}{marker}\n"
    all_queries_block += "-" * 60 + "\n"

    # Sections block — full content since it's scoped to this query only
    sections_block = f"RESEARCH SECTIONS FOR THIS CHAPTER ({len(sections)} sections):\n" + "=" * 60 + "\n\n"
    for idx, section in enumerate(sections):
        content = section.get("section_content", "")
        section_id = section.get("section_id", "unknown")
        sections_block += f"--- Section {idx + 1} [section_id: {section_id}] ---\n{content}\n\n"
    sections_block += "=" * 60 + "\n"

    available_ids = [s.get("section_id", "unknown") for s in sections]

    prompt = f"""You are an expert research report architect. Your task is to design the structure for ONE chapter of a multi-chapter research report.

{'=' * 70}
{all_queries_block}
{'=' * 70}

YOUR ASSIGNMENT: Design Chapter {chapter_num} of {total_chapters}
Research Focus: "{query}"
{position_note}

{'=' * 70}
{sections_block}
{'=' * 70}

TASK: Produce the outline for CHAPTER {chapter_num} ONLY.

Rules:
1. The chapter title must be numbered: "{chapter_num}. [Descriptive Title That Reflects The Research Focus]"
2. Carefully determine the *most effective* number and structure of subchapters (usually 2 to 6, but only as needed) by deeply analyzing the *actual content, type, and depth* of information in the Research Sections for this chapter. Go beyond making a chapter outline—think about how the report will actually be shown to readers and what arrangement delivers the clearest, richest, and most logically progressing reading experience. You must not default to a template or spread content to fill subchapters unnecessarily; every decision on chapter structure should be dictated by the genuine information present, its focus and relationships, and by how people will understand the report best.

   - If some research sections contain only brief, minor, or closely related points, consider merging them into a single subchapter or grouping—do *not* create an artificial subchapter for every small section.
   - Conversely, if content is deep, multifaceted, or supports multiple key ideas, split it appropriately—but never split just to increase the number of subchapters or to make the outline look longer.
   - Always aim for logical, meaningful structure: Each subchapter must present a clear conceptual grouping or necessary logical step in the narrative. Avoid fragmenting content or grouping unrelated ideas just to match a number.
   - Your decisions for splitting or merging subchapters must maximize clarity, thematic progression, and value for the reader. Never stretch or compress chapters just for symmetry—let information density and natural flow lead the outline.

3. Every section_id in the provided list MUST be included under *at least* one subchapter in the outline. Do not omit any section_ids.
4. **STRICTLY MINIMIZE REPEATING:** Each section_id should ideally be assigned to just ONE subchapter and must not be repeated across multiple subchapters unless that overlap is absolutely necessary for understanding. Any overlap must be rare, brief, and clearly justified by distinct purposes, never simple duplication that forces the reader to re-read the same material.
5. The chapter-level entry in "outline" must be the UNION of all its subchapters' section_ids.
6. If some research section is large and conceptually distinct, it can stand alone as a subchapter. If multiple research sections are small and very closely related, merge them into a single subchapter instead of creating many tiny subchapters.
6. Subchapter titles must be sharply focused and descriptive—never generic labels like "Overview" or "Details." Each title must give the reader a *precise* sense of what specific content or angle is covered, always reflecting the real substance and sequence of the research sections grouped below it.
7. Maintain Contextual Flow: Both the chapter and subchapter titles must fit naturally into the full report plan—avoid redundant or ambiguous headings. The sequence of subchapters should read as a compelling, non-redundant step-by-step narrative when viewed among all chapter titles in the full report.
Available section_ids: {available_ids}
8. Approach this as designing the *presentation* of the report: always select the structure, subchapter splits/merges, and narrative flow that will show the chapter’s content in the richest, clearest form, making it both information-dense and easy to follow, while never simply repeating or padding.
9. Do not overstretch the chapter with unnecessary subdivisions, and do not make it too brief by omitting important material—balance depth, coherence, and succinctness, and ensure the best presentation of all available research content.
10. Any sequential relationship between sections should be respected—if some subchapters build naturally on those coming before, reflect this progressive logic, but avoid repetition or backtracking over the same topics.
11. The chapter title must provide a concise general overview of the entire chapter, while each subchapter title must capture specific, unique facets of the chapter’s main topic based on the grouped section_ids. For main chapter headings (like "5. …" that have 5.1, 5.2, etc. beneath them), treat the top-level chapter as an overview that previews what the subchapters will cover and how the sections connect, instead of repeating subchapter content.
12. Decide all chapter and subchapter titles analytically, with care—base every grouping, sequence, and title explicitly on the actual content of your research sections and the needs of a reader encountering this part of the report for the first time.

OUTPUT FORMAT — respond with exactly this JSON object, no markdown fences, no extra text:
{{
  "chapter_title": "{chapter_num}. [Your Chapter Title]",
  "subchapters": [
    "{chapter_num}.1 [Subchapter Title]",
    "{chapter_num}.2 [Subchapter Title]"
  ],
  "outline": {{
    "{chapter_num}. [Your Chapter Title]": ["section-id-a", "section-id-b", "section-id-c"],
    "{chapter_num}.1 [Subchapter Title]": ["section-id-a", "section-id-b"],
    "{chapter_num}.2 [Subchapter Title]": ["section-id-c"]
  }}
}}
"""
    return prompt










def generate_framing_sections_prompt(
    user_query: str,
    ordered_chapter_titles: List[str],

) -> str:
    """
    Generates a lightweight prompt for abstract, introduction, and conclusion.
    """
    toc_block = "REPORT TABLE OF CONTENTS:\n"
    for title in ordered_chapter_titles:
        toc_block += f"  {title}\n"

    prompt = f"""You are an expert research writer. Based on the research topic and the report's chapter structure, write three framing sections for the report.{'=' * 70}
USER RESEARCH QUERY: {user_query}
{'=' * 70}

{toc_block}

{'=' * 70}
YOUR TASK
{'=' * 70}

Write three sections based SOLELY on the query and the chapter titles above.
Do not invent data or statistics — write in terms of scope, structure, and intent.

ABSTRACT (100–200 words):
  Summarizes the report's purpose, scope, what chapters cover collectively,
  and the significance of the topic. Written for a reader who reads only this.

INTRODUCTION (200–350 words):
  Establishes why this topic matters, what question the report answers,
  how the report is structured (referencing the chapters), and what the
  reader will gain by the end.

CONCLUSION (200–350 words):
  Synthesizes the logical arc of the report, draws forward-looking insights
  tied to the chapter themes, and closes with a clear takeaway for the reader.

All three must be returned as clean HTML. Permitted tags:
<p>, <strong>, <em>, <ul>, <ol>, <li>, <br>, <blockquote>
Do NOT use <html>, <head>, <body>, <style>, or <!DOCTYPE> tags.
Wrap each section in a root <div>.

OUTPUT FORMAT — respond with exactly this JSON object, no markdown fences, no extra text:
{{
  "abstract":     "<div><p>...</p></div>",
  "introduction": "<div><p>...</p><p>...</p></div>",
  "conclusion":   "<div><p>...</p><p>...</p></div>"
}}
"""
    return prompt

async def main():
    """Module entry point for testing."""
    pass


if __name__ == "__main__":
    asyncio.run(main())
