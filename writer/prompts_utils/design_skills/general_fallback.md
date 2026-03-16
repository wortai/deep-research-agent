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

## Citation Style — General Sources
- Use inline numerical citations: [1], [2] — clean and unobtrusive.
- Alternatively, inline links: "According to `<a href='URL'>source name</a>`."
- Numbered reference list at section or chapter end.
- Format: `[n] Author(s), "Title," <a href="URL">Source</a>, Date.`
- For government data: cite the agency and dataset.
- For news sources: cite the publication and date.
- General reports need solid sourcing to establish credibility across any topic domain.

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

## Adaptive Instructions — How the LLM Should Use This Skill
- **This is the universal fallback.** If no specialized skill matches, use this. But "general" does not mean "boring" — it means "universally professional."
- **Never sacrifice content for layout.** If the research is data-heavy, use more charts and tables. If it's argument-heavy, use more prose and callout boxes. Adapt the tool mix to the content.
- **Steal from specialized skills when appropriate.** If a general report happens to include financial data, borrow the KPI card pattern from the finance skill. If it includes a historical timeline, borrow the timeline from the history skill. General reports can adopt ANY visual element.
- **Structure is never optional.** Every section must have a clear heading. The reader must be able to skim headers and understand the report's structure.
- **Don't over-design.** The general fallback's strength is restraint. A clean table is better than a flashy chart if the data only has 4 rows.

### What This Report NEVER Does
- Never uses extreme design choices (dark themes, oversized numbers, decorative gradients)
- Never forces charts where prose or a simple table works
- Never uses more than one accent color family
- Never uses serif fonts (this is the modern, neutral default)
- Never prioritizes style over substance
- Never assumes the reader is an expert — always accessible
