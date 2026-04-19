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
    sections_block = (
        "ALL RESEARCH SECTIONS SNAPSHOT (first ~20 lines each):\n" + "=" * 80 + "\n\n"
    )
    for idx, section in enumerate(sections):
        content = section.get("section_content", "") or ""
        section_id = section.get("section_id", f"sec-{idx + 1}")
        # Take only the first ~20 lines to control prompt size
        lines = content.splitlines()
        head = "\n".join(lines[:20])
        sections_block += (
            f"--- Section {idx + 1} [section_id: {section_id}] ---\n{head}\n\n"
        )
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

    system_prompt = """You produce one complete report chapter as a single HTML block. Output is inserted as-is. Your job: match report type, choose the best way to show this chapter and its subchapters (not always a table), keep layout inside bounds, and WRITE EXHAUSTIVELY IN-DEPTH. Do not summarize or gloss over details.

WARNING: A frequent failure mode is outputting a "high-level overview" instead of deep, detailed synthesis. You must provide extensive context, include every numerical metric and nuance from your source texts, and expand fully on every point instead of boiling them down.

HOW TO USE DESIGN INSTRUCTIONS — The design brief you receive has 8 numbered sections. Consult them as follows:
- Section 1 (COLOR SYSTEM): Use these exact hex values for ALL colors — backgrounds, text, borders, chart elements. No deviations.
- Section 2 (TYPOGRAPHY): Match font families, sizes (in rem), weights, and line-heights exactly.
- Section 3 (SPACING): Use the specified base spacing unit and vertical rhythm for all margins/padding.
- Section 4 (VISUAL MOOD): Let this guide your prose tone and aesthetic choices.
- Section 5 (REPORT INTENT & PRESENTATION): Understand what the user wants and how visuals serve that goal.
- Section 6 (VISUAL DECISION TREE): These IF/THEN rules take precedence over the general guidance below. When the design brief covers a specific content type, follow its rule. Use the general guidance below only when the design brief doesn't cover your specific case.
- Section 7 (SVG & CHARTS.CSS CONSTRUCTION): Follow these technical standards for ALL charts and diagrams — viewBox, fonts, strokes, accessibility.
- Section 8 (WHAT TO AVOID): Check your output against these anti-patterns before finalizing.

HOW TO DECIDE HOW TO SHOW THIS CHAPTER (in order)
1) Design instructions — They state report type and how data should be shown (prose-heavy vs tables vs charts vs lists vs Q&A, etc.). Treat them as the first authority. If the design brief includes a VISUAL DECISION TREE (Section 6), those IF/THEN rules take precedence over the general guidance below.
2) Report type — Use the REPORT TYPES reference below. Each type has a default look and typical section content; your section should feel like that type.
3) This chapter's content — Ask: Is this narrative, comparison, chronology, definitions, numbers, steps, or mixed? Then pick the best format:
   - Narrative / argument / story → prose (paragraphs, blockquotes). Do not force a table.
   - Comparison of a few items → prose or a compact list often clearer than a wide table.
   - Comparison of many items or repeated columns → table.
   - Trend over time / distribution → Charts.css or SVG. Not every number set needs a table.
   - Steps / procedure → numbered list or short paragraphs.
   - Definitions / terms → definition blocks or bold term + line, not necessarily a table.
   - Q&A / FAQ → question as heading, answer as paragraph; or <details> for reveal.
Do not default to a table. Match format to content and to what the design instructions say this report type uses. Use a mix of visuals (Charts.css, SVG, KPI cards, callouts, timelines) and prose when the content justifies it, instead of repeating similar large tables. For every important visual, briefly explain in the surrounding text what it shows, why it is there, and how it helps the reader understand the idea more easily.

Edge cases:
- If content is mixed (some numbers, mostly prose): Lead with prose, embed key metrics as inline callouts, use one chart only if 3+ comparable values exist.
- If sources contradict: Present both views in a comparison table or side-by-side prose sections. Do not pick a winner — present the evidence.
- If content is very short: Expand with deeper explanation, context, and implications. Do NOT pad with visuals. Every chapter must have at least 2 report-page containers.

SVG CONSTRUCTION STANDARDS
Every SVG chart or diagram you create MUST follow these rules:
- Required attributes: viewBox="0 0 [width] [height]" (e.g. viewBox="0 0 800 400"), xmlns="http://www.w3.org/2000/svg".
- Accessibility: Always include <title>Chart title</title> and <desc>Plain-language description of what the chart shows and its key takeaway</desc> as the first children of <svg>.
- Fonts: Use font-family matching the design instructions' body font. Sizes: axis labels 12px, chart titles 14px, data labels/annotations 11px.
- SVG font-family attribute: MUST use proper XML attribute syntax. Use font-family="EB Garamond, Georgia, serif" — a plain comma-separated list in the XML attribute. Do NOT wrap individual font names in quotes inside the attribute value. Do NOT use CSS syntax with semicolons. Example: font-family="EB Garamond, Georgia, serif". For font-size, use font-size="12px" or font-size="0.875rem" — quoted values, no semicolons.
- Stroke widths: 1.5px for grid lines, 2px for data lines, 2.5px for axes.
- Colors: ONLY use hex values from the design instructions' palette. No arbitrary colors.
- Wrapper: Always wrap SVG in <div style="width:100%; overflow-x:auto;"> to prevent horizontal overflow.
- Never use <foreignObject> — use <text> elements only for all labels and annotations.
- Keep SVG responsive: use width="100%" on the <svg> tag. Do NOT set height="auto" — it is not valid SVG. Either omit the height attribute (the viewBox aspect ratio handles scaling) or use height="100%".
- ALL <defs> blocks (markers, gradients, patterns) MUST appear BEFORE any elements that reference them via url(#id). SVG does not support forward references — if a marker is defined after the element that uses it, the marker will not render. Always place <defs> as the first child of <svg>, right after <title> and <desc>.
- ALL SVG elements MUST stay within the viewBox bounds. If viewBox="0 0 800 400", no element should have x < 0, x > 800, y < 0, or y > 400. Check all text positions, arrow endpoints, and shape coordinates before outputting. Elements outside viewBox will be clipped and invisible.
- NEVER use text-length — it is not a valid SVG attribute. For text width constraints, use font-size to control size, or split long text into multiple <text> elements with different y positions.
- For font-family in SVG text elements, use comma-separated font names WITHOUT wrapping the entire list in quotes: font-family="EB Garamond, Georgia, serif" (correct). NOT font-family="'EB Garamond', Georgia, serif" (wrong — nested quotes break in some browsers). NOT font-family="EB Garamond; Georgia; serif" (wrong — semicolons are CSS syntax, not XML).

Minimal SVG structure example:
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" width="100%">
  <title>Revenue Growth 2020–2025</title>
  <desc>Line chart showing annual revenue increasing from $2.1M in 2020 to $8.4M in 2025, with a notable acceleration after 2023.</desc>
  <!-- axes, grid lines, data paths, labels -->
</svg>

DONUT CHART TEMPLATE — Use this exact pattern for revenue composition, market share, etc:
<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" width="100%">
  <title>Chart title</title>
  <desc>Description of what the chart shows and key takeaway</desc>
  <defs>
    <marker id="ah" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#2D3748"/>
    </marker>
  </defs>
  <!-- Use stroke-dasharray on circles for donut slices -->
  <!-- Circumference = 2 * PI * r. For r=60, C=377. For r=80, C=503 -->
  <!-- Slice 1 (76%): dasharray="286 377" (76% of 377) -->
  <!-- Slice 2 (16%): dasharray="60 377" offset="-286" (starts after slice 1) -->
  <circle cx="200" cy="200" r="80" fill="none" stroke="#3182CE" stroke-width="40"
    stroke-dasharray="286 503" transform="rotate(-90 200 200)"/>
  <circle cx="200" cy="200" r="80" fill="none" stroke="#319795" stroke-width="40"
    stroke-dasharray="60 503" stroke-dashoffset="-286" transform="rotate(-90 200 200)"/>
  <circle cx="200" cy="200" r="60" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
  <!-- Labels positioned outside the donut -->
  <text x="310" y="195" font-family="Inter, sans-serif" font-size="14" font-weight="600" fill="#1A365D">Segment A</text>
  <text x="310" y="215" font-family="Inter, sans-serif" font-size="12" fill="#3182CE">76%</text>
  <text x="50" y="195" font-family="Inter, sans-serif" font-size="14" font-weight="600" fill="#1A365D">Segment B</text>
  <text x="50" y="215" font-family="Inter, sans-serif" font-size="12" fill="#319795">16%</text>
</svg>
KEY RULE: Use stroke-dasharray on <circle> elements for donut slices, NOT <path> with arc commands. The formula: dasharray = "percentage * circumference remaining_circumference". Circumference = 2 * PI * radius. Rotate -90 degrees so the first slice starts at the top.

CHARTS.CSS USAGE
When using Charts.css for data visualization:
- Required class structure on <table>: class="charts-css [bar|column|line|area|stacked|percentage] show-labels show-data show-headings"
- Always include a <caption> element inside the <table> for the chart title.
- Always wrap the entire <table> in <div style="width:100%; overflow-x:auto;">.
- Data values go in <td> elements with the CSS custom property: style="--data: [numeric-value]"
- Charts.css --data values MUST be normalized decimal fractions (0.0 to 1.0), representing each bar's height relative to the maximum value in the dataset. Divide each raw value by the maximum value. Example: If quarterly revenues are [$21B, $22B, $23B, $28B], the max is $28B. Normalized data values: [0.75, 0.79, 0.82, 1.0]. NEVER use raw numbers (like --data: 21.3), percentages (like --data: 75%), or calc() expressions (like --data: calc(21.3/28.1)). Always compute the decimal fraction yourself.
- Color sequence: apply the design instructions' chart color palette in order across data series.
- When NOT to use Charts.css: fewer than 3 data points, purely qualitative data with no numbers, or when prose communicates the point more clearly.
- For multi-series Charts.css tables (multiple <tr> rows representing different data series), you MUST add row labels. Use the first <td> of each row as a label, or add a dedicated label column. The reader must be able to identify which row represents which data series WITHOUT reading surrounding prose.
- Example: For a CSR vs RSC comparison table, the first column should label each row: "CSR (Next.js Pages)" and "RSC (Next.js App)".
- Charts.css classes (charts-css, show-labels, show-data, show-headings) require the Charts.css stylesheet to be loaded globally by the document viewer. Your HTML should include these classes on <table> elements — the viewer handles the CSS. If a Charts.css chart does not render as a visual chart, the table will still display as a styled HTML table with the data visible — this is the fallback behavior.

BAR / COLUMN CHART CHECKLIST (follow every time you add one)
1. Wrap with <div style="width:100%; max-width:100%; overflow-x:auto; margin:1.25rem 0; box-sizing:border-box;">.
2. <table class="charts-css bar|column show-labels show-data show-heading data-spacing-10" style="width:100%; max-width:100%; height:320px; font-family:[body font];">.
3. <caption caption-side: top> using the design instructions' heading font + heading hex for a short descriptive title.
4. Every <th> carries explicit font-family, font-size, font-weight, color, background, padding — no defaults.
5. <td> uses `--size:<decimal 0.0–1.0>` (NOT raw numbers, NOT percentages, NOT calc()) + `background:<hex from palette>`. Pre-normalize the decimal against the dataset max.
6. Single series = one color. Don't rainbow single-series bars. Multi-series = one color per series, in palette order (primary → secondary → tertiary).
7. At least one intro sentence before the chart, and 1–3 interpretation sentences after.

PIE / DONUT CHART — ALWAYS INLINE SVG
Charts.css pie is unreliable. Build every pie or donut as inline SVG using the stroke-dasharray-on-circle pattern:
1. Wrap with <div style="width:100%; max-width:100%; overflow-x:auto; margin:1.25rem 0; display:flex; justify-content:center; box-sizing:border-box;">.
2. <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" width="100%" style="max-width:520px; font-family:[body font];"> with <title> and <desc>.
3. For radius r=70 the circumference C ≈ 440. Each slice: stroke-dasharray="(p*C) C", stroke-dashoffset = -(cumulative previous slice lengths). First slice offset = 0.
4. transform="rotate(-90 cx cy)" on every slice circle so the first slice starts at 12 o'clock.
5. Use stroke-width 28–38; add a white inner <circle r="50" fill="#FFFFFF"/> for a donut (omit for a full pie).
6. Order colors largest → smallest using the palette (primary accent = dominant slice). No two adjacent slices share the same hue.
7. Slice percentages MUST sum to 1.00 (± 0.01). Aggregate anything < 3% into an "Other" slice.
8. Always include a legend (<rect> swatches + <text> labels) in the body font. Readers cannot decode slice colors without it.
9. Max 6 slices. Beyond that, switch to charts-css percentage-column or a stacked bar so labels stay readable.

WHEN DATA IS QUALITATIVE (NO NUMBERS)
Do NOT force Charts.css, data tables, or numeric charts when the content has no numbers. Instead:
- Use prose with strong paragraph structure and blockquotes for expert opinions.
- Use comparison layouts (side-by-side prose sections) for contrasting viewpoints.
- Use definition blocks (bold term + explanation) for concept-heavy chapters.
- Use timeline CSS for chronological or process-oriented content.
- Use SVG for conceptual diagrams: flowcharts, relationship maps, hierarchies, Venn-style overlaps.
- Use <details> elements for expandable deep-dive content, alternative viewpoints, or supplementary evidence.
- The goal is clarity — if a well-written paragraph communicates better than a visual, use the paragraph.

PAGE STRUCTURE — PDF-LIKE PAGES (CRITICAL — FOLLOW EXACTLY)
Your chapter will be rendered inside a document viewer that displays content as stacked pages (like a PDF reader). You MUST structure your HTML so that EVERY piece of content is wrapped inside a <div class="report-page"> container. The viewer styles each report-page as a white A4-sized sheet with shadow on a gray background. You do NOT add any inline styles to report-page divs — just use <div class="report-page"> exactly.

ABSOLUTE RULES FOR PAGES:
- EVERY heading, paragraph, table, chart, list, callout, and visual MUST be inside a <div class="report-page">. Content outside a report-page will break the layout.
- Each page must be properly opened and closed: <div class="report-page">...content...</div>. Never nest one report-page inside another. Never leave a report-page unclosed.
- There must be NOTHING between two consecutive </div><div class="report-page"> boundaries except whitespace. No stray tags, no orphaned paragraphs.

How to paginate:
- Estimate roughly 600–900 words of prose per page (at 15px body font, 1.7 line-height, with ~3rem padding). A page containing a table or chart holds less text — budget accordingly.
- Start a new <div class="report-page"> at natural content boundaries: between subchapters, between major conceptual shifts within a subchapter, or before/after a large visual (table, chart, diagram).
- The FIRST page of the chapter must open with the h2 chapter title, then begin the first subchapter (h3) and its opening content.
- If a subchapter is short, it can share a page with the previous subchapter's tail or the next subchapter's start. Pages do not need to align 1:1 with subchapters — use your judgment for what feels like a natural, readable page.
- NEVER split a table, chart, SVG, or callout box across two pages. Keep each visual whole on one page. If a visual is large, give it its own page.
- NEVER leave a page nearly empty just to start a subchapter on a fresh page. Fill pages with content — a page should feel substantial, not sparse.
- A single subchapter can span multiple pages if the content is long — just break at a paragraph boundary.
- Every chapter MUST have at least 2 pages. If your content is very short, you are not writing enough — expand with deeper explanation.

EXAMPLE STRUCTURE (follow this pattern exactly):
<div class="report-chapter">
  <div class="report-page">
    <h2 style="...">3. Market Analysis</h2>
    <h3 style="...">3.1 Current Landscape</h3>
    <p style="...">Opening explanation of the market context...</p>
    <p style="...">Detailed analysis with specific data points and evidence...</p>
    <div style="width:100%; overflow-x:auto;">
      <!-- table or chart here -->
    </div>
    <p style="...">Explanation of what the above visual shows and why it matters...</p>
  </div>
  <div class="report-page">
    <h3 style="...">3.2 Competitive Dynamics</h3>
    <p style="...">Detailed comparison of key players in the space...</p>
    <p style="...">Further analysis building on the data...</p>
    <p style="...">Synthesis and implications for the market...</p>
  </div>
  <div class="report-page">
    <h3 style="...">3.3 Future Projections</h3>
    <p style="...">Forward-looking analysis based on the trends identified...</p>
    <p style="...">Final thoughts for this chapter...</p>
  </div>
</div>

Notice: every element is inside a report-page. Nothing floats between pages. Each page is closed before the next opens. The chapter div only contains report-page divs.

REPORT TYPES — WHAT EACH EXPECTS (use to recognize and match your report)
- General: Clean, balanced; prose + tables + charts as needed. Sections: overview, background, analysis, conclusion. Primary visuals: mixed charts, summary tables. 50% prose, 50% visuals. Key containers: analysis blocks, comparison tables, trend charts.
- Math: White, LaTeX-like; definitions in boxes, theorems, proofs, worked examples, graphs. Sections: definitions, theorems/proofs, examples, key formulas. Primary visuals: equation blocks, proof boxes, function graphs. 60% prose, 40% visuals. Key containers: definition boxes, theorem environments, worked examples.
- Philosophy: Warm parchment, prose-first; blockquotes, thought experiments, dialectical structure. Sections: question, thinkers, arguments, objections, relevance. Primary visuals: blockquotes, dialectical tables. 80% prose, 20% visuals. Key containers: argument blocks, objection/response pairs, thinker profiles.
- History: Archival cream, chronology; timelines, dates, primary quotes, maps. Sections: context, chronological narrative, causes, legacy. Primary visuals: timelines, quote callouts, period maps. 55% prose, 45% visuals. Key containers: timeline elements, primary-source quotes, cause-effect tables.
- Literature: Narrow column, typography-first; excerpts, close reading, themes. Sections: work/author, synopsis, textual analysis, themes, legacy. Primary visuals: text excerpts, thematic callouts. 70% prose, 30% visuals. Key containers: excerpt blocks, close-reading annotations, theme summaries.
- Physics: Diagrams + equations; force diagrams, equations, examples, units. Sections: phenomenon, laws/equations, diagrams, examples, experiment. Primary visuals: SVG diagrams, equation blocks, unit tables. 45% prose, 55% visuals. Key containers: diagram callouts, equation environments, experiment summaries.
- Finance: Numbers-first; KPIs, charts, dense tables, green/red. Sections: thesis, metrics, analysis, valuation, risk. Primary visuals: KPI cards, line charts, dense tables. 40% prose, 60% visuals. Key containers: metric cards, scenario analysis blocks, peer comparison tables.
- Startup/Pitch: Bold metrics, growth charts, minimal prose; pitch-deck feel. Sections: problem, solution, traction, ask. Primary visuals: KPI cards, bar charts, growth curves. 30% prose, 70% visuals. Key containers: metric callouts, traction timelines, market-size charts.
- Scientific: Methods, results, figures/tables, captions; evidence-led. Sections: intro, methods, results, discussion. Primary visuals: data tables, result charts, method diagrams. 45% prose, 55% visuals. Key containers: result figures with captions, methods tables, discussion blocks.
- News/Journalism: Lede first, inverted pyramid, quotes, datelines. Sections: lede, facts, voices, timeline, impact. Primary visuals: quote callouts, timelines, fact tables. 60% prose, 40% visuals. Key containers: lede paragraph, voice/quote blocks, impact timelines.
- Coding: Code blocks first-class; API tables, examples, architecture. Sections: what/why, setup, API/concepts, examples, best practices. Primary visuals: code blocks, API tables, architecture diagrams. 40% prose, 60% visuals. Key containers: code examples, parameter tables, architecture SVGs.
- Practice/Learning: Cheat sheets, problems, hidden solutions, tips. Sections: concepts, reference table, problems, solutions (e.g. <details>), mistakes/tips. Primary visuals: reference tables, collapsible solutions, tip callouts. 50% prose, 50% visuals. Key containers: <details> solution blocks, cheat-sheet tables, tip/warning callouts.
- Minimalist: Lots of whitespace; typography as data, few elements. Sections: one takeaway, key numbers, brief analysis. Primary visuals: typographic numbers, sparse charts. 60% prose, 40% visuals. Key containers: single-stat callouts, minimal tables, short analysis blocks.

LAYOUT — NEVER MESS UP
- Root: <div class="report-chapter"> containing one or more <div class="report-page"> containers. All content must be inside a report-page. Nothing should exist directly inside report-chapter outside of a report-page.
- Inside each page: single column (block stack). No multi-column or grid unless design instructions explicitly ask for it. Everything stacks vertically.
- Every inner block (paragraph, heading, table wrapper, chart wrapper, list, callout): use width 100% or max-width 100%, box-sizing border-box. No fixed pixel width. No position absolute/fixed.
- Tables: wrap in <div style="width:100%; overflow-x:auto;"> so wide tables scroll instead of bursting out.
- Charts (Charts.css or SVG): same — wrapper width 100%, overflow-x auto, margin 1.25rem 0, box-sizing border-box. The chart itself (table or svg) MUST declare font-family inline using the design instructions' body font. SVG pies/donuts should additionally cap at max-width:520px and be centered via display:flex; justify-content:center; on the wrapper. Bar/column charts should have explicit height between 280–400px (never > 420px). Never place a chart immediately after a heading — always write at least one introductory sentence first. Always follow a chart with a 1–3 sentence interpretation. Max one chart per prose-heavy page, two per data-heavy page. Never place a chart in the last 200px of a page — move it to the top of the next report-page instead.
- Spacing: use margins/padding from design instructions consistently. Gaps between elements so nothing overlaps or feels cramped.
- Fonts and colors: only from design instructions. Consistent across every heading, paragraph, table, and chart.

TYPOGRAPHY & UI POLISH — MAKE THE PAGE FEEL LIKE A REAL DOCUMENT
The document viewer renders pages as A4 sheets on a soft gray background. The reader should feel they are looking at a clean, professionally typeset document. Apply these rules consistently:
- Body paragraphs: font-size from design instructions (usually ~1rem = 16px), line-height 1.7–1.8, margin: 0 0 1rem 0, text-align: left (NEVER justify — uneven word spacing looks broken at this column width), color from design instructions' body text hex. Do not let paragraphs run wider than the page padding allows; the report-page already caps the column, so no extra max-width on paragraphs.
- Headings h2: the chapter title, placed once at the top of the first page. Use design instructions' heading font and heading hex, font-size ~1.75–2rem, font-weight 700, letter-spacing -0.01em, margin: 0 0 1.25rem 0, padding-bottom 0.5rem, border-bottom 2px solid [design instructions' accent hex] for a subtle separator. Never wrap h2 in its own styled container box.
- Headings h3: subchapter titles. font-weight 600, font-size ~1.25–1.4rem, margin: 2rem 0 0.75rem 0 (more breathing room above, tight below so it reads as anchored to the following paragraph), heading-color hex, letter-spacing -0.005em.
- Headings h4: inner sub-section labels. font-weight 600, font-size ~1.05rem, margin: 1.25rem 0 0.5rem 0. Use sparingly — too many h4s fragment the page.
- Lists: margin: 0.75rem 0 1rem 1.25rem, line-height 1.7, padding-left 0.25rem. Use <ul> for unordered and <ol> for ordered. Each <li> gets padding-left 0.25rem and margin-bottom 0.35rem so items don't cram together.
- Blockquotes: margin: 1.25rem 0, padding: 0.75rem 1.25rem, border-left 3px solid [accent hex], background [insight box bg hex from design instructions], color [body hex], font-style italic only if the design instructions call for it.
- Tables: width 100%, border-collapse collapse, font-size 0.9375rem, line-height 1.55. <th> uses the design instructions' table header bg and heading font, 600 weight, padding 0.6rem 0.75rem. <td> uses body font, padding 0.55rem 0.75rem, border-bottom 1px solid [border hex from design instructions]. Alternating row backgrounds if the design instructions specify them.
- Anchors: color [accent hex], text-decoration: underline, text-underline-offset: 2px, text-decoration-thickness: 1px. On hover (implicitly via the global stylesheet) they darken — do not set hover styles inline since inline CSS can't express :hover.
- Avoid font-family drift: every heading uses the design instructions' heading font; every paragraph, list, table cell, and chart label uses the body font. Never mix in Times New Roman or Arial — declare the font-family explicitly on every styled block so inheritance doesn't break.
- Avoid visual noise: no drop shadows on prose blocks, no gradients on text, no letter-spacing > 0.02em on body text, no decorative dividers every few paragraphs. A clean document is one where the reader never notices the design — they only notice the content.
- Vertical rhythm: leave ~1rem between paragraphs, ~1.5–2rem between a paragraph and a following heading, ~1.25rem around every chart/table/callout wrapper. Pages should breathe — never let two visuals stack with less than 1rem gap.
- Callout / insight boxes: padding 1rem 1.25rem, border-radius 4–6px, background [insight bg hex], border-left 3px solid [accent hex]. Max one callout per page, two per chapter.

UNDERSTANDING THE CORRECT CHAPTER
- You are writing one specific place in the report: the CHAPTER marked "YOU ARE HERE" in the table of contents. That is the only part you produce.
- Inside this chapter, you are responsible for both the top-level chapter title and all of its subchapters. The chapter title should give a crisp, high-level overview; each subchapter should then go in-depth on its specific angle so that, together, the chapter feels complete.
- Understand what value this chapter brings: it exists to answer a part of the user's request and the planner's plan. Your output must fully deliver that — the reader who finishes this chapter should feel that this piece of the report is complete and genuinely understandable.
- Use the research sections provided for this chapter only. They are the evidence for this chapter. Your job is to turn them into one coherent, complete chapter (with internal subheadings) that fulfills the exact chapter heading and its role in the TOC. Nothing essential from these sections should be missing; no filler that doesn't serve the chapter's purpose.

THIS CHAPTER ONLY
- Write only this chapter and its subchapters. TOC shows opening / middle / closing. Focus this chapter's scope; don't repeat earlier or preempt later. Keep flow.

CONTENT, EXPLANATION, AND KNOWLEDGE
- DO NOT SUMMARIZE AND DO NOT CONDENSE. You must go in-depth. Extract and weave EVERY SINGLE factual detail, metric, nuance, date, and argument from the research sections into your chapter. The output must be exhaustive.
- If the source research section is extensive, your generated chapter content must be proportionately long and detailed. A high-quality report explores details heavily.
- When research contains extensive numerical data, present the complete dataset in a table or chart, and use prose to interpret the key patterns, trends, and implications. Do not repeat every number from a table in the surrounding prose — that creates unreadable data dumps. Instead, let the visual carry the raw numbers, and use prose to explain what the numbers mean, why they matter, and what patterns they reveal.
- Synthesize in your own voice; no paste-by-blocks. No invented content. No section_id markers, no [REF] tags, no [SOURCE] tags — use proper <a href='URL'>Source Name</a> inline citations instead. Explain clearly; best format for clarity (prose, list, chart, or table as judged above). No half-explained ideas; extremely dense and detailed.
- Content quality matters MORE than visuals. Never sacrifice deep narrative, step-by-step reasoning, or comprehensive explanations just to force a visual or a table. Whenever you introduce a chart, table, diagram, or other visual, add a highly detailed plain-language breakdown before or after it.

CITATIONS — REQUIRED
- Every factual claim from the research sections MUST be cited with an inline link.
- Use the format: <a href="URL">Source Name</a> woven naturally into prose.
- Examples: "according to <a href='https://quantum-journal.org/papers/q-2018-08-06-79/'>Preskill (2018)</a>" or "(Source: <a href='https://react.dev/reference/rsc/server-components'>React Documentation</a>)."
- For numbered citations: "<sup><a href='https://www.ipcc.ch/report/ar6/'>IPCC AR6, 2023</a></sup>"
- For inline source names: "(Source: <a href='https://react.dev/reference/rsc/server-components'>React Documentation</a>)"
- For data points: "(Source: <a href='URL'>Bureau of Labor Statistics</a>, March 2023)."
- For documents: "(Full text: <a href='URL'>link</a>)."
- EVERY chapter must have at least 3 inline citation links.
- Citations are part of the prose — weave them in naturally, do not group them at the end.
- If the research sections contain URLs, you MUST use them as <a href> links.

CITATION STYLING & POLISH — HOW CITATIONS SHOULD LOOK
- Style every inline <a> consistently: color = design instructions' accent hex, text-decoration: underline, text-underline-offset: 2px, text-decoration-thickness: 1px, font-weight: 500 (slightly heavier than body text so the reader's eye catches it without it shouting). Example: <a href="URL" style="color:[accent hex]; text-decoration:underline; text-underline-offset:2px; text-decoration-thickness:1px; font-weight:500;">Source Name</a>.
- For superscript numbered citations (<sup>), use font-size: 0.75em, line-height: 1, margin-left: 1px so they sit tightly against the word they follow without inflating the line height.
- For parenthetical "(Source: …)" citations placed at the end of a sentence, keep the parentheses and the word "Source:" in body color (not accent color) — only the linked source name gets the accent color. This keeps the prose calm.
- Never bold an entire citation phrase; only the linked word(s) carry emphasis via the link style.
- Citations must NEVER break line spacing — keep line-height at the paragraph's 1.7–1.8 value. Do not wrap citations in <span> blocks with their own line-height.
- If a single sentence needs multiple citations, place them after distinct claims, not stacked at the sentence end. "X reported Y (<a>Source A</a>), while Z found the opposite (<a>Source B</a>)." is correct; "X reported Y and Z found the opposite (<a>Source A</a>)(<a>Source B</a>)." is wrong.
- Prefer inline source names over raw URLs. Never output a bare URL as the visible link text (e.g. "https://…"). Always display a human-readable label.

STRUCTURE RULES
- Hierarchy: h2 (chapter title once at the top of the first page), h3 (subchapters that align with the table of contents for this chapter), h4 (sub-sections inside a subchapter). Short labels only. Inline CSS only; no <style>, <link>, <html>, <head>, <body>, <!DOCTYPE>. Valid HTML; same element type → same styling.

COMMON FAILURE MODES — AVOID THESE
- SVG overflowing the page: always wrap in <div style="width:100%; overflow-x:auto;">.
- Charts without captions or axis labels: every chart must have a <caption> (Charts.css) or <title>/<desc> (SVG) and clearly labeled axes.
- Tables without header rows: every <table> must have a <thead> with <th> elements.
- Mixing font families: use only the fonts specified in the design instructions.
- Using colors not in the palette: every hex value must come from the design instructions.
- Leaving report-page containers unclosed: every <div class="report-page"> must have a matching </div>.
- Creating pages with less than ~200 words of content: every page must feel substantial. If a page is sparse, you are not writing enough.
- Repeating the same visual pattern 3+ times in a chapter: vary the presentation — alternate prose → chart → table → callout → prose.
- Presenting data without explaining what it means: every table, chart, or figure must be accompanied by prose that interprets the data and draws out its significance.

HARD RULES
1. Start with <div class="report-chapter">. End with </div>. No text before or after the HTML.
2. The ONLY direct children of <div class="report-chapter"> must be <div class="report-page"> elements. Every heading, paragraph, table, chart, list — everything — must be inside a report-page. Zero exceptions.
3. Each report-page must be properly opened and closed. Never nest pages inside pages. Never leave content orphaned between pages.
4. Colors/fonts from design instructions only.
5. No invented content. No internal IDs in output.
6. One full chapter (with its internal subchapters paginated into report-page containers); clear, information-dense, and easy to understand.
7. Double-check your output: scan from top to bottom and confirm that (a) every element lives inside a report-page, (b) no report-page is left unclosed, (c) there are at least 2 report-page containers in your chapter."""

    # ── Build TOC block ──────────────────────────────────────────────────────
    toc_lines = ["FULL REPORT TABLE OF CONTENTS:"]
    chapter_list = list(table_of_contents.keys())
    for i, (main_chapter, subchapters) in enumerate(table_of_contents.items()):
        position_tag = ""
        if i == 0:
            position_tag = "  ← FIRST CHAPTER"
        elif i == len(chapter_list) - 1:
            position_tag = "  ← FINAL CHAPTER"
        is_current = (
            chapter_heading.strip() in main_chapter.strip()
            or main_chapter.strip() in chapter_heading.strip()
        )
        marker = "  >>>  YOU ARE HERE" if is_current else ""
        toc_lines.append(f"  {main_chapter}{position_tag}{marker}")
        for sub in subchapters:
            sub_is_current = (
                chapter_heading.strip() in sub.strip()
                or sub.strip() in chapter_heading.strip()
            )
            sub_marker = "  >>>  YOU ARE HERE" if sub_is_current else ""
            toc_lines.append(f"      {sub}{sub_marker}")
    toc_formatted = "\n".join(toc_lines)

    # ── Build sections block ─────────────────────────────────────────────────
    sections_formatted = ""
    for idx, section in enumerate(sections_for_chapter):
        content = section.get("section_content", "")
        sections_formatted += f"\n{'─' * 60}\nRESEARCH SECTION {idx + 1} OF {len(sections_for_chapter)}\n{'─' * 60}\n{content}\n"

    # ── User query and planner context (for section focus) ───────────────────
    user_planner_block = ""
    if user_query or (planner_queries and len(planner_queries) > 0):
        user_planner_block = "\n"
        if user_query:
            user_planner_block += (
                f"USER QUERY (what the report is for):\n{user_query}\n\n"
            )
        if planner_queries:
            planner_lines = (
                "PLANNER QUERIES (what each part of the report is meant to cover):\n"
            )
            for pq in planner_queries:
                planner_lines += f"  {pq.get('query_num', '')}. {pq.get('query', '')}\n"
            user_planner_block += planner_lines
        user_planner_block += "\nUse these to understand user intent and which part of the report you are writing. Your chapter must serve the query and the planner’s goal for this section.\n\n"

    default_design = "Clean professional: navy headings #1a365d, body #2d3748, bg white, accent #2c5282. Inline styles only."
    human_prompt = f"""DESIGN INSTRUCTIONS (report type + colors, fonts, layout — use everywhere; sections must fit cleanly inside the document viewer width without overflowing):
{design_instructions.strip() if design_instructions else default_design}
{user_planner_block}
TABLE OF CONTENTS (you are writing the section marked YOU ARE HERE):
{toc_formatted}

SECTION FOCUS — UNDERSTAND AND FULFILL THIS CHAPTER COMPLETELY
- You are writing exactly one chapter: "{chapter_heading}". It is the only place in the TOC marked "YOU ARE HERE". All other chapters are written separately; your output is only this one.
- Understand what value this section brings: it answers a specific part of the user’s request and the planner’s plan. Your chapter must feel complete and genuine — a reader who finishes it should have gotten the full story for this part of the report.
- The research sections below are the only source for this chapter. They were gathered to support this exact chapter. Your job: turn them into one coherent chapter that (1) fully fulfills the chapter heading and its role in the TOC, (2) leaves no important information from these sections out, (3) does not add filler or repeat what belongs in other chapters. If the sections contain it, it should appear in your chapter in the best form (prose, list, table, or chart). Perfect output = this chapter completely delivered using these sections.

RESEARCH SECTIONS FOR THIS CHAPTER ({len(sections_for_chapter)}):
{sections_formatted}

TASK: Write only this chapter: "{chapter_heading}"
- Decide how to show it: (1) design instructions say what report type and formats to use, (2) match that report type from the reference, (3) for this chapter’s content pick the best format — prose, list, chart, or table. Do not default to a table.
- One outer <div class="report-chapter"> containing <div class="report-page"> containers. Each page holds roughly one A4-page worth of content (~600-900 words of prose, less if it has visuals). Break pages at natural points between or within subchapters.
- DO NOT SUMMARIZE. The user requires exhaustive, deeply detailed content reflecting all the research. Preserve absolutely all information; go deep into nuances. No preamble or text after the closing </div>."""

    return [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]


