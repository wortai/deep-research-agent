# Physics Report Design

## Identity & Scope
This skill activates when the user's query is about physics: classical mechanics, quantum mechanics, thermodynamics, electromagnetism, relativity, astrophysics, optics, particle physics, wave phenomena, or any topic where natural laws, equations, and physical phenomena are central. The report should look like a great physics textbook — Griffiths' Electrodynamics, Halliday/Resnick, Feynman Lectures, or a Springer physics monograph.

## How a Real Physics Book Looks & Feels
A physics textbook is the most VISUAL of all scientific texts. Every abstract concept gets a diagram — force arrows, field lines, energy levels, wave functions, orbital paths. Physics is inherently spatial and temporal, so the page must make the invisible visible. The rhythm alternates: "read → see → calculate." Equations are centerpieces, but unlike pure math, they always connect to something you can IMAGINE happening in the physical world. Color is used meaningfully — red for hot, blue for cold, arrows for direction. The page feels like a window into the universe's operating manual. There's a sense of awe mixed with precision.

## What Information Matters Most to Physicists & Physics Students
- **The physical picture**: What is ACTUALLY happening? Before any equation, the student needs to visualize the phenomenon.
- **Equations as language**: The math IS the physics. But every symbol must be defined, every unit stated.
- **Order of magnitude**: Does the answer make sense? Is this the right ballpark? Physical intuition.
- **Units and dimensions**: A number without units is meaningless. Dimensional analysis catches errors.
- **Limiting cases**: What happens when v → c? When T → 0? When n → ∞? Limiting behavior reveals the physics.
- **Experimental connection**: How do we KNOW this? What experiment confirmed it? Data grounds theory.
- **Analogies between domains**: E&M parallels gravity. Waves appear in mechanics and quantum. Cross-domain connections deepen understanding.

## Content Structure & Narrative Flow
1. **The Phenomenon**: Describe what actually happens in the physical world — make it tangible before going abstract.
2. **Governing Laws & Equations**: The fundamental equations, derived step-by-step. Every variable defined.
3. **Diagrams & Visualizations**: Force diagrams, wave plots, energy level diagrams, field visualizations.
4. **Numerical Examples**: Equations in action with real numbers, units, and dimensional analysis.
5. **Experimental Context**: How this is measured in labs, including data tables of real measurements.

## Complete Visual Toolkit — Everything the LLM Can Use

Physics demands the richest visual vocabulary of any domain. The LLM should freely combine these techniques.

### Equations — The Core Visual Element
- **Centered display equations**: Own line, numbered right-aligned `(2.1)`. Use `<i>` for scalar variables, `<b><i>` for vectors.
- **Variable definition blocks**: Immediately after every equation — list each variable, its meaning, its SI unit.
- **Multi-step derivations**: Show algebraic progression. Use `<details>` for long chains (10+ steps), showing start and end in the summary.
- **Systems of equations**: Aligned with a large brace, each equation on its own line.
- **Approximations**: Show the exact form, then the approximation with the conditions under which it holds (e.g., "For v << c, γ ≈ 1").
- Wrap in `overflow-x: auto` for wide expressions.

### Diagrams — Physics NEEDS Pictures (SVG)
Every concept involving direction, motion, fields, or spatial relationships should have a diagram:
- **Free-body diagrams**: Arrows for force vectors on objects. Label each with name AND magnitude.
- **Field line diagrams**: Curved lines for E, B, or gravitational fields around sources. Show direction, density.
- **Wave diagrams**: Sine/cosine with labeled amplitude (A), wavelength (λ), period (T), propagation direction.
- **Energy level diagrams**: Horizontal lines at different heights for quantized states. Arrows for transitions with ΔE labeled.
- **Circuit diagrams**: Standard symbols for resistors, capacitors, batteries, inductors.
- **Ray diagrams**: For optics — light rays, lenses, mirrors, focal points, image formation.
- **Orbital/trajectory plots**: Planetary ellipses, projectile parabolas, charged particle spirals in B fields.
- **Phase diagrams**: Solid/liquid/gas regions with triple point and critical point marked.
- **Vector decomposition**: Component arrows with dotted projections, angle labeled.
- **Potential energy curves**: U(x) vs x with equilibrium points, turning points, and energy levels marked.
- **Spacetime diagrams**: Light cones, worldlines for relativity topics.
- **Interference/diffraction patterns**: Intensity distributions, slit geometries.
- All diagrams: labeled arrows, distinct colors for different quantities, numbered figure caption below.

