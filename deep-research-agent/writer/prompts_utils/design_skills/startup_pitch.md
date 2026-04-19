# Startup & Pitch Report Design

## Identity & Scope
This skill activates when the user's query is about startups, business plans, market opportunities, investment pitches, product strategy, competitive analysis, go-to-market, or any forward-looking, persuasive business content. Think of a Sequoia Capital memo, a YC application, a Benchmark pitch review, or a premium pitch deck converted to a document.

## How a Real Pitch Looks & Feels
A pitch document is BOLD and CONFIDENT. Giant numbers. Clean grids. Minimal prose — every section makes one clear point backed by a metric. The visual energy is high but controlled. Think slides-in-document format: a big visual statement followed by brief supporting text. Charts show GROWTH, not complexity. The overall impression is forward momentum, clarity, and conviction. It feels like the future is inevitable. Color is confident — deep navies, vibrant greens for growth, bold accents.

## What Information Matters Most to Investors & Business Strategists
- **Market size**: TAM/SAM/SOM — how big is the opportunity? Numbers dominate.
- **Traction proof**: Don't tell me your product is great. Show me the users, the revenue, the growth rate.
- **Unit economics**: CAC, LTV, burn rate, months of runway. The math of sustainability.
- **Competitive moat**: Why can't someone else do this? What's defensible?
- **Team credibility**: Who's building this and why they're the right people.
- **The "why now"**: Why is this the right moment for this product/company?
- **Clear ask**: What does the company need? How much capital? For what milestones?

## Content Structure & Narrative Flow
1. **The Problem**: Market pain, painted with data.
2. **The Solution**: How this product/company solves it. Clear, specific.
3. **Market Opportunity**: TAM/SAM/SOM. Numbers dominate.
4. **Traction & Metrics**: Users, revenue, growth rates.
5. **Business Model & Ask**: How money is made, what's needed.

## Complete Visual Toolkit — Everything the LLM Can Use

### Giant Metric Callouts
- The most important numbers displayed EXTRA LARGE: 3-4rem, 800-900 font weight.
- Centered, small label above, giant number, trend indicator below.
- The pitch-deck-slide-headline of documents.
- Can include multiple metrics in a CSS grid row.

### Feature / Value Proposition Grids
- CSS Grid (3 columns) for product features or competitive advantages.
- Each cell: icon/emoji, bold title, one-line description.
- Clean, balanced, scannable.
- Can scale to 2 or 4 columns based on content.

### Charts.css for Growth Visualization
- **Line charts**: Revenue trajectory, user adoption curve — the MOST important chart. Shows momentum.
- **Bar charts**: Revenue by segment, feature comparison, market sizing.
- **Area charts**: TAM visualization, cumulative growth.
- **Column charts**: QoQ comparisons, milestone progression.
- **Percentage bars**: Market penetration, conversion funnels.
- **Stacked bars**: Revenue composition, cost breakdown.
- Bold colors — navy, green for growth, blue for neutral. Growth should FEEL upward.

