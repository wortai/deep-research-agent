# Coding & Software Report Design

## Identity & Scope
This skill activates when the user's query is about programming, software engineering, frameworks, APIs, system design, DevOps, databases, or any technology topic. The report should look like the best developer documentation — Stripe Docs, MDN, React Docs, Cloudflare Blog, or a premium O'Reilly book.

## How Real Dev Docs Look & Feel
Developer documentation is FUNCTIONAL above all else. Code blocks are first-class citizens — styled like editor/terminal windows with dark backgrounds and syntax-colored text. API parameters live in exhaustive tables. Architecture is shown through diagrams. Prose is minimal and punchy — developers scan, they don't read novels. The color scheme supports dark-mode-friendly code blocks. Everything is copy-paste ready. Navigation is extremely clear — the developer should find what they need in seconds, not minutes. Think of the clarity of Stripe's API docs: every endpoint documented, every parameter typed, every response shown.

## What Information Matters Most to Developers
- **Working code**: Code that RUNS. Not pseudocode, not fragments — complete, copy-paste-able examples.
- **Parameters and types**: Every function parameter, its type, whether it's required, and what happens when it's missing.
- **Error handling**: What goes wrong and how to fix it. Error messages and their meanings.
- **Performance trade-offs**: O(n) vs O(n²). Memory vs. speed. Sync vs. async. Developers need to make informed choices.
- **Architecture decisions**: WHY was it designed this way? What alternatives were considered?
- **Versioning and compatibility**: Which version introduced this? What's deprecated? Breaking changes.
- **Quick setup**: Get from zero to working code in the fewest possible steps.

## Content Structure & Narrative Flow
1. **What & Why**: What this technology IS and what problem it solves. Concise.
2. **Setup / Getting Started**: Installation, config, prerequisites. Copy-paste ready.
3. **Core Concepts & API Reference**: Functions, classes, patterns in structured form.
4. **Working Code Examples**: Complete, runnable code blocks.
5. **Architecture & Best Practices**: Trade-offs, performance, security.

## Complete Visual Toolkit — Everything the LLM Can Use

