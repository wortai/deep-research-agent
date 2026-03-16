# Practice & Learning Report Design

## Identity & Scope
This skill activates when the user wants to actively learn or practice — study guides, cheat sheets, flashcard-style content, exam prep, problem sets, tutorials, step-by-step skill building, or revision summaries. Think of a premium Notion study guide, the best Anki deck, a Kumon worksheet, or Khan Academy's best moments turned into a document.

## How Real Study Material Looks & Feels
The best study materials are INTERACTIVE and SCANNABLE. Information is organized for rapid lookup, not sequential reading. Color-coded difficulty levels guide the student. Click-to-reveal solutions force active recall. Dense reference tables give instant answers. Tip boxes warn about mistakes. The layout says: "This was designed by someone who understands how learning works." Every element serves retention. Nothing is decorative — but everything is visually clean and inviting enough to make studying feel achievable, not daunting.

## What Information Matters Most to Students & Learners
- **Crystal clarity**: No ambiguity. Definitions must be exact. Steps must be numbered. Answers must be definitive.
- **Active recall**: The student must TRY before they see the answer. Hidden solutions are pedagogically superior to visible ones.
- **Graduated difficulty**: Start easy, build up. The student can self-assess their level by attempting the right difficulty tier.
- **Common mistakes**: Knowing what goes WRONG is as valuable as knowing what's right. Error awareness prevents repeat failures.
- **Analogies and mnemonics**: Abstract concepts stick when connected to something concrete or memorable.
- **Quick reference**: Formulas, rules, syntax — the "cheat sheet" that saves time during practice. Dense, scannable, always nearby.
- **Immediate feedback**: See the problem → attempt it → reveal the answer → understand any gap. Short feedback loops.

## Content Structure & Narrative Flow
1. **Concept Overview**: Brief, crystal-clear explanation. No fluff. Use analogies.
2. **Key Reference Table / Cheat Sheet**: Dense table of formulas, definitions, rules.
3. **Practice Problems (Graded by Difficulty)**: Easy → Medium → Hard, each labeled.
4. **Solutions (Hidden)**: Every problem has step-by-step solution behind `<details>`.
5. **Common Mistakes & Tips**: Warning boxes about frequent errors.

## Complete Visual Toolkit — Everything the LLM Can Use

### Concept Explanations
- Short, punchy paragraphs (3-4 sentences max). Bold key terms. Use analogies.
- If a concept fits better as a table, diagram, or comparison — use that instead of prose.
- Numbered steps for procedures, bullet points for properties/characteristics.
- "In plain English" rephrasing after any technical definition.

### Cheat Sheet / Reference Tables
- Dense, compact tables — alternating row colors, clear headers.
- Monospace for code/formulas, sans-serif for descriptions.
- Maximum information density — the "tear-out page."
- Can use multi-column layouts for very dense reference material.
- Group related formulas/rules by category within the table.

### Difficulty Badges
- Every problem: colored inline pill badge — Easy (green), Medium (yellow/amber), Hard (red).
- Small, clear, instant visual categorization.
- Optional: estimated time to complete.

### Interactive Click-to-Reveal (The Signature Element)
- Problem fully visible in a bordered card container.
- Solution hidden in `<details><summary>Click to reveal solution ▸</summary>...</details>`.
- Solutions show step-by-step reasoning, not just final answers.
- Final answers boxed/highlighted within the solution.
- Pattern works for: math problems, coding challenges, MCQ, fill-in-blank, concept checks, vocabulary, translations.

### Flashcard-Style Q&A Blocks
- Question visible, answer behind `<details>`.
- Card-like styling — rounded corners, subtle border.
- Great for definitions, vocabulary, key facts, concept verification.

### Tip / Warning / Gotcha Boxes
- **⚠️ Common Mistake** (Orange): Errors students typically make. Amber border, warm cream background.
- **💡 Pro Tip** (Blue): Shortcuts, mnemonics, efficiency tricks. Blue border, pale blue background.
- **📌 Remember** (Green): Critical facts to memorize. Green border, pale green background.
- **🚨 Watch Out** (Red): Dangerous misconceptions, tricky edge cases. Red border, pale red background.

### Step-by-Step Tutorials
- Numbered ordered lists with each step as a clear, actionable instruction.
- Each step can include code blocks, formulas, or brief explanations.
- Connector styling (vertical line, arrows) between steps to show progression.
- Expected output shown after each step for immediate verification.