### SVG Custom Charts
- **Funnel diagrams**: Conversion funnels from awareness to purchase.
- **Pie/donut**: Market share split, revenue distribution.
- **Comparison bars**: Us vs. competitor on a single metric.
- **Gauges**: Target achievement, NPS scores, satisfaction metrics.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide charts (growth trajectories, revenue bars, funnel diagrams); `viewBox="0 0 400 400"` for square diagrams (donut charts, gauge meters, TAM concentric circles).
- **Font sizing**: `font-family` must match body font (Inter/Outfit). Axis labels 12px, chart titles 14px, data labels 11px.
- **Stroke widths**: 1.5px for grid lines, 2px for data lines, 2.5px for axes, 1px for decorative elements.
- **Color application**: Use the exact startup palette — Deep navy (#1A365D), Vibrant green (#38A169), Bold blue (#3182CE), Purple (#805AD5). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Revenue growth trajectory: Q1 2024 – Q4 2025") and `<desc>` (describe the trend, key inflection points, and growth rate).
- **Background**: Transparent — pitch charts overlay on white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Dollar amounts use `<tspan>` for currency + value.
- **Domain-specific SVG patterns**:
  - *Funnel diagram*: Sequential `<rect>` elements decreasing in width, `<text>` stage labels and conversion rates, `<path>` arrows between stages.
  - *Donut chart*: `<circle>` with `stroke-dasharray` for segments, center `<text>` for total/metric, legend via `<text>` + colored `<rect>` swatches.
  - *TAM concentric circles*: Nested `<circle>` elements with `<text>` labels (TAM → SAM → SOM), each with dollar value.
  - *Gauge/meter*: `<path>` arc for the gauge range, `<line>` needle pointer, `<text>` value and label below.

### Charts.css Decision Guide
- IF comparing categories (features, segments, competitors) → horizontal bar chart
- IF comparing time periods (quarters, months, milestones) → column chart
- IF showing trend over continuous time (revenue, users, growth rate) → line chart
- IF showing composition (revenue split, cost breakdown) → stacked bar chart
- IF showing part-to-whole (market penetration, conversion rate) → percentage bar
- IF comparing multiple series (this year vs. last, us vs. competitor) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart with source attribution
- Do NOT use Charts.css when: fewer than 3 data points (use giant metric callouts), purely qualitative pitch elements (use value proposition grids), or data is better shown as a funnel diagram

### Competitive Comparison Matrices
- "Us vs. Them" tables with ✓/✗ feature matrices.
- Subject company highlighted with accent color/bold.
- Clear visual winner for each dimension.
- Can include pricing comparison rows.

### Goal / Milestone Trackers
- Progress bar fills showing achieved vs. target milestones.
- "Achieved" badges (green) vs. "Upcoming" (gray outline, dashed border).
- Creates a sense of momentum and trajectory.

### Testimonial / Social Proof Blocks
- Customer quotes, advisor endorsements, partner logos.
- Styled blockquotes with name, title, company.
- Star ratings or NPS scores displayed prominently.

### Timeline / Roadmap
- Past achievements (solid, colored) → present → future milestones (dashed outlines).
- Horizontal or vertical depending on number of items.
- Shows trajectory and ambitious-but-credible planning.

### Unit Economics Displays
- Side-by-side metric cards: CAC, LTV, LTV/CAC ratio, payback period.
- Each with clear label and trend.
- The math that proves the business works.

### Market Sizing Visualization
- Concentric circles or nested containers showing TAM → SAM → SOM.
- Each layer labeled with dollar value and percentage.

### Edge Cases & Adaptations
- **No quantitative data**: For early-stage pitches (pre-revenue, pre-product), use market sizing visualizations, competitive matrices, and value proposition grids. Replace growth charts with milestone roadmaps.
- **Too much data**: For mature companies with extensive metrics, summarize with the 5-7 most important KPIs as giant callouts. Use `<details>` for full financial data. Show representative growth charts.
- **Mixed content**: When narrative dominates (e.g., vision/mission sections), use feature grids and testimonial blocks. Reserve Charts.css for traction and market data sections.
- **Contradictory market data**: When market sizing sources disagree, present the range: "TAM estimated at $X–$Y billion" with source attribution. Use the conservative estimate in projections.
- **Variable chapter length**: Short pitches (single product) get problem + solution + metrics + ask. Full company pitches use the complete toolkit with competitive analysis and unit economics.
- **Default format mismatch**: If the startup topic is technical (e.g., "Deep Tech Pitch"), borrow architecture diagram patterns from the coding skill. If it's financial (e.g., "SaaS Metrics Deep Dive"), borrow finance-style data tables and KPI cards.

## Citation Style — Business/Startup Sources
- Use inline source attribution: "(Source: `<a href='URL'>Gartner, 2026</a>`)" or "(PitchBook Data, Q1 2026)."
- For market sizing: always cite the research firm or methodology.
- For traction data: "Internal metrics, as of March 2026" or "Per `<a href='URL'>company blog</a>`."
- For competitor data: cite the public source — Crunchbase, annual reports, press releases.
- Investor-grade credibility requires sourced market claims. Never state market size without attribution.
- **Multiple formats**: Use inline parenthetical for market data, footnote-style for internal metrics, and source blocks for full datasets.
- **No URL available**: Cite as "(Gartner, 'Market Guide for X,' 2026)" — report title and year serve as reference.
- **Multiple sources for same claim**: List in order of recency and credibility: "(PitchBook, Q1 2026; CB Insights, 2025; company filing)."
- **Beautiful citations**: Style source attributions as compact inline text with small source-type indicators. Group market research sources at section end.
- **Source credibility hierarchy**: Company internal data (verified) > SEC filing/annual report > established research firm (Gartner, Forrester) > market data provider (PitchBook, CB Insights) > news article > blog/opinion. Always prefer primary data.

## Typography & Color — The Startup Palette

### Fonts
- **Body**: Modern sans-serif — Inter, Outfit, DM Sans. Contemporary, confident.
- **Metrics**: Extra bold (800-900 weight), 2-4rem. Numbers as visual headlines.
- **Headings**: Clean, bold sans-serif in navy. h2 = 1.6rem, h3 = 1.3rem.

### Color System — Bold, Forward, Confident
- **Background**: White (#FFFFFF) — clean canvas for bold elements.
- **Body text**: Dark gray (#2D3748).
- **Headings/giant metrics**: Deep navy (#1A365D) — authority and ambition.
- **Positive growth**: Vibrant green (#38A169) — growth is the hero.
- **Primary accent**: Bold blue (#3182CE) — confidence, technology.
- **Secondary accent**: Purple (#805AD5) — innovation, premium.
- **Grid card backgrounds**: Very light gray (#F7FAFC).
- **Competitive comparison highlight**: Light blue (#EBF8FF) for "our" row.
- **Milestone achieved**: Green badge (#C6F6D5 bg, #22543D text).
- **Milestone future**: Gray dashed border (#CBD5E0).
- **Line height**: 1.6 — compact, energetic.
- **Extended chart palette** (7+ colors): Deep navy (#1A365D), Bold blue (#3182CE), Vibrant green (#38A169), Purple (#805AD5), Orange (#DD6B20), Teal (#319795), Gold (#D69E2E). All WCAG AA compliant on white.
- **Semantic color rules**: Deep navy = headings/metrics/authority. Bold blue = primary data series/neutral. Vibrant green = growth/positive/achieved. Purple = innovation/premium/secondary series. Orange = warning/caution/attention. Teal = tertiary comparison. Gold = benchmark/target values.
- **Hover/interaction**: On hover, chart elements increase opacity and show exact values. Use CSS `:hover` with smooth transitions. Metric cards can have subtle scale effect.
- **Print-friendly**: All colors maintain ≥ 3:1 contrast in grayscale. Green growth indicators supplemented by ▲ symbols for print legibility.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio. Chart colors ≥ 3:1 against white. Deep navy (#1A365D) on white = 12.5:1 — excellent. Vibrant green (#38A169) on white = 3.0:1 — acceptable for non-text chart elements.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If there are 8 competitive advantages, show all 8 in a grid — just use more rows.
- **Every claim needs a metric.** "We're growing fast" is unacceptable. "340% YoY revenue growth" is a pitch.
- **Match the stage.** Pre-seed pitches emphasize market + team. Series B emphasizes unit economics + traction. IPO-stage emphasizes financial performance.
- **Build new formats.** If content demands a "Pricing Comparison Matrix," a "Go-to-Market Playbook," or a "Risk Mitigation Table," create it.
- **Energy, not decoration.** Bold colors and big numbers create energy. Gradients and illustrations create decoration. This skill wants the former.
- Never presents a pitch without at least one growth or market visualization. If the research contains market data, growth metrics, or competitive landscape, you MUST create at least one SVG chart (market size diagram, growth curve, or competitive matrix).
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., KPI card + growth chart SVG + market size diagram, or traction timeline + competitive matrix + team profile). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never uses long paragraphs
- Never hides metrics in prose
- Never uses muted, timid energy — pitches have conviction
- Never presents a market claim without sourced data
- Never buries the competitive advantage
- Never uses Charts.css without labeled axes and a source caption
- Never presents projections without stating underlying assumptions
- Never uses red/green as the only differentiator — always pair with ▲/▼ symbols
- Never uses decorative gradients — energy comes from data, not decoration
- Never skips SVG visualizations when the data supports them — at least one SVG chart is mandatory per chapter. If the research contains market data, growth metrics, or competitive landscape, you MUST create at least one SVG chart (market size diagram, growth curve, or competitive matrix).


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
