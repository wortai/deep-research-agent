# History Report Design

## Identity & Scope
This skill activates when the user's query is about history: world events, wars, political movements, civilizations, biographies, ancient/medieval/modern history, or any topic where chronology, cause-and-effect, primary sources, and narrative storytelling are central. Think of a Penguin History, an Oxford Illustrated History, or a Smithsonian Magazine feature.

## How a Real History Book Looks & Feels
A history book is a NARRATIVE document grounded in the passage of time. The pages have warm, aged tones — cream backgrounds, rich brown and burgundy accents reminiscent of leather-bound volumes and archive rooms. Dates are NEVER hidden in prose — they stand out as visual anchors. The most distinctive visual element is the timeline: a visual spine showing the march of events. Primary source quotations appear frequently, giving direct contact with voices of the past. Maps and geographical context sit alongside political narratives. There's an implicit warmth and gravity — the weight of human experience across centuries. Engravings, sepia-toned borders, and classical typography evoke the feeling of opening a rare manuscript.

## What Information Matters Most to Historians & History Readers
- **Chronological precision**: WHEN did it happen? Dates are navigation. Without dates, history is just a story.
- **Causation**: WHY did it happen? What forces, decisions, and conditions made this inevitable or surprising?
- **Primary voices**: What did the people who LIVED it say? Speeches, letters, diaries — firsthand testimony is irreplaceable.
- **Multiple perspectives**: History has winners and losers. Both sides must be heard — the conquered, the colonized, the dissenting.
- **Scale and scope**: How many people? How large an area? How many years? Numbers create the canvas.
- **Legacy chains**: This event → caused this shift → which led to this modern reality. The thread from past to present.
- **Material conditions**: Economics, technology, geography, disease — the physical forces that shape history beyond human decisions.

## Content Structure & Narrative Flow
1. **Setting the Stage**: Political, social, economic conditions BEFORE the events.
2. **Chronological Narrative**: The story in order with clear date anchors.
3. **Primary Source Voices**: Direct quotes from letters, speeches, treaties, diaries.
4. **Analysis & Cause-Effect**: WHY events happened — connecting to larger patterns.
5. **Legacy & Lasting Impact**: How these events shape the world today.

## Complete Visual Toolkit — Everything the LLM Can Use

History is one of the most visually rich domains. Combine these freely to create an immersive experience.

### Timelines — The Defining Visual
Multiple timeline styles available:
- **Vertical CSS timelines**: Continuous left border with date-node circles. Bold date, event description branching right. Built with `border-left`, absolute-positioned circles, `margin-left` for content.
- **Horizontal timelines**: For shorter sequences (5-10 events) — dates above the line, descriptions below.
- **Nested timelines**: Major events as large nodes with sub-events indented beneath.
- **Highlighted turning points**: Certain nodes visually emphasized (larger circle, different color, stronger border) for pivotal moments.
- **Parallel timelines**: Two simultaneous sequences (e.g., events in Europe vs. events in Asia) running side by side.
- **Era markers**: Background color bands spanning the timeline to show different periods (e.g., "Renaissance," "Industrial Revolution").

### Narrative Prose
- Flowing, engaging paragraphs in warm serif. First-line indentation, justified text.
- The writer is a storyteller. Prose draws the reader into the period.
- Short topic sentences anchor each paragraph to a specific moment or theme.
- Transition phrases connect events: "Meanwhile in the East...", "Three years later..."

### Primary Source Quotations
Multiple styles based on source type:
- **Speeches and declarations**: Large blockquotes, warm background, formal attribution (speaker, role, date, occasion).
- **Letters and personal writing**: Slightly softer styling — lighter background, suggesting handwritten correspondence. More intimate feel.
- **Treaties and legal text**: Darker, more formal container — border on all sides, suggesting an official document.
- **Census/statistical data**: Simple tables styled to evoke period documents.
- **Newspaper excerpts**: Could use a bordered container with a "newspaper" font feel — justified text, headline in bold.
- **Oral histories and testimony**: Italic, with clear attribution of the speaker and context of recording.
- Every quote: WHO said it, their TITLE/ROLE, WHERE, and WHEN.

### Date Anchors & Chronological Navigation
- Dates are visually prominent throughout — bold, larger font, accent color.
- Pivotal dates as standalone heading-level elements.
- The reader ALWAYS knows exactly where in time they are.
- Year/decade markers can act as section headers.