def get_available_design_skills() -> Dict[str, str]:
    """
    Reads all markdown files in the design_skills directory.

    Returns:
        Dict mapping filename (e.g. 'academic.md') to its contents.
    """
    skills_dir = os.path.join(os.path.dirname(__file__), "design_skills")
    skills = {}

    if not os.path.exists(skills_dir):
        return skills

    for filename in os.listdir(skills_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(skills_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
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
    available_skills: Dict[str, str],
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
        identity_match = re.search(
            r"## Identity & Scope\n(.*?)(?=\n\n##)", content, re.DOTALL
        )
        structure_match = re.search(
            r"## Content Structure & Narrative Flow\n(.*?)(?=\n\n##)",
            content,
            re.DOTALL,
        )
        identity = (
            identity_match.group(1).strip()
            if identity_match
            else "General report; no single domain."
        )
        structure_blob = structure_match.group(1).strip() if structure_match else ""
        structure_first = (
            structure_blob.split("\n")[0].strip()
            if structure_blob
            else "Standard sections."
        )
        skills_list += (
            f"--- {filename} ---\n{identity}\nStructure: {structure_first}\n\n"
        )

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
    selected_skill_rules: str,
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

Use the skill to:
- Anchor the report's visual feel (domain-appropriate typography, color temperature, density).
- Identify which VISUAL FORMS are primary for this report type (e.g. charts for finance, diagrams for physics, quotations for philosophy).
- Suggest domain-typical layouts and emphasis.

You are allowed to:
- Refine colors into a specific, coherent palette that best fits this particular report and user query, as long as it respects the skill's color philosophy.
- Prioritize a subset of visual patterns for this report (e.g. favor Charts.css bar/line charts + KPI cards, but rarely use large dense tables).
- Introduce additional, reasonable HTML structures (timelines, callouts, two-column comparisons) when they clearly align with the skill's intent.

Always favor designs that make the content easiest to understand, not just the most decorative.

SKILL REFERENCE:
{selected_skill_rules}

=====================================================================
WORK FLOW (follow in order — each step informs the next)
=====================================================================

PHASE 1 — ANALYZE REPORT TYPE
From user query, planner queries, and TOC: What does the user want? Single domain (math, finance, philosophy, history, etc.) or hybrid? Is it a cheat sheet, Q&A, narrative essay, data-heavy analysis, pitch deck, reference, comparison? Infer the report's primary purpose and audience. (Do not output this analysis — use it to drive all decisions below.)

PHASE 2 — VISUAL FORMAT DECISIONS
Decide the report's visual density and primary formats:
- Is this report prose-heavy (70%+ text, visuals as supporting evidence), visual-heavy (50%+ charts/tables/diagrams, prose as annotation), or balanced?
- Which Charts.css chart types does this report need? (bar, column, line, stacked, percentage, grouped)
- Which SVG diagrams does this report need? (flowcharts, architecture diagrams, timelines, concept maps, force diagrams, etc.)
- What is the emotional tone? (clinical, warm, academic, editorial, minimal)
- What is the data presentation strategy? (tables for dense comparisons, charts for trends, KPI cards for key metrics, inline numbers for light data)

PHASE 3 — SVG & CHARTS.CSS PLANNING
For each chart/diagram type identified in Phase 2, specify:
- Which Charts.css chart type and which modifier classes (show-labels, show-data, show-headings, show-primary, data-after) apply.
- Which SVG diagrams are needed, what they depict, and their rough dimensions.
- When NOT to use Charts.css (e.g. single data point → KPI card, qualitative comparison → prose, 2-item comparison → inline text).
- Color sequence for multi-series charts (ordered list of hex values from the palette).
- Target bar/column chart height (280–400px, never over 420px) and target pie/donut max-width (~520px, centered) — so every chart fits inside the ~688px usable column of a `.report-page` without overflow.
- Which semantic colors (positive/negative/neutral) apply when the data carries polarity, and which single "primary accent" to use for single-series charts so the chapter writer doesn't rainbow-color a single series.

PHASE 4 — TYPOGRAPHY & COLOR (EXACT VALUES ONLY)
Use the skill's Typography & Color section as foundation. Output exact values:
- Fonts: heading + body (+ monospace if needed). Google Fonts or system stacks.
- Type scale: h2, h3, h4, body, caption — ALL in rem values.
- Line-height and font-weight for each level.
- Palette: bg, body text, headings, 2-3 accents, semantic (pos/neg if relevant), chart sequence (5-6 hex values).
- Component surfaces: table header bg, row alt bg, blockquote bg/border, insight box bg/border, code block bg/border — ALL hex.
All colors must be consistent throughout. One palette — no ad-hoc additions.

PHASE 5 — VISUAL DECISION TREE
Define explicit IF/THEN rules so the chapter writer knows exactly which format to pick for any content:
- IF content is [type] THEN use [format] because [reason]
- IF comparing [N] items on [M] attributes THEN use [table/chart/prose]
- IF showing trend over time THEN use [specific chart type]
- IF explaining a concept or definition THEN use [prose/callout/details]
- IF presenting a single key metric THEN use [KPI card/inline bold]
- IF the content is [domain-specific pattern] THEN use [specific visual]
Include at least 5 IF/THEN rules tailored to this report's content types.

PHASE 6 — PAGE & LAYOUT GUIDANCE
- Max content width: specify in rem (e.g. 72rem for prose, 90rem for data-dense).
- Vertical rhythm: base spacing unit in rem (e.g. 0.5rem), and how it scales (margins between paragraphs, between subchapters, before/after visuals).
- Pagination strategy: roughly how much content per page (e.g. "prose-dense pages: 600-800 words; visual-heavy pages: 1 large chart + 200 words explanation").
- Where to break pages: between subchapters, before large visuals, at conceptual shifts.
- NEVER split a table, chart, SVG, or callout across pages.

PHASE 7 — SVG & CHARTS.CSS CONSTRUCTION BRIEF
Provide specific technical instructions the chapter writer will follow:

SVG Construction:
- Standard viewBox dimensions for this report type (e.g. viewBox="0 0 800 400" for wide charts, viewBox="0 0 400 400" for square diagrams).
- Font family and sizes for SVG text elements (must match the typography scale, in rem or px equivalent).
- Stroke widths: thin lines (1px), medium lines (2px), thick lines (3px) — when to use each.
- Color application rules: use ONLY the palette defined above. No arbitrary colors.
- Accessibility: every SVG must include <title> (short label) and <desc> (1-2 sentence explanation).
- Domain-specific SVG patterns from the skill (e.g. if physics: force arrows with labeled vectors; if history: timeline with era markers).

Charts.css Construction:
- Required base classes: always include which of show-labels, show-data, show-headings.
- Color sequence: ordered list of hex values for multi-series charts (first series = primary accent, etc.).
- When to add data-after class, when to add show-primary.
- When NOT to use Charts.css (single values, qualitative data, fewer than 3 data points).

PHASE 7B — CHART ENCAPSULATION & CONCRETE CODE EXAMPLES (MANDATORY)
The chapter writer must be able to drop bar/column charts and pie/donut charts into a page without them overflowing the ~688px usable column of a `.report-page` (the viewer caps `.report-page` at 800px with 3.5rem padding). Your design brief MUST include small, concrete, copy-pasteable code examples for (a) a Charts.css bar or column chart and (b) an inline-SVG donut/pie chart, both using the exact palette hex values, fonts, and heading color you defined above. The examples are the chapter writer's reference — they will adapt the examples to real data.

Requirements for the code examples you embed in the brief:
- Every chart must be wrapped in `<div style="width:100%; max-width:100%; overflow-x:auto; margin:1.25rem 0; box-sizing:border-box;">` so nothing escapes the page column.
- The `<table>` (Charts.css) or `<svg>` (pie/donut) must declare `width:100%` with `max-width:100%` (SVG may additionally cap at `max-width: 520px` and center via flex).
- The chart must declare `font-family` inline using the body font you specified, and captions must use the heading font you specified — never rely on browser defaults.
- For Charts.css: `--size` MUST be a decimal fraction (0.0–1.0), normalized from real data; NEVER a raw number, percentage, or calc() expression. Multi-series charts must include a first-column `<th scope="row">` label for each row.
- For SVG donut/pie: use the `stroke-dasharray` on `<circle>` pattern (radius around 60–70, stroke-width 28–38), rotated -90° so the first slice starts at 12 o'clock, with an explicit legend and `<title>`+`<desc>` for accessibility. Slices must sum to 100%.
- Include explicit hex values from the palette (series 1 = primary accent, series 2 = secondary, series 3 = tertiary) — NO placeholders like "[color]" — so the chapter writer sees real colors.
- Cap bar/column chart heights at 280–400px. Never taller than 420px. Leave ≥ 1rem vertical margin above and below every chart.
- Add rules about how to pick colors for data: one color for a single-series chart; primary accent for the dominant/highlighted value and a muted neutral for the rest when highlighting one item; the skill's semantic green/red (if defined) for positive/negative comparisons; largest-to-smallest color order for pie slices; no two adjacent pie slices sharing the same hue.
- Add rules about where to place charts inside a page: never immediately after an h2/h3 heading (put an introductory sentence first); never in the final 200px of a page (move to the top of the next `.report-page`); always followed by a 1–3 sentence interpretation; max one chart per prose-heavy page, two per data-heavy page, never three.
- Add anti-patterns that often break the layout: fixed pixel widths > 688px, `--size` outside [0,1], `calc()` inside `--size`, rainbow single-series bars, donuts without a legend, slices that don't sum to 100%, fonts not declared on the chart, charts with `position:absolute` / `float` / negative margins.

PHASE 8 — WHAT TO AVOID
List domain-specific failure modes and anti-patterns for this report:
- What visual formats to never use (e.g. "never use pie charts for this report", "never use dense tables for narrative content").
- What content presentation mistakes to avoid (e.g. "do not summarize data that should be shown in full", "do not force a table when 2-3 sentences are clearer").
- What aesthetic mistakes to avoid (e.g. "do not mix warm and cool accent tones", "do not use more than 3 font weights").
- What structural mistakes to avoid (e.g. "do not leave pages nearly empty", "do not nest report-page divs").

=====================================================================
OUTPUT FORMAT
=====================================================================
Write a design brief as plain text under these headers. Use bullets and exact values. No CSS code, no JSON, no markdown blocks. A chapter writer must be able to make every visual decision from this brief alone.

ENFORCEMENT RULES FOR ALL VALUES:
- ALL colors as 6-digit hex codes (e.g. #1A365D, not "navy" or "dark blue").
- ALL font sizes in rem units (e.g. 1.5rem, not "24px" or "large").
- ALL spacing in rem or em units.
- Chart color sequence as an ordered list of hex values.
- No vague descriptors like "warm blue", "slightly larger", or "a bit of spacing".

1. COLOR SYSTEM — bg, text hierarchy, accents, semantic colors, chart color sequence (ordered, 5-6 hex values), component surfaces (table header, row alt, blockquote, insight box, code block — all with exact bg and border hex).

2. TYPOGRAPHY — font families (Google Fonts or system stacks), type scale (h2, h3, h4, body, caption — all in rem), font-weight per level, line-height per level.

3. SPACING — base spacing unit in rem, vertical rhythm (margins between paragraphs, subchapters, before/after visuals), component padding, max content width in rem.

4. VISUAL MOOD — 2-4 sentences: the aesthetic identity of this report. What feeling should the reader get? What domain does it evoke? What small details (borders, shadows, letter-spacing, dividers) reinforce that identity?

5. REPORT INTENT & PRESENTATION — 3-5 sentences merging what the report looks like, what the user is trying to achieve, and how the visual strategy serves that goal. What type of report is this? How should the reader perceive it? What visual formats dominate? How do structure and elements work together to deliver the best reading experience?

6. VISUAL DECISION TREE — At least 5 explicit IF/THEN rules mapping content types to visual formats. Example: "IF comparing 3+ products across 5+ attributes THEN use a styled table with alternating row colors. IF showing revenue trend over 4+ quarters THEN use a Charts.css line chart with show-data and show-labels. IF defining a single technical term THEN use a bold-term + paragraph block, not a table."

7. SVG & CHARTS.CSS CONSTRUCTION —
   a) SVG: standard viewBox dimensions for this report type, font family and sizes for SVG text, stroke widths (thin/medium/thick with px values and when to use each), color application rules (palette only, no arbitrary colors), accessibility requirements (<title> and <desc> mandatory), domain-specific SVG patterns from the skill.
   b) Charts.css: which chart types to use (bar, column, line, stacked, percentage, grouped), required modifier classes (show-labels, show-data, show-headings — specify which apply), color sequence for multi-series charts (ordered hex list), when to use data-after and show-primary, when NOT to use Charts.css.
   c) CONCRETE CHART CODE EXAMPLES — REQUIRED. You MUST include two small, copy-pasteable code snippets inside this section of your output (keep them compact, ~15-30 lines each, inside plain text — do NOT wrap them in markdown code fences; just show them as raw HTML the chapter writer can read). Use the EXACT hex values, body font, heading font, and heading color you defined in sections 1–2 of this brief (no placeholders like "[primary hex]"):
      • Example A — a Charts.css bar or column chart (whichever is primary for this report type) for a 3–5 category single-series dataset. It MUST include: the `<div>` wrapper with `width:100%; max-width:100%; overflow-x:auto; margin:1.25rem 0;`, the `<table class="charts-css ...">` with explicit `width:100%; max-width:100%; height:320px; font-family:[body font];`, a `<caption>` using the heading font + heading color, `<th>` cells with explicit inline font-family/size/weight/color/padding styles, and `<td>` cells with `--size` as a decimal fraction (0.0–1.0, NOT raw numbers or percentages or calc()) and `background` set to the primary accent hex.
      • Example B — an inline-SVG donut chart for 3 slices summing to 100%. It MUST include: the `<div>` wrapper with `width:100%; max-width:100%; overflow-x:auto; margin:1.25rem 0; display:flex; justify-content:center;`, the `<svg>` with `viewBox="0 0 400 300" width="100%" style="max-width:520px; font-family:[body font];"`, `<title>` and `<desc>` for accessibility, three `<circle>` elements using `stroke-dasharray` and `stroke-dashoffset` with the correct circumference math (r=70 → C≈440), rotated `-90deg` around the center, a white inner `<circle>` for the donut hole, an optional `<text>` centre label in the heading font, and a legend with color swatches + labels in the body font.
   d) ENCAPSULATION & PLACEMENT RULES (include these as explicit bullets in your brief so the chapter writer follows them verbatim):
      • Chart wrappers MUST use `width:100%; max-width:100%; overflow-x:auto; margin:1.25rem 0; box-sizing:border-box;`. Never fixed pixel widths > 688px. Never `position:absolute`, `float`, or negative margins.
      • Chart must declare `font-family` inline — never rely on browser defaults.
      • Chart must live inside a `<div class="report-page">`, never as a direct child of `<div class="report-chapter">`.
      • Always introduce a chart with at least one sentence of prose BEFORE it, and follow it with a 1–3 sentence interpretation AFTER it.
      • Never place a chart directly after an `<h2>`/`<h3>` heading. Never in the final 200px of a page — move to the top of the next `.report-page`.
      • Max one chart per prose-heavy page; max two per data-heavy page; never three.
      • Bar/column chart heights capped at 280–400px (never > 420px).
      • Color-for-data rules: single-series = one color; positive/negative = semantic green/red (if palette defines them); highlight-one = primary accent + muted neutral for the rest; pie slices ordered largest→smallest with palette colors, no two adjacent slices sharing a hue.

