# Practice & Learning Report Design

## Identity & Scope
This skill activates when the user wants to actively learn or practice — study guides, cheat sheets, flashcard-style content, exam prep, problem sets, tutorials, step-by-step skill building, or revision summaries. Think of a premium Notion study guide, the best Anki deck, a Kumon worksheet, or Khan Academy's best moments turned into a document.

## How Real Study Material Looks & Feels
The best study materials are INTERACTIVE and SCANNABLE. Information is organized for rapid lookup, not sequential reading. Color-coded difficulty levels guide the student. Click-to-reveal solutions force active recall. Dense reference tables give instant answers. Tip boxes warn about mistakes. The layout says: "This was designed by someone who understands how learning works." Every element serves retention. Nothing is decorative — but everything is visually clean and inviting enough to make studying feel achievable, not daunting.

## What Information Matters Most to Students & Learners
- **Crystal clarity**: No ambiguity. Definitions must be exact. Steps must be numbered. Answers must be definitive.
- **Active recall**: The student must TRY before they see the answer. Hidden solutions are pedagogically superior to visible ones.
- **Graduated difficulty**: Start easy, build up. The student can self-assess their level by attempting the right difficulty tier.
- **Common mistakes**: Knowing what goes WRONG is as valuable as knowing what's right. Error awareness prevents repeat failures.
- **Analogies and mnemonics**: Abstract concepts stick when connected to something concrete or memorable.
- **Quick reference**: Formulas, rules, syntax — the "cheat sheet" that saves time during practice. Dense, scannable, always nearby.
- **Immediate feedback**: See the problem → attempt it → reveal the answer → understand any gap. Short feedback loops.

## Content Structure & Narrative Flow
1. **Concept Overview**: Brief, crystal-clear explanation. No fluff. Use analogies.
2. **Key Reference Table / Cheat Sheet**: Dense table of formulas, definitions, rules.
3. **Practice Problems (Graded by Difficulty)**: Easy → Medium → Hard, each labeled.
4. **Solutions (Hidden)**: Every problem has step-by-step solution behind `<details>`.
5. **Common Mistakes & Tips**: Warning boxes about frequent errors.

## Complete Visual Toolkit — Everything the LLM Can Use

### Concept Explanations
- Short, punchy paragraphs (3-4 sentences max). Bold key terms. Use analogies.
- If a concept fits better as a table, diagram, or comparison — use that instead of prose.
- Numbered steps for procedures, bullet points for properties/characteristics.
- "In plain English" rephrasing after any technical definition.

### Cheat Sheet / Reference Tables
- Dense, compact tables — alternating row colors, clear headers.
- Monospace for code/formulas, sans-serif for descriptions.
- Maximum information density — the "tear-out page."
- Can use multi-column layouts for very dense reference material.
- Group related formulas/rules by category within the table.

### Difficulty Badges
- Every problem: colored inline pill badge — Easy (green), Medium (yellow/amber), Hard (red).
- Small, clear, instant visual categorization.
- Optional: estimated time to complete.

### Interactive Click-to-Reveal (The Signature Element)
- Problem fully visible in a bordered card container.
- Solution hidden in `<details><summary>Click to reveal solution ▸</summary>...</details>`.
- Solutions show step-by-step reasoning, not just final answers.
- Final answers boxed/highlighted within the solution.
- Pattern works for: math problems, coding challenges, MCQ, fill-in-blank, concept checks, vocabulary, translations.

### Flashcard-Style Q&A Blocks
- Question visible, answer behind `<details>`.
- Card-like styling — rounded corners, subtle border.
- Great for definitions, vocabulary, key facts, concept verification.

