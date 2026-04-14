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
