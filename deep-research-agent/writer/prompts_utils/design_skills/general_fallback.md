# General Fallback Report Design

## Identity & Scope
This is the default skill when no specialized skill is a clear match. It produces a clean, professional, universally accessible research report. Think of the best Wikipedia article, a McKinsey white paper, an Economist Intelligence Unit briefing, or a well-produced Brookings Institution policy paper — balanced, readable, comprehensive.

## How a General Research Report Looks & Feels
A general research report strikes the perfect balance. Clean prose for narrative. Tables for structured comparisons. Charts for quantitative data. Lists for enumerations. No extreme design choices — no dark backgrounds, no oversized typography, no domain-specific quirks. The design is INVISIBLE — the reader focuses entirely on understanding the content. It is the "Swiss knife" of report designs: professional, adaptable, and universally appropriate. There's an understated competence — the report looks like it came from a well-funded think tank.

## What Information Matters in a General Report
- **Balanced coverage**: All major angles of a topic explored. No obvious blind spots.
- **Clear structure**: The reader should instantly understand the organization from headers alone.
- **Evidence for claims**: Data, expert opinions, or established consensus backing every claim.
- **Actionable conclusions**: What SHOULD the reader take away? What are the implications?
- **Accessibility**: No assumed expertise. Jargon explained. Acronyms expanded on first use.
- **Breadth over extreme depth**: Cover the full landscape rather than tunneling into one narrow area.

## Content Structure & Narrative Flow
1. **Executive Summary**: Topic overview, significance, scope.
2. **Background & Context**: Foundation knowledge.
3. **Detailed Analysis**: Core content in logical thematic sections.
4. **Conclusion & Takeaways**: Summary and implications.

## Complete Visual Toolkit — Everything the LLM Can Use

The general fallback has access to ALL standard visual techniques. Choose based on content needs.

### Prose Paragraphs
- Standard, readable paragraphs (4-6 sentences). Bold for key terms.
- Left-aligned (not justified) for maximum screen readability.
- Clean sans-serif body font.
- Topic sentences anchor each paragraph.

### Bulleted & Numbered Lists
- Unordered for features, advantages, properties.
- Ordered for processes, rankings, sequences.
- One sentence per item. Nested lists for sub-categories.

### Tables
- Standard accessible tables with light header row, subtle alternation.
- Clear column headers, consistent alignment (text left, numbers right).
- Use for: comparisons, feature matrices, data summaries, before/after, pros/cons.

### Charts.css for Quantitative Data
- **Bar charts**: Comparing values across categories.
- **Column charts**: Period comparisons.
- **Line charts**: Trends over time.
- **Area charts**: Cumulative data.
- **Stacked bars**: Composition breakdown.
- **Percentage bars**: Market share, survey results.
- Only when real quantitative comparison data exists. Never force charts.

