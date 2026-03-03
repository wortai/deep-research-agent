# Programmer & API Documentation Layout

**Vibe**: Developer-focused, dark mode (or high-contrast sharp light mode), monospace-heavy, GitHub/Stripe docs style.
**Colors**: 
- Background: Dark Mode (`#0D1117`) or Sleek Light Mode (`#FFFFFF` with `#F6F8FA` blocks)
- Text: Light Gray (`#C9D1D9`) or Dark Gray (`#24292F`)
- Headings: Pure White (`#FFFFFF`) or True Black (`#000000`)
- Accents: Electric Blue (`#58A6FF`) or Primary Purple (`#8250DF`).

**Typography**:
- Font-Family: Headings and Interface in system sans-serif ('Inter', '-apple-system').
- Code & Tech terms: Exclusively monospace ('Fira Code', 'JetBrains Mono', 'Menlo').

**Components**:
- `pre` / `code`: The star of the show. Dark background (`#161B22`), rounded corners (`6px`), syntax highlighting colors if possible, horizontal scrolling. Inline code gets a subtle grayish background bounding box.
- `blockquote`: Used for "Warnings" or "Notes". Border-left in bright yellow or red, depending on context.
- `table`: Parameter descriptions. Columns for "Name", "Type", "Description". Mono-spaced types, very clean borders (`1px solid #30363D`).
- Links (`a`): Distinct tech blue, underline only on hover.
- `h1`-`h3`: Very tight margins, bold, perhaps with an `id` anchor `#` symbol implemented via CSS `::before` on hover.

**Focus**: Extreme clarity on code snippets, strict visual hierarchy representing object relations, high contrast for long staring sessions.
