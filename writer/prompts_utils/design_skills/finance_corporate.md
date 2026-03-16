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
- Color convention: green (#38A169) for growth/positive, red (#E53E3E) for decline/negative, blue (#3182CE) for neutral.

### SVG Custom Financial Charts
When Charts.css doesn't cover the exact pattern:
- **Waterfall charts**: Revenue → minus costs → equals profit, showing build-up/breakdown.
- **Donut/pie representations**: Portfolio allocation, market share, revenue split.
- **Sparklines**: Tiny inline trend lines within table cells showing directional movement.
- **Gauge/meter charts**: Utilization rates, target achievement, capacity usage.
- **Funnel diagrams**: Sales pipeline, conversion rates.
- **Candlestick-style bars**: Simplified price range visualization.

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

## Citation Style — Financial Sources
- Use inline source attribution: "(Source: Company 10-K, FY2024)" or "(Bloomberg, March 2026)."
- For market data: cite the data provider — Bloomberg, Reuters, Yahoo Finance.
- For regulatory filings: cite the exact filing — "SEC Form 10-K, Filed 2024-02-15."
- For analyst reports: "Source: `<a href='URL'>Goldman Sachs Equity Research</a>`, Date."
- For government statistics: "Source: `<a href='URL'>Bureau of Labor Statistics</a>`, Dataset, Date."
- Financial credibility depends on source quality — always cite, always link.

## Typography & Color — The Finance Palette

### Fonts
- **Body**: Clean sans-serif — Inter (first choice), Helvetica Neue, -apple-system. Financial docs are screen-optimized.
- **Numbers**: Tabular figures (if font supports it), right-aligned, consistent weight.
- **Headings**: Same sans-serif, bold, deep navy. h2 = 1.5rem, h3 = 1.25rem.
- **Table content**: 0.9rem for dense data tables.

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
- **Chart palette**: Blue (#3182CE), Teal (#319795), Orange (#DD6B20), Purple (#805AD5), Gold (#D69E2E).
- **Line height**: 1.6 — compact, executive-friendly.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains 50 data points, build a bigger table. If there are 10 comparable companies, show all 10 in the peer comparison. Don't truncate data.
- **Charts should match the data.** Line charts for trends, bar charts for comparisons, stacked bars for composition. Never force a chart type that doesn't serve the data.
- **Executive summary is mandatory.** No matter the depth of the report, the first thing visible must be the core conclusion and key metrics.
- **Invent new financial visualizations.** If the content demands a "Competitive Positioning Matrix," a "Revenue Bridge," or a "Sensitivity Table," build it. Real financial analysts use dozens of chart types — the toolkit lists common ones, not the only ones.
- **Numbers are never optional.** If a financial claim is made in prose, a supporting figure MUST appear. Qualitative financial analysis without quantification is unacceptable.

### What This Report NEVER Does
- Never presents a financial claim without a supporting number
- Never uses warm, decorative colors — finance is cold and precise
- Never buries key metrics in prose — numbers are visual headlines
- Never skips trend comparisons (YoY, QoQ)
- Never shows bare numbers without currency/percentage formatting
- Never omits the source for financial data