### SVG Diagrams
- **Process flows**: Boxes-and-arrows for workflows.
- **Relationship diagrams**: How concepts/systems connect.
- **Comparison visuals**: Quadrant layouts, Venn diagrams.
- **Hierarchies**: Organizational or conceptual trees.
- Use when spatial/relational thinking aids understanding.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide diagrams (process flows, timelines); `viewBox="0 0 400 400"` for square diagrams (Venn diagrams, hierarchies).
- **Font sizing**: `font-family` must match body font (Inter). Labels 12px, titles 14px, annotations 11px.
- **Stroke widths**: 1.5px for grid lines, 2px for connection arrows, 2.5px for borders, 1px for decorative elements.
- **Color application**: Use the exact universal palette — Blue (#3182CE), Teal (#319795), Orange (#DD6B20), Purple (#805AD5), Green (#38A169). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Process flow: Input → Processing → Output") and `<desc>` (describe all elements and their relationships).
- **Background**: Transparent — diagrams overlay on white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`.
- **Domain-specific SVG patterns**:
  - *Process flow*: `<rect>` nodes with rounded corners, `<path>` arrows between them. Sequential left-to-right or top-to-bottom layout.
  - For process-based topics (e.g., greenhouse effect, supply chain, workflow, lifecycle), use an SVG process flow diagram with labeled nodes and directional arrows. Minimum 4 nodes. Each node: rounded rectangle with label. Arrows: directional with arrowhead markers. Color-code nodes by stage or category.
  - *Venn diagram*: Overlapping `<circle>` or `<ellipse>` elements with semi-transparent fills (`opacity="0.3"`). Labels in intersection regions.
  - *Hierarchy/tree*: Root `<rect>` at top, child `<rect>` elements below, connected by `<path>` lines. Level-based vertical spacing.
  - *Quadrant*: Four `<rect>` quadrants divided by `<line>` axes. Labels in each quadrant. Items as `<text>` positioned within.

### Charts.css Decision Guide
- IF comparing categories (options, features, entities) → horizontal bar chart
- IF comparing time periods (years, quarters, months) → column chart
- IF showing trend over continuous time → line chart
- IF showing composition (budget split, survey breakdown) → stacked bar chart
- IF showing part-to-whole (completion, market share) → percentage bar
- IF comparing multiple series (this year vs. last, option A vs. B) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart with brief description
- Do NOT use Charts.css when: fewer than 3 data points (use a table), purely qualitative content (use prose), or data is better expressed as a comparison matrix
- **NEVER use Charts.css when: fewer than 3 data points** — use a simple table or KPI card instead. Charts.css with 2 data points produces a meaningless visualization that wastes space and confuses readers.
- For Charts.css bar/column charts, use `--size` as a decimal fraction (0.0 to 1.0), NOT as a `calc()` expression. Example: `style="--size: 0.76"` for 76%. Do NOT use `calc(76 * 0.5%)` — this produces invalid CSS.
- **ALL `<th>` elements in Charts.css tables MUST have explicit inline styles** for `font-family`, `font-size`, `font-weight`, `color`, and `padding`. Do NOT rely on browser defaults or inherited styles. Example: `<th style="font-family: Inter, sans-serif; font-size: 0.875rem; font-weight: 600; color: #FFFFFF; background: #1A365D; padding: 0.5rem 0.75rem;">`

### Key Insight / Callout Boxes
- Blue-tinted background, blue left border, bold text.
- 1-2 per chapter maximum — sparingly used for maximum impact.

### Comparison Layouts
- Two-column CSS grid for pros/cons, option A vs B.
- ✓/✗ feature matrices.
- "Strengths/Weaknesses" organized sections.

### Definition / Glossary Blocks
- Subtle styled containers for technical terms introduced for the first time.
- Bold term, regular weight definition.

### Section Dividers
- Thin horizontal rules between major sections.
- Extra vertical spacing.

### Summary Boxes
- At section ends, compact summary containers listing key takeaways.
- Distinct background, clear heading.

### Sidebar / Context Boxes
- For background information or tangential context.
- Subtle styling that doesn't interrupt the main flow.

### Edge Cases & Adaptations
- **No quantitative data**: For purely qualitative topics (e.g., "Philosophy of Art"), use comparison tables, prose analysis, and SVG concept diagrams. Skip Charts.css entirely.
- **Too much data**: For large datasets, summarize with key statistics in a compact table and show representative charts. Use `<details>` for full data.
- **Mixed content**: When prose dominates with occasional numbers, embed key metrics inline and use charts only for sections with 3+ comparable data points.
- **Contradictory sources**: Present competing viewpoints side-by-side in a comparison table. Note source credibility and methodology differences.
- **Variable chapter length**: Short topics get a single section with key insight box. Long topics use the full toolkit with summary boxes at each section end.
- **Default format mismatch**: Borrow from specialized skills as needed — finance KPI cards for data-heavy topics, history timelines for chronological content, coding diagrams for technical topics.

## Citation Style — General Sources
- Use inline numerical citations: [1], [2] — clean and unobtrusive.
- Alternatively, inline links: "According to `<a href='URL'>source name</a>`."
- Numbered reference list at section or chapter end.
- Format: `[n] Author(s), "Title," <a href="URL">Source</a>, Date.`
- For government data: cite the agency and dataset.
- For news sources: cite the publication and date.
- General reports need solid sourcing to establish credibility across any topic domain.
- **Multiple formats**: Use inline [n] for formal claims, inline links for navigational references, and source blocks for datasets.
- **No URL available**: Cite as `[n] Author(s), "Title," Publication, Date. [Archive: URL or identifier]` — provide the most persistent identifier available.
- **Multiple sources for same claim**: Use range notation [1–3] for consensus. For contested claims, list individually with context.
- **Beautiful citations**: Style the reference list as a clean numbered table with clickable links and subtle alternating backgrounds.
- **Source credibility hierarchy**: Peer-reviewed journal > government/official data > established news outlet > expert blog > general website. Always prefer primary sources.

## Typography & Color — The Universal Palette

### Fonts
- **Body**: Inter, system-ui, -apple-system — maximum legibility across all devices.
- **Headings**: Same sans-serif, heavier weight. Deep navy (#1A365D). h2 = 1.5rem, h3 = 1.25rem, h4 = 1.1rem.
- **Code (if any)**: Fira Code at 0.9rem.
- **Table content**: 0.95rem for readability.

### Color System — Professional, Neutral, Universally Appropriate
- **Background**: White (#FFFFFF).
- **Body text**: Dark charcoal (#2D3748) — professional, high contrast.
- **Headings**: Deep navy (#1A365D) — authoritative without being aggressive.
- **Borders/dividers**: Light gray (#E2E8F0) — subtle structure.
- **Key insight boxes**: Pale blue (#EBF8FF), blue accent (#3182CE).
- **Table header bg**: Light gray (#EDF2F7), dark text.
- **Alternating rows**: Barely-there gray (#F7FAFC).
- **Chart palette**: Blue (#3182CE), Teal (#319795), Orange (#DD6B20), Purple (#805AD5), Green (#38A169). Colorblind-accessible set.
- **Positive/negative** (when needed): Green (#38A169) / Red (#E53E3E).
- **Line height**: 1.7.
- **Max width**: 780px.
- **Extended chart palette** (7+ colors): Blue (#3182CE), Teal (#319795), Orange (#DD6B20), Purple (#805AD5), Green (#38A169), Steel (#4A5568), Gold (#D69E2E). All WCAG AA compliant on white.
- **Semantic color rules**: Blue = default/primary series. Teal = secondary series. Orange = emphasis/warning. Purple = tertiary comparison. Green = positive outcome. Steel = reference/baseline. Gold = benchmark/standard.
- **Hover/interaction**: On hover, chart elements increase opacity to 1.0 while others dim to 0.6.
- **Print-friendly**: All colors maintain ≥ 3:1 contrast in grayscale. Color differentiation supplemented by labels.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio. Chart colors ≥ 3:1 against white. The palette is deuteranopia-safe.

## Adaptive Instructions — How the LLM Should Use This Skill
- **This is the universal fallback.** If no specialized skill matches, use this. But "general" does not mean "boring" — it means "universally professional."
- **Never sacrifice content for layout.** If the research is data-heavy, use more charts and tables. If it's argument-heavy, use more prose and callout boxes. Adapt the tool mix to the content.
- **Steal from specialized skills when appropriate.** If a general report happens to include financial data, borrow the KPI card pattern from the finance skill. If it includes a historical timeline, borrow the timeline from the history skill. General reports can adopt ANY visual element.
- **Structure is never optional.** Every section must have a clear heading. The reader must be able to skim headers and understand the report's structure.
- **Don't over-design.** The general fallback's strength is restraint. A clean table is better than a flashy chart if the data only has 4 rows.
- Never presents a topic without at least one visual beyond tables and prose. If the research contains process flows, comparisons, hierarchies, or relationships, you MUST create at least one SVG diagram (process flow, comparison chart, hierarchy tree, or relationship map).
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., data table + process flow SVG + key insight callout, or comparison chart + timeline + explanatory prose). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never uses extreme design choices (dark themes, oversized numbers, decorative gradients)
- Never forces charts where prose or a simple table works
- Never uses more than one accent color family
- Never uses serif fonts (this is the modern, neutral default)
- Never prioritizes style over substance
- Never assumes the reader is an expert — always accessible
- Never uses Charts.css without labeled axes and a caption
- Never presents contradictory claims without noting the disagreement
- Never uses color as the sole differentiator — always pair with text labels
- Never skips SVG visualizations when the data supports them — at least one SVG diagram is mandatory per chapter. If the research contains process flows, comparisons, hierarchies, or relationships, you MUST create at least one SVG diagram (process flow, comparison chart, hierarchy tree, or relationship map).
