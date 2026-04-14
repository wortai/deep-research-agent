# Modern Minimalist Report Design

## Identity & Scope
This skill activates when the user wants a clean, ultra-concise, highly scannable summary or briefing. Best for executive summaries, competitive snapshots, product overviews, market briefings, or any topic where maximum information density per element is the goal. The report should look like an Apple keynote turned document, a Notion summary, or a Dieter Rams-designed briefing.

## How a Minimalist Briefing Looks & Feels
A minimalist document is the OPPOSITE of a textbook. Every word earns its place. Whitespace is the dominant visual element — it's not empty space, it's intentional breathing room. Data is presented as TYPOGRAPHY: giant numbers, not charts. Tables have no visible borders — alignment alone creates structure. A single accent color, if any. The overall impression is sophistication, extreme confidence, and surgical clarity. Less IS more. What remains on the page is perfect.

## What Information Matters in Minimalist Context
- **The single most important takeaway.** What is the one sentence the reader must remember?
- **Key numbers without decoration.** Three data points, clearly presented, are worth more than a 10-row table.
- **Hierarchy without ornament.** Size, weight, and position communicate importance — not color or borders.
- **Negative space as communication.** What you LEAVE OUT tells the reader what to focus ON.
- **Decisiveness.** Minimalist documents make a clear point. They don't hedge or list alternatives — they choose.

## Content Structure & Narrative Flow
1. **Core Takeaway**: Single most important conclusion in 1-2 sentences.
2. **Key Data Points**: 3-5 critical metrics as typographic elements.
3. **Analysis**: Brief, focused sections. No filler prose.

## Complete Visual Toolkit — Everything the LLM Can Use

### Typographic Data Display — The Signature Technique
- Key data as oversized text elements: small muted label above, giant bold number below, optional trend beneath.
- This IS the minimalist chart — typography replaces visualization.
- Separated by subtle bottom borders or generous spacing.

### Borderless Tables
- Zero visible borders. Alignment and whitespace create structure.
- Only the lightest divider rules (1px, nearly invisible gray).
- Two-column: label left, value right-aligned.
- Dense but elegant.

