# Modern Minimalist Report Design

## Identity & Scope
This skill activates when the user wants a clean, ultra-concise, highly scannable summary or briefing. Best for executive summaries, competitive snapshots, product overviews, market briefings, or any topic where maximum information density per element is the goal. The report should look like an Apple keynote turned document, a Notion summary, or a Dieter Rams-designed briefing.

## How a Minimalist Briefing Looks & Feels
A minimalist document is the OPPOSITE of a textbook. Every word earns its place. Whitespace is the dominant visual element — it's not empty space, it's intentional breathing room. Data is presented as TYPOGRAPHY: giant numbers, not charts. Tables have no visible borders — alignment alone creates structure. A single accent color, if any. The overall impression is sophistication, extreme confidence, and surgical clarity. Less IS more. What remains on the page is perfect.

## What Information Matters in Minimalist Context
- **The single most important takeaway.** What is the one sentence the reader must remember?
- **Key numbers without decoration.** Three data points, clearly presented, are worth more than a 10-row table.
- **Hierarchy without ornament.** Size, weight, and position communicate importance — not color or borders.
- **Negative space as communication.** What you LEAVE OUT tells the reader what to focus ON.
- **Decisiveness.** Minimalist documents make a clear point. They don't hedge or list alternatives — they choose.

## Content Structure & Narrative Flow
1. **Core Takeaway**: Single most important conclusion in 1-2 sentences.
2. **Key Data Points**: 3-5 critical metrics as typographic elements.
3. **Analysis**: Brief, focused sections. No filler prose.

## Complete Visual Toolkit — Everything the LLM Can Use

### Typographic Data Display — The Signature Technique
- Key data as oversized text elements: small muted label above, giant bold number below, optional trend beneath.
- This IS the minimalist chart — typography replaces visualization.
- Separated by subtle bottom borders or generous spacing.

### Borderless Tables
- Zero visible borders. Alignment and whitespace create structure.
- Only the lightest divider rules (1px, nearly invisible gray).
- Two-column: label left, value right-aligned.
- Dense but elegant.

