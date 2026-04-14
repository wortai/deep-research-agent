# Philosophy Report Design

## Identity & Scope
This skill activates when the user's query is about philosophy, ethics, existentialism, logic, epistemology, metaphysics, political philosophy, aesthetics, or any topic where ideas, arguments, and the history of human thought are central. The report should look and feel like a beautiful philosophical text — think Penguin Classics editions of Plato, Routledge Philosophy Guidebooks, or the Stanford Encyclopedia of Philosophy.

## How a Real Philosophy Book Looks & Feels
A philosophy book is the most text-driven document that exists. The words ARE the content — there are no dashboards, no data grids. Instead: warm, aged-paper tones reminiscent of ancient libraries. Generous margins wide enough for marginalia and private reflection. Unhurried, flowing prose with impeccable typography. Beautiful blockquotes pulling primary-source text from great thinkers across millennia. Drop caps at the opening of major sections. Ornamental section dividers that echo the classical tradition. The page feels like it was designed for slow, careful reading — like sitting in a candlelit study with a glass of wine. Every element radiates intellectual depth and quiet beauty.

## What Information Matters Most to Philosophers & Philosophy Students
- **WHO said it**: Every argument must be attributed. Philosophy is a conversation between named thinkers across centuries.
- **WHEN and WHERE**: Ideas exist in historical context. Plato responded to the Sophists. Kant responded to Hume. Context is meaning.
- **The argument structure**: Not just WHAT was claimed, but HOW it was argued. Premises, conclusions, logical structure.
- **Objections and counterarguments**: No philosophical position is complete without its strongest objections. Steelmanning every side.
- **Original language**: Key terms in their original language (Greek: εὐδαιμονία, German: Dasein) carry irreplaceable meaning.
- **Contemporary relevance**: How does a 2,400-year-old idea apply to today's AI ethics or political crisis?
- **The texture of thought**: Philosophy values nuance, qualification, and the acknowledgment of uncertainty. Absolutes are suspicious.

## Content Structure & Narrative Flow
1. **The Question**: Open with the core philosophical question — frame it as a genuine open inquiry.
2. **Historical Context & Thinkers**: Key philosophers chronologically, each with name, era, school identified.
3. **The Arguments (Dialectical)**: Thesis → Supporting Arguments → Objections → Replies.
4. **Thought Experiments**: Classic or modern scenarios as concrete anchors for abstract ideas.
5. **Contemporary Relevance**: Connect classical arguments to modern life and current ethical dilemmas.

## Complete Visual Toolkit — Everything the LLM Can Use

Philosophy reports achieve visual richness through TYPOGRAPHY and TEXT PRESENTATION, not data visualizations. The following comprehensive set of techniques creates the aesthetic of a masterfully crafted philosophical text.

### Prose & Paragraph Styling
- **The primary content element.** Philosophy reports are 90%+ flowing prose.
- Fully justified text with generous line-height (1.8–1.9) for contemplative reading.
- First-line indentation (2em) on every paragraph after the first in a section — this is how real books are typeset.
- `text-indent` CSS creates natural paragraph flow without gaps between paragraphs.
- Body font size slightly larger than typical (1.1rem) for careful word-by-word reading.
- `hyphens: auto` for cleaner justified edges.

### Quotation Presentation — The Crown Jewel
Multiple quotation styles available depending on the weight and purpose of the quote:
- **Indented blockquotes**: Large padding, warm accent left border, serif italic font. Include philosopher's name, work title, section, and year in a `<footer>` with `<cite>`.
- **Centered pull quotes**: For powerful single-line quotes — larger font size, centered, decorative borders top and bottom. Used sparingly for maximum impact.
- **Epigraphs**: At section openings — brief quote, right-aligned, smaller italic font, setting thematic tone before analysis begins.
- **Nested quotations**: When a philosopher quotes another (common in commentary traditions) — use nested `<blockquote>` with progressively deeper indentation.
- **Original-language quotes**: When quoting in Greek, Latin, or German, show the original in italic with the translation immediately beneath in regular weight.

### Philosopher Introductions
When a new thinker enters the discussion:
- Name as a heading (warm serif, slightly larger).
- A metadata line immediately below: dates and lifespan, nationality, school of thought — smaller italic, muted color.
- Think of this as the "museum placard" for each mind being exhibited.
- Can include a brief one-line description of their core contribution: "Argued that knowledge is justified true belief."

