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

## Citation Style — Business/Startup Sources
- Use inline source attribution: "(Source: `<a href='URL'>Gartner, 2026</a>`)" or "(PitchBook Data, Q1 2026)."
- For market sizing: always cite the research firm or methodology.
- For traction data: "Internal metrics, as of March 2026" or "Per `<a href='URL'>company blog</a>`."
- For competitor data: cite the public source — Crunchbase, annual reports, press releases.
- Investor-grade credibility requires sourced market claims. Never state market size without attribution.

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

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If there are 8 competitive advantages, show all 8 in a grid — just use more rows.
- **Every claim needs a metric.** "We're growing fast" is unacceptable. "340% YoY revenue growth" is a pitch.
- **Match the stage.** Pre-seed pitches emphasize market + team. Series B emphasizes unit economics + traction. IPO-stage emphasizes financial performance.
- **Build new formats.** If content demands a "Pricing Comparison Matrix," a "Go-to-Market Playbook," or a "Risk Mitigation Table," create it.
- **Energy, not decoration.** Bold colors and big numbers create energy. Gradients and illustrations create decoration. This skill wants the former.

### What This Report NEVER Does
- Never uses long paragraphs
- Never hides metrics in prose
- Never uses muted, timid energy — pitches have conviction
- Never presents a market claim without sourced data
- Never buries the competitive advantage