### Minimal Charts.css
- If charts are strictly necessary, use the simplest representation possible.
- Single-color bars. No gridlines. No axis labels if context is obvious.
- Area charts with a single soft fill.
- Charts should feel like a "gentle suggestion" — not a data-dense visualization.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide layouts (trend lines, comparisons); `viewBox="0 0 400 400"` for square diagrams (proportional representations).
- **Font sizing**: `font-family` must match body font (Inter). Labels 12px, titles 14px, data labels 11px.
- **Stroke widths**: 1.5px for minimal grid lines, 2px for data lines, 2.5px for primary axes, 1px for subtle decorative elements.
- **Color application**: Use ONLY the minimalist palette — near-black (#1A202C), muted gray (#A0AEC0), single accent blue (#3182CE). No other colors permitted.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Revenue trend: Q1–Q4") and `<desc>` (describe the trend direction and key values).
- **Background**: Transparent — minimalist diagrams overlay on pure white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Keep text minimal — labels only, no explanations.
- **Domain-specific SVG patterns**:
  - *Trend line*: Minimal `<polyline>` with no grid, no axes labels, just the shape. Single accent color stroke.
  - *Proportional bar*: Single `<rect>` elements, no grid, no labels beyond values. Monochrome with accent for emphasis.
  - *Comparison*: Two or three `<rect>` bars side-by-side, minimal spacing, no decoration.

### Charts.css Decision Guide
- IF comparing categories (options, features) → horizontal bar chart (single color, no gridlines)
- IF comparing time periods (quarters, months) → column chart (single color, minimal)
- IF showing trend over continuous time → line chart (single line, no grid)
- IF showing composition → stacked bar chart (single color family, varying opacity)
- IF showing part-to-whole → percentage bar (single accent fill)
- IF comparing multiple series → grouped bar chart (avoid if possible — violates minimalism)
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart — single line, muted gray, no source attribution unless critical
- Do NOT use Charts.css when: fewer than 3 data points (use typographic display), purely qualitative content (use prose), or data is better shown as giant numbers

### Card-Style Information Blocks
- No visible borders — only spacing separation.
- Optional very light background tint.
- Information grouped by proximity alone.

### Prose
- Ultra-minimal. No paragraph longer than 3 sentences. Maximum information per word.
- No transition sentences. No filler. No hedging.
- Active voice only. Declarative statements.

### Section Spacing as Design
- 4-5em vertical gaps between sections — whitespace IS the design.
- No decorative dividers — space alone separates.

### Single Accent Color
- At most ONE accent color, used sparingly. A single blue link. A single highlighted figure.
- The constraint creates elegance.

### Key Insight Line
- A single sentence, bold, slightly larger font, centered — the "thesis statement" of the document.
- Used once, for maximum impact.

### Edge Cases & Adaptations
- **No quantitative data**: For purely qualitative topics, use typographic emphasis (bold, size) for key phrases instead of numbers. Replace charts with concise prose statements.
- **Too much data**: Minimalism cannot handle hundreds of data points. Summarize to the 3-5 most critical metrics. Use `<details>` for full data if absolutely necessary — but consider whether minimalism is the right skill.
- **Mixed content**: When some numbers exist, show only the 3 most important as typographic elements. Everything else goes into a borderless table.
- **Contradictory sources**: State the disagreement in one sentence. Do not create comparison tables — that violates minimalism. Pick the most credible source and note the disagreement inline.
- **Variable chapter length**: Short topics get a single takeaway + 3 metrics. Long topics — reconsider if minimalism is appropriate. If forced, use multiple sections each with their own takeaway.
- **Default format mismatch**: If the topic demands rich visual explanation, minimalism is the wrong skill. Flag this and borrow sparingly from other skills only for essential elements.

## Citation Style — Minimalist Sources
- Inline, ultra-discreet: "(Source: `<a href='URL'>link</a>`)" — never more than necessary.
- Or a single "Sources" line at the document end listing URLs.
- Citations are footnotes to footnotes — present but invisible unless sought.
- **Multiple formats**: Use inline parenthetical for data claims. No formal reference list unless legally required.
- **No URL available**: Cite as "(Source: Organization Name, Date)" — minimal attribution.
- **Multiple sources for same claim**: Cite only the most authoritative source. Minimalism does not do source lists.
- **Beautiful citations**: Style as a single muted-gray line at document end. No table, no numbering, no decoration.
- **Source credibility hierarchy**: Official data source > established publication > expert source. Cite only the top source.

## Typography & Color — The Minimalist Palette

### Fonts
- **Body**: Geometric sans-serif — Inter (first choice), Outfit, Helvetica Neue, SF Pro. Every glyph mathematically precise.
- **Key numbers**: Extra bold (800-900), oversized (2-3rem).
- **Labels**: Small (0.75rem), uppercase, letter-spacing 0.1em, muted gray — the faintest whisper of context.

### Color System — Absence as Aesthetic
- **Background**: White (#FFFFFF) — not off-white, not cream. Pure.
- **Body text**: Near-black (#1A202C) — confident, not harsh.
- **Labels/captions**: Muted gray (#A0AEC0) — barely there.
- **Dividers**: Whisper gray (#EDF2F7) — rules that almost don't exist.
- **Accent (if used at all)**: Single cool blue (#3182CE) — applied to ONE element on the page.
- **Line height**: 1.5 — tighter than most. Dense, considered.
- **Max width**: 600px — narrow. Focused. Intimate.
- **Paragraph spacing**: 0.5em — tight, controlled.
- **Extended chart palette** (7+ colors, rarely used): Near-black (#1A202C), Muted gray (#A0AEC0), Blue (#3182CE), Steel (#4A5568), Light gray (#CBD5E0), Whisper (#EDF2F7), White (#FFFFFF). All WCAG AA compliant.
- **Semantic color rules**: Near-black = primary data/text. Muted gray = secondary/labels. Blue = single accent for emphasis. Steel = tertiary data (avoid if possible). Light gray = structural elements. Whisper = dividers. White = background only.
- **Hover/interaction**: None. Minimalism is static and confident.
- **Print-friendly**: The entire palette is inherently print-friendly — it's already grayscale-adjacent.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio on white. The near-black on white = 16.5:1 — excellent. Blue (#3182CE) on white = 4.6:1 — meets minimum.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Brevity is the entire point.** If the content is too complex for minimalism, consider whether this skill is the right choice. But IF it's selected, commit fully to concision.
- **Cut ruthlessly.** For every sentence, ask: does this add new information? If not, delete it.
- **Never sacrifice critical data.** Minimalism means showing LESS, not hiding what matters. The key numbers must be prominent. Everything else can be removed.
- **Don't force complexity.** If the content naturally lends itself to 3 bullet points, don't expand to 10 for "completeness." Minimalism rewards restraint.
- **One accent color maximum.** If you feel the need for a second color, rethink the design.
- Never presents a minimalist report without at least one carefully crafted visual. Even minimal reports need one strong visual anchor — an SVG diagram, a key number display, or a clean chart.
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., key number display + minimal chart + short analysis, or single-statement callout + sparse data table + brief context). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never uses decorative elements, gradients, or illustrations
- Never writes more than 3 sentences per paragraph
- Never uses serif fonts — this is geometric and modern
- Never uses visible borders when spacing works
- Never uses more than one accent color
- Never uses complex chart configurations
- Never uses ornamental dividers or icons
- Never uses SVG diagrams unless the visual is essential and cannot be expressed in typography
- Never cites more than one source per claim
- Never uses hover effects or interactive elements
- Never skips SVG visualizations when the data supports them — at least one carefully crafted visual is mandatory per chapter. Even minimal reports need one strong visual anchor — an SVG diagram, a key number display, or a clean chart.
