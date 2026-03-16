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

### Error & Uncertainty Representation
- SVG lines for error bars where feasible.
- Always state the error type: SD, SE, 95% CI.
- In tables: ± notation for uncertainty.

### Hypothesis Testing Displays
- Clear statement of null and alternative hypotheses.
- Test used, test statistic, p-value, conclusion — in a compact results block.

## Citation Style — Scientific Sources
- Use inline numerical citations: [1], [2], [3] — matching journal conventions (Nature, Science style).
- Numbered reference list at chapter end.
- Format: `[n] Author(s), "Title," <a href="URL">Journal</a>, Volume(Issue), Pages, Year.`
- For review articles: same format with "[Review]" tag.
- For databases/datasets: "Source: `<a href='URL'>NCBI GenBank</a>`, Accession: XYZ123."
- For methods: cite the original method paper directly.
- Scientific credibility demands traceability — every claim linked to its source.

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

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains 12 experimental results, show all 12 in tables/charts. Don't summarize to fit a template.
- **Charts must match data types.** Continuous data → line charts. Categorical comparisons → bar charts. Composition → stacked bars. Don't force chart types.
- **Methodology is never optional.** Every scientific report must include HOW the data was obtained. Without methods, results have no credibility.
- **Invent new containers.** If the content demands a "Dose-Response Summary," a "Gene Expression Heatmap Description," or a "Multi-Variable Correlation Matrix," build it. Science uses dozens of specialized figure types.
- **Uncertainty is always stated.** Never present a measurement without its error range. Never present a comparison without statistical testing.
- **Adapt to the sub-field.** Biology reports might need more diagrams and lifecycle charts. Chemistry reports need reaction equations and molecular structures. Psychology reports need more about methodology and statistical validity.

### What This Report NEVER Does
- Never presents a result without statistical context
- Never uses emotional or subjective language
- Never skips methodology
- Never shows a chart without labeled axes, units, and caption
- Never uses decorative backgrounds or gradients
- Never presents a measurement without uncertainty
