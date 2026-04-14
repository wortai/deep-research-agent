# Finance & Corporate Report Design

## Identity & Scope
This skill activates when the user's query is about finance, economics, markets, stock analysis, corporate earnings, investment strategy, monetary policy, banking, crypto/fintech, or any topic where numbers, metrics, trends, and financial data are central. The report should look like a Goldman Sachs equity research note, a Bloomberg intelligence briefing, or a McKinsey financial analysis.

## How a Real Financial Report Looks & Feels
A financial document is NUMBERS-FIRST. The reader's eye goes immediately to large metric callouts, colorful charts showing trends, and dense data tables comparing periods. Prose exists to interpret data, not to carry the argument alone. Every claim is backed by a figure. Green universally means up/positive; red means down/negative. Tables are dense with numbers — right-aligned, consistently formatted. Charts dominate — revenue bars, trend lines, pie breakdowns. The overall impression is clinical precision, executive confidence, and data density. A senior analyst should be able to scan this report in 60 seconds and get the key numbers, then read deeper for the analysis.

## What Information Matters Most to Financial Analysts & Business Readers
- **Numbers with context**: Raw numbers are meaningless. $50B revenue is nothing without YoY growth %, industry comparison, or margin context.
- **Trends over time**: Is it going up or down? How fast? Period-over-period comparison is essential.
- **Relative performance**: How does this entity compare to its peers? Peer benchmarking drives investment decisions.
- **Risk quantification**: Not just "there are risks." HOW MUCH down side? What probability? What's the bear case?
- **Forward-looking indicators**: What do leading indicators suggest? Guidance, order backlog, pipeline — the future matters more than the past.
- **Source credibility**: Financial claims require sourced data — SEC filings, earnings calls, Bloomberg terminals, official statistics.
- **Executive summary**: Decision-makers read the first paragraph and the key metrics. If those are weak, the rest doesn't matter.

## Content Structure & Narrative Flow
1. **Executive Summary / Thesis**: Core conclusion in 3-5 sentences with key metrics.
2. **KPI Dashboard**: Critical numbers as large, bold visual cards.
3. **Financial Analysis**: Revenue, margins, cash flow — every claim backed by data.
4. **Valuation & Comparables**: DCF, peer comparisons, growth assumptions.
5. **Risk Assessment**: Downside scenarios with quantified risks.

## Complete Visual Toolkit — Everything the LLM Can Use

### KPI Metric Cards
- CSS Grid (3-4 columns) of large, bold number cards.
- Each card: small uppercase label, giant number, trend indicator (▲ green / ▼ red).
- The FIRST thing the reader sees. Show: Revenue, Net Income, Margins, P/E, Market Cap, Growth.
- Can include sparkline-style mini trends within the card.