### Code Blocks — The Star of the Show
- Terminal/editor-style with header bar showing filename and language tag.
- Dark backgrounds (#1A202C) with warm syntax-colored text.
- Monospace font ('Fira Code', 'JetBrains Mono', monospace).
- `overflow-x: auto` for wide lines.
- Line numbers for reference when needed.
- Multiple blocks in different languages for the same concept.
- "Before/After" blocks showing refactoring improvements.
- "Input → Output" blocks showing command and result.
- Diff-style blocks showing changes: `+` added lines, `-` removed lines.
- **Syntax highlighting is mandatory.** Every code block MUST use inline `<span>` elements with color classes for at minimum: keywords (blue `#63B3ED`), strings (green `#68D391`), comments (gray `#718096` italic), and numbers (purple `#D6BCFA`). At minimum, highlight keywords and strings. Monochrome code blocks are unacceptable — they make code harder to scan and less professional.
- **Every code block must have a header bar** showing the HTTP method/endpoint or filename AND the language tag. Format: `<div style="background: #2D3748; padding: 0.5rem 1.25rem; color: #A0AEC0; font-family: 'Fira Code', monospace; font-size: 0.875rem;">METHOD /endpoint — JSON</div>` or `<div style="background: #2D3748; padding: 0.5rem 1.25rem; color: #A0AEC0; font-family: 'Fira Code', monospace; font-size: 0.875rem;">filename.js — JavaScript</div>`. No code block without a header.

### API Reference Tables
- Dense, precise tables: Parameter | Type | Required | Default | Description.
- Type badges — small colored pills: `string`, `number`, `boolean`, `object`, `array`.
- Monospace for parameter names and default values.
- Nested indentation for complex object parameters.
- Return value documentation in a separate table or block.

### Architecture & System Diagrams (SVG)
- **Flow diagrams**: Boxes → arrows → boxes showing data flow or request lifecycle.
- **Component diagrams**: Nested rectangles for system architecture.
- **Sequence diagrams**: Vertical lifelines with horizontal arrows for request/response.
- **Database schemas**: Entity-relationship diagrams with typed fields.
- **Dependency graphs**: Module/package relationships.
- **State machine diagrams**: States and transitions for complex logic.
- All clean, labeled SVG. Dark outlines, white fills, blue/gray accents.

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide diagrams (flow diagrams, sequence diagrams, architecture); `viewBox="0 0 400 400"` for square diagrams (state machines, component diagrams).
- **Font sizing**: `font-family` must match body font (Inter). Node labels 12px, diagram titles 14px, annotation labels 11px.
- **Stroke widths**: 1.5px for grid/guide lines, 2px for connection arrows, 2.5px for component borders, 1px for decorative elements.
- **Color application**: Use the exact coding palette — dark outlines (#2D3748), white fills, blue accents (#2B6CB0), gray secondary (#718096). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Request lifecycle: Client → API → Database") and `<desc>` (describe all components, connections, and data flow direction).
- **Background**: Transparent — diagrams overlay on white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Code within labels uses `<tspan font-family="monospace">`.
- **Domain-specific SVG patterns**:
  - *Flow diagram*: `<rect>` nodes with rounded corners (`rx="4"`), `<path>` arrows with `<polygon>` arrowheads. Labels centered in nodes.
  - *Sequence diagram*: Vertical `<line>` lifelines, horizontal `<path>` arrows between them. Activation bars as narrow `<rect>` on lifelines.
  - *ER diagram*: `<rect>` entities with `<line>` separators for fields. Relationship `<path>` with cardinality `<text>` labels.
  - *State machine*: `<ellipse>` states, `<path>` transitions with `<text>` trigger labels. Initial state as filled `<circle>`.

ARCHITECTURE/ER DIAGRAM TEMPLATE — Use for API relationships, system architecture, data flow:
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" width="100%">
  <title>Architecture diagram title</title>
  <desc>Description of components and their relationships</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2D3748"/>
    </marker>
  </defs>
  <!-- Component boxes -->
  <rect x="50" y="150" width="160" height="80" rx="6" fill="#EBF8FF" stroke="#3182CE" stroke-width="2"/>
  <text x="130" y="185" text-anchor="middle" font-family="Inter, sans-serif" font-size="14" font-weight="600" fill="#1A365D">Client</text>
  <text x="130" y="205" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="#2D3748">Browser/App</text>
  <rect x="320" y="150" width="160" height="80" rx="6" fill="#F0FFF4" stroke="#38A169" stroke-width="2"/>
  <text x="400" y="185" text-anchor="middle" font-family="Inter, sans-serif" font-size="14" font-weight="600" fill="#1A365D">API Server</text>
  <text x="400" y="205" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="#2D3748">REST Endpoints</text>
  <rect x="590" y="150" width="160" height="80" rx="6" fill="#FFFAF0" stroke="#DD6B20" stroke-width="2"/>
  <text x="670" y="185" text-anchor="middle" font-family="Inter, sans-serif" font-size="14" font-weight="600" fill="#1A365D">Database</text>
  <text x="670" y="205" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="#2D3748">PostgreSQL</text>
  <!-- Connection arrows -->
  <line x1="210" y1="190" x2="320" y2="190" stroke="#2D3748" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="480" y1="190" x2="590" y2="190" stroke="#2D3748" stroke-width="2" marker-end="url(#arrow)"/>
  <!-- Labels on arrows -->
  <text x="265" y="180" text-anchor="middle" font-family="Inter, sans-serif" font-size="10" fill="#4A5568">HTTP/JSON</text>
  <text x="535" y="180" text-anchor="middle" font-family="Inter, sans-serif" font-size="10" fill="#4A5568">SQL Queries</text>
</svg>

### Charts.css Decision Guide
- IF comparing categories (frameworks, libraries, approaches) → horizontal bar chart
- IF comparing time periods (version releases, performance over time) → column chart
- IF showing trend over continuous time (response time vs. load, memory growth) → line chart
- IF showing composition (bundle size breakdown, time spent by phase) → stacked bar chart
- IF showing part-to-whole (test coverage, feature completion) → percentage bar
- IF comparing multiple series (before vs. after optimization, framework A vs. B) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart with source/tool version
- Do NOT use Charts.css when: fewer than 3 data points (use a table), purely qualitative comparison (use feature matrix), or data is code-based (use code blocks)
- **NEVER use Charts.css when: fewer than 3 data points** — use a simple table or KPI card instead. Charts.css with 2 data points produces a meaningless visualization that wastes space and confuses readers.
- For Charts.css bar/column charts, use `--size` as a decimal fraction (0.0 to 1.0), NOT as a `calc()` expression. Example: `style="--size: 0.76"` for 76%. Do NOT use `calc(76 * 0.5%)` — this produces invalid CSS.
- **ALL `<th>` elements in Charts.css tables MUST have explicit inline styles** for `font-family`, `font-size`, `font-weight`, `color`, and `padding`. Do NOT rely on browser defaults or inherited styles. Example: `<th style="font-family: Inter, sans-serif; font-size: 0.875rem; font-weight: 600; color: #FFFFFF; background: #1A365D; padding: 0.5rem 0.75rem;">`

### Admonition / Callout Boxes
- **⚠️ Warning** (Orange): Destructive operations, breaking changes, deprecations.
- **ℹ️ Note** (Blue): Important context, caveats, edge cases.
- **💡 Tip** (Green): Performance optimizations, shortcuts, best practices.
- **🚨 Danger** (Red): Security risks, data loss, irreversible operations.
- **📝 Example** (Gray): Supplementary code examples or usage notes.

### Comparison Tables
- Library vs library, framework vs framework, approach vs approach.
- ✓/✗ feature matrices.
- Highlight recommended option with accent background.
- Performance benchmarks in tabular form.

### Step-by-Step Tutorials
- Numbered steps with code blocks interspersed.
- Each step complete and testable.
- Expected output shown after each step.
- "✅ If successful, you should see..." confirmation messages.

### Charts.css for Performance/Benchmark Data
- **Bar charts**: Response times, memory usage, throughput across approaches.
- **Line charts**: Performance scaling, request handling over load.
- Tech-friendly colors — blues, purples, teals.

### Terminal Output Blocks
- Distinct from code — lighter or different background, labeled "Output."
- Command → output patterns for CLI workflows.
- Error messages in red-tinted output blocks.

### Configuration File Displays
- YAML, JSON, TOML, `.env` configurations in code blocks with appropriate language tag.
- Inline comments explaining each field.

### Edge Cases & Adaptations
- **No quantitative data**: For purely conceptual topics (e.g., "What is Functional Programming?"), use code examples, comparison tables, and architecture diagrams. Skip Charts.css entirely.
- **Too much data**: For API docs with hundreds of endpoints, organize by resource category with summary tables. Use `<details>` for full parameter lists. Show representative examples.
- **Mixed content**: When prose dominates with some code, embed code inline for short snippets and use full blocks for anything over 3 lines. Use Charts.css only for benchmark sections.
- **Contradictory sources**: When docs conflict (e.g., different framework versions), present both with version labels. Note deprecation status and recommend the current best practice.
- **Variable chapter length**: Short topics (single function) get code block + parameter table + example. Long topics (full framework) use the complete toolkit with architecture diagrams and benchmark charts.
- **Default format mismatch**: If the coding topic is historical (e.g., "Evolution of JavaScript"), borrow timeline patterns from the history skill. If it's tutorial-heavy, borrow practice patterns from the practice_learn skill.

## Citation Style — Technical Sources
- Use inline links directly in context: "See the `<a href='URL'>official docs</a>`" or "According to `<a href='URL'>RFC 7231</a>`."
- For specific API references: link the function or endpoint name directly.
- For blog posts or articles: "Source: `<a href='URL'>Article Title, Author</a>`."
- For GitHub repositories: "Repository: `<a href='URL'>org/repo</a>`."
- Technical citations are navigational — they take the developer directly to the authoritative source.
- No formal bibliography needed — inline linking is the convention.
- **Multiple formats**: Use inline links for docs, footnote-style numbers for academic papers, and source blocks for specifications.
- **No URL available**: Cite as "RFC 7231, Section 4.3.1" or "MDN Web Docs, 'Array.prototype.map'" — standard identifiers serve as permanent references.
- **Multiple sources for same claim**: Link the most authoritative source first (official docs > RFC/spec > well-known blog > Stack Overflow). Use "See also" for supplementary sources.
- **Beautiful citations**: Style reference links as compact inline badges with source type icon (📄 spec, 📖 docs, 💻 repo). Group by source type at section end.
- **Source credibility hierarchy**: Official documentation / RFC / language spec > peer-reviewed paper > well-known technical blog > community wiki > Stack Overflow > personal blog. Always prefer official docs.

## Typography & Color — The Developer Palette

### Fonts
- **Body**: Clean sans-serif — Inter, system-ui, -apple-system. Developers read on screens.
- **Code**: Monospace — Fira Code (first choice), JetBrains Mono, Source Code Pro.
- **Headings**: Same sans-serif as body, bolder weight.

### Color System — Clean, High-Contrast, Code-Centric
- **Background**: White (#FFFFFF) for prose, dark (#1A202C) for code blocks.
- **Body text**: Dark gray (#2D3748).
- **Headings**: Near-black (#1A202C).
- **Code header bar**: Dark gray (#2D3748), muted text (#A0AEC0).
- **Code text**: Light gray (#E2E8F0) on dark background.
- **Type badges**: Light blue bg (#BEE3F8), dark blue text (#2A4365).
- **Links/accents**: Blue (#2B6CB0).
- **Warning box**: Orange border (#ED8936), orange-cream bg (#FFFAF0).
- **Note box**: Blue border (#3182CE), pale blue bg (#EBF8FF).
- **Danger box**: Red border (#E53E3E), pale red bg (#FFF5F5).
- **Table headers**: Light gray bg (#EDF2F7), dark text.
- **Line height**: 1.6 for prose, 1.5 for code.
- **Extended chart palette** (7+ colors): Blue (#3182CE), Teal (#319795), Purple (#805AD5), Green (#38A169), Orange (#DD6B20), Steel (#4A5568), Gold (#D69E2E). All WCAG AA compliant on white.
- **Semantic color rules**: Blue = default/primary data series. Teal = secondary comparison. Purple = advanced/optimization metrics. Green = success/pass rates. Orange = warning/degradation. Steel = baseline/reference. Gold = premium/benchmark values.
- **Hover/interaction**: On hover, chart bars increase opacity and show exact values. Use CSS `:hover` transitions.
- **Print-friendly**: Code blocks print with light gray background instead of dark. All chart colors maintain ≥ 3:1 contrast in grayscale.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio. Chart colors ≥ 3:1 against white. Code text on dark background (#E2E8F0 on #1A202C) = 10.5:1 — excellent.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research covers 15 API endpoints, document all 15. If there are 8 code examples, show all 8.
- **Code completeness is non-negotiable.** Every code block must be complete and runnable as-is. No "..." ellipsis, no "// your code here." Fill in real, working defaults.
- **Match depth to audience.** A "Getting Started" guide uses more step-by-step tutorials. A reference document uses more API tables. An architectural overview uses more diagrams.
- **Invent new patterns.** If the content demands a "Migration Guide" format, a "Troubleshooting Decision Tree," or a "Configuration Matrix," build it. The toolkit is a palette, not a cage.
- **Don't over-document obvious things.** `console.log("hello")` doesn't need a paragraph of explanation. Save prose for non-obvious concepts.
- Never documents API relationships, architecture, or data flow without an SVG diagram. If the research describes entity relationships (Users → Orders), request lifecycles, system architecture, or data flow, you MUST create at least one SVG diagram (ER diagram, architecture diagram, sequence diagram, or flow chart).
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., code block + API table + architecture SVG, or terminal output + parameter table + sequence diagram). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never shows incomplete code — every block must be runnable
- Never hides API parameters — everything documented
- Never uses serif fonts
- Never writes long prose when code would be clearer
- Never presents architecture without a diagram attempt
- Never omits error handling discussion for critical operations
- Never discusses security, deprecation, breaking changes, or important caveats without a semantic admonition box (⚠️ Warning, 🚨 Danger, ℹ️ Note, 💡 Tip).
- Never uses Charts.css for data that's better shown as a code example
- Never presents deprecated APIs without clear deprecation warnings
- Never uses decorative elements in architecture diagrams — every shape carries meaning
- Never skips SVG visualizations when the data supports them — at least one SVG diagram is mandatory per chapter. If the research describes entity relationships (Users → Orders), request lifecycles, system architecture, or data flow, you MUST create at least one SVG diagram (ER diagram, architecture diagram, sequence diagram, or flow chart).
