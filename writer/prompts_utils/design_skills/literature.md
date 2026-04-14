# Literature Report Design

## Identity & Scope
This skill activates when the user's query is about literature, poetry, novels, plays, literary criticism, narrative analysis, authorial style, or textual analysis. The report should look like a high-end literary journal or a beautifully typeset critical edition — The Paris Review, Penguin Modern Classics interiors, or an Oxford World's Classics annotated edition.

## How a Real Literature Book Looks & Feels
A literary text or literary criticism volume is perhaps the most typographically sensitive document. The text itself IS the art. The page has almost no charts, no dashboards. Instead: a single narrow column of beautifully set text with enormous respect for whitespace and line breaks. Poetry is set with sacred precision — every line break intentional, never reflowed. Blockquotes from the original work are visually elevated, like a painting hung in a gallery. The overall impression is quiet elegance, bookishness, and reverence for the written word. The page whispers; it never shouts. You feel like you're holding a first edition under warm library light.

## What Information Matters Most to Literature Scholars & Readers
- **The text itself**: Original passages are the primary evidence. Everything revolves around WHAT the author wrote, not just what critics SAID about it.
- **Context of creation**: When was this written? What was happening in the author's life? What literary movement does it belong to?
- **Close reading**: The magic is in the details — a single word choice, a line break, an unusual comma. Analysis at the sentence level.
- **Intertextuality**: How does this work respond to, reference, or subvert other works? Literary echoes and allusions.
- **The author's voice and style**: Sentence rhythm, diction choices, use of metaphor, narrative perspective.
- **Reader experience**: What does this text DO to you? Emotional and aesthetic impact matters alongside intellectual analysis.
- **Evolution of interpretation**: How has this work been read differently across generations?

## Content Structure & Narrative Flow
1. **The Work & Its Author**: Biographical context, era, literary movement.
2. **Synopsis & Narrative Structure**: Plot summary; analysis of the structure (linear, fragmented, epistolary, etc.).
3. **Textual Excerpts & Close Reading**: Pull exact passages and analyze word by word.
4. **Thematic Analysis**: Core themes traced with textual evidence.
5. **Legacy & Influence**: Impact on later literature and culture.

## Complete Visual Toolkit — Everything the LLM Can Use

Literature reports achieve visual richness through TYPOGRAPHY, WHITESPACE, and TEXT PRESENTATION.

### Prose & Paragraph Styling
- Flowing, justified paragraphs, generous line-height (1.85–1.9).
- First-line indentation (2em) on consecutive paragraphs — real book typesetting.
- Body font slightly larger (1.1rem).
- Max content width 680px — narrow column like a real book page.
- `hyphens: auto` for cleaner justified edges.
- Drop caps on section openers — first letter 3x body size, decorative serif, floated left.

### Textual Excerpts — The Sacred Element
Multiple styles for quoting original works:
- **Block quotations**: Generous indentation, different font weight or italic, with `<footer>` or `<cite>` showing author, work, chapter/page, year.
- **Centered poetry blocks**: `white-space: pre-wrap`. NEVER reflow poetry. Each stanza separated by extra vertical space. Preserve exact indentation the poet intended.
- **Inline quotations**: Short phrases in `<q>` tags with smart-quote CSS.
- **Epigraphs**: Right-aligned, smaller italic font, setting tone before analysis.
- **Extended passages**: Long excerpts in a visually distinct container — slight background tint, or increased margin.
- **Parallel translations**: For analyzing works in translation, show original language on the left and translation on the right using a subtle two-part container.
- **Dramatic dialogue**: For plays, format character names in small caps followed by their lines, preserving the dramatic script format.

