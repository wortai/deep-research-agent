# News & Journalism Report Design

## Identity & Scope
This skill activates when the user's query is about current events, breaking news, geopolitical developments, investigative reporting, political analysis, policy analysis, or any topic requiring journalistic rigor. Think of The New York Times long-form features, The Guardian's investigative pieces, Reuters wire reporting, or The Economist's analytical style.

## How a Real News Article Looks & Feels
A professional news article is sharp and functional. The lede (opening sentence) delivers the core fact with zero buildup. The "inverted pyramid" structure puts the most critical info first — a reader who stops after paragraph one still got the essential news. Pull quotes from officials are large and dramatic. Datelines anchor the story. Short paragraphs (2-3 sentences) create quick, punchy pacing. Headlines are bold and declarative. The overall impression is urgency, objectivity, and authority. A well-designed news feature also uses photography-style white space — clean, confident, and letting the weight of the facts speak for themselves.

## What Information Matters Most to News Readers
- **The facts first**: What happened, who was involved, where, when, and why — in that order.
- **Attribution on everything**: Every claim must be attributed — "officials said," "data shows," "according to."
- **Timeliness**: When did this happen? Is this developing? Is there a deadline or next event?
- **Impact**: Who is affected and how many? What changes as a result?
- **Context**: How does this compare to previous events? What's the historical pattern?
- **Multiple perspectives**: Both sides heard. Officials AND affected communities. Government AND opposition.
- **What happens next**: What to watch, upcoming decisions, expected developments.

## Content Structure & Narrative Flow
1. **The Lede**: Most important fact in the very first paragraph.
2. **Inverted Pyramid**: Most important → supporting details → background context.
3. **Stakeholder Voices**: Direct quotes with full attribution.
4. **Timeline**: For unfolding stories, chronological progression.
5. **Impact & What's Next**: Who is affected, what to watch.

## Complete Visual Toolkit — Everything the LLM Can Use

### Dateline & Byline
- Location, date, and source in small uppercase muted text at the top.
- Establishes immediate journalistic frame and credibility.

### Pull Quotes — Editorial Emphasis
- Large, dramatic quotes from key figures.
- Centered, serif italic, bordered top and bottom by thick dark rules.
- Attribution below with speaker's name, role, and context.
- Used for the most powerful or revealing statements.

### Headlines & Subheadlines
- Main headline: Large display serif (Playfair Display), bold, near-black.
- Subheadline/deck: Shorter, lighter weight, providing a second layer of context.
- Section headers within the piece: clean, bold, sans-serif.

### Event Timelines
- Vertical CSS timelines for unfolding stories with dates and brief descriptions.
- Compact, factual — no narrative in the timeline itself.
- Highlight the latest/most critical event.

### Factual Prose
- Short paragraphs (2-3 sentences). Every sentence adds a new fact.
- Every claim attributed.
- Sans-serif for maximum screen readability.
- No first person. No opinion in body text.

