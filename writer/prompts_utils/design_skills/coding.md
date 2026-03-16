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
- Monospace font (Fira Code, JetBrains Mono).
- `overflow-x: auto` for wide lines.
- Line numbers for reference when needed.
- Multiple blocks in different languages for the same concept.
- "Before/After" blocks showing refactoring improvements.
- "Input → Output" blocks showing command and result.
- Diff-style blocks showing changes: `+` added lines, `-` removed lines.

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

## Citation Style — Technical Sources
- Use inline links directly in context: "See the `<a href='URL'>official docs</a>`" or "According to `<a href='URL'>RFC 7231</a>`."
- For specific API references: link the function or endpoint name directly.
- For blog posts or articles: "Source: `<a href='URL'>Article Title, Author</a>`."
- For GitHub repositories: "Repository: `<a href='URL'>org/repo</a>`."
- Technical citations are navigational — they take the developer directly to the authoritative source.
- No formal bibliography needed — inline linking is the convention.

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

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research covers 15 API endpoints, document all 15. If there are 8 code examples, show all 8.
- **Code completeness is non-negotiable.** Every code block must be complete and runnable as-is. No "..." ellipsis, no "// your code here." Fill in real, working defaults.
- **Match depth to audience.** A "Getting Started" guide uses more step-by-step tutorials. A reference document uses more API tables. An architectural overview uses more diagrams.
- **Invent new patterns.** If the content demands a "Migration Guide" format, a "Troubleshooting Decision Tree," or a "Configuration Matrix," build it. The toolkit is a palette, not a cage.
- **Don't over-document obvious things.** `console.log("hello")` doesn't need a paragraph of explanation. Save prose for non-obvious concepts.

### What This Report NEVER Does
- Never shows incomplete code — every block must be runnable
- Never hides API parameters — everything documented
- Never uses serif fonts
- Never writes long prose when code would be clearer
- Never presents architecture without a diagram attempt
- Never omits error handling discussion for critical operations