### Close Reading Annotations
- `<mark>` tags with very light yellow background (#FFF9C4) to highlight analyzed words/phrases within quoted passages.
- Immediately follow with an analysis paragraph on WHY that language choice matters.
- Subtle CSS underline decorations for alliteration, meter, or rhyme patterns.
- Footnote-style numbered annotations for line-by-line analysis of poetry.

### Author & Context Presentations
- **Author intro blocks**: Name as heading, then dates/nationality/movement in metadata line (smaller, italic, muted).
- **Biographical sidebars**: Floating or inset boxes with author life context.
- **Literary movement context**: Subtle containers about the broader movement (Romanticism, Modernism, Postcolonialism).
- **Publication history**: When relevant, a brief note on the work's publication journey.

### Section Flow & Dividers
- Centered ornamental elements: ✦, ── ✦ ──, thin decorative `<hr>`.
- Extra vertical spacing (3em+) between major sections.
- Transitions should feel like turning a page in a hardcover.

### SVG Diagrams for Literary Structure
- **Narrative structure diagrams**: Freytag's pyramid, narrative arcs, plot tension curves.
- **Character relationship maps**: Elegant labeled connections between characters.
- **Thematic recurrence maps**: Showing where themes appear across chapters/acts.
- **Influence trees**: Literary lineage — who influenced whom.
- Use minimal, elegant SVG — these are literary tools, not data charts.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide diagrams (narrative arcs, influence trees); `viewBox="0 0 400 400"` for square diagrams (character relationship maps, thematic circles).
- **Font sizing**: `font-family` must match body font (EB Garamond). Labels 12px, titles 14px, annotations 11px.
- **Stroke widths**: 1.5px for guide lines, 2px for connection lines and arcs, 2.5px for borders, 1px for decorative elements.
- **Color application**: Use the exact literature palette — near-black (#1A1A1A), warm gray (#BDBDBD), medium gray (#757575), light yellow (#FFF9C4). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Freytag's pyramid for Hamlet") and `<desc>` (describe the narrative structure and key plot points).
- **Background**: Transparent or soft white (#FAFAFA) to match the page.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Character names use `<tspan font-variant="small-caps">`.
- **Domain-specific SVG patterns**:
  - *Freytag's pyramid*: `<path>` arc shape (exposition → rising → climax → falling → denouement), `<text>` labels at each stage, `<text>` plot events positioned along the curve.
  - *Character relationship*: `<circle>` character nodes, `<path>` connection lines with `<text>` relationship labels. Line weight indicates relationship strength.
  - *Influence tree*: Root `<text>` or `<rect>` for origin author, branching `<path>` lines to influenced authors. Chronological left-to-right flow.
  - *Thematic recurrence*: Vertical `<line>` representing the work's length, horizontal `<line>` marks at chapter/act positions where a theme appears, labeled `<text>`.

### Charts.css Decision Guide
- Literature reports RARELY use Charts.css — this is a prose-first domain.
- IF comparing categories (themes across works, author characteristics) → horizontal bar chart (only if quantitative data exists)
- IF comparing time periods (publication dates, literary periods) → column chart
- IF showing trend (word frequency, sentiment analysis in computational literary studies) → line chart
- IF showing composition (genre distribution in an author's oeuvre) → stacked bar chart
- Do NOT use Charts.css when: data is purely textual/qualitative (use prose analysis), fewer than 3 data points, or the comparison is better served by a side-by-side passage comparison.
- When used: `class="charts-css [type]" show-labels show-data show-headings` with muted, warm colors only.

### Thematic & Structural Analysis Visuals
- **Theme tracking**: Indented list or minimal timeline showing a theme's appearances across chapters/acts.
- **Character relationship maps**: Elegant labeled connections — not data visualizations, but literary relationship diagrams.
- **Narrative structure diagrams**: Minimal SVG arc for Freytag's pyramid (exposition, rising action, climax, falling, denouement).
- **Motif repetition displays**: A vertical list showing where and how a recurring symbol appears across the text.

### Comparative Analysis Layouts
- When comparing works, authors, or interpretations: alternating sections with clear labels.
- For brief comparisons: minimal 2-column table (Work A vs Work B, Theme X vs Theme Y).
- **Side-by-side passage comparison**: Two quoted passages showing how different authors treat the same subject.

### Reading Lists & Further Reading
- Elegantly styled lists of related works — author, title (italic), year.
- Can include brief one-line annotations for each recommendation.

### Edge Cases & Adaptations
- **No quantitative data**: This is the DEFAULT state for literature. Use SVG narrative diagrams, close reading annotations, and textual comparison layouts. Charts.css is almost never appropriate.
- **Too much data**: For computational literary analysis (e.g., word frequency across 100 novels), summarize with key statistics and show representative charts. Use `<details>` for full data tables.
- **Mixed content**: When literary analysis includes some statistics (e.g., stylometry), embed key metrics inline and use small charts only for sections with 3+ comparable data points.
- **Contradictory interpretations**: Present competing critical readings side-by-side with clear attribution to each school of criticism. Note the interpretive lens each uses.
- **Variable chapter length**: Short topics (single poem) get the full text + close reading. Long topics (author's complete works) use the complete toolkit with influence trees and thematic maps.
- **Default format mismatch**: If the literature topic is historical (e.g., "History of the Novel"), borrow timeline patterns from the history skill. If it's philosophical (e.g., "Existentialism in Dostoevsky"), borrow philosophy argument patterns.

## Citation Style — Literary Sources
- Use inline author-date or parenthetical citations: (Fitzgerald, 1925, Ch. IX) or (Eliot, "Prufrock," l. 45).
- For poetry: cite by line number (l. 45) or stanza number.
- For plays: cite by Act, Scene, and line — (Shakespeare, *Hamlet*, III.i.56).
- For novels: cite by chapter or page if a specific edition is referenced.
- Direct quotes ALWAYS include: author name, work title (italicized), specific location in the text, and year.
- Source links formatted as: `<a href="URL">Project Gutenberg</a>` or the critical edition.
- Full works-cited list at chapter end — MLA style or similar humanities format.
- In literary analysis, citations are acts of respect — they show which voices and texts are being engaged.
- **Multiple formats**: Use parenthetical for textual claims, footnote-style numbers for critical theory references, and source blocks for archival manuscripts.
- **No URL available**: Cite as "Author, *Title*, Publisher, Edition, Year, p. XX" — standard bibliographic format. For manuscripts: "Archive Name, MS Collection, Folio X."
- **Multiple sources for same claim**: List critical sources chronologically to show interpretive evolution: "(Bradley, 1904; Bloom, 1994; Greenblatt, 2004)."
- **Beautiful citations**: Style the works-cited list with hanging indents, italic titles, and a subtle warm border. Separate primary works (the texts being analyzed) from secondary sources (criticism) with a decorative divider.
- **Source credibility hierarchy**: Authoritative critical edition (Oxford, Penguin Classics) > peer-reviewed literary criticism > established literary journal > reputable review/essay > general reference. Always prefer the most authoritative edition of the primary text.

## Typography & Color — The Literature Palette

### Fonts
- **Body text**: Premium serif — EB Garamond (first choice), Cormorant Garamond, or Palatino. Must feel like a printed book.
- **Excerpts**: Same family italic, or Courier Prime (typewriter monospace) for certain effects — manuscript feel.
- **Headings**: Playfair Display or similar display serif. Understated sizing — headings should not overpower the text.
- **Character names in drama**: Small caps of the body font.

### Color System — Quiet, Bookish, Neutral
- **Background**: Soft white (#FAFAFA) — not stark, not yellow. Neutral and gentle.
- **Body text**: Near-black (#1A1A1A) — dark enough for authority, soft enough for long reads.
- **Headings**: Pure black (#111111) or deep near-black.
- **Metadata/captions**: Medium gray (#757575) — present but recessive.
- **Annotations/highlights**: Very light yellow (#FFF9C4) — like a pencil mark on a library page.
- **Dividers**: Light gray (#E0E0E0) — barely there.
- **Blockquote accents**: Very subtle left border in warm gray (#BDBDBD) or none at all — just indentation.
- **Epigraph text**: Lighter gray (#616161).
- **Line height**: 1.85–1.9 — generous literary reading pace.
- **Max width**: 680px — narrow, focused, bookish.
- **Extended chart palette** (7+ colors, for rare quantitative use): Near-black (#1A1A1A), Warm gray (#BDBDBD), Medium gray (#757575), Light yellow (#FFF9C4), Sepia (#704214), Burgundy (#800020), Dark olive (#556B2F). All WCAG AA compliant on soft white.
- **Semantic color rules**: Near-black = primary text/data. Warm gray = secondary/structural elements. Medium gray = metadata/annotations. Light yellow = highlights/analyzed passages. Sepia = historical/manuscript references. Burgundy = emphasis/key themes. Dark olive = nature/pastoral motifs (when relevant).
- **Hover/interaction**: Minimal — literature is a reading medium, not interactive. Subtle underline on links only.
- **Print-friendly**: The entire palette is designed for print. All colors maintain excellent contrast on soft white in grayscale.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio on soft white (#FAFAFA). Chart colors ≥ 3:1. The muted palette is inherently accessible.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research sources contain 10 textual excerpts, present all 10 — use varying quotation styles to avoid visual monotony.
- **Poetry is inviolable.** Never reflow, rejustify, or alter the line breaks of any quoted poem. `white-space: pre-wrap` is mandatory. If the poem is long, show it in its entirety — poems are not summarized.
- **Build new containers when needed.** If the content demands a "Translation Comparison" layout or a "Dramatic Scene Breakdown," build it. The skill defines the aesthetic, not the limits.
- **Match tone to genre analyzed.** Analyzing a Romantic poem? The prose can be slightly warmer. Analyzing a brutalist postmodern novel? The prose can be more clipped and contemporary. The core aesthetic (serif, narrow column, warm neutrals) stays, but register can flex.
- **Excerpts are primary evidence, not decoration.** Every quote used must be analyzed. Don't include a beautiful passage without explaining why it matters.
- Never presents literary analysis without at least one structural visual. If the research contains narrative analysis, character relationships, or thematic patterns, you MUST create at least one SVG diagram (narrative arc, character map, or thematic recurrence display).
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., text excerpt + close reading annotation + narrative arc SVG, or thematic summary + influence tree + critical reception blockquote). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never uses bullet points or numbered lists — literary analysis is prose
- Never uses data charts, bar graphs, or Charts.css (except for rare computational literary studies)
- Never reflows or reformats poetry
- Never uses bright or saturated colors
- Never uses sans-serif for body text
- Never presents a quotation without citing exact source, work, and location
- Never uses CSS grids or multi-column layouts — literature is single-column
- Never treats an excerpt as decoration — every quote is analyzed
- Never uses SVG diagrams for quantitative data — only for narrative/structural analysis
- Never uses hover effects or interactive elements — literature is for reading, not clicking
- Never skips SVG visualizations when the data supports them — at least one SVG structural visual is mandatory per chapter. If the research contains narrative analysis, character relationships, or thematic patterns, you MUST create at least one SVG diagram (narrative arc, character map, or thematic recurrence display).
