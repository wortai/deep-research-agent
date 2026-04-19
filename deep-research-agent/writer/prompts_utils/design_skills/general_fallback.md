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


---

## Chart Construction — Bar Chart & Pie Chart Reference (Essential)

This reference specifies EXACTLY how to build Charts.css bar/column charts and SVG pie/donut charts so they render cleanly inside the report-page container (the viewer caps `.report-page` at ~800px width, with ~3.5rem of left/right padding, so the usable column is ≈ 688px). Use it whenever you add a chart — it replaces guesswork. All colors referenced here MUST come from the chart palette defined in this skill's "Typography & Color" section above.

### Universal Encapsulation Rules (apply to EVERY chart, bar or pie)
- Every chart MUST be wrapped in `<div style="width:100%; max-width:100%; overflow-x:auto; margin:1.25rem 0; padding:0.25rem 0; box-sizing:border-box;">` so nothing escapes the page column.
- Never set a fixed pixel width on the chart itself. Use `width:100%` and let the wrapper cap at `max-width:100%`.
- The chart wrapper MUST sit directly inside a `<div class="report-page">` — never as a direct child of `<div class="report-chapter">`, never inside a floated or absolutely-positioned container.
- Leave at least 1rem of vertical breathing room above AND below every chart so it does not touch neighboring prose or a heading.
- Always pair a chart with a 1–3 sentence prose interpretation placed BELOW it (what the chart shows + key takeaway). A chart on its own is incomplete.
- Always declare `font-family` explicitly on the chart itself (`<table>` or `<svg>`) — inherit the skill's body font for labels and the skill's heading font for captions. Never rely on browser defaults.
- Never use `position: absolute`, `position: fixed`, CSS `float`, or negative margins on a chart or its labels — they break pagination.

### 1) Bar / Column Charts — Charts.css

Use `<table class="charts-css bar|column ...">` for categorical comparisons (3+ categories) or period-over-period trends. Horizontal bar charts read best when category labels are long; column charts read best for time series or short labels.

**Sizing**
- Target chart block height: 280–360px for single-series, 320–400px for multi-series with legend. Never exceed 420px — taller charts crowd subsequent content off the page.
- Set `height` on the `<table>` explicitly (e.g. `height: 320px`) AND keep `width:100%; max-width:100%;`. Do not set an inline `height` on the wrapper div — let the table drive height.
- Add `data-spacing-5` or `data-spacing-10` to the table classes for breathable bars. Use `data-spacing-10` whenever you have fewer than 6 bars.
- Always include `show-labels show-data show-heading`. Add `show-data-on-hover` only if you want the label hidden until mouseover.

**Data encoding (critical — Charts.css gotchas)**
- `--size` MUST be a decimal fraction from `0.0` to `1.0`. Normalize each value against the dataset maximum yourself. Example: raw values `[21, 22, 23, 28]` → max `28` → `--size` values `[0.75, 0.79, 0.82, 1.0]`. NEVER pass raw numbers, percentages (e.g. `75%`), or `calc()` expressions.
- Put the human-readable raw value inside the `<td>` so the reader sees it: `<td style="--size: 0.82"><span>$42.1B</span></td>`.
- For grouped/stacked (multi-series) charts, each `<tr>` is one data series. The first `<th scope="row">` of each row MUST label the series (e.g. "2023", "Control group") so readers identify it without reading prose.
- ALL `<th>` elements need explicit inline `font-family`, `font-size`, `font-weight`, `color`, `background`, `padding` — browser defaults will break the skill's typography.

**Color choices (how to pick colors that represent the data well)**
- Use ONLY the chart palette defined in this skill's Typography & Color section. Apply colors in strict order: series 1 → primary accent, series 2 → secondary accent, series 3 → tertiary, and so on.
- Single-series charts: ONE color for all bars. Do NOT rainbow-color bars within a single series — that implies the bars represent different categories when they don't, and it misleads readers.
- Growth/decline, over/under, pass/fail, gain/loss comparisons: use the skill's semantic green for positive and semantic red for negative (if the skill defines them). Otherwise use the primary accent vs a muted/neutral tone.
- Highlight-one-bar patterns (e.g. "this quarter vs the rest"): primary accent for the focus bar, a muted neutral gray/steel from the palette for the remaining bars. Never two bright accents fighting for attention.
- Keep ≥ 3:1 luminance contrast between the bar fill and the page background. On white pages, pale pastels under 3:1 fail — use the palette's mid-tone values instead.
- Never use alpha/opacity < 0.75 for primary data bars — it makes numbers hard to compare. Use opacity only for secondary/reference bars (e.g. historical average underlay).

