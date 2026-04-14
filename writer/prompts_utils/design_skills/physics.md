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
