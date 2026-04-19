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