**Labels & caption**
- Every chart MUST include a `<caption>` with a short descriptive title. Use this skill's heading font, 0.95rem, 600 weight, heading-color hex, `caption-side: top`. If this skill uses figure numbering, prefix "Figure N:".
- Example caption: `<caption style="caption-side: top; font-family: [heading font], sans-serif; font-size: 0.95rem; font-weight: 600; color: [heading hex]; padding: 0.25rem 0 0.75rem; text-align: left;">Figure 1 — Revenue by segment, FY2024</caption>`.
- Axis / row labels: 0.8125rem body font, 400–500 weight, muted color (e.g. #4A5568 on white backgrounds). Padding on `<th>`/`<td>` of at least 0.5rem so labels never touch bars.
- When axis labels are long, rotate them via `writing-mode: vertical-rl` only on column charts — NEVER on bar charts (horizontal).

**Minimal copy-paste example** (single-series column chart, 4 quarters):
```
<div style="width:100%; max-width:100%; overflow-x:auto; margin:1.25rem 0; padding:0.25rem 0; box-sizing:border-box;">
  <table class="charts-css column show-labels show-data show-heading data-spacing-10"
         style="width:100%; max-width:100%; height:320px; font-family: [body font], sans-serif;">
    <caption style="caption-side: top; font-family: [heading font], sans-serif; font-size:0.95rem; font-weight:600; color:[heading hex]; padding:0.25rem 0 0.75rem; text-align:left;">
      Figure 1 — Quarterly revenue, FY2024 (USD billions)
    </caption>
    <thead><tr>
      <th scope="col" style="font-family:[body font],sans-serif; font-size:0.8125rem; font-weight:600; color:[heading hex]; padding:0.5rem;">Quarter</th>
      <th scope="col" style="font-family:[body font],sans-serif; font-size:0.8125rem; font-weight:600; color:[heading hex]; padding:0.5rem;">Revenue</th>
    </tr></thead>
    <tbody>
      <tr><th scope="row" style="font-family:[body font],sans-serif; font-size:0.8125rem; color:#4A5568; padding:0.5rem;">Q1</th>
          <td style="--size:0.75; background:[primary accent hex]; color:#FFFFFF; font-family:[body font],sans-serif; font-size:0.8125rem;"><span>$21.1B</span></td></tr>
      <tr><th scope="row" style="font-family:[body font],sans-serif; font-size:0.8125rem; color:#4A5568; padding:0.5rem;">Q2</th>
          <td style="--size:0.79; background:[primary accent hex]; color:#FFFFFF; font-family:[body font],sans-serif; font-size:0.8125rem;"><span>$22.0B</span></td></tr>
      <tr><th scope="row" style="font-family:[body font],sans-serif; font-size:0.8125rem; color:#4A5568; padding:0.5rem;">Q3</th>
          <td style="--size:0.82; background:[primary accent hex]; color:#FFFFFF; font-family:[body font],sans-serif; font-size:0.8125rem;"><span>$23.0B</span></td></tr>
      <tr><th scope="row" style="font-family:[body font],sans-serif; font-size:0.8125rem; color:#4A5568; padding:0.5rem;">Q4</th>
          <td style="--size:1.00; background:[primary accent hex]; color:#FFFFFF; font-family:[body font],sans-serif; font-size:0.8125rem;"><span>$28.1B</span></td></tr>
    </tbody>
  </table>
</div>
```

**Placement inside the page**
- Always introduce the chart with a sentence of prose FIRST ("As Figure 1 shows, …") and follow it with a 1–3 sentence interpretation.
- One chart per page maximum in prose-heavy skills; two charts per page maximum in data-heavy skills. Never three — the page becomes a data dump.
- Do not drop a chart immediately after an `<h2>`/`<h3>` — at least one introductory sentence must separate heading and chart.
- If a chart would land in the bottom third of a page with no room for its interpretation, move the chart to the TOP of the next `<div class="report-page">`.

### 2) Pie / Donut Charts — Inline SVG (Preferred)

Charts.css pie support is unreliable across renderers. Always build pie/donut charts as inline SVG using the `stroke-dasharray` trick below. Reserve Charts.css percentage bars for part-to-whole stories where a full circular pie is not essential.

**When to use a pie/donut**
- 2–6 categorical slices summing to exactly 100% (e.g. revenue mix, market share, budget split, composition).
- Readers care about relative proportions more than absolute values.
- Do NOT use a pie chart for time series, comparisons across entities, or any data that doesn't sum to a whole.

**Sizing**
- Use `viewBox="0 0 400 300"` for donuts with a side legend, or `viewBox="0 0 300 300"` for square centered donuts.
- Wrap the `<svg>` with `width="100%"` and `style="max-width: 520px;"` so it doesn't stretch across the full 688px column. Center with `display:flex; justify-content:center;` on the outer wrapper.
- For r=70 with stroke-width 38, the donut fills a ~200px diameter block — readable without crowding. For r=60 with stroke-width 28, it's a compact donut for tighter layouts.

**Donut math (the only tricky part)**
- Circumference `C = 2 × π × r`. For r=70, C ≈ 439.82. For r=60, C ≈ 376.99.
- For each slice with percentage `p` (0.0–1.0): `stroke-dasharray = "(p × C)   C"`.
- `stroke-dashoffset` for slice N is the NEGATIVE cumulative length of slices 1…N-1. First slice offset = 0.
- ALWAYS rotate `-90deg` around the centre (`transform="rotate(-90 cx cy)"`) so the first slice starts at 12 o'clock. Readers expect this.
- Slice percentages must sum to 1.00 (± 0.01). If they don't, recompute or add a small "Other" slice.

**Color choices**
- Order slice colors largest → smallest using this skill's chart palette: primary accent for the dominant slice, secondary for the next, tertiary for the next, etc. The dominant slice carries the most visual weight.
- Adjacent slices must differ in hue, not brightness. Never put two blues next to each other unless separated by a 1.5–2px white divider stroke.
- Keep total slice count ≤ 6. If you have more, aggregate the smallest into an "Other" slice — readers cannot visually compare more than 6 wedges.
- For a donut meant to highlight ONE slice, use the primary accent for that slice and desaturate the rest into one muted neutral (steel/gray from the palette).

**Drop-in donut template** (edit slice percentages, labels, and colors only):
```
<div style="width:100%; max-width:100%; overflow-x:auto; margin:1.25rem 0; padding:0.25rem 0; display:flex; justify-content:center; box-sizing:border-box;">
  <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" width="100%" style="max-width: 520px; font-family: [body font], sans-serif;">
    <title>Revenue composition by segment, FY2024</title>
    <desc>Donut chart. Three segments: Cloud 58%, Licensing 27%, Services 15%. Cloud dominates.</desc>

    <!-- r=70, C≈440. Slice lengths: 58%=255, 27%=119, 15%=66. Offsets: 0, -255, -374 -->
    <circle cx="150" cy="150" r="70" fill="none" stroke="[series-1 hex]" stroke-width="38"
            stroke-dasharray="255 440" transform="rotate(-90 150 150)"/>
    <circle cx="150" cy="150" r="70" fill="none" stroke="[series-2 hex]" stroke-width="38"
            stroke-dasharray="119 440" stroke-dashoffset="-255" transform="rotate(-90 150 150)"/>
    <circle cx="150" cy="150" r="70" fill="none" stroke="[series-3 hex]" stroke-width="38"
            stroke-dasharray="66 440" stroke-dashoffset="-374" transform="rotate(-90 150 150)"/>
    <!-- Inner hole for donut effect. Omit this circle for a full pie. -->
    <circle cx="150" cy="150" r="50" fill="#FFFFFF"/>

    <!-- Centre label (optional) -->
    <text x="150" y="147" text-anchor="middle" font-family="[heading font], sans-serif" font-size="14" font-weight="600" fill="[heading hex]">FY2024</text>
    <text x="150" y="165" text-anchor="middle" font-family="[body font], sans-serif" font-size="11" fill="[body text hex]">Total $72B</text>

    <!-- Legend on the right -->
    <g font-family="[body font], sans-serif" font-size="11" fill="[body text hex]">
      <rect x="250" y="90"  width="10" height="10" fill="[series-1 hex]"/>
      <text x="266" y="99">Cloud — 58%</text>
      <rect x="250" y="120" width="10" height="10" fill="[series-2 hex]"/>
      <text x="266" y="129">Licensing — 27%</text>
      <rect x="250" y="150" width="10" height="10" fill="[series-3 hex]"/>
      <text x="266" y="159">Services — 15%</text>
    </g>
  </svg>
</div>
```

**Placement**
- Pie/donut charts need a 2–3 sentence interpretation paragraph beside or below them. Never stack two pies on the same page — the reader can't compare them side-by-side at this width.
- Do not place a pie in the final 200px of a page; move it to the top of the next `<div class="report-page">`.
- If you have more than 6 slices, switch to a horizontal `charts-css percentage-column` or a stacked-bar chart — micro-slices become unreadable.

### 3) When NOT to Use These Charts
- Fewer than 3 data points → use a KPI callout, a bold inline number, or a 2-row table.
- Purely qualitative content with no real numbers → use prose, a comparison table, or a definition block.
- Slice percentages < 3% → invisible wedges. Aggregate them into "Other" or switch to horizontal percentage bars where micro-slices can still show labels.
- Comparing absolute magnitudes across categories that don't sum to a whole → use a bar chart, not a pie.

### 4) Anti-Patterns to Avoid (Chart-Specific)
- Fixed pixel widths wider than 688px — they overflow the page column. Always `width:100%` with `max-width:100%`.
- `--size` values outside `[0.0, 1.0]` — Charts.css renders them as zero- or full-height bars and the chart silently breaks.
- `calc()` expressions inside `--size` (e.g. `--size: calc(21.3/28.1)`) — produce invalid CSS in many renderers. Pre-compute the decimal fraction.
- Rainbow-colored bars within a single series — misleading.
- A donut without a legend — readers cannot map slice colors back to categories.
- Slices that don't sum to 100% — the donut visually "floats" and readers distrust the data.
- Two charts placed side-by-side via CSS grid/flex inside the 688px column — they overlap. Stack vertically instead.
- Fonts not declared on the chart (`<table>` or `<svg>`) — browser defaults (Times New Roman / sans-serif) override the skill's typography.
- Charts taller than 420px or placed in the bottom 200px of a page without enough room for their caption and interpretation.