### Thought Experiment Containers
- Visually separated blocks with warm, distinct background (soft amber or cream).
- A label in small caps: "THOUGHT EXPERIMENT" at the top.
- The scenario described in slightly different styling to distinguish from analytical prose.
- These are islands of vivid narrative in a sea of abstract argument — they should feel inviting, concrete, and imaginable.
- Can include numbered "decision points" within the experiment to guide the reader's thinking.

### Dialectical Argument Structure
- Use progressive heading labels: "The Utilitarian Position," "The Deontological Objection," "A Virtue Ethics Synthesis."
- Do NOT use side-by-side columns — philosophical arguments are sequential, building on each other in time.
- Use subtle visual dividers (thin rules or extra spacing) between opposing positions.
- Optionally use indentation to show the "thesis → antithesis → synthesis" hierarchy visually.
- Concluding integrations or the author's assessment can use a distinct container similar in weight to a theorem box (lightly shaded, clear label).

### Drop Caps & Section Openers
- Use CSS drop caps for the opening paragraph of each major section — first letter 3x body size, decorative serif, floated left.
- Creates an elegant book-opening feel that signals "a new chapter of thought begins."

### Marginalia & Side Notes
- Floating `<aside>` elements for brief annotations: term definitions, cross-references to other thinkers, dates of key events.
- On wider layouts, these sit in the margin; on narrow, they collapse inline.
- Styled in smaller font, muted color, italic — whispered context.

