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