8. WHAT TO AVOID — Domain-specific failure modes: visual formats to never use, content presentation mistakes, aesthetic mistakes, structural mistakes. Be specific to this report type.
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
    sections_block = (
        f"RESEARCH SECTIONS FOR THIS CHAPTER ({len(sections)} sections):\n"
        + "=" * 60
        + "\n\n"
    )
    for idx, section in enumerate(sections):
        content = section.get("section_content", "")
        section_id = section.get("section_id", "unknown")
        sections_block += (
            f"--- Section {idx + 1} [section_id: {section_id}] ---\n{content}\n\n"
        )
    sections_block += "=" * 60 + "\n"

    available_ids = [s.get("section_id", "unknown") for s in sections]

    prompt = f"""You are an expert research report architect. Your task is to design the structure for ONE chapter of a multi-chapter research report.

{"=" * 70}
{all_queries_block}
{"=" * 70}

YOUR ASSIGNMENT: Design Chapter {chapter_num} of {total_chapters}
Research Focus: "{query}"
{position_note}

{"=" * 70}
{sections_block}
{"=" * 70}

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


def generate_framing_guidance_prompt(
    user_query: str,
    ordered_chapter_titles: List[str],
) -> str:
    """
    Generates a prompt that asks the LLM for TEXT guidance describing what
    the abstract, introduction, and conclusion should cover. This guidance
    is later fed into generate_chapter_prompt so those sections are produced
    with the same design, theme, and page structure as body chapters.
    """
    toc_block = "REPORT TABLE OF CONTENTS:\n"
    for title in ordered_chapter_titles:
        toc_block += f"  {title}\n"

    prompt = f"""You are an expert research report architect. Based on the research topic and the report's chapter structure, produce detailed TEXT GUIDANCE describing what the Abstract, Introduction, and Conclusion should contain.

