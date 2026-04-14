# Scientific General Report Design

## Identity & Scope
This skill activates when the user's query is about empirical science — biology, chemistry, environmental science, psychology, medicine, neuroscience, geology, ecology, or any topic where experimental methodology, data collection, and evidence-based conclusions are central. Think of a paper from Nature, Science, PLOS ONE, or a well-illustrated scientific review.

## How a Real Scientific Paper Looks & Feels
A scientific paper is the most OBJECTIVE document. Clean white background, clinical precision. Charts and data tables carry the core message — prose interprets them. The structure is instinctive to any scientist: Abstract → Introduction → Methods → Results → Discussion. Statistical significance is always stated. Methodology is isolated in its own visual block so it can be evaluated independently. Every figure has a numbered caption with enough detail to understand without reading body text. The visual hierarchy: Figure/Table → Caption → Interpretation paragraph. No decoration, no emotion, just evidence. There's a quiet beauty in a perfectly labeled chart with clear results.

## What Information Matters Most to Scientists & Researchers
- **Data quality**: Sample size, statistical significance, confidence intervals. Data without context is noise.
- **Methodology**: HOW was this measured? Can it be reproduced? Methods are the foundation of credibility.
- **Controls and comparisons**: What was the control group? What alternative explanations were considered?
- **Quantification**: "Improved" is meaningless. "34% improvement (p < 0.01, n=120)" is science.
- **Limitations acknowledged**: What CAN'T this study prove? Intellectual honesty builds trust.
- **Visual data**: Scientists think in graphs. A well-made chart communicates faster than a paragraph.
- **Reproducibility**: Enough detail that someone else could replicate the experiment.

## Content Structure & Narrative Flow
1. **Abstract & Introduction**: Research question and significance.
2. **Background / Literature**: What existing research says.
3. **Methods & Approach**: How data was collected, controls, instruments.
4. **Results & Data**: Findings via tables, charts, statistical analysis.
5. **Discussion & Conclusion**: Interpretation, limitations, future directions.

## Complete Visual Toolkit — Everything the LLM Can Use

### Charts.css — Essential for Scientific Data
The heaviest Charts.css user alongside finance:
- **Bar charts**: Comparing measurements across conditions, groups, or variables.
- **Column charts**: Time-series experimental data, growth measurements.
- **Line charts**: Dose-response curves, temperature vs. time, population dynamics, kinetics.
- **Area charts**: Cumulative measurements, total exposure, bioaccumulation curves.
- **Stacked bars**: Composition analysis — species distribution, element proportions, energy sources.
- **Grouped bars**: Control vs. experimental, placebo vs. treatment, before vs. after.
- **Percentage bars**: Proportional composition, survival rates, conversion percentages.
- Always include: labeled axes with units, sample sizes, significance stars (*), error bars where feasible.

