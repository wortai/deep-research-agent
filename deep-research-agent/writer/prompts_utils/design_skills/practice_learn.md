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

### SVG Construction Standards
- **viewBox**: `viewBox="0 0 800 400"` for wide diagrams (process flows, comparison charts); `viewBox="0 0 400 400"` for square diagrams (concept maps, knowledge trees).
- **Font sizing**: `font-family` must match body font (Inter). Labels 12px, diagram titles 14px, data labels 11px.
- **Stroke widths**: 1.5px for grid lines, 2px for connection arrows, 2.5px for borders, 1px for decorative elements.
- **Color application**: Use the exact study guide palette — Blue (#2B6CB0), Green (#38A169), Amber (#ED8936), Red (#E53E3E). No arbitrary colors.
- **Accessibility**: Every SVG must have `<title>` (e.g., "Knowledge map: Algebra fundamentals") and `<desc>` (describe all concepts and their relationships).
- **Background**: Transparent — diagrams overlay on off-white pages.
- **Text elements**: Use `<text>` with `text-anchor="start|middle|end"` — never `<foreignObject>`. Formulas use `<tspan font-family="monospace">`.
- **Domain-specific SVG patterns**:
  - *Knowledge map/tree*: Root `<rect>` for main topic, branching `<path>` lines to subtopics, `<text>` labels. Color-coded by difficulty level.
  - *Process flow*: Sequential `<rect>` nodes with `<path>` arrows, numbered steps, color-coded by stage.
  - *Concept comparison*: Side-by-side `<rect>` panels with `<text>` labels, connecting `<path>` for similarities/differences.
  - *Progress tracker*: Horizontal `<rect>` segments showing completion, `<text>` milestone labels, checkmark symbols for achieved.

### Charts.css Decision Guide
- IF comparing categories (concepts, topics, skill areas) → horizontal bar chart
- IF comparing time periods (study progress over weeks, score improvement) → column chart
- IF showing trend over continuous time (learning curve, practice scores) → line chart
- IF showing composition (time spent by topic, skill breakdown) → stacked bar chart
- IF showing part-to-whole (mastery percentage, completion rate) → percentage bar
- IF comparing multiple series (student A vs. student B, pre-test vs. post-test) → grouped bar chart
- Always include: `class="charts-css [type]" show-labels show-data show-headings`
- Caption placement: `<caption>` below chart with brief description
- Do NOT use Charts.css when: fewer than 3 data points (use a table or flashcard), purely conceptual content (use knowledge maps), or data is better shown as a progress tracker

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

### Edge Cases & Adaptations
- **No quantitative data**: For purely conceptual topics (e.g., "Introduction to Philosophy"), use knowledge maps, flashcard Q&A blocks, and comparison tables. Skip Charts.css entirely.
- **Too much data**: For subjects with hundreds of practice problems, organize by topic and difficulty tier. Show representative problems for each tier. Use `<details>` for full problem sets.
- **Mixed content**: When theory dominates with occasional practice, embed key concepts as cheat sheet tables and use practice problems only for sections with clear exercise potential.
- **Contradictory sources**: When textbooks disagree (e.g., different notation conventions), present both with clear labels: "Convention A (most common)" vs. "Convention B (alternative)." Note which is used in standard exams.
- **Variable chapter length**: Short topics (single concept) get overview + cheat sheet + 3-5 problems. Long topics (full subject) use the complete toolkit with knowledge maps and progress trackers.
- **Default format mismatch**: If the learning topic is code-heavy (e.g., "Learn Python"), borrow code block patterns from the coding skill. If it's math-heavy (e.g., "Calculus Practice"), borrow theorem/proof patterns from the math skill.

## Citation Style — Learning Sources
- Use simple inline links: "Learn more: `<a href='URL'>Khan Academy</a>`" or "See: `<a href='URL'>source</a>`."
- For textbook references: Author, *Title*, Chapter/Section.
- For video resources: "[Video] Title, Platform, Duration."
- Citations in learning materials are navigational — they point the student to deeper resources, not academic authority.
- Group additional resources in a "Further Reading" or "Explore More" section at the end.
- **Multiple formats**: Use inline links for resources, textbook references for formal content, and source blocks for datasets.
- **No URL available**: Cite as "Author, *Title*, Publisher, Edition, Chapter/Section" — standard textbook reference.
- **Multiple sources for same claim**: Link the most student-friendly source first (Khan Academy, textbook) then supplementary sources.
- **Beautiful citations**: Style the "Further Reading" section as a clean list with resource type badges (📖 book, 🎥 video, 🌐 website, 📝 practice).
- **Source credibility hierarchy**: Standard textbook > official curriculum > established educational platform (Khan Academy, Coursera) > expert blog > general website. Always prefer standard textbooks and official curricula.

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
- **Extended chart palette** (7+ colors): Blue (#2B6CB0), Green (#38A169), Amber (#ED8936), Red (#E53E3E), Purple (#805AD5), Teal (#319795), Steel (#4A5568). All WCAG AA compliant on off-white.
- **Semantic color rules**: Blue = default/primary data series. Green = easy/positive/correct answers. Amber = medium/warning/caution. Red = hard/incorrect/danger. Purple = advanced/bonus content. Teal = secondary data series. Steel = reference/baseline values.
- **Hover/interaction**: On hover, chart elements show exact values. Click-to-reveal elements show subtle background change. Use CSS `:hover` transitions.
- **Print-friendly**: All colors maintain ≥ 3:1 contrast in grayscale. Badge colors supplemented by text labels (Easy/Medium/Hard) for print legibility.
- **WCAG AA compliance**: All text ≥ 4.5:1 contrast ratio. Chart colors ≥ 3:1 against off-white (#FDFDFD). Badge text colors are specifically chosen for readability on their backgrounds.

## Adaptive Instructions — How the LLM Should Use This Skill
- **Never sacrifice content for layout.** If the research contains 30 practice problems, include all 30 — organize them by difficulty tier. Don't truncate to fit a template.
- **Scale interactivity to content.** Simple memorization topics → heavy flashcard usage. Complex problem-solving → worked examples with `<details>` solutions. Procedural skills → step-by-step tutorials.
- **Adapt difficulty to audience.** If the planner suggests "beginner learner," use more analogies and simpler problems. For advanced prep (GRE, MCAT), use dense reference tables and hard problems.
- **Create new exercise types.** If the content demands "Match the term," "Fill in the blank," or "Complete the diagram," build those interactive patterns. The toolkit shows common patterns, not the only patterns.
- **Cheat sheets are never optional.** Every practice/learning report should have at least one dense reference table — this is the most reused element.
- **Never show solutions without hiding them first.** Active recall is the entire pedagogical purpose of this skill.
- Never presents a learning topic without a structural visual. If the research contains steps, processes, or concept hierarchies, you MUST create at least one SVG diagram (flowchart, hierarchy tree, or concept map).
- **Visual diversity is mandatory.** Every chapter MUST include at least 3 different visual types from the toolkit (e.g., reference table + collapsible solution + tip callout, or concept diagram + practice problem + common mistakes box). A chapter with only tables and prose is insufficient — it fails to leverage the full visual toolkit and creates a monotonous reading experience. Spread visuals across pages — do not cluster all visuals on one page.

### What This Report NEVER Does
- Never hides the difficulty level — every problem is labeled
- Never shows solutions without hiding them behind click-to-reveal
- Never writes long paragraphs — concept explanations are SHORT
- Never uses decorative fonts — everything is functional
- Never presents a solution without step-by-step reasoning
- Never expects passive reading — every section encourages engagement
- Never uses Charts.css for data that's better shown as a knowledge map
- Never presents a concept without at least one practice opportunity
- Never uses color as the sole difficulty indicator — always include text labels (Easy/Medium/Hard)
- Never skips SVG visualizations when the data supports them — at least one SVG diagram is mandatory per chapter. If the research contains steps, processes, or concept hierarchies, you MUST create at least one SVG diagram (flowchart, hierarchy tree, or concept map).