### Minimal Charts.css
- If charts are strictly necessary, use the simplest representation possible.
- Single-color bars. No gridlines. No axis labels if context is obvious.
- Area charts with a single soft fill.
- Charts should feel like a "gentle suggestion" — not a data-dense visualization.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide layouts (trend lines, comparisons); `viewBox="0 0 400 400"` for square diagrams (proportional representations).
- **Font sizing**: `font-family` must match body font (Inter). Labels 12px, titles 14px, data labels 11px.
- **Stroke widths**: 1.5px for minimal grid lines, 2px for data lines, 2.5px for primary axes, 1px for subtle decorative elements.
- **Color application**: Use ONLY the minimalist palette — near-black (#1A202C), muted gray (#A0AEC0), single accent blue (#3182CE). No other colors permitted.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Revenue trend: Q1–Q4") and `<desc>` (describe the trend direction and key values).
- **Background**: Transparent — minimalist diagrams overlay on pure white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Keep text minimal — labels only, no explanations.
- **Domain-specific SVG patterns**:
  - *Trend line*: Minimal `<polyline>` with no grid, no axes labels, just the shape. Single accent color stroke.
  - *Proportional bar*: Single `<rect>` elements, no grid, no labels beyond values. Monochrome with accent for emphasis.
  - *Comparison*: Two or three `<rect>` bars side-by-side, minimal spacing, no decoration.

### Charts.css Decision Guide
- IF comparing categories (options, features) → horizontal bar chart (single color, no gridlines)
- IF comparing time periods (quarters, months) → column chart (single color, minimal)
- IF showing trend over continuous time → line chart (single line, no grid)
- IF showing composition → stacked bar chart (single color family, varying opacity)
- IF showing part-to-whole → percentage bar (single accent fill)
- IF comparing multiple series → grouped bar chart (avoid if possible — violates minimalism)
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart — single line, muted gray, no source attribution unless critical
- Do NOT use Charts.css when: fewer than 3 data points (use typographic display), purely qualitative content (use prose), or data is better shown as giant numbers

### Card-Style Information Blocks
- No visible borders — only spacing separation.
- Optional very light background tint.
- Information grouped by proximity alone.

### Prose
- Ultra-minimal. No paragraph longer than 3 sentences. Maximum information per word.
- No transition sentences. No filler. No hedging.
- Active voice only. Declarative statements.

### Section Spacing as Design
- 4-5em vertical gaps between sections — whitespace IS the design.
- No decorative dividers — space alone separates.

### Single Accent Color
- At most ONE accent color, used sparingly. A single blue link. A single highlighted figure.
- The constraint creates elegance.

### Key Insight Line
- A single sentence, bold, slightly larger font, centered — the "thesis statement" of the document.
- Used once, for maximum impact.

### Edge Cases & Adaptations
- **No quantitative data**: For purely qualitative topics, use typographic emphasis (bold, size) for key phrases instead of numbers. Replace charts with concise prose statements.
- **Too much data**: Minimalism cannot handle hundreds of data points. Summarize to the 3-5 most critical metrics. Use `<details>` for full data if absolutely necessary — but consider whether minimalism is the right skill.
- **Mixed content**: When some numbers exist, show only the 3 most important as typographic elements. Everything else goes into a borderless table.
- **Contradictory sources**: State the disagreement in one sentence. Do not create comparison tables — that violates minimalism. Pick the most credible source and note the disagreement inline.
- **Variable chapter length**: Short topics get a single takeaway + 3 metrics. Long topics — reconsider if minimalism is appropriate. If forced, use multiple sections each with their own takeaway.
- **Default format mismatch**: If the topic demands rich visual explanation, minimalism is the wrong skill. Flag this and borrow sparingly from other skills only for essential elements.

## Citation Style — Minimalist Sources
- Inline, ultra-discreet: "(Source: `<a href='URL'>link</a>`)" — never more than necessary.
- Or a single "Sources" line at the document end listing URLs.
- Citations are footnotes to footnotes — present but invisible unless sought.
- **Multiple formats**: Use inline parenthetical for data claims. No formal reference list unless legally required.
- **No URL available**: Cite as "(Source: Organization Name, Date)" — minimal attribution.
- **Multiple sources for same claim**: Cite only the most authoritative source. Minimalism does not do source lists.
- **Beautiful citations**: Style as a single muted-gray line at document end. No table, no numbering, no decoration.
- **Source credibility hierarchy**: Official data source > established publication > expert source. Cite only the top source.

## Typography & Color — The Minimalist Palette

### Fonts
- **Body**: Geometric sans-serif — Inter (first choice), Outfit, Helvetica Neue, SF Pro. Every glyph mathematically precise.
- **Key numbers**: Extra bold (800-900), oversized (2-3rem).
- **Labels**: Small (0.75rem), uppercase, letter-spacing 0.1em, muted gray — the faintest whisper of context.

### Color System — Absence as Aesthetic
- **Background**: White (#FFFFFF) — not off-white, not cream. Pure.
- **Body text**: Near-black (#1A202C) — confident, not harsh.
- **Labels/captions**: Muted gray (#A0AEC0) — barely there.
- **Dividers**: Whisper gray (#EDF2F7) — rules that almost don't exist.
- **Accent (if used at all)**: Single cool blue (#3182CE) — applied to ONE element on the page.
- **Line height**: 1.5 — tighter than most. Dense, considered.
- **Max width**: 600px — narrow. Focused. Intimate.
- **Paragraph spacing**: 0.5em — tight, controlled.
- **Extended chart palette** (7+ colors, rarely used): Near-black (#1A202C), Muted gray (#A0AEC0), Blue (#3182CE), Steel (#4A5568), Light gray (#CBD5E0), Whisper (#EDF2F7), White (#FFFFFF). All WCAG AA compliant.
- **Semantic color rules**: Near-black = primary data/text. Muted gray = secondary/labels. Blue = single accent for emphasis. Steel = tertiary data (avoid if possible). Light gray = structural elements. Whisper = dividers. White = background only.
- **Hover/interaction**: None. Minimalism is static and confident.
- **Print-friendly**: The entire palette is inherently print-friendly — it's already grayscale-adjacent.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio on white. The near-black on white = 16.5:1 — excellent. Blue (#3182CE) on white = 4.6:1 — meets minimum.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Brevity is the entire point.** If the content is too complex for minimalism, consider whether this skill is the right choice. But IF it's selected, commit fully to concision.
- **Cut ruthlessly.** For every sentence, ask: does this add new information? If not, delete it.
- **Never sacrifice critical data.** Minimalism means showing LESS, not hiding what matters. The key numbers must be prominent. Everything else can be removed.
- **Don't force complexity.** If the content naturally lends itself to 3 bullet points, don't expand to 10 for "completeness." Minimalism rewards restraint.
- **One accent color maximum.** If you feel the need for a second color, rethink the design.
- Never presents a minimalist report without at least one carefully crafted visual. Even minimal reports need one strong visual anchor — an SVG diagram, a key number display, or a clean chart.
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., key number display + minimal chart + short analysis, or single-statement callout + sparse data table + brief context). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never uses decorative elements, gradients, or illustrations
- Never writes more than 3 sentences per paragraph
- Never uses serif fonts — this is geometric and modern
- Never uses visible borders when spacing works
- Never uses more than one accent color
- Never uses complex chart configurations
- Never uses ornamental dividers or icons
- Never uses SVG diagrams unless the visual is essential and cannot be expressed in typography
- Never cites more than one source per claim
- Never uses hover effects or interactive elements
- Never skips SVG visualizations when the data supports them — at least one carefully crafted visual is mandatory per chapter. Even minimal reports need one strong visual anchor — an SVG diagram, a key number display, or a clean chart.


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
