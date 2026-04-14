"""
Prompt generation for the editor node.

Produces a SystemMessage + HumanMessage pair for section-level HTML editing,
inspired by generate_chapter_prompt's structure but focused on applying
user feedback to an existing chapter — no design instructions, no research
sections. The edit_mode ("visual" or "research") is dynamically injected
into the constraint block via f-string interpolation.
"""

from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import SystemMessage, HumanMessage


# ── Mode-specific constraint blocks ─────────────────────────────────────
_VISUAL_CONSTRAINT = """You are in VISUAL-ONLY mode.
- Keep ALL facts, numbers, dates, claims, and references exactly as they are.
- Change ONLY: layout, structure, formatting, order, visual elements (tables, charts, callouts, styling).
- Do NOT add new information. Do NOT remove existing information unless the user explicitly requests it."""

_RESEARCH_CONSTRAINT = """You are in RESEARCH mode.
- You MAY incorporate the additional research snippets provided below.
- You may rephrase, reorganize, and restructure the chapter freely.
- Do NOT invent facts, numbers, or claims that are not in the original chapter or the research snippets.
- Do NOT remove existing information unless the user explicitly requests it."""


async def generate_edit_chapter_prompt(
    *,
    chapter_heading: str,
    table_of_contents: Optional[Union[Dict[str, List[str]], str]] = None,
    design_instructions: Optional[str] = None,
    old_html: str,
    feedback: str,
    edit_mode: str = "visual",
    additional_research: Optional[str] = None,
) -> List:
    """
    Builds a [SystemMessage, HumanMessage] pair for section-level HTML editing.

    The system prompt contains the editing rules and page-structure constraints
    (inspired by generate_chapter_prompt). The human prompt supplies the
    current chapter HTML, user feedback, optional research snippets, and
    the table of contents for positional awareness.

    Args:
        chapter_heading: Title of the chapter being edited.
        table_of_contents: Full report TOC for context.
        old_html: Current rendered HTML of the section.
        feedback: User's edit instructions.
        edit_mode: "visual" (layout-only) or "research" (may add new info).
        additional_research: Extra research snippets for research-mode edits.

    Returns:
        Two-element list: [SystemMessage, HumanMessage].
    """
    mode = (edit_mode or "visual").strip().lower()
    if mode not in {"visual", "research"}:
        mode = "visual"

    constraint_block = _VISUAL_CONSTRAINT if mode == "visual" else _RESEARCH_CONSTRAINT

    system_prompt = f"""You rewrite ONE existing report chapter to apply the user's feedback. Output is a COMPLETE replacement HTML block — not a diff, not a patch.

EDITING MODE: {mode.upper()}
{constraint_block}

PAGE STRUCTURE — FOLLOW EXACTLY
Your chapter will be rendered inside a document viewer that displays content as stacked pages. Every piece of content MUST be inside a <div class="report-page"> container.

ABSOLUTE RULES FOR PAGES:
- Every heading, paragraph, table, chart, list, callout MUST be inside a <div class="report-page">. Content outside a report-page will break layout.
- Each page: <div class="report-page">...content...</div>. Never nest pages. Never leave a page unclosed.
- Nothing between consecutive </div><div class="report-page"> except whitespace.
- Never split a table, chart, SVG, or callout across pages.
- Each page holds roughly 600–900 words of prose (less if it has visuals). Break at natural content boundaries.
- A chapter must have at least 2 pages.

OUTPUT FORMAT
- Root: <div class="report-chapter"> containing only <div class="report-page"> elements.
- Hierarchy: h2 (chapter title, once), h3 (subchapters), h4 (sub-sections inside subchapter).
- Inline CSS only — no <style>, <link>, <html>, <head>, <body>, <!DOCTYPE>.
- Preserve the same visual style (colors, fonts, spacing) from the original chapter HTML.
- For wide tables: wrap in <div style="width:100%; overflow-x:auto;">
- If you add any new visual (chart, table, KPI card), add 1–2 sentences explaining what it shows.

HARD RULES
1. Start with <div class="report-chapter">. End with </div>. No text before or after.
2. Only direct children of report-chapter are report-page divs.
3. No invented content (except in research mode with provided snippets).
4. Output the FULL chapter HTML. The old HTML is completely replaced by yours.
5. No markdown fences, no preamble, no commentary."""

    # ── Build TOC block ──────────────────────────────────────────────────
    toc = table_of_contents or {}
    toc_lines: List[str] = []
    
    if isinstance(toc, dict):
        for ch, subs in toc.items():
            is_current = (
                chapter_heading.strip() in ch.strip()
                or ch.strip() in chapter_heading.strip()
            )
            marker = "  >>> EDITING THIS CHAPTER" if is_current else ""
            toc_lines.append(f"  {ch}{marker}")
            for s in (subs or []):
                toc_lines.append(f"      {s}")
        toc_text = "\n".join(toc_lines).strip() or "(no table of contents available)"
    else:
        import re
        toc_text = re.sub(r"<[^>]+>", "", str(toc)).strip()
        toc_text = re.sub(r"\n\s*\n", "\n", toc_text)
        toc_text += f"\n\n  >>> CURRENTLY EDITING: {chapter_heading}"

    # ── Build additional research block (research mode only) ─────────────
    research_block = ""
    if mode == "research" and additional_research:
        research_block = f"""
ADDITIONAL RESEARCH SNIPPETS (use these to enrich the chapter):
{'─' * 60}
{additional_research}
{'─' * 60}
"""

    if design_instructions:
        design_block = f"""
DESIGN INSTRUCTIONS (apply this styling to your output):
{'─' * 60}
{design_instructions}
{'─' * 60}
"""
    else:
        design_block = ""

    human_prompt = f"""TABLE OF CONTENTS (your chapter is marked):
{toc_text}

{design_block}
CHAPTER BEING EDITED: "{chapter_heading}"

USER FEEDBACK (apply this — this is the primary instruction):
{feedback}

CURRENT CHAPTER HTML (rewrite this completely, applying the feedback):
{'═' * 60}
{old_html}
{'═' * 60}
{research_block}
TASK: Rewrite the chapter "{chapter_heading}" applying the user's feedback. Output the complete replacement HTML now."""

    return [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