### Maps & Geographical Context
- Simple SVG representations: borders, territories, battle positions, trade routes.
- Labeled block containers representing different regions.
- CSS grids for empire comparisons showing territorial extent.
- Arrow overlays showing invasion routes, migration patterns, trade paths.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide diagrams (timelines, trade route maps, battle formations); `viewBox="0 0 400 400"` for square diagrams (territorial maps, coat of arms, seal representations).
- **Font sizing**: `font-family` must match body font (Merriweather/Georgia). Labels 12px, titles 14px, annotations 11px.
- **Stroke widths**: 1.5px for grid/guide lines, 2px for borders and route lines, 2.5px for timeline spines and major borders, 1px for decorative elements.
- **Color application**: Use the exact history palette — Burgundy (#800020), Old Gold (#B8860B), Forest (#228B22), Dark Navy (#000080), Burnt Sienna (#A0522D), Warm Sienna (#8B4513). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Trade routes of the Silk Road, 1st-14th century CE") and `<desc>` (describe all regions, routes, and historical context).
- **Background**: Transparent or archival cream (#FAF8F5) to match the page.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Historical dates use `<tspan font-weight="bold">`.
- **Domain-specific SVG patterns**:
  - *Timeline*: Horizontal `<line>` spine, `<circle>` event nodes, `<text>` date labels above, `<text>` descriptions below. Turning points use larger circles.
  - *Territorial map*: `<path>` shapes for regions with distinct fills, `<text>` labels, `<path>` arrows for invasion/migration routes.
  - *Battle formation*: `<circle>` or `<rect>` unit markers, `<path>` movement arrows, `<text>` commander names and unit types.
  - *Trade route map*: `<path>` curved routes with `<text>` city labels, `<circle>` node markers for key cities.

### Charts.css Decision Guide
- IF comparing categories (armies, rulers, civilizations) → horizontal bar chart
- IF comparing time periods (decades, centuries, reigns) → column chart
- IF showing trend over continuous time (population growth, territory expansion) → line chart
- IF showing composition (army makeup, trade goods, demographic shifts) → stacked bar chart
- IF showing part-to-whole (land control, population distribution) → percentage bar
- IF comparing multiple series (empire A vs. empire B, before vs. after) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart with date range and source
- Do NOT use Charts.css when: fewer than 3 data points (use a table), purely narrative content (use prose + timeline), or data is better shown as a map

### Comparison Tables
- **Opposing forces**: Resources, armies, leadership, strategies — tabular comparison.
- **Treaty terms**: Parties, conditions, outcomes in clean table format.
- **Before/After**: State of a region or people pre- and post-event.
- **Ruler succession**: Ordered list or table of monarchs/leaders with dates and key actions.
- Warm header colors (brown, burgundy) matching the history aesthetic.

### Charts.css for Historical Data
- **Bar charts**: Population changes, casualty counts, GDP comparisons. Use warm, muted colors.
- **Stacked bars**: Army composition, resource allocation, trade goods.
- **Line charts**: Population growth over centuries, territory expansion, inflation.
- **Percentage bars**: Land control, demographic shifts.
- Avoid bright modern colors — use browns, burgundies, golds, muted greens.

### Biographical Panels
- Distinct visual blocks for key figures: name, dates, title/role, brief bio summary.
- Styled like museum placard labels — understated, informative.
- Can include lineage information for monarchs/dynastic histories.

### Era Context Containers
- Subtle background blocks providing period context: "In 1914, Europe was governed by four empires..."
- Orient the reader before diving into specifics.

### Cause-and-Effect Flow Diagrams
- Simple CSS arrow chains: Event A → leads to → Event B → results in → Event C.
- Not complex flowcharts — clear visual causation chains.
- Can branch to show multiple consequences from a single event.

### Artifact & Document Callouts
- When referencing a specific historical document (Magna Carta, Declaration of Independence), give it a special styled container — heavier border, slightly different typography — suggesting a physical artifact.

### Edge Cases & Adaptations
- **No quantitative data**: For purely narrative history (e.g., biography, cultural history), use timelines, primary source quotations, and cause-effect diagrams. Skip Charts.css entirely.
- **Too much data**: For topics spanning centuries with hundreds of events, use era-level timelines with nested `<details>` for detailed sub-timelines. Show representative charts for key periods.
- **Mixed content**: When narrative dominates with occasional statistics, embed key numbers inline and use charts only for sections with 3+ comparable data points.
- **Contradictory sources**: When historians disagree, present competing interpretations side-by-side with source attribution. Note the historiographical school each represents.
- **Variable chapter length**: Short topics (single event) get timeline + primary sources + analysis. Long topics (era/civilization) use the complete toolkit with biographical panels and era containers.
- **Default format mismatch**: If the history topic is data-heavy (e.g., "Economic History of the Roman Empire"), borrow finance-style data tables. If it's philosophical (e.g., "Enlightenment Ideas"), borrow philosophy quotation patterns.

## Citation Style — Historical Sources
- Use inline author-date for secondary sources: (Hobsbawm, 1962, p. 47).
- For primary sources: "(Lincoln, Gettysburg Address, 1863)" or "(Treaty of Versailles, Article 231, 1919)."
- For archival sources: describe the archive and document type.
- Source links: `<a href="URL">National Archives</a>` or the digitized primary source.
- Full bibliography at chapter end — Chicago Manual of Style format (preferred for history).
- Primary vs. secondary sources should be visually or structurally distinguishable in the reference list.
- **Multiple formats**: Use author-date for scholarly claims, descriptive citations for primary sources, and source blocks for archival materials.
- **No URL available**: Cite as "Author, *Title*, Publisher, Year, p. XX" for books; "Archive Name, Collection, Box X, Folder Y" for archival materials.
- **Multiple sources for same claim**: List chronologically: "(Smith, 1990; Jones, 2005; Williams, 2018)" — showing the historiographical evolution.
- **Beautiful citations**: Style the bibliography as a clean list with primary sources in a separate section (warm border accent) from secondary sources. Use italics for titles, small caps for author names.
- **Source credibility hierarchy**: Primary source (eyewitness, document, artifact) > peer-reviewed historical monograph > academic journal article > reputable popular history > general reference. Always prefer primary sources.

## Typography & Color — The History Palette

### Fonts
- **Body**: Warm serif — Merriweather (first choice), Georgia, Lora. History is storytelling.
- **Headings**: Same serif family, heavier weight, or Playfair Display for chapter headings.
- **Dates**: Bold, slightly larger, warm brown accent — dates are navigation anchors.
- **Primary sources**: Slightly different serif or italic weight to distinguish quoted voices from analysis.

### Color System — Warm, Archival, Authoritative
- **Background**: Archival cream (#FAF8F5) — the color of old paper under warm light.
- **Body text**: Deep brown (#3E2723) — warm, human, readable.
- **Headings**: Dark brown (#4E342E) — rich and authoritative.
- **Date anchors**: Warm sienna (#8B4513) — the color of aged leather bindings.
- **Timeline spine**: Same warm sienna (#8B4513).
- **Primary source blocks**: Warm stone (#EFEBE9) — parchment-adjacent.
- **Table headers**: Medium coffee (#795548), white text.
- **Chart palette**: Burgundy (#800020), Old Gold (#B8860B), Forest (#228B22), Dark Navy (#000080), Burnt Sienna (#A0522D).
- **Dividers**: Muted warm gray (#BCAAA4).
- **Line height**: 1.8.
- **Max width**: 750px — wide enough for timelines, narrow enough for narrative.
- **Extended chart palette** (7+ colors): Burgundy (#800020), Old Gold (#B8860B), Forest (#228B22), Dark Navy (#000080), Burnt Sienna (#A0522D), Olive (#6B8E23), Rust (#B7410E). All WCAG AA compliant on cream background.
- **Semantic color rules**: Burgundy = primary/emphasis series. Old Gold = secondary/wealth/trade data. Forest = growth/population. Dark Navy = military/power metrics. Burnt Sienna = territorial/geographic data. Olive = agricultural/economic base. Rust = conflict/casualty data.
- **Hover/interaction**: On hover, chart elements increase opacity to 1.0 while others dim to 0.6.
- **Print-friendly**: All warm colors maintain ≥ 3:1 contrast on cream in grayscale. Burgundy and navy provide strongest print contrast.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio on cream (#FAF8F5). Chart colors ≥ 3:1 against cream. The warm palette is colorblind-safe.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research covers 200 years, build a longer timeline. If there are 12 primary sources, quote all 12 — vary the quote styling to avoid monotony.
- **Chronology is king.** Even when the analysis is thematic, anchor every section to specific dates. The reader must always know WHERE in time they are.
- **Build new containers for unique content.** If the research demands a "Dynastic Succession Chart" or a "Trade Route Map," build it. The toolkit describes common patterns, not limitations.
- **Scale the timeline to the scope.** A report on "The French Revolution (1789-1799)" needs a detailed month-by-month timeline. A report on "The Fall of Rome" needs a century-scale timeline with different granularity.
- **Let primary sources breathe.** A powerful speech deserves a full blockquote, not a one-line excerpt. If the source material is rich, let the voices of the past speak at length.
- Never presents historical events without a timeline visualization. If the research contains chronological data, you MUST create at least one SVG timeline or period map.
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., timeline SVG + primary source quote + period map, or chronology table + cause-effect diagram + legacy analysis). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never presents events out of chronological order without explicit justification
- Never discusses a period without specific date anchors
- Never uses cold, clinical colors — history is warm and human
- Never presents a quote without full attribution (who, role, where, when)
- Never uses bullet points for historical narrative — prose tells the story
- Never shows a sequence of events without timeline or date structure
- Never treats all primary sources identically — a letter and a treaty look different
- Never uses Charts.css without a date range in the caption
- Never presents a single historical interpretation as the only truth
- Never uses modern bright colors that clash with the archival aesthetic
- Never skips SVG visualizations when the data supports them — at least one SVG timeline or period map is mandatory per chapter. If the research contains chronological data, you MUST create at least one SVG timeline or period map.