### SVG Diagrams for Scientific Concepts
- **Molecular structures**: Ball-and-stick models, structural formulas, simple reaction diagrams.
- **Cell/organ diagrams**: Labeled organelles, tissue cross-sections, anatomical structures.
- **Process flows**: Metabolic pathways, chemical reaction chains, ecological cycles (carbon, nitrogen, water).
- **Phylogenetic trees**: Branching diagrams for evolutionary relationships.
- **Cross-sections**: Geological strata, tissue layers, material structures.
- **Lifecycle diagrams**: Organism life stages, product degradation stages.
- **Food webs/trophic levels**: Energy flow through ecosystems.
- **Experimental setup diagrams**: Simple illustrations of apparatus or experimental design.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide plots (growth curves, dose-response, spectra); `viewBox="0 0 400 400"` for square diagrams (molecular structures, cell diagrams, Venn diagrams).
- **Font sizing**: `font-family` must match body font (Inter/Roboto). Axis labels 12px, diagram titles 14px, data labels 11px.
- **Stroke widths**: 1.5px for grid lines, 2px for data lines/pathway arrows, 2.5px for axes, 1px for construction lines and decorative elements.
- **Color application**: Use the exact scientific palette — Blue (#3182CE), Teal (#319795), Coral (#E57373), Purple (#805AD5), Green (#38A169), Orange (#DD6B20). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Dose-response curve for compound X") and `<desc>` (describe all axes, data series, and key findings).
- **Background**: Transparent — scientific diagrams overlay on white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Species names use `<tspan font-style="italic">`.
- **Domain-specific SVG patterns**:
  - *Process flow/metabolic pathway*: `<rect>` or `<ellipse>` nodes for compounds, `<path>` arrows for reactions, labeled with enzyme names. Branching paths show alternative routes.
  - *Phylogenetic tree*: `<path>` branching structure with `<text>` labels at tips. Branch lengths proportional to divergence. Bootstrap values in small `<text>` at nodes.
  - *Cell/organelle diagram*: `<ellipse>` or `<path>` shapes for organelles, labeled with `<text>` and leader `<line>` pointers. Color-coded by function.
  - *Molecular structure*: `<circle>` for atoms (color-coded by element), `<line>` for bonds. Double bonds as parallel `<line>`.

### Charts.css Decision Guide
- IF comparing categories (treatment groups, species, conditions) → horizontal bar chart
- IF comparing time periods (daily measurements, yearly data) → column chart
- IF showing trend over continuous time (growth, decay, kinetics) → line chart
- IF showing composition (element proportions, species distribution) → stacked bar chart
- IF showing part-to-whole (survival rate, conversion percentage) → percentage bar
- IF comparing multiple series (control vs. treatment, pre vs. post) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart, numbered "Figure N:" with units and sample size
- Do NOT use Charts.css when: fewer than 3 data points (use a table), purely qualitative observations (use prose + SVG diagrams), or data requires complex error representation (use SVG with error bars)
- **NEVER use Charts.css when: fewer than 3 data points** — use a simple table or KPI card instead. Charts.css with 2 data points produces a meaningless visualization that wastes space and confuses readers.
- For Charts.css bar/column charts, use `--size` as a decimal fraction (0.0 to 1.0), NOT as a `calc()` expression. Example: `style="--size: 0.76"` for 76%. Do NOT use `calc(76 * 0.5%)` — this produces invalid CSS.
- **ALL `<th>` elements in Charts.css tables MUST have explicit inline styles** for `font-family`, `font-size`, `font-weight`, `color`, and `padding`. Do NOT rely on browser defaults or inherited styles. Example: `<th style="font-family: Inter, sans-serif; font-size: 0.875rem; font-weight: 600; color: #FFFFFF; background: #1A365D; padding: 0.5rem 0.75rem;">`

### Data Tables — Core Communication
- Units in every header column. Right-aligned numbers. Consistent decimal places.
- Include: n (sample size), mean, SD (±), p-values.
- Asterisks for significance levels: * p < 0.05, ** p < 0.01, *** p < 0.001.
- Row alternation for dense datasets.
- `<caption>` providing context.
- Footnotes for methodological notes.

### Method/Protocol Blocks
- Visually distinct containers with subtle background and clear "Methodology" label.
- Allows quick identification of HOW the study was done.
- Can include numbered protocol steps.

### Key Findings Callouts
- Distinct boxes for the most significant results.
- Blue-tinted background, blue left border, bold statement with stats.
- Used sparingly — 1-2 per major section.

### Comparison & Control Tables
- Side-by-side: Control vs. Experimental, Drug A vs. Drug B, Pre vs. Post.
- Statistical test results in a dedicated column.
- Clearly labeled which group is which.

### Figure Numbering & Captions
- Every visual: "Figure 1:", "Table 2:" — numbered sequentially.
- Captions below figures, above tables — scientific convention.
- Captions detailed enough to understand independently from body text.
- **EVERY visual element (chart, table, diagram) MUST be numbered sequentially**: "Figure 1:", "Figure 2:", "Table 1:", "Table 2:". Include the number in the `<caption>` element. This is non-negotiable scientific convention. Reference figures in prose: "As shown in Figure 1, ..."

### Error & Uncertainty Representation
- SVG lines for error bars where feasible.
- Always state the error type: SD, SE, 95% CI.
- In tables: ± notation for uncertainty.

### Hypothesis Testing Displays
- Clear statement of null and alternative hypotheses.
- Test used, test statistic, p-value, conclusion — in a compact results block.

### Edge Cases & Adaptations
- **No quantitative data**: For purely observational/descriptive science (e.g., new species description, field notes), use SVG diagrams, process flows, and structured prose tables. Emphasize methodology and qualitative evidence.
- **Too much data**: For datasets with hundreds of measurements (e.g., genomic data, climate records), summarize with statistical aggregates (mean, SD, range) and show representative Charts.css plots. Use `<details>` for full data tables.
- **Mixed content**: When prose dominates with occasional numbers, embed key metrics as inline callouts and use small charts only for sections with 3+ comparable data points.
- **Contradictory studies**: Present competing findings side-by-side in a comparison table with methodology differences highlighted. Discuss sample size, controls, and statistical power as possible explanations.
- **Variable chapter length**: Short topics (single experiment) get methods block + results table + one chart. Long topics (full research area) use the complete toolkit with literature comparison and meta-analysis summaries.
- **Default format mismatch**: If the science topic is historical (e.g., "Discovery of DNA"), borrow timeline patterns from the history skill. If it's computational (e.g., bioinformatics pipeline), borrow code block patterns from the coding skill.

## Citation Style — Scientific Sources
- Use inline numerical citations: [1], [2], [3] — matching journal conventions (Nature, Science style).
- Numbered reference list at chapter end.
- Format: `[n] Author(s), "Title," <a href="URL">Journal</a>, Volume(Issue), Pages, Year.`
- For review articles: same format with "[Review]" tag.
- For databases/datasets: "Source: `<a href='URL'>NCBI GenBank</a>`, Accession: XYZ123."
- For methods: cite the original method paper directly.
- Scientific credibility demands traceability — every claim linked to its source.
- **Multiple formats**: Use inline [n] for journal claims, superscript footnote numbers for method references, and source blocks for datasets.
- **No URL available**: Cite as `[n] Author(s), "Title," Journal, Volume(Issue), Pages, Year. [DOI: xxx]` — DOI is the permanent scientific identifier.
- **Multiple sources for same claim**: Use range notation [1–5] for consensus claims. For contested claims, list individually and note disagreement: "Supported by [2, 4]; challenged by [7]."
- **Beautiful citations**: Style the reference list as a clean numbered table with clickable journal links, DOI badges, and subtle alternating row backgrounds. Primary research gets a blue dot; reviews get a green dot.
- **Source credibility hierarchy**: Peer-reviewed primary research (Nature, Science, cell-specific journals) > systematic review/meta-analysis > preprint (bioRxiv, arXiv) > institutional report > textbook > popular science. Always prefer primary data over secondary interpretation.

## Typography & Color — The Scientific Palette

### Fonts
- **Body**: Clean sans-serif — Inter (first choice), Roboto, Source Sans Pro. Scientific papers are screen and print optimized.
- **Headings**: Same sans-serif, bold, dark blue-gray (#1A365D).
- **Data/Units**: Right-aligned, tabular figures if available.
- **Species names/variables**: Italic (biological convention for species, math convention for variables).

### Color System — Clean, Clinical, Evidence-Based
- **Background**: White (#FFFFFF) — pristine, clinical.
- **Body text**: Slate (#2D3748).
- **Headings**: Deep blue-gray (#1A365D).
- **Method blocks**: Light gray fill (#F7FAFC), subtle border.
- **Key findings**: Light blue fill (#EBF8FF), blue left border (#3182CE).
- **Warning/limitation boxes**: Amber fill (#FFFAF0), amber border (#ED8936).
- **Chart primary palette**: Blue (#3182CE), Teal (#319795), Coral (#E57373), Purple (#805AD5), Green (#38A169), Orange (#DD6B20). Chosen for colorblind accessibility.
- **Significance stars**: Deep red (#C53030).
- **Line height**: 1.7.
- **Max width**: 780px — wide enough for figures and tables.
- **Extended chart palette** (7+ colors): Blue (#3182CE), Teal (#319795), Coral (#E57373), Purple (#805AD5), Green (#38A169), Orange (#DD6B20), Steel (#4A5568), Gold (#D69E2E). All WCAG AA compliant on white.
- **Semantic color rules**: Blue = control/baseline group. Teal = experimental group 1. Coral = experimental group 2. Purple = tertiary comparison. Green = positive outcome/improvement. Orange = warning/adverse effect. Steel = reference/standard values.
- **Hover/interaction**: On hover, data series opacity increases to 1.0 while others dim to 0.6. Use CSS `:hover` with smooth transitions.
- **Print-friendly**: All colors maintain ≥ 3:1 contrast in grayscale. Supplement color differentiation with patterns (solid, striped, dotted fills) for print legibility.
- **WCAG AA compliance**: All text elements ≥ 4.5:1 contrast ratio. Chart colors ≥ 3:1 against white. The palette is specifically chosen for deuteranopia and protanopia accessibility.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains 12 experimental results, show all 12 in tables/charts. Don't summarize to fit a template.
- **Charts must match data types.** Continuous data → line charts. Categorical comparisons → bar charts. Composition → stacked bars. Don't force chart types.
- **Methodology is never optional.** Every scientific report must include HOW the data was obtained. Without methods, results have no credibility.
- **Invent new containers.** If the content demands a "Dose-Response Summary," a "Gene Expression Heatmap Description," or a "Multi-Variable Correlation Matrix," build it. Science uses dozens of specialized figure types.
- **Uncertainty is always stated.** Never present a measurement without its error range. Never present a comparison without statistical testing.
- **Adapt to the sub-field.** Biology reports might need more diagrams and lifecycle charts. Chemistry reports need reaction equations and molecular structures. Psychology reports need more about methodology and statistical validity.
- Never presents a process-based scientific topic without an SVG diagram. If the research describes mechanisms, cycles, pathways, or systems (e.g., greenhouse effect, carbon cycle, metabolic pathway, ecological food web), you MUST create at least one SVG process flow or system diagram.
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., data table + process flow SVG + key findings callout, or experimental results chart + methodology box + limitations note). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never presents a result without statistical context
- Never uses emotional or subjective language
- Never skips methodology
- Never shows a chart without labeled axes, units, and caption
- Never uses decorative backgrounds or gradients
- Never presents a measurement without uncertainty
- Never uses Charts.css without stating sample size and significance
- Never presents a single study's findings as definitive — always note limitations
- Never uses color as the sole differentiator in charts — always pair with labels or patterns
- Never skips SVG visualizations when the data supports them — at least one SVG diagram is mandatory per chapter. If the research describes mechanisms, cycles, pathways, or systems (e.g., greenhouse effect, carbon cycle, metabolic pathway, ecological food web), you MUST create at least one SVG process flow or system diagram.