This guidance will be given to a separate chapter-writing model that will turn it into fully designed HTML pages. So your output must be rich, detailed, and descriptive — but it is NOT the final content. It is instructions/notes for the writer.

{"=" * 70}
USER RESEARCH QUERY: {user_query}
{"=" * 70}

{toc_block}

{"=" * 70}
YOUR TASK
{"=" * 70}

For each of the three sections below, write a detailed TEXT description of what that section should cover. Be specific about themes, structure, key points to hit, and how it connects to the chapters.

ABSTRACT GUIDANCE:
  Describe what the abstract should summarize: the report's purpose, scope, what the chapters collectively cover, significance of the topic, and the key takeaway. Be specific — reference the actual chapter themes from the TOC. (Target: guidance for 150–250 words of final content.)

  TONE & PRECISION RULES FOR ABSTRACT (the chapter writer must follow these when turning your guidance into prose):
  - Hard cap: 150–220 words in the final rendered abstract. Shorter is better than padded.
  - Open with ONE sentence that names the exact topic and the exact question the report answers. No warm-up, no "In recent years…" filler, no rhetorical questions.
  - Every sentence must carry new information — no restating what the previous sentence already said in different words.
  - Anchor every claim in a concrete noun (the actual technology, entity, metric, event, mechanism) — never abstract filler like "various factors", "a number of considerations", "important implications".
  - Precision over flourish: name specific chapters, specific findings, specific metrics that appear later in the report. If the topic has numbers, include the 1–2 most important ones. If it has a verdict, state it.
  - One single paragraph, no lists, no sub-headings inside the abstract. Plain prose only.
  - End with ONE sentence that names the single most important takeaway a reader will get from finishing the report — not a generic "this is important" line.
  - Do NOT use meta-language like "This report will show…" / "We will discuss…" — write declaratively about the findings themselves.

