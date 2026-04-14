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
