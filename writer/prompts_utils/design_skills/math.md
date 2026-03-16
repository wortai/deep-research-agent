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

## Complete Visual Toolkit — Everything the LLM Can Use

The following is a comprehensive library of visual and structural techniques available for mathematics reports. The LLM should choose freely from these based on what the specific content demands — not every report needs every technique, but knowing all possibilities allows the best choice for each situation.

### Equations & Mathematical Notation
- **Centered display equations**: Every major equation gets its own centered line with equation numbering (right-aligned). Use `<i>` for variables, `<sup>` for exponents, `<sub>` for subscripts. Wrap in `overflow-x: auto` containers for wide expressions.
- **Inline math**: Within prose, variables are always italic (`<i>x</i>`), constants upright.
- **Multi-step derivations**: Show algebraic progression step-by-step, each line indented and aligned. Use `<details><summary>Full Derivation</summary>...</details>` to collapse long chains while showing the starting and final expressions.
- **Equation numbering**: Float equation numbers to the right like `(2.1)` for cross-referencing.
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

### Charts.css for Statistical & Discrete Data
- When presenting statistical distributions, experimental counts, or frequency data, use `Charts.css` bar or column charts.
- Use `Charts.css` area charts for cumulative distribution functions.
- Use `Charts.css` stacked bars for probability composition or partition problems.
- Apply `show-labels` and `show-data` classes for maximum data visibility.
- Keep chart styling monochrome or 2-color (navy + accent) to match the austere math aesthetic.

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

## Citation Style — Mathematical Sources
- Use inline numerical citations: [1], [2], [3] — matching the convention in mathematical journals.
- At the end of a chapter or major section, provide a numbered reference list.
- Format each citation as: `[n] Author(s), "Title," <a href="URL">source</a>, Year.`
- For textbook references: Author, *Title*, Publisher, Edition, Year.
- For online resources (Wolfram, Khan Academy, arXiv): include the direct URL as a clickable link.
- Citations should be unobtrusive — mathematics readers care about the logic, not the source, but sources must be traceable.

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

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains information that doesn't fit neatly into the Definition → Theorem → Example structure, CREATE a new presentation format for it. Invent a new box type, a new visual container, or simply use clean prose. The content always wins.
- **Scale structure to content depth.** A report on basic algebra doesn't need numbered theorems. A report on real analysis does. Match the formality of the visual treatment to the formality of the mathematics.
- **Adapt based on the plan.** If the planner's research plan is "explain this to a beginner," use more worked examples and fewer formal proofs. If it's "analyze this theorem deeply," use full proof chains and formal notation.
- **Mix techniques freely.** A single chapter might contain a definition box, followed by a prose explanation, followed by an SVG graph, followed by a worked example, followed by a Charts.css histogram. The visual variety should serve the content, not conform to a rigid template.
- **Don't lose data.** If the research sources contain 15 worked examples, show all 15. Don't truncate to fit a template. If needed, use `<details>` blocks to organize them without losing any.

### What This Report NEVER Does
- Never uses flashy gradients, dark backgrounds, or decorative elements
- Never skips the Definition → Theorem → Proof → Example structure when the content is formal mathematics
- Never presents an equation without defining every variable
- Never shows a graph without labeled axes and a caption
- Never uses bullet points for mathematical arguments — proofs are sequential prose
- Never uses colors for decoration — color always carries mathematical meaning
