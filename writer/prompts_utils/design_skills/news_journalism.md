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

## Citation Style — Journalistic Sources
- Use inline source attribution naturally in prose: "according to `<a href='URL'>Reuters</a>`" or "a `<a href='URL'>White House statement</a>` said."
- For data: "(Source: `<a href='URL'>Bureau of Labor Statistics</a>`, March 2026)."
- For documents: "(Full text: `<a href='URL'>link</a>`)."
- For named sources: direct attribution in text. For unnamed: "a senior official who spoke on condition of anonymity."
- Journalistic citations are woven INTO the text, not relegated to footnotes.

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

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If there are 8 stakeholder perspectives, include all 8 with proper attribution.
- **The lede is sacred.** The most important fact must be in the very first paragraph. Period.
- **Adapt the format to the story type.** Breaking news → ultra-short paragraphs, timeline, dateline. Investigative feature → longer analytical sections, context boxes. Data story → heavy Charts.css usage.
- **Build new patterns.** If the content demands a "Fact Check" comparison box, a "Policy Impact Table," or an "Expert Panel Roundup," create it.
- **Sources are non-negotiable.** Every factual claim must be attributed. Every data point sourced. No exceptions.

### What This Report NEVER Does
- Never presents a quote without full attribution
- Never buries the lede
- Never uses first person or opinion in body text
- Never uses decorative visual elements
- Never presents unsourced claims as fact
- Never uses warm/historical colors — news is current and cool-toned