### Charts.css for News Data
- **Bar charts**: Polling data, economic indicators, casualty counts, election results.
- **Line charts**: Trends — COVID cases, inflation, approval ratings, crime statistics.
- **Stacked bars**: Budget allocation, vote distribution, demographic breakdowns.
- **Percentage bars**: Electoral margins, market share changes, survey results.
- Neutral colors — blues, grays, with red only for "critical" data points.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide charts (trend lines, polling data, election results); `viewBox="0 0 400 400"` for square diagrams (geographic markers, proportional representations).
- **Font sizing**: `font-family` must match body font (Inter). Axis labels 12px, chart titles 14px, data labels 11px.
- **Stroke widths**: 1.5px for grid lines, 2px for data lines, 2.5px for axes, 1px for decorative elements.
- **Color application**: Use the exact news palette — Steel blue (#3182CE), Neutral gray (#718096), Alert red (#E53E3E), Muted teal (#319795). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Approval rating trend: Jan–Dec 2025") and `<desc>` (describe the trend, key data points, and significance).
- **Background**: Transparent — news graphics overlay on white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Location names use `<tspan font-weight="bold">`.
- **Domain-specific SVG patterns**:
  - *Geographic marker map*: Simple `<path>` region outlines, `<circle>` event markers (size proportional to impact), `<text>` location labels.
  - *Polling trend*: `<polyline>` or `<path>` trend line, `<circle>` data points, horizontal `<line>` for margin of error band.
  - *Election results*: `<rect>` bars for each candidate/party, colored by party convention, `<text>` percentage labels.
  - *Timeline infographic*: Horizontal `<line>` spine, `<circle>` event nodes, `<text>` date and brief description.

### Charts.css Decision Guide
- IF comparing categories (candidates, countries, policies) → horizontal bar chart
- IF comparing time periods (months, quarters, years) → column chart
- IF showing trend over continuous time (approval ratings, case counts) → line chart
- IF showing composition (budget allocation, demographic breakdown) → stacked bar chart
- IF showing part-to-whole (vote share, market penetration) → percentage bar
- IF comparing multiple series (this year vs. last, party A vs. party B) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart with source attribution: "(Source: Reuters, March 2026)"
- Do NOT use Charts.css when: fewer than 3 data points (use infographic stat blocks), purely narrative content (use prose), or data is better shown as a timeline

### Data Tables
- Survey results, election returns, policy comparisons, economic statistics.
- Clean, functional, attributed to source.
- Sortable-looking headers (even if not interactive).

### Infographic Stat Blocks
- Large numbers as visual elements: "3.4 million displaced," "$2.1 trillion in damages."
- Newspaper sidebar-style fact boxes.

### Sidebar Context Boxes
- Brief explainer boxes: "Who is [person]?" or "What is [policy]?" or "Background on [event]."
- Distinct containers providing context without interrupting narrative flow.

### Developing Story Markers
- For actively developing stories, a distinctive header/banner indicating urgency.
- Red accent, bold text, timestamp of latest update.

### Source Attribution Patterns
- Inline attribution in every paragraph.
- Can include dedicated "Sources" or "Methodology" notes for data-driven pieces.

### Maps & Geographic Context
- Simple SVG location markers for where events are happening.
- Region outlines showing affected areas.

### Edge Cases & Adaptations
- **No quantitative data**: For purely narrative stories (e.g., human interest, profile pieces), use pull quotes, timelines, and prose. Skip Charts.css entirely.
- **Too much data**: For complex datasets (e.g., full election returns by precinct), summarize with key results (winner, margin, turnout) and show representative charts. Use `<details>` for full data.
- **Mixed content**: When narrative dominates with occasional statistics, embed key numbers as infographic stat blocks and use charts only for sections with 3+ comparable data points.
- **Contradictory sources**: When sources conflict, attribute each claim specifically: "Government officials said X, while independent monitors reported Y." Do not reconcile — present both.
- **Variable chapter length**: Breaking news gets lede + timeline + stat blocks. Investigative features get the complete toolkit with context boxes and stakeholder voices.
- **Default format mismatch**: If the news topic is historical (e.g., "Anniversary of a Major Event"), borrow timeline patterns from the history skill. If it's scientific (e.g., "New Climate Study"), borrow scientific data table patterns.

## Citation Style — Journalistic Sources
- Use inline source attribution naturally in prose: "according to `<a href='URL'>Reuters</a>`" or "a `<a href='URL'>White House statement</a>` said."
- For data: "(Source: `<a href='URL'>Bureau of Labor Statistics</a>`, March 2026)."
- For documents: "(Full text: `<a href='URL'>link</a>`)."
- For named sources: direct attribution in text. For unnamed: "a senior official who spoke on condition of anonymity."
- Journalistic citations are woven INTO the text, not relegated to footnotes.
- **Multiple formats**: Use inline attribution in prose for claims, parenthetical source for data, and source blocks for documents.
- **No URL available**: Cite as "(Associated Press, March 15, 2026)" — wire service + date serves as reference.
- **Multiple sources for same claim**: Attribute each source inline: "Both the White House and Pentagon officials confirmed..." List sources in order of directness (eyewitness > official statement > secondhand report).
- **Beautiful citations**: Style source notes as compact inline text with small source-type indicators. Group by source type at article end if needed.
- **Source credibility hierarchy**: Eyewitness/on-the-ground reporting > official government statement > wire service (Reuters, AP) > established newspaper > broadcast network > blog/opinion. Always prefer on-the-ground and official sources.

## Typography & Color — The News Palette

### Fonts
- **Body**: Clean sans-serif — Inter, system-ui, -apple-system. News is screen-first.
- **Main headline**: Large display serif — Playfair Display, Noto Serif Display. Bold, declarative.
- **Pull quotes**: Serif italic — dramatic, editorial weight.
- **Dateline**: Small uppercase, wide letter-spacing.

### Color System — Authoritative, Restrained, Urgent When Needed
- **Background**: White (#FFFFFF) — clean, professional.
- **Body text**: Dark gray (#2D3748).
- **Headlines**: Near-black (#1A202C) — maximum authority.
- **Dateline/metadata**: Medium gray (#718096) — present but recessive.
- **Pull quote borders**: Black (#1A202C) — bold, declarative.
- **Breaking/critical accent**: Deep red (#C53030) — sparingly used for urgency.
- **Chart palette**: Steel blue (#3182CE), Neutral gray (#718096), Alert red (#E53E3E), Muted teal (#319795).
- **Sidebar boxes**: Very light gray (#F7FAFC), subtle border.
- **Line height**: 1.7.
- **Extended chart palette** (7+ colors): Steel blue (#3182CE), Neutral gray (#718096), Alert red (#E53E3E), Muted teal (#319795), Forest (#38A169), Orange (#DD6B20), Purple (#805AD5). All WCAG AA compliant on white.
- **Semantic color rules**: Steel blue = default/neutral data series. Neutral gray = baseline/comparison. Alert red = critical/urgent data points only. Muted teal = secondary series. Forest = positive/growth indicators. Orange = warning/caution metrics. Purple = tertiary/analytical series.
- **Hover/interaction**: On hover, chart elements show exact values. Use CSS `:hover` with subtle opacity transitions.
- **Print-friendly**: All colors maintain ≥ 3:1 contrast in grayscale. Red differentiation supplemented by bold weight for print legibility.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio. Chart colors ≥ 3:1 against white. The palette is colorblind-safe.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If there are 8 stakeholder perspectives, include all 8 with proper attribution.
- **The lede is sacred.** The most important fact must be in the very first paragraph. Period.
- **Adapt the format to the story type.** Breaking news → ultra-short paragraphs, timeline, dateline. Investigative feature → longer analytical sections, context boxes. Data story → heavy Charts.css usage.
- **Build new patterns.** If the content demands a "Fact Check" comparison box, a "Policy Impact Table," or an "Expert Panel Roundup," create it.
- **Sources are non-negotiable.** Every factual claim must be attributed. Every data point sourced. No exceptions.
- Never presents a news topic without at least one structural visual. If the research contains timelines, stakeholder relationships, or data trends, you MUST create at least one SVG diagram (timeline infographic, polling trend chart, or geographic marker map).
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., pull quote + timeline SVG + data table, or infographic stat block + Charts.css chart + sidebar context box). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never presents a quote without full attribution
- Never buries the lede
- Never uses first person or opinion in body text
- Never uses decorative visual elements
- Never presents unsourced claims as fact
- Never uses warm/historical colors — news is current and cool-toned
- Never uses Charts.css without source attribution in the caption
- Never presents opinion as fact — always attribute
- Never uses red as the default chart color — reserve it for critical/urgent data only
- Never skips SVG visualizations when the data supports them — at least one SVG diagram is mandatory per chapter. If the research contains timelines, stakeholder relationships, or data trends, you MUST create at least one SVG diagram (timeline infographic, polling trend chart, or geographic marker map).


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