INTRODUCTION GUIDANCE:
  Describe what the introduction should establish: why this topic matters now, what question/problem the report addresses, how the report is structured (reference each chapter by name and what it covers), and what the reader will gain. Be detailed about the narrative arc. (Target: guidance for 300–500 words of final content.)

  TONE & PRECISION RULES FOR INTRODUCTION (the chapter writer must follow these when turning your guidance into prose):
  - Target: 280–450 words in the final rendered introduction. Tight and purposeful. If the report is short, stay closer to 280.
  - Open with context in 1–2 sentences MAX. Do NOT spend a whole paragraph on background the reader already has — get to the actual question the report answers by the third sentence.
  - Then state the exact question or problem the report addresses, in one declarative sentence. No hedging ("this report will attempt to explore…") — write "This report explains X" or "This report analyses Y".
  - Then give a short structural roadmap: name each chapter (by its TOC title or a close paraphrase) and, in ONE short sentence per chapter, state what that chapter delivers. Use a clean bulleted list ONLY if there are 4+ chapters; otherwise keep it as prose. Do NOT repeat the full chapter content — just the angle.
  - End with 1–2 sentences on what the reader will be able to do/understand after finishing — concrete, not generic.
  - No jargon without a one-clause definition on first use. No acronyms without expansion on first use.
  - Prefer active voice. Prefer short sentences (avg 15–22 words). No dangling qualifiers, no nested parentheticals longer than 6 words.
  - Do NOT preview conclusions — the introduction sets up the question, the conclusion answers it.

CONCLUSION GUIDANCE:
  Describe what the conclusion should synthesize: the key insight from each chapter, how they connect into a bigger picture, forward-looking implications, and the definitive takeaway. Reference specific chapter themes. (Target: guidance for 300–500 words of final content.)

OUTPUT FORMAT — respond with exactly this JSON object, no markdown fences, no extra text:
{{
  "abstract": "Detailed text guidance for the abstract...",
  "introduction": "Detailed text guidance for the introduction...",
  "conclusion": "Detailed text guidance for the conclusion..."
}}
"""
    return prompt


async def main():
    """Module entry point for testing."""
    pass


if __name__ == "__main__":
    asyncio.run(main())
