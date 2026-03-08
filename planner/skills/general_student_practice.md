# Student Practice & Cheat Sheet Skill

## Identity & Scope
This skill activates when the user wants material for **active practice**: cheat sheets, question banks, flashcard-style content, exam prep, interview prep, revision summaries, or structured problem sets. Applies to ANY field — math, coding, language learning, science, finance certifications, etc.

---

## Step 1 — Practice Format Detection
Before planning, determine the exact format the user needs:
1. **Cheat Sheet** — Condensed reference card (formulas, syntax, shortcuts, mnemonics). Optimized for quick lookup during work.
2. **Question Bank / Problem Set** — Progressive difficulty questions with answers. Structured by topic and difficulty tier.
3. **Exam Prep** — Simulates real exam conditions. Includes time estimates, mark weights, and mixed-topic coverage.
4. **Interview Prep** — Role-specific questions (behavioral, technical, case study). Focuses on what interviewers actually ask.
5. **Revision Sheet** — Concept summaries organized by topic with key takeaways, common mistakes, and memory aids.
6. **Flashcard Set** — Question/answer pairs optimized for spaced repetition.

If the format is unclear, infer from context: "cheat sheet" → format 1, "practice" → format 2, "prepare for exam" → format 3.

---

## Step 2 — Field & Level Calibration
Determine:
- **Which field** does this practice material belong to? (CS, Math, Science, Language, Business, Medicine, Law, etc.)
- **What level?** (beginner/introductory → intermediate → advanced/expert)
- **What scope?** (single topic like "SQL joins" vs. broad like "full SQL")
- **Any standard/syllabus?** (e.g., LeetCode patterns, AP Exam, GMAT, AWS Certification, university course)

---

## Step 3 — Query Design Through Practice Lens
Queries should target content that enables BUILDING practice material, not just learning:

### Foundation Layer
- **Topic inventory**: What are ALL the sub-topics that must be covered? Build a complete topic tree.
- **Difficulty progression**: What does easy, medium, hard look like in this specific domain?
- **Common patterns**: What question types appear most frequently? What patterns emerge?

### Content Layer
- **Core formulas/syntax/rules**: The exact reference material needed for a cheat sheet
- **Worked examples**: Step-by-step solutions that demonstrate the method
- **Edge cases and gotchas**: The tricky scenarios students commonly get wrong
- **Common mistakes**: Most frequent errors and how to avoid them

### Validation Layer
- **Real exam/interview questions**: What do actual assessments look like?
- **Answer explanations**: Not just correct answers, but WHY each answer is correct and why others are wrong
- **Time/difficulty benchmarks**: How long should each problem take? What's the expected difficulty curve?

---

## Step 4 — Data Representation
- **Structure by topic, then by difficulty** — never dump random questions
- Use clear numbering: Topic → Sub-topic → Question number
- For cheat sheets: use table format (Command | Syntax | Example | Notes)
- For question banks: include difficulty tag (Easy/Medium/Hard), expected time, and topic tag
- Include both the question AND a detailed solution/explanation
- Use visual separators between topics for scannability

---

## Step 5 — Depth Calibration
| User Signal | Response |
|-------------|----------|
| "cheat sheet" / "quick reference" | Densely packed reference card, minimal explanation, maximum coverage |
| "practice questions" / "problems" | 15-30 questions with full solutions, graded difficulty |
| "exam prep" / "test" | Simulated test with timing, scoring, and answer key |
| "interview prep" | Top 20-30 actual interview questions with STAR/framework answers |
| "revision" / "summary" | Topical breakdown with key points, formulas, and memory aids |

---

## Anti-Patterns
- ✗ Do NOT generate generic "learn about X" queries — focus on actionable practice content
- ✗ Do NOT forget answer keys / solutions — practice without answers is useless
- ✗ Do NOT skip difficulty ordering — always progress easy → hard
- ✗ Do NOT mix unrelated topics in a single practice block
- ✗ Do NOT assume one format — detect what the user actually needs
- ✗ Do NOT ignore the field-specific conventions (e.g., coding needs code blocks, math needs formulas)
