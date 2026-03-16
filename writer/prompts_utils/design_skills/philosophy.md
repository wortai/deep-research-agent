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

## Citation Style — Philosophical Sources
- Use inline author-date citations in the continental/humanities style: (Kant, 1781) or (Plato, *Republic*, Book VII).
- For direct quotes, include the specific section, page, or Stephanus number: (Aristotle, *Nicomachean Ethics*, 1097a).
- Provide source links as clickable text: `<a href="URL">Stanford Encyclopedia of Philosophy</a>` or the source title.
- For translations, credit the translator: (Plato, *Phaedo*, trans. Grube, 1997).
- Full reference list at the end of each chapter, formatted with the work title in italics.
- Citations are part of the intellectual conversation — they show the reader which voices are being engaged.

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

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains a quantitative argument (utilitarian calculations, voting paradoxes), CREATE a table or simple chart for it. Philosophy is not anti-data — it's just primarily prose. Adapting the layout to serve unusual content is expected.
- **Match formality to content.** A report on Plato's *Republic* demands the full classical treatment — drop caps, epigraphs, rich quotations. A report on modern applied ethics might feel more contemporary — same warm tones but simpler structure.
- **Let the thinkers speak.** If the research sources contain six powerful primary-source quotes, use all six. Don't compress to two because the template "feels like" it should have fewer. Quotations are not decoration — they are the primary evidence.
- **Build new containers.** If the content demands a "Timeline of Ethical Frameworks" or a "Comparison of Moral Theories," build those visual elements even though they're not traditional philosophy layout. The skill sets the aesthetic, not the ceiling.
- **Respect the pace.** Philosophy reports are long-form. Don't rush sections. Don't bullet-point arguments. Give ideas room to develop across full paragraphs.

### What This Report NEVER Does
- Never uses bullet points or numbered lists — philosophy is prose, not lists
- Never uses bar charts or Charts.css — philosophy is not quantitative data
- Never uses bright, cold colors (neon blues, greens) — only warm earth tones
- Never uses sans-serif fonts for body text
- Never presents a philosopher's argument without naming who said it, when, and in what work
- Never rushes — every paragraph earns its space through the weight of its ideas
- Never reduces a nuanced position to a simplistic summary