### Tip / Warning / Gotcha Boxes
- **⚠️ Common Mistake** (Orange): Errors students typically make. Amber border, warm cream background.
- **💡 Pro Tip** (Blue): Shortcuts, mnemonics, efficiency tricks. Blue border, pale blue background.
- **📌 Remember** (Green): Critical facts to memorize. Green border, pale green background.
- **🚨 Watch Out** (Red): Dangerous misconceptions, tricky edge cases. Red border, pale red background.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide diagrams (process flows, comparison charts); `viewBox="0 0 400 400"` for square diagrams (concept maps, knowledge trees).
- **Font sizing**: `font-family` must match body font (Inter). Labels 12px, diagram titles 14px, data labels 11px.
- **Stroke widths**: 1.5px for grid lines, 2px for connection arrows, 2.5px for borders, 1px for decorative elements.
- **Color application**: Use the exact study guide palette — Blue (#2B6CB0), Green (#38A169), Amber (#ED8936), Red (#E53E3E). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Knowledge map: Algebra fundamentals") and `<desc>` (describe all concepts and their relationships).
- **Background**: Transparent — diagrams overlay on off-white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Formulas use `<tspan font-family="monospace">`.
- **Domain-specific SVG patterns**:
  - *Knowledge map/tree*: Root `<rect>` for main topic, branching `<path>` lines to subtopics, `<text>` labels. Color-coded by difficulty level.
  - *Process flow*: Sequential `<rect>` nodes with `<path>` arrows, numbered steps, color-coded by stage.
  - *Concept comparison*: Side-by-side `<rect>` panels with `<text>` labels, connecting `<path>` for similarities/differences.
  - *Progress tracker*: Horizontal `<rect>` segments showing completion, `<text>` milestone labels, checkmark symbols for achieved.

### Charts.css Decision Guide
- IF comparing categories (concepts, topics, skill areas) → horizontal bar chart
- IF comparing time periods (study progress over weeks, score improvement) → column chart
- IF showing trend over continuous time (learning curve, practice scores) → line chart
- IF showing composition (time spent by topic, skill breakdown) → stacked bar chart
- IF showing part-to-whole (mastery percentage, completion rate) → percentage bar
- IF comparing multiple series (student A vs. student B, pre-test vs. post-test) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart with brief description
- Do NOT use Charts.css when: fewer than 3 data points (use a table or flashcard), purely conceptual content (use knowledge maps), or data is better shown as a progress tracker

### Step-by-Step Tutorials
- Numbered ordered lists with each step as a clear, actionable instruction.
- Each step can include code blocks, formulas, or brief explanations.
- Connector styling (vertical line, arrows) between steps to show progression.
- Expected output shown after each step for immediate verification.

### Comparison Tables
- "X vs Y" for confusing concepts students often mix up.
- ✓/✗ symbols for feature comparisons.
- "Before → After" for transformations or process changes.

### Progress / Self-Assessment Checklists
- Checkbox-style lists (☐ / ☑) for students to mentally track mastery.
- Organized by topic area or difficulty level.

### Charts.css for Data-Based Exercises
- **Bar charts**: Within exercises ("Read this chart and answer...") or for showing frequency distributions.
- **Column charts**: For comparing quantities in exercises.
- Clean, labeled, with the data clearly readable — these charts are pedagogical tools.

### Mnemonic & Memory Aid Blocks
- Distinct styled containers for mnemonic devices.
- Large bold text for the acronym, expanded letters below.
- Visually distinct from other content — signals "this is a memory tool."

### Knowledge Map / Topic Overview
- A structured outline or tree showing what subtopics belong to what parent topic.
- Helps students see the big picture before diving into details.

### Code Blocks (for coding practice)
- Terminal-style dark blocks, monospace, language-indicated header.
- Paired with problem statement above and solution `<details>` below.

### Summary / Key Takeaway Boxes
- At the end of each major section, a compact box summarizing the 3-5 most important points.
- Distinct background, clear heading ("Section Summary").

### Edge Cases & Adaptations
- **No quantitative data**: For purely conceptual topics (e.g., "Introduction to Philosophy"), use knowledge maps, flashcard Q&A blocks, and comparison tables. Skip Charts.css entirely.
- **Too much data**: For subjects with hundreds of practice problems, organize by topic and difficulty tier. Show representative problems for each tier. Use `<details>` for full problem sets.
- **Mixed content**: When theory dominates with occasional practice, embed key concepts as cheat sheet tables and use practice problems only for sections with clear exercise potential.
- **Contradictory sources**: When textbooks disagree (e.g., different notation conventions), present both with clear labels: "Convention A (most common)" vs. "Convention B (alternative)." Note which is used in standard exams.
- **Variable chapter length**: Short topics (single concept) get overview + cheat sheet + 3-5 problems. Long topics (full subject) use the complete toolkit with knowledge maps and progress trackers.
- **Default format mismatch**: If the learning topic is code-heavy (e.g., "Learn Python"), borrow code block patterns from the coding skill. If it's math-heavy (e.g., "Calculus Practice"), borrow theorem/proof patterns from the math skill.

## Citation Style — Learning Sources
- Use simple inline links: "Learn more: `<a href='URL'>Khan Academy</a>`" or "See: `<a href='URL'>source</a>`."
- For textbook references: Author, *Title*, Chapter/Section.
- For video resources: "[Video] Title, Platform, Duration."
- Citations in learning materials are navigational — they point the student to deeper resources, not academic authority.
- Group additional resources in a "Further Reading" or "Explore More" section at the end.
- **Multiple formats**: Use inline links for resources, textbook references for formal content, and source blocks for datasets.
- **No URL available**: Cite as "Author, *Title*, Publisher, Edition, Chapter/Section" — standard textbook reference.
- **Multiple sources for same claim**: Link the most student-friendly source first (Khan Academy, textbook) then supplementary sources.
- **Beautiful citations**: Style the "Further Reading" section as a clean list with resource type badges (📖 book, 🎥 video, 🌐 website, 📝 practice).
- **Source credibility hierarchy**: Standard textbook > official curriculum > established educational platform (Khan Academy, Coursera) > expert blog > general website. Always prefer standard textbooks and official curricula.

## Typography & Color — The Study Guide Palette

### Fonts
- **Body**: Clean sans-serif — Inter (first choice), Roboto, system-ui. Optimized for scanning.
- **Code/Formulas**: Monospace — Fira Code, Source Code Pro.
- **Headings**: Bold same sans-serif in blue (#2B6CB0).
- **Problem numbers**: Bold, slightly larger than body text.

### Color System — Clean, Functional, Engaging
- **Background**: Off-white (#FDFDFD) — clean and fresh.
- **Body text**: Dark gray (#2D3748) — highly readable.
- **Headings**: Blue (#2B6CB0) — active, educational energy.
- **Table headers**: Blue bg (#2B6CB0), white text — strong anchors.
- **Easy badge**: Green bg (#C6F6D5), dark green text (#22543D).
- **Medium badge**: Amber bg (#FEFCBF), dark amber text (#744210).
- **Hard badge**: Red bg (#FED7D7), dark red text (#822727).
- **Common Mistake box**: Orange border (#ED8936), cream bg (#FFFAF0).
- **Pro Tip box**: Blue border (#3182CE), pale blue bg (#EBF8FF).
- **Remember box**: Green border (#38A169), pale green bg (#F0FFF4).
- **Card borders**: Light gray (#E2E8F0).
- **Solution backgrounds**: Very light gray (#F7FAFC).
- **Boxed answers**: Blue border (#2B6CB0).
- **Line height**: 1.6 — compact, functional, scannable.
- **Extended chart palette** (7+ colors): Blue (#2B6CB0), Green (#38A169), Amber (#ED8936), Red (#E53E3E), Purple (#805AD5), Teal (#319795), Steel (#4A5568). All WCAG AA compliant on off-white.
- **Semantic color rules**: Blue = default/primary data series. Green = easy/positive/correct answers. Amber = medium/warning/caution. Red = hard/incorrect/danger. Purple = advanced/bonus content. Teal = secondary data series. Steel = reference/baseline values.
- **Hover/interaction**: On hover, chart elements show exact values. Click-to-reveal elements show subtle background change. Use CSS `:hover` transitions.
- **Print-friendly**: All colors maintain ≥ 3:1 contrast in grayscale. Badge colors supplemented by text labels (Easy/Medium/Hard) for print legibility.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio. Chart colors ≥ 3:1 against off-white (#FDFDFD). Badge text colors are specifically chosen for readability on their backgrounds.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains 30 practice problems, include all 30 — organize them by difficulty tier. Don't truncate to fit a template.
- **Scale interactivity to content.** Simple memorization topics → heavy flashcard usage. Complex problem-solving → worked examples with `<details>` solutions. Procedural skills → step-by-step tutorials.
- **Adapt difficulty to audience.** If the planner suggests "beginner learner," use more analogies and simpler problems. For advanced prep (GRE, MCAT), use dense reference tables and hard problems.
- **Create new exercise types.** If the content demands "Match the term," "Fill in the blank," or "Complete the diagram," build those interactive patterns. The toolkit shows common patterns, not the only patterns.
- **Cheat sheets are never optional.** Every practice/learning report should have at least one dense reference table — this is the most reused element.
- **Never show solutions without hiding them first.** Active recall is the entire pedagogical purpose of this skill.
- Never presents a learning topic without a structural visual. If the research contains steps, processes, or concept hierarchies, you MUST create at least one SVG diagram (flowchart, hierarchy tree, or concept map).
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., reference table + collapsible solution + tip callout, or concept diagram + practice problem + common mistakes box). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never hides the difficulty level — every problem is labeled
- Never shows solutions without hiding them behind click-to-reveal
- Never writes long paragraphs — concept explanations are SHORT
- Never uses decorative fonts — everything is functional
- Never presents a solution without step-by-step reasoning
- Never expects passive reading — every section encourages engagement
- Never uses Charts.css for data that's better shown as a knowledge map
- Never presents a concept without at least one practice opportunity
- Never uses color as the sole difficulty indicator — always include text labels (Easy/Medium/Hard)
- Never skips SVG visualizations when the data supports them — at least one SVG diagram is mandatory per chapter. If the research contains steps, processes, or concept hierarchies, you MUST create at least one SVG diagram (flowchart, hierarchy tree, or concept map).


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