### Charts.css for Experimental & Quantitative Data
- **Bar charts**: Comparing measurements across conditions, materials, or experiments.
- **Line charts**: Dose-response, temperature vs. time, I-V characteristics, decay curves.
- **Area charts**: Accumulated quantities, total energy dissipated over time, spectra.
- **Stacked bars**: Energy source composition, particle decay channels, material composition.
- **Grouped bars**: Control vs. experimental, theoretical vs. measured.
- Use physically meaningful colors: warm (red/orange) for energy/heat, cool (blue) for cold/potential, green for equilibrium.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide plots (waveforms, spectra, I-V curves); `viewBox="0 0 400 400"` for square diagrams (free-body, vector decomposition, orbital paths).
- **Font sizing**: `font-family` must match body font (EB Garamond/Georgia). Axis labels 12px, diagram titles 14px, data point labels 11px.
- **Stroke widths**: 1.5px for grid lines, 2px for data lines/field lines, 2.5px for axes, 1px for construction lines (dashed projections).
- **Color application**: Use the exact diagram palette — no arbitrary colors. Red (#E53E3E) for force/energy, blue (#3182CE) for fields/potential, green (#38A169) for equilibrium, orange (#DD6B20) for kinetic energy, purple (#805AD5) for magnetic/quantum.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Free-body diagram of block on incline") and `<desc>` (detailed description of all elements and their physical meaning).
- **Background**: Transparent — physics diagrams overlay on white pages. Use `fill="none"` for backgrounds.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. All labels use `<tspan>` for multi-line text.
- **Domain-specific SVG patterns**:
  - *Force diagram*: Object as `<rect>` or `<circle>`, force vectors as `<line>` with `<polygon>` arrowheads, labels via `<text>` near arrow tips.
  - *Field lines*: `<path>` with smooth curves (`C` or `Q` commands), arrowheads at intervals, density proportional to field strength.
  - *Energy level*: Horizontal `<line>` elements at y-positions proportional to energy, transition arrows as diagonal `<line>` with labeled ΔE.
  - *Wave plot*: `<path>` with sine approximation using many `L` commands, axes as `<line>`, amplitude/wavelength annotations with `<text>` and dashed `<line>` guides.

### Charts.css Decision Guide
- IF comparing categories (materials, conditions, experiments) → horizontal bar chart
- IF comparing time periods (quarterly measurements, yearly data) → column chart
- IF showing trend over continuous time (temperature vs. time, decay) → line chart
- IF showing composition (energy breakdown, particle channels) → stacked bar chart
- IF showing part-to-whole (material composition, efficiency) → percentage bar
- IF comparing multiple series (theory vs. experiment, control vs. treatment) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart, numbered "Figure N:" with descriptive text
- Do NOT use Charts.css when: fewer than 3 data points (use a table), purely qualitative descriptions (use prose), or data requires error bars (use SVG)

### Data Tables
- Experimental measurements with units in headers, right-aligned numbers.
- Uncertainty values (±) where applicable.
- Significant figures respected.
- For: physical constants, material properties, spectral data, measurement comparisons.
- Mark significant results with bold or accent.

### Worked Numerical Examples
- Structure: Problem → Given (listed with units) → Solution steps → Boxed final answer with units and sig figs.
- Distinct container: light green background, green left border.
- Always show unit cancellation and dimensional analysis explicitly.
- Include a "sanity check" line: "This makes sense because..."

### Constants Reference Boxes
- Compact boxes listing physical constants: c, G, ℏ, k_B, ε₀, μ₀, etc.
- Placed near first use, subtle gray-toned info box.

### Comparison & Analogy Layouts
- Side-by-side panels for related concepts: classical vs. quantum, wave vs. particle, E-field vs. B-field.
- CSS grid or flexbox, two columns with clear dividing line.
- Great for showing parallels: "The electric force equation has the same form as the gravitational force equation..."

### Scaling & Limiting Case Containers
- Distinct callout blocks showing what happens at extreme values.
- Label: "Limiting Case" or "When v → 0" — styled like a note box.
- Useful for building physical intuition.

### Color Coding — Physical Quantities
- **Red/warm**: Energy, heat, high intensity, positive charge, compression.
- **Blue/cool**: Cold, low energy, potential energy, negative charge, rarefaction.
- **Green**: Equilibrium, ground state, stable points.
- **Orange**: Warning, high values, kinetic energy.
- **Purple**: Magnetic fields, quantum states.
- Consistent within a chapter so the reader develops color-physics associations.

### Edge Cases & Adaptations
- **No quantitative data**: For purely theoretical/conceptual physics (e.g., philosophy of QM), use SVG concept diagrams and analogy layouts instead of charts. Emphasize equations-as-language and thought experiments.
- **Too much data**: For datasets with hundreds of points (e.g., particle collision data), summarize with statistical aggregates in tables and show representative SVG plots. Use `<details>` for full data.
- **Mixed content**: When prose dominates but some numbers exist, embed key metrics as inline callouts and use small SVG diagrams for physical intuition. Reserve Charts.css for sections with 3+ comparable data points.
- **Contradictory sources**: Present competing experimental results side-by-side in a comparison table with methodology notes. Discuss systematic errors and confidence intervals.
- **Variable chapter length**: Short topics (single law) get a compact equation + diagram + example. Long topics (full theory) use the full toolkit with collapsible derivations.
- **Default format mismatch**: If the physics topic is historical (e.g., "Discovery of the Electron"), borrow timeline patterns from the history skill. If it's computational, borrow code block patterns from the coding skill.

## Citation Style — Physics Sources
- Use inline numerical citations: [1], [2] — matching physics journal conventions (Physical Review style).
- Numbered reference list at the end of the chapter.
- Format: `[n] Author(s), "Title," <a href="URL">Journal/Source</a>, Volume, Pages, Year.`
- For textbooks: Author, *Title*, Publisher, Edition, Year, Chapter.
- For experimental data: cite the original experiment or NIST database with URL.
- For simulations or computational results: cite the method and software.
- **Multiple formats**: Use inline [n] for journal claims, superscript-style footnote numbers for textbook references, and source blocks for datasets.
- **No URL available**: Cite as `[n] Author(s), "Title," Journal, Volume, Pages, Year. [DOI: xxx]` — DOI serves as permanent identifier.
- **Multiple sources for same claim**: Use range notation [1–3] or list all: [1, 4, 7]. Order by credibility: primary experiment > review article > textbook.
- **Beautiful citations**: Style the reference list as a clean table with numbered rows, clickable links, and subtle alternating backgrounds. Primary sources get a small green dot indicator.
- **Source credibility hierarchy**: Peer-reviewed journal (Physical Review, Nature Physics) > arXiv preprint > textbook > lecture notes > popular science. Always prefer primary experimental data over secondary summaries.

## Typography & Color — The Physics Palette

### Fonts
- **Body**: Serif — EB Garamond, Georgia, or Computer Modern for LaTeX feel.
- **Headings**: Clean sans-serif — Inter, Helvetica Neue. Deep blue-gray (#1A365D). h2 = 1.5rem, h3 = 1.25rem.
- **Variables**: Always italic serif. Vectors bold italic. Units always upright. Function names upright.
- **Code/Computational**: Fira Code for any simulation or computational physics content.

### Color System
- **Background**: White (#FFFFFF).
- **Body text**: Dark charcoal (#2D3748).
- **Headings**: Deep navy (#1A365D).
- **Example boxes**: Light green fill (#F0FFF4), green left border (#38A169).
- **Constant boxes**: Light blue-gray (#EDF2F7), subtle border.
- **Theorem/Law boxes**: Pale blue fill (#EBF4FF), blue left border (#3182CE).
- **Warning/limiting cases**: Amber fill (#FFFAF0), amber border (#ED8936).
- **Diagram palette**: Blue (#3182CE), Crimson (#E53E3E), Forest (#38A169), Orange (#DD6B20), Purple (#805AD5).
- **Line height**: 1.7.
- **Extended chart palette** (7+ colors for complex charts): Blue (#3182CE), Teal (#319795), Crimson (#E53E3E), Forest (#38A169), Orange (#DD6B20), Purple (#805AD5), Gold (#D69E2E), Steel (#4A5568). All WCAG AA compliant on white (contrast ≥ 4.5:1 for text elements).
- **Semantic color rules**: Use blue as the default/neutral series. Red for energy/heat/positive charge. Green for equilibrium/stable states. Orange for kinetic/warning values. Purple for magnetic/quantum phenomena. Teal for secondary data series. Gold for reference/benchmark values.
- **Hover/interaction**: On hover, data series opacity increases to 1.0 while others dim to 0.5. Use CSS `:hover` on chart elements.
- **Print-friendly**: All colors maintain ≥ 3:1 contrast on white when printed in grayscale. Avoid red/green-only differentiation — use patterns (solid vs. dashed) as secondary encoding.
- **WCAG AA compliance**: All text elements meet 4.5:1 minimum. Chart colors meet 3:1 against white backgrounds. Test with colorblind simulators — the palette is deuteranopia-safe.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains 8 different measurements, put them all in a table. If there are 5 concepts to compare, build a 5-column comparison. Don't truncate data to fit a template.
- **Diagram everything spatial.** If the text describes a physical scenario (a ball on a ramp, a circuit, a wave), the LLM MUST attempt to create a diagram even if the research sources didn't include one. Physics without pictures is incomplete.
- **Scale formality to audience.** A report for a general audience on "How do magnets work?" uses fewer formal equations and more diagrams and analogies. A report on "Quantum Decoherence" uses full Dirac notation and density matrices.
- **Invent new visual containers.** If the content demands a "Phase Space Portrait" or an "Energy Budget Table," build it. The toolkit is a starting point, not a limitation.
- **Respect dimensional analysis.** Every number must have units. Every equation must be dimensionally consistent. This is a non-negotiable physics requirement.
- Never describes a physical phenomenon without an SVG diagram. If the research contains forces, fields, waves, energy levels, or spatial relationships, you MUST create at least one SVG diagram (force diagram, field visualization, wave plot, or energy level diagram).
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., equation block + force diagram SVG + worked example, or energy level diagram + experimental data table + limiting case callout). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never presents an equation without defining every variable and its unit
- Never describes a spatial concept without attempting a diagram
- Never shows a numerical result without units and significant figures
- Never skips showing the calculation work
- Never uses decorative gradients or non-functional visual elements
- Never presents conflicting experimental results without discussing the tension
- Never uses arbitrary colors in diagrams — every color maps to a physical quantity
- Never shows a chart without labeled axes, units, and a figure caption
- Never presents a physical constant without its uncertainty value
- Never skips SVG visualizations when the data supports them — at least one SVG diagram is mandatory per chapter. If the research contains forces, fields, waves, energy levels, or spatial relationships, you MUST create at least one SVG diagram (force diagram, field visualization, wave plot, or energy level diagram).


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
