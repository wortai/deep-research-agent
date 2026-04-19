# Mathematics Report Design

## Identity & Scope
This skill activates when the user's query is about mathematics: algebra, calculus, number theory, geometry, topology, statistics, discrete math, linear algebra, or any topic where theorems, proofs, equations, and problem-solving are the language. The report should look and feel like a real mathematics textbook — think Stewart's Calculus, Rudin's Real Analysis, or a Springer graduate text.

## How a Real Math Book Looks & Feels
A mathematics textbook is the most structured document that exists. Every page has a clear hierarchy: definitions in boxes, theorems with formal statements, proofs that follow a logical chain, worked examples that show the math in action, and graphs that make abstract functions tangible. The page is WHITE — no distracting backgrounds. The typography is classical serif, resembling LaTeX-rendered documents. Equations are centered and given room to breathe. Margins are wide (for the reader's own scratch work). The palette is austere: black ink, blue theorem accents, and occasional color only in diagrams. The overall feeling is one of precision, clarity, and logical inevitability — like reading the laws of the universe.

## What Information Matters Most to Mathematicians & Math Students
- **Logical rigor**: Every step in a proof or derivation must be justified. No handwaving.
- **Precise definitions**: A mathematician cannot reason about something that isn't precisely defined.
- **Examples that illuminate**: Abstract theorems become real when you see them applied to concrete numbers.
- **Visual intuition**: A graph of a function tells a story that the formula alone cannot. Geometric diagrams make abstract spaces tangible.
- **Connections between ideas**: How does this theorem relate to that definition? Cross-references matter.
- **Edge cases and counterexamples**: What breaks? Where does the theorem fail? Counterexamples are as important as proofs.

## Content Structure & Narrative Flow
1. **Definitions & Foundations**: Every concept opens with a numbered, boxed formal definition before any discussion.
2. **Theorems & Proofs**: Present as "Theorem → Proof → QED" blocks. Proofs can be collapsed in `<details>` for long derivations.
3. **Worked Examples**: After every concept, fully worked examples: Problem → Step-by-step Solution → Final Answer in a bordered box.
4. **Visualizations**: Graphs, geometric diagrams, function plots wherever a concept has a visual interpretation.
5. **Summary & Key Formulas**: Each chapter ends with a compact reference listing key results.
- **Section numbers must be sequential and unique.** Never reuse a section number (e.g., two "1.1" sections). Use a hierarchical numbering scheme: 1.1, 1.2, 1.3 for sub-sections. Each new sub-section gets the next number in sequence.

## Complete Visual Toolkit — Everything the LLM Can Use

The following is a comprehensive library of visual and structural techniques available for mathematics reports. The LLM should choose freely from these based on what the specific content demands — not every report needs every technique, but knowing all possibilities allows the best choice for each situation.

### Equations & Mathematical Notation
- **Centered display equations**: Every major equation gets its own centered line with equation numbering (right-aligned). Use `<i>` for variables, `<sup>` for exponents, `<sub>` for subscripts. Wrap in `overflow-x: auto` containers for wide expressions.
- **Inline math**: Within prose, variables are always italic (`<i>x</i>`), constants upright.
- **Multi-step derivations**: Show algebraic progression step-by-step, each line indented and aligned. Use `<details><summary>Full Derivation</summary>...</details>` to collapse long chains while showing the starting and final expressions.
- **Equation numbering**: Float equation numbers to the right like `(2.1)` for cross-referencing.
- **EVERY major displayed equation MUST have a right-aligned equation number** in parentheses, e.g., `(1)`, `(2.1)`. Use `<span style="float: right; color: #718096; font-size: 0.875rem;">(1)</span>` after the equation. Unnumbered equations make cross-referencing impossible. Number sequentially within each section (1.1, 1.2, etc.) or globally (1, 2, 3, ...).
- **Systems of equations**: Use aligned column layouts (CSS flexbox) with a large left brace character for systems of simultaneous equations.
- **Piecewise functions**: Vertically stacked conditions with a large brace, each branch on its own line with its condition.

### Definition Boxes
- Wrap every formal definition in a container with thin solid border, very light gray background, numbered label ("Definition 2.3" in bold at top-left), and the term being defined in bold italic.
- Definitions are visually distinct from everything else — they are the "axioms" the reader must absorb.
- Use subtle left-border accent in a muted gray-blue to give a clean, academic feel.

### Theorem & Proof Blocks
- **Theorems**: Stronger visual treatment than definitions — colored left border (blue), light tinted background, bold "Theorem X.Y" label with optional name in parentheses (e.g., "Theorem 3.1 — Mean Value Theorem").
- **Proofs**: Follow immediately below, indented, slightly smaller font. End every proof with the tombstone symbol ∎ right-aligned. For long proofs, use `<details>` to make them collapsible.
- **Lemmas & Corollaries**: Same structure as theorems but with different label text and a subtler border color (teal or green) to show the hierarchy: Lemma → Theorem → Corollary.
- **Remarks & Notes**: Lighter still — italic text in a borderless indented block for editorial commentary.

### Worked Examples
- Each example is a numbered block ("Example 4.2") with clear visual boundaries.
- Structure: Problem statement → Given/Known values → Solution steps (numbered or sequential) → Final answer inside a double-bordered box.
- The boxed final answer is the visual climax of every example.
- **Multi-part examples**: Use labeled sub-parts (a), (b), (c) for related problems.
- **Counterexamples**: Styled differently from positive examples — use a reddish or amber accent to signal "this is what goes WRONG."

### Graphs & Function Plots (SVG)
- **Function graphs**: Plot y = f(x) curves using inline SVG with clean axes, gridlines, labeled tick marks, and a caption. Use distinct colors (blue, red, green) for multiple curves on the same axes.
- **Geometric diagrams**: Triangles, circles, angles with labeled vertices, side lengths, and angle measurements. Dashed lines for construction lines. Right-angle squares for 90° marks.
- **Number lines**: For inequalities, intervals, and real analysis. Open/closed circles for endpoint inclusion.
- **3D surface suggestions**: For multivariable calculus, describe the surface and provide a 2D projection or contour plot.
- **Probability distributions**: Bell curves, uniform distributions, histogram-style bar representations. Shaded areas under curves for probability regions.
- **Venn diagrams**: For set theory — overlapping circles with labeled regions.
- **Tree diagrams**: For combinatorics and probability — branching structures with probabilities on each branch.
- **Coordinate transformations**: Before/after diagrams showing how transformations (rotation, scaling, reflection) change geometric objects.
- Every visual MUST have: labeled axes, tick marks with values, a figure number, and a descriptive caption.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide plots (function graphs, number lines, probability distributions); `viewBox="0 0 400 400"` for square diagrams (geometric figures, Venn diagrams, coordinate transformations).
- **Font sizing**: `font-family` must match body font (EB Garamond/Georgia). Axis labels 12px, graph titles 14px, data labels 11px.
- **NEVER use `<style>` blocks with CSS `font-family` declarations containing multiple quoted font families (e.g., `font-family: "'EB Garamond', Georgia, serif"`). The nested quotes break in many browsers. Instead, apply `font-family` directly as an attribute on each `<text>` element: `font-family="EB Garamond, Georgia, serif"` (no nested quotes). Or use a single unquoted font name in `<style>`: `font-family: serif`.
- **Stroke widths**: 1.5px for grid lines, 2px for function curves and data lines, 2.5px for axes, 1px for construction lines (dashed, dotted).
- **Color application**: Use the exact math palette — Blue (#3182CE), Crimson (#C53030), Forest Green (#2F855A), Burnt Orange (#C05621). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Graph of f(x) = x² showing vertex and axis of symmetry") and `<desc>` (describe the function, key points, intercepts, and behavior).
- **Background**: Transparent — math diagrams overlay on white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Mathematical symbols use `<tspan font-style="italic">` for variables.
- **Domain-specific SVG patterns**:
  - *Function graph*: `<path>` curve with many `L` commands for smooth approximation, `<line>` axes with `<text>` tick labels, `<circle>` for key points (intercepts, extrema), shaded `<path>` for areas under curves.
  - *Geometric diagram*: `<polygon>` or `<path>` for shapes, `<text>` for vertex labels (A, B, C), `<line>` with `stroke-dasharray` for construction lines, small `<rect>` for right-angle marks.
  - *Venn diagram*: Overlapping `<circle>` elements with semi-transparent fills (`opacity="0.2"`), `<text>` labels in each region, bold `<text>` for set names.
  - *Tree diagram*: Root `<circle>` or `<text>`, branching `<line>` elements with probability `<text>` on each branch, leaf `<text>` for outcomes.

### Charts.css for Statistical & Discrete Data
- When presenting statistical distributions, experimental counts, or frequency data, use `Charts.css` bar or column charts.
- Use `Charts.css` area charts for cumulative distribution functions.
- Use `Charts.css` stacked bars for probability composition or partition problems.
- Apply `show-labels` and `show-data` classes for maximum data visibility.
- Keep chart styling monochrome or 2-color (navy + accent) to match the austere math aesthetic.

### SVG Construction Standards (for Charts.css alternatives)
- When Charts.css doesn't provide the needed precision (e.g., custom probability distributions), use SVG with the standards above.

### Charts.css Decision Guide
- IF comparing categories (discrete values, frequency counts) → horizontal bar chart
- IF comparing time periods (sequential measurements) → column chart
- IF showing trend over continuous domain (function behavior, convergence) → line chart
- IF showing composition (probability partition, set decomposition) → stacked bar chart
- IF showing part-to-whole (percentage of total, probability mass) → percentage bar
- IF comparing multiple series (two functions, theoretical vs. empirical) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart, numbered "Figure N:" with function/description
- Do NOT use Charts.css when: fewer than 3 data points (use a table), purely theoretical proofs (use prose + equations), or data requires mathematical precision (use SVG with exact coordinates)
- **NEVER use Charts.css when: fewer than 3 data points** — use a simple table or KPI card instead. Charts.css with 2 data points produces a meaningless visualization that wastes space and confuses readers.
- For Charts.css bar/column charts, use `--size` as a decimal fraction (0.0 to 1.0), NOT as a `calc()` expression. Example: `style="--size: 0.76"` for 76%. Do NOT use `calc(76 * 0.5%)` — this produces invalid CSS.
- **ALL `<th>` elements in Charts.css tables MUST have explicit inline styles** for `font-family`, `font-size`, `font-weight`, `color`, and `padding`. Do NOT rely on browser defaults or inherited styles. Example: `<th style="font-family: Inter, sans-serif; font-size: 0.875rem; font-weight: 600; color: #FFFFFF; background: #1A365D; padding: 0.5rem 0.75rem;">`

### Tables
- **Comparison tables**: For comparing properties of different mathematical objects (e.g., convergence tests side-by-side, types of matrices, integration techniques).
- **Truth tables**: For logic and discrete math — clean grid, centered values, alternating row shading.
- **Value tables**: For presenting function values at specific inputs — useful before graphing to show key points.
- **Transformation tables**: Showing input → output for function transformations.
- Tables use minimal borders — only horizontal rules separating header from body (LaTeX booktabs style). Numbers right-aligned, text left-aligned.

### Interactive / Collapsible Elements
- `<details>` blocks for: long proofs, extensive derivations, optional advanced material, hint systems in problem sets.
- Summary text should clearly indicate what's hidden: "Click to expand full proof" or "Derivation steps (12 steps)".
- Use for "Try it yourself" prompts where the solution is hidden until revealed.

### Notation Reference Sidebar
- For reports introducing many symbols, include a compact "Notation" reference block listing each symbol and its meaning.
- Placed at the start of the chapter or floating near first use.

### Edge Cases & Adaptations
- **No quantitative data**: For purely theoretical/mathematical logic topics (e.g., "Gödel's Incompleteness Theorems"), use definition boxes, theorem/proof blocks, and logical argument prose. Skip Charts.css entirely.
- **Too much data**: For large datasets (e.g., prime number tables, statistical distributions), summarize with key properties and show representative plots. Use `<details>` for full tables.
- **Mixed content**: When proofs dominate with occasional numerical examples, embed examples as worked blocks and use charts only for sections with 3+ comparable data points.
- **Contradictory approaches**: When multiple proof methods exist (e.g., algebraic vs. geometric proof of the same theorem), present both side-by-side with a comparison of elegance and generality.
- **Variable chapter length**: Short topics (single theorem) get definition + theorem + proof + example. Long topics (full theory) use the complete toolkit with notation references and summary formulas.
- **Default format mismatch**: If the math topic is applied (e.g., "Mathematics of Finance"), borrow finance-style data tables and KPI cards. If it's computational (e.g., "Numerical Methods"), borrow coding-style code blocks.

## Citation Style — Mathematical Sources
- Use inline numerical citations: [1], [2], [3] — matching the convention in mathematical journals.
- At the end of a chapter or major section, provide a numbered reference list.
- Format each citation as: `[n] Author(s), "Title," <a href="URL">source</a>, Year.`
- For textbook references: Author, *Title*, Publisher, Edition, Year.
- For online resources (Wolfram, Khan Academy, arXiv): include the direct URL as a clickable link.
- Citations should be unobtrusive — mathematics readers care about the logic, not the source, but sources must be traceable.
- **Multiple formats**: Use inline [n] for journal claims, footnote-style numbers for textbook references, and source blocks for online resources.
- **No URL available**: Cite as `[n] Author(s), *Title*, Publisher, Edition, Year.` — standard bibliographic format for books.
- **Multiple sources for same claim**: Use range notation [1–4] for well-established results. For contested or recent results, list individually.
- **Beautiful citations**: Style the reference list as a clean numbered table with subtle alternating backgrounds. Classic texts get a small gold accent indicator.
- **Source credibility hierarchy**: Peer-reviewed journal (Annals of Math, JAMS) > authoritative textbook (Springer, Cambridge) > arXiv preprint > lecture notes > popular math. Always prefer peer-reviewed proofs.

## Typography & Color — The Mathematics Palette

### Fonts
- **Body text**: Classical serif — EB Garamond (first choice), Georgia, Palatino, or Computer Modern (the LaTeX font). These fonts carry the visual authority of printed mathematics.
- **Headings**: Clean sans-serif contrast — Inter, Helvetica Neue, or Source Sans Pro. Deep navy (#1A365D). Sizes: h2 = 1.6rem, h3 = 1.3rem, h4 = 1.1rem.
- **Math variables**: Always italic serif. Vectors bold italic. Constants (π, e, i) upright. Function names (sin, cos, log) upright.
- **Code/Computational**: Fira Code or JetBrains Mono for any algorithmic or computational content.

### Color System
- **Background**: Pure white (#FFFFFF) — the mathematical page is pristine.
- **Body text**: Dark charcoal (#2D3748) — high contrast but not harsh black.
- **Heading text**: Deep navy (#1A365D) — authoritative and structured.
- **Definition boxes**: Fill #F7F8FA (barely-there gray), border #CBD5E0 (cool gray).
- **Theorem boxes**: Fill #EBF4FF (whisper of blue), left border #3182CE (clear academic blue).
- **Lemma boxes**: Fill #F0FFF4 (whisper of green), left border #38A169 (mathematical green).
- **Example indicators**: Deep charcoal border (#2D3748) for boxed answers.
- **Counterexample accent**: Amber fill (#FFFAF0), amber border (#ED8936).
- **Graph curve colors**: Blue (#3182CE), Crimson (#C53030), Forest Green (#2F855A), Burnt Orange (#C05621) — chosen for maximum visual distinction and colorblind accessibility.
- **Grid lines in graphs**: Very light gray (#EDF2F7).
- **Line height**: 1.7 — math needs breathing room around inline notation.
- **Paragraph spacing**: 1.2em between paragraphs, 2em before new sections.
- **Extended chart palette** (7+ colors): Blue (#3182CE), Crimson (#C53030), Forest Green (#2F855A), Burnt Orange (#C05621), Purple (#805AD5), Steel (#4A5568), Gold (#D69E2E). All WCAG AA compliant on white.
- **Semantic color rules**: Blue = primary/default function. Crimson = contrasting function or boundary. Forest Green = positive region or solution set. Burnt Orange = warning/exception region. Purple = secondary/derived function. Steel = reference/baseline. Gold = optimal/extremal values.
- **Hover/interaction**: On hover, curve opacity increases to 1.0 while others dim to 0.5. Use CSS `:hover` on SVG `<path>` elements.
- **Print-friendly**: All colors maintain ≥ 3:1 contrast in grayscale. Curve differentiation supplemented by line style (solid, dashed, dotted) for print legibility.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio. Chart colors ≥ 3:1 against white. The palette is deuteranopia-safe.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains information that doesn't fit neatly into the Definition → Theorem → Example structure, CREATE a new presentation format for it. Invent a new box type, a new visual container, or simply use clean prose. The content always wins.
- **Scale structure to content depth.** A report on basic algebra doesn't need numbered theorems. A report on real analysis does. Match the formality of the visual treatment to the formality of the mathematics.
- **Adapt based on the plan.** If the planner's research plan is "explain this to a beginner," use more worked examples and fewer formal proofs. If it's "analyze this theorem deeply," use full proof chains and formal notation.
- **Mix techniques freely.** A single chapter might contain a definition box, followed by a prose explanation, followed by an SVG graph, followed by a worked example, followed by a Charts.css histogram. The visual variety should serve the content, not conform to a rigid template.
- **Don't lose data.** If the research sources contain 15 worked examples, show all 15. Don't truncate to fit a template. If needed, use `<details>` blocks to organize them without losing any.
- Never presents a theorem, proof, or mathematical concept without at least one visual aid. If the research contains functions, geometric relationships, coordinate systems, or data distributions, you MUST create at least one SVG diagram (function graph, geometric diagram, coordinate transformation, or Venn diagram).
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., definition box + SVG function graph + worked example, or theorem box + proof + coordinate diagram). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never uses flashy gradients, dark backgrounds, or decorative elements
- Never skips the Definition → Theorem → Proof → Example structure when the content is formal mathematics
- Never presents an equation without defining every variable
- Never shows a graph without labeled axes and a caption
- Never uses bullet points for mathematical arguments — proofs are sequential prose
- Never uses colors for decoration — color always carries mathematical meaning
- Never uses Charts.css for data that requires mathematical precision — use SVG instead
- Never presents a theorem without stating its conditions and scope
- Never uses arbitrary colors in graphs — every color distinguishes a different function or set
- Never skips SVG visualizations when the data supports them — at least one SVG diagram is mandatory per chapter. If the research contains functions, geometric relationships, coordinate systems, or data distributions, you MUST create at least one SVG diagram (function graph, geometric diagram, coordinate transformation, or Venn diagram).


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