### Charts.css — Primary Visualization Engine
Finance is the heaviest Charts.css user:
- **Bar charts**: Revenue by segment, market share, competitor comparison. Vertical or horizontal.
- **Column charts**: Quarterly revenue, monthly performance, period-over-period.
- **Line charts**: Stock price trajectory, revenue growth, margin trends — the most important chart type for finance.
- **Area charts**: Cumulative returns, market growth, cash flow accumulation.
- **Stacked bars**: Revenue composition, cost breakdown, portfolio allocation.
- **Grouped bars**: Multiple data series side-by-side (revenue vs. profit, price vs. volume).
- **Percentage bars**: Market share, expense ratios, asset allocation as horizontal progress bars.
- Always: `show-labels`, `show-data`, descriptive `<caption>`.
- Every Charts.css chart MUST have a `<caption>` element that includes a source attribution. Format: `<caption style="caption-side: top; font-size: 0.875rem; color: #718096; padding: 0.5rem 0;">Chart description. Source: Company 10-K, FY2024.</caption>`
- Color convention: green (#38A169) for growth/positive, red (#E53E3E) for decline/negative, blue (#3182CE) for neutral.

### SVG Custom Financial Charts
When Charts.css doesn't cover the exact pattern:
- **Waterfall charts**: Revenue → minus costs → equals profit, showing build-up/breakdown.
- **Donut/pie representations**: Portfolio allocation, market share, revenue split.
- **Sparklines**: Tiny inline trend lines within table cells showing directional movement.
- **Gauge/meter charts**: Utilization rates, target achievement, capacity usage.
- **Funnel diagrams**: Sales pipeline, conversion rates.
- **Candlestick-style bars**: Simplified price range visualization.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide charts (trend lines, revenue bars, waterfall); `viewBox="0 0 400 400"` for square diagrams (donut charts, gauge meters, portfolio allocation).
- **Font sizing**: `font-family` must match body font (Inter). Axis labels 12px, chart titles 14px, data labels 11px.
- **Stroke widths**: 1.5px for grid lines, 2px for data lines, 2.5px for axes, 1px for decorative elements (sparklines, reference lines).
- **Color application**: Use the exact finance palette — green (#38A169) for positive, red (#E53E3E) for negative, blue (#3182CE) for neutral. No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Q1-Q4 2024 Revenue Trend") and `<desc>` (describe all data points, axes, and trend direction).
- **Background**: Transparent — financial charts sit on white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Dollar amounts use `<tspan>` for currency symbol + value.
- **Domain-specific SVG patterns**:
  - *Waterfall chart*: Sequential `<rect>` elements — first at baseline, subsequent floating (positive above previous, negative below). Connector `<line>` between bars. Final total bar grounded.
  - *Donut chart*: `<circle>` with `stroke-dasharray` for segments. Center `<text>` for total/label. Legend via `<text>` + colored `<rect>` swatches.
  - *Sparkline*: Compact `<polyline>` or `<path>` within table cell. 60×20 viewBox. No axes, no labels — pure trend shape.
  - *Candlestick*: `<rect>` for body (open-close range), `<line>` for wicks (high-low). Green fill for bullish, red for bearish.

### Charts.css Decision Guide
- IF comparing categories (segments, competitors, products) → horizontal bar chart
- IF comparing time periods (quarters, months, fiscal years) → column chart
- IF showing trend over continuous time (stock price, revenue growth) → line chart
- IF showing composition (revenue split, cost breakdown) → stacked bar chart
- IF showing part-to-whole (market share, expense ratio) → percentage bar
- IF comparing multiple series (revenue vs. profit, this year vs. last) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart with source attribution: "Source: Company 10-K, FY2024"
- **NEVER use Charts.css when: fewer than 3 data points** — use a simple table or KPI card instead. Charts.css with 2 data points produces a meaningless visualization that wastes space and confuses readers.
- For Charts.css bar/column charts, use `--size` as a decimal fraction (0.0 to 1.0), NOT as a `calc()` expression. Example: `style="--size: 0.76"` for 76%. Do NOT use `calc(76 * 0.5%)` — this produces invalid CSS.
- **ALL `<th>` elements in Charts.css tables MUST have explicit inline styles** for `font-family`, `font-size`, `font-weight`, `color`, and `padding`. Do NOT rely on browser defaults or inherited styles. Example: `<th style="font-family: Inter, sans-serif; font-size: 0.875rem; font-weight: 600; color: #FFFFFF; background: #1A365D; padding: 0.5rem 0.75rem;">`

### Data Tables — The Workhorse
- Dense, precise financial tables — right-aligned numbers, consistent decimals.
- Multiple time periods (FY2022, FY2023, FY2024) for trend analysis.
- % change columns with conditional green/red text.
- Bold totals and subtotals. Indentation for subcategories.
- Currency formatting: $, €, ¥ with thousand separators.
- Alternating row backgrounds for scannability.
- Can include footnotes for adjusted figures or non-GAAP metrics.

### Conditional Color Coding
- Universal: Green (#38A169) positive, Red (#E53E3E) negative.
- Applied to: table cells, metric cards, chart elements, trend text.
- Bold weight for emphasis on significant changes.

### Comparison & Peer Analysis
- Side-by-side tables for competing companies, funds, instruments.
- Valuation multiples, growth rates, key differentiators.
- Highlight the subject entity with subtle accent background.

### Scenario Analysis / Bull-Bear-Base
- Three cards or columns: Bull (green tint), Base (gray), Bear (red tint).
- Each scenario: probability weight, target value, key assumptions.

### Timeline Event Markers
- Compact CSS timeline for financial events: earnings, acquisitions, regulatory changes.
- Date + event + market impact (price change, if relevant).

### Executive Summary Blocks
- A distinct, shaded block at the very top of the report.
- Contains: the core thesis in 2-3 sentences, the 3-4 most important KPIs, and the recommendation.

### Edge Cases & Adaptations
- **No quantitative data**: For qualitative topics (e.g., "ESG Strategy Trends"), use comparison tables, timeline markers, and prose analysis. Substitute KPI cards with qualitative milestone callouts.
- **Too much data**: For datasets with hundreds of rows (e.g., full ticker histories), summarize with key statistics (mean, median, max, min) in a compact table and show representative Charts.css visualizations. Use `<details>` for full datasets.
- **Mixed content**: When analysis is mostly narrative with some numbers, embed key metrics as inline callouts and use small bar charts only where 3+ comparable values exist.
- **Contradictory sources**: Present competing analyst estimates side-by-side in a table with methodology notes. Show consensus vs. outlier ranges.
- **Variable chapter length**: Short topics (single metric analysis) get KPI cards + one chart + brief prose. Long topics (full company analysis) use the complete toolkit with scenario analysis and peer comparisons.
- **Default format mismatch**: If the finance topic is historical (e.g., "2008 Financial Crisis"), borrow timeline patterns from the history skill. If it's policy-focused, borrow sidebar context boxes from the news skill.

## Citation Style — Financial Sources
- Use inline source attribution: "(Source: Company 10-K, FY2024)" or "(Bloomberg, March 2026)."
- For market data: cite the data provider — Bloomberg, Reuters, Yahoo Finance.
- For regulatory filings: cite the exact filing — "SEC Form 10-K, Filed 2024-02-15."
- For analyst reports: "Source: `<a href='URL'>Goldman Sachs Equity Research</a>`, Date."
- For government statistics: "Source: `<a href='URL'>Bureau of Labor Statistics</a>`, Dataset, Date."
- Financial credibility depends on source quality — always cite, always link.
- **Multiple formats**: Use inline parenthetical for data points, footnote-style numbers for analytical claims, and source blocks for full datasets.
- **No URL available**: Cite as "(SEC Form 10-K, CIK: 0001234567, Filed 2024-02-15)" — filing identifiers serve as permanent references.
- **Multiple sources for same claim**: List all sources in priority order: SEC filing > Bloomberg terminal > company press release > news article. Use "(Source: SEC 10-K; corroborated by Bloomberg)" format.
- **Beautiful citations**: Style source blocks as compact cards with source logo/name, date, document type, and clickable link. Use a subtle hierarchy: primary sources get a green left border, secondary get gray.
- **Source credibility hierarchy**: SEC/official regulatory filing > company earnings call transcript > Bloomberg/Reuters terminal data > analyst report > financial news > blog/opinion. Never cite unverified social media for financial claims.

## Typography & Color — The Finance Palette

### Fonts
- **Body**: Clean monospace for a data-terminal aesthetic — JetBrains Mono (first choice), Fira Code, SF Mono. Finance is numbers-first; monospace gives every figure equal weight and perfect alignment. Line height 1.7 for readability.
- **Numbers**: Tabular figures, right-aligned, consistent weight. Monospace ensures perfect column alignment for financial data.
- **Headings**: Clean sans-serif contrast — Inter, Helvetica Neue. Bold, deep navy. h2 = 1.5rem, h3 = 1.25rem.
- **Prose paragraphs**: When longer narrative text appears, switch to sans-serif (Inter) for comfortable reading. Use monospace for data-heavy sections, tables, KPI cards, and numerical callouts.
- **Table content**: Monospace 0.9rem for dense data tables — ensures perfect decimal alignment.

### Color System — Clinical, Precise, Corporate
- **Background**: White (#FFFFFF) — pristine, professional.
- **Body text**: Dark gray (#2D3748).
- **Headings**: Deep navy (#1A365D) — the color of corporate authority. Investment bank blue.
- **Positive values**: Forest green (#38A169) — universally understood.
- **Negative values**: Clear red (#E53E3E) — instant alarm signal.
- **Neutral accent**: Steel blue (#3182CE).
- **Table headers**: Navy bg (#1A365D), white text — bold, clear anchors.
- **KPI card bg**: Off-white (#F7FAFC), subtle border (#E2E8F0).
- **Scenario cards**: Bull (#F0FFF4 bg), Base (#F7FAFC bg), Bear (#FFF5F5 bg).
- **Line height**: 1.6 — compact, executive-friendly.
- **Chart palette**: Blue (#3182CE), Teal (#319795), Orange (#DD6B20), Purple (#805AD5), Gold (#D69E2E).
- **Extended chart palette** (10 colors): Blue (#3182CE), Teal (#319795), Orange (#DD6B20), Purple (#805AD5), Gold (#D69E2E), Coral (#E57373), Forest (#38A169), Steel (#4A5568), Slate Blue (#6B7FB0), Dusty Rose (#C07C8F). All WCAG AA compliant on white.
- **Aesthetic mid-tone accent palette** (for cards, highlights, subtle backgrounds): Mauve (#B8A9C9), Sage (#9CAF88), Dusty Blue (#8BACC4), Warm Taupe (#A89B8C), Slate (#7B8794), Soft Copper (#B87333), Ocean (#4F7CAC), Muted Olive (#8A9A6B), Pewter (#899499), Ash (#A8A8A0). These are elegant middle tones that add visual richness without competing with data colors.
- **Semantic color rules**: Green = growth/positive/profit. Red = decline/negative/loss. Blue = neutral/baseline/reference. Teal = secondary data series. Orange = warning/caution metrics. Purple = innovation/R&D spend. Gold = premium/benchmark values. Mauve = qualitative/commentary accents. Sage = sustainability/ESG. Dusty Blue = forecast/projected.
- **Hover/interaction**: On hover, chart bars/lines increase opacity and show data value tooltip. Use CSS `:hover` with `opacity` transitions.
- **Print-friendly**: All colors maintain ≥ 3:1 contrast in grayscale. Green/red differentiation supplemented by ▲/▼ symbols for print legibility.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio. Chart colors ≥ 3:1 against white. Green (#38A169) on white = 3.0:1 — acceptable for non-text chart elements. Red (#E53E3E) on white = 3.9:1 — acceptable for chart elements.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains 50 data points, build a bigger table. If there are 10 comparable companies, show all 10 in the peer comparison. Don't truncate data.
- **Charts should match the data.** Line charts for trends, bar charts for comparisons, stacked bars for composition. Never force a chart type that doesn't serve the data.
- **Executive summary is mandatory.** No matter the depth of the report, the first thing visible must be the core conclusion and key metrics.
- **Invent new financial visualizations.** If the content demands a "Competitive Positioning Matrix," a "Revenue Bridge," or a "Sensitivity Table," build it. Real financial analysts use dozens of chart types — the toolkit lists common ones, not the only ones.
- **Numbers are never optional.** If a financial claim is made in prose, a supporting figure MUST appear. Qualitative financial analysis without quantification is unacceptable.
- Never skips SVG financial charts when the data supports them. If the research contains revenue breakdowns, portfolio allocations, valuation comparisons, or trend data, you MUST create at least one SVG chart (waterfall, donut, gauge, or line chart). Tables alone are insufficient for financial analysis.
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., KPI cards + Charts.css chart + data table, or SVG waterfall chart + scenario analysis cards + peer comparison table). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never presents a financial claim without a supporting number
- Never uses warm, decorative colors — finance is cold and precise
- Never buries key metrics in prose — numbers are visual headlines
- Never skips trend comparisons (YoY, QoQ)
- Never shows bare numbers without currency/percentage formatting
- Never omits the source for financial data
- Never uses Charts.css without labeled axes and a data source caption
- Never presents projections without stating the underlying assumptions
- Never uses red/green as the only differentiator — always pair with ▲/▼ symbols
- Never relies solely on tables when SVG financial charts (waterfall, donut, funnel) would communicate more effectively
- Never skips SVG financial charts when the data supports them — at least one SVG financial chart (waterfall, donut, gauge, or line chart) is mandatory per chapter. If the research contains revenue breakdowns, portfolio allocations, valuation comparisons, or trend data, you MUST create at least one SVG chart. Tables alone are insufficient for financial analysis.