### Comparison Tables
- "X vs Y" for confusing concepts students often mix up.
- ✓/✗ symbols for feature comparisons.
- "Before → After" for transformations or process changes.

### Progress / Self-Assessment Checklists
- Checkbox-style lists (☐ / ☑) for students to mentally track mastery.
- Organized by topic area or difficulty level.

### Charts.css for Data-Based Exercises
- **Bar charts**: Within exercises ("Read this chart and answer...") or for showing frequency distributions.
- **Column charts**: For comparing quantities in exercises.
- Clean, labeled, with the data clearly readable — these charts are pedagogical tools.

### Mnemonic & Memory Aid Blocks
- Distinct styled containers for mnemonic devices.
- Large bold text for the acronym, expanded letters below.
- Visually distinct from other content — signals "this is a memory tool."

### Knowledge Map / Topic Overview
- A structured outline or tree showing what subtopics belong to what parent topic.
- Helps students see the big picture before diving into details.

### Code Blocks (for coding practice)
- Terminal-style dark blocks, monospace, language-indicated header.
- Paired with problem statement above and solution `<details>` below.

### Summary / Key Takeaway Boxes
- At the end of each major section, a compact box summarizing the 3-5 most important points.
- Distinct background, clear heading ("Section Summary").

## Citation Style — Learning Sources
- Use simple inline links: "Learn more: `<a href='URL'>Khan Academy</a>`" or "See: `<a href='URL'>source</a>`."
- For textbook references: Author, *Title*, Chapter/Section.
- For video resources: "[Video] Title, Platform, Duration."
- Citations in learning materials are navigational — they point the student to deeper resources, not academic authority.
- Group additional resources in a "Further Reading" or "Explore More" section at the end.

## Typography & Color — The Study Guide Palette

### Fonts
- **Body**: Clean sans-serif — Inter (first choice), Roboto, system-ui. Optimized for scanning.
- **Code/Formulas**: Monospace — Fira Code, Source Code Pro.
- **Headings**: Bold same sans-serif in blue (#2B6CB0).
- **Problem numbers**: Bold, slightly larger than body text.

### Color System — Clean, Functional, Engaging
- **Background**: Off-white (#FDFDFD) — clean and fresh.
- **Body text**: Dark gray (#2D3748) — highly readable.
- **Headings**: Blue (#2B6CB0) — active, educational energy.
- **Table headers**: Blue bg (#2B6CB0), white text — strong anchors.
- **Easy badge**: Green bg (#C6F6D5), dark green text (#22543D).
- **Medium badge**: Amber bg (#FEFCBF), dark amber text (#744210).
- **Hard badge**: Red bg (#FED7D7), dark red text (#822727).
- **Common Mistake box**: Orange border (#ED8936), cream bg (#FFFAF0).
- **Pro Tip box**: Blue border (#3182CE), pale blue bg (#EBF8FF).
- **Remember box**: Green border (#38A169), pale green bg (#F0FFF4).
- **Card borders**: Light gray (#E2E8F0).
- **Solution backgrounds**: Very light gray (#F7FAFC).
- **Boxed answers**: Blue border (#2B6CB0).
- **Line height**: 1.6 — compact, functional, scannable.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains 30 practice problems, include all 30 — organize them by difficulty tier. Don't truncate to fit a template.
- **Scale interactivity to content.** Simple memorization topics → heavy flashcard usage. Complex problem-solving → worked examples with `<details>` solutions. Procedural skills → step-by-step tutorials.
- **Adapt difficulty to audience.** If the planner suggests "beginner learner," use more analogies and simpler problems. For advanced prep (GRE, MCAT), use dense reference tables and hard problems.
- **Create new exercise types.** If the content demands "Match the term," "Fill in the blank," or "Complete the diagram," build those interactive patterns. The toolkit shows common patterns, not the only patterns.
- **Cheat sheets are never optional.** Every practice/learning report should have at least one dense reference table — this is the most reused element.
- **Never show solutions without hiding them first.** Active recall is the entire pedagogical purpose of this skill.

### What This Report NEVER Does
- Never hides the difficulty level — every problem is labeled
- Never shows solutions without hiding them behind click-to-reveal
- Never writes long paragraphs — concept explanations are SHORT
- Never uses decorative fonts — everything is functional
- Never presents a solution without step-by-step reasoning
- Never expects passive reading — every section encourages engagement