### SVG Diagrams for Philosophical Structure
- **Argument structure maps**: Premise → inference → conclusion flow diagrams.
- **School relationship trees**: How philosophical schools relate and influence each other.
- **Concept lineage diagrams**: Tracing an idea from origin through development.
- **Ethical framework comparisons**: Visual mapping of how different frameworks approach the same dilemma.
- Use minimal, elegant SVG — these are conceptual tools, not data charts.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide diagrams (argument flows, lineage trees); `viewBox="0 0 400 400"` for square diagrams (concept maps, framework comparisons).
- **Font sizing**: `font-family` must match body font (EB Garamond). Labels 12px, titles 14px, annotations 11px.
- **Stroke widths**: 1.5px for guide lines, 2px for connection arrows, 2.5px for borders, 1px for decorative elements.
- **Color application**: Use the exact philosophy palette — warm brown (#8D6E63), dark coffee (#4E342E), deep brown (#3E2723), soft amber (#FFF8E1), medium brown (#795548). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Argument structure: Kant's categorical imperative") and `<desc>` (describe all premises, inferences, and conclusions).
- **Background**: Transparent or warm parchment (#FAF8F5) to match the page.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Original-language terms use `<tspan font-style="italic">`.
- **Domain-specific SVG patterns**:
  - *Argument structure*: `<rect>` nodes for premises and conclusions, `<path>` arrows for logical inferences, labeled with inference type (deductive, inductive, abductive).
  - *School relationship tree*: Root `<rect>` for origin school, branching `<path>` lines to descendant schools, `<text>` labels with dates.
  - *Concept lineage*: Horizontal `<line>` timeline, `<circle>` nodes for key thinkers, `<text>` concept evolution labels.
  - *Ethical framework comparison*: `<rect>` panels for each framework, `<text>` decision outcomes, connecting `<path>` showing shared/different conclusions.

### Charts.css Decision Guide
- Philosophy reports RARELY use Charts.css — this is a prose-first domain.
- IF comparing categories (philosophical positions on a topic) → horizontal bar chart (only if survey/quantitative data exists)
- IF comparing time periods (philosopher birth dates, publication dates) → column chart
- Do NOT use Charts.css when: content is purely argumentative (use dialectical prose), fewer than 3 data points, or the comparison is better served by side-by-side argument analysis.
- When used: `class="charts-css [type]" show-labels show-data show-headings` with warm, muted colors only.

### Section Dividers
- Centered ornamental elements between major sections: a single ✦, or ── ✦ ──, or a thin HR.
- Replaces aggressive colored headers — transitions should feel like turning a page in an ancient book.
- Extra vertical spacing (3em+) between major sections.

### Concept Relationship Displays
- When mapping how schools relate (Rationalism vs. Empiricism, Analytic vs. Continental), use indented list trees or simple CSS-styled hierarchies.
- NOT data charts — conceptual lineage maps showing intellectual inheritance.
- Can show influence arrows: "Inspired by ← Plato → Influenced → Neoplatonism."

### Key Terms & Glossary
- When introducing a technical philosophical term (ontology, epistemology, qualia), present it in bold with a brief in-context definition.
- Optionally use a subtle styled inline element (slight background tint or underline) for newly introduced terms.
- For reports heavy on terminology, a compact glossary table at the chapter's end.

### Timeline Context (Philosophical History)
- When discussing the progression of philosophical thought, a minimal timeline can anchor ideas in time.
- Simpler than a history timeline — just date anchors with thinker names and key works.
- Warm brown styling consistent with the overall palette.

### Edge Cases & Adaptations
- **No quantitative data**: This is the DEFAULT state for philosophy. Use SVG argument maps, dialectical prose, and quotation presentations. Charts.css is almost never appropriate.
- **Too much data**: For topics with extensive scholarly debate (e.g., "Interpretations of Kant"), summarize the main schools of thought with representative quotes. Use `<details>` for extensive secondary literature lists.
- **Mixed content**: When philosophical analysis includes some empirical data (e.g., experimental philosophy, survey of moral intuitions), embed key metrics inline and use small charts only for sections with 3+ comparable data points.
- **Contradictory arguments**: This is philosophy's bread and butter. Present thesis → strongest objection → reply → counter-objection in sequential prose. Use dialectical structure, not comparison tables.
- **Variable chapter length**: Short topics (single concept) get definition + argument + objection + reply. Long topics (full philosophical system) use the complete toolkit with philosopher introductions and thought experiments.
- **Default format mismatch**: If the philosophy topic is historical (e.g., "History of Stoicism"), borrow timeline patterns from the history skill. If it's mathematical (e.g., "Logic and Set Theory"), borrow definition/theorem patterns from the math skill.

## Citation Style — Philosophical Sources
- Use inline author-date citations in the continental/humanities style: (Kant, 1781) or (Plato, *Republic*, Book VII).
- For direct quotes, include the specific section, page, or Stephanus number: (Aristotle, *Nicomachean Ethics*, 1097a).
- Provide source links as clickable text: `<a href="URL">Stanford Encyclopedia of Philosophy</a>` or the source title.
- For translations, credit the translator: (Plato, *Phaedo*, trans. Grube, 1997).
- Full reference list at the end of each chapter, formatted with the work title in italics.
- Citations are part of the intellectual conversation — they show the reader which voices are being engaged.
- **Multiple formats**: Use author-date for scholarly claims, descriptive citations for primary texts, and source blocks for translations.
- **No URL available**: Cite as "Author, *Title*, Publisher, Edition, Year, p./section XX" — standard humanities bibliographic format.
- **Multiple sources for same claim**: List chronologically to show interpretive tradition: "(Aristotle, EN 1097a; Aquinas, ST I-II q.3; MacIntyre, 1981)."
- **Beautiful citations**: Style the reference list with hanging indents, italic titles, and a warm border accent. Separate primary texts from secondary commentary with a decorative divider (── ✦ ──).
- **Source credibility hierarchy**: Authoritative critical edition (Oxford, Cambridge) > peer-reviewed philosophy journal (Mind, Ethics, Philosophy & Public Affairs) > Stanford Encyclopedia of Philosophy > academic monograph > reputable essay/review > general reference. Always prefer the most authoritative edition of primary texts.

## Typography & Color — The Philosophy Palette

### Fonts
- **Body text**: Premium serif — EB Garamond (first choice), Cormorant Garamond, or Palatino. The typeface carries the weight of centuries of intellectual tradition.
- **Headings**: Playfair Display or similar display serif — warm, authoritative, classical. Sizes: h2 = 1.6rem, h3 = 1.35rem, h4 = 1.15rem. No sans-serif anywhere — philosophy lives entirely in serifs.
- **Quotations**: Same serif family in italic, or Cormorant Garamond italic for visual distinction.
- **Metadata**: Lighter weight of body font, or the body font in italic at 0.85rem.

### Color System — Warm, Scholarly, Earth-Toned
- **Background**: Warm parchment (#FAF8F5) — not white, not yellow. The color of aged philosophical texts under lamplight.
- **Body text**: Deep brown (#3E2723) — softer and warmer than black. Easier on the eyes for long reading.
- **Headings**: Dark coffee (#4E342E) — rich, authoritative, warm.
- **Accent (borders, quotes)**: Warm brown (#8D6E63) — evoking leather-bound spines and aged bindings.
- **Thought experiment containers**: Soft amber fill (#FFF8E1), golden border (#FFE082) — warmth of candlelight.
- **Metadata text**: Medium brown (#795548) — present but unobtrusive.
- **Dividers/ornaments**: Muted warm gray (#BCAAA4).
- **Key terms highlight**: Warm cream (#FFF3E0) background.
- **Line height**: 1.8–1.9 — slow, contemplative reading pace. This is not a sprint.
- **Text alignment**: Justified with `hyphens: auto`.
- **Max content width**: 700px — a comfortable, bookish reading width.
- **Paragraph spacing**: Minimal (0.3em) between paragraphs within a section — text-indent handles the paragraph separation.
- **Extended chart palette** (7+ colors, for rare quantitative use): Deep brown (#3E2723), Dark coffee (#4E342E), Warm brown (#8D6E63), Medium brown (#795548), Soft amber (#FFF8E1), Burgundy (#800020), Forest (#228B22). All WCAG AA compliant on parchment.
- **Semantic color rules**: Deep brown = primary text/data. Dark coffee = headings/emphasis. Warm brown = accents/borders. Medium brown = metadata/secondary. Soft amber = thought experiments/highlights. Burgundy = key arguments/emphasis. Forest = positive/constructive positions.
- **Hover/interaction**: Minimal — philosophy is a reading medium. Subtle underline on links only.
- **Print-friendly**: The entire warm palette is designed for print. All colors maintain excellent contrast on parchment in grayscale.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio on warm parchment (#FAF8F5). Deep brown (#3E2723) on parchment = 13.5:1 — excellent. Chart colors ≥ 3:1.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains a quantitative argument (utilitarian calculations, voting paradoxes), CREATE a table or simple chart for it. Philosophy is not anti-data — it's just primarily prose. Adapting the layout to serve unusual content is expected.
- **Match formality to content.** A report on Plato's *Republic* demands the full classical treatment — drop caps, epigraphs, rich quotations. A report on modern applied ethics might feel more contemporary — same warm tones but simpler structure.
- **Let the thinkers speak.** If the research sources contain six powerful primary-source quotes, use all six. Don't compress to two because the template "feels like" it should have fewer. Quotations are not decoration — they are the primary evidence.
- **Build new containers.** If the content demands a "Timeline of Ethical Frameworks" or a "Comparison of Moral Theories," build those visual elements even though they're not traditional philosophy layout. The skill sets the aesthetic, not the ceiling.
- **Respect the pace.** Philosophy reports are long-form. Don't rush sections. Don't bullet-point arguments. Give ideas room to develop across full paragraphs.
- Never presents philosophical arguments without a structural visual. If the research contains competing positions, argument chains, or conceptual relationships, you MUST create at least one SVG diagram (dialectical structure, concept map, or influence tree).
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., argument block + thought experiment container + dialectical table, or philosopher profile + concept map + objection/response pair). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.
- **Visual variety is essential.** A philosophy report must NOT be only prose and blockquotes across many pages. You MUST include: (1) at least one dialectical comparison table or structured "Position → Objection → Reply" layout, (2) thought experiment containers for any thought experiments in the research, (3) philosopher introduction blocks with dates/schools for each thinker discussed, (4) concept relationship displays showing how philosophical positions relate. Spread these across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never uses bullet points or numbered lists — philosophy is prose, not lists
- Never uses bar charts or Charts.css — philosophy is not quantitative data (except for rare experimental philosophy)
- Never uses bright, cold colors (neon blues, greens) — only warm earth tones
- Never uses sans-serif fonts for body text
- Never presents a philosopher's argument without naming who said it, when, and in what work
- Never rushes — every paragraph earns its space through the weight of its ideas
- Never reduces a nuanced position to a simplistic summary
- Never uses SVG diagrams for quantitative data — only for argument/concept structure
- Never presents a single philosophical position as definitive — always include objections
- Never uses hover effects or interactive elements — philosophy is for contemplation, not interaction
- Never presents 3+ consecutive pages with only prose and blockquotes — must include dialectical tables, thought experiment containers, or concept relationship displays
- Never skips SVG visualizations when the data supports them — at least one SVG structural visual is mandatory per chapter. If the research contains competing positions, argument chains, or conceptual relationships, you MUST create at least one SVG diagram (dialectical structure, concept map, or influence tree).
