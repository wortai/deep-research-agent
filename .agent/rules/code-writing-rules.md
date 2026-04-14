---
trigger: always_on
---

WORT Engine — Project Rules
v2 · Naming · Structure · Comments · Clean Code

1 · Naming
Casing conventions
mandatory
PascalCase → classes  |  snake_case → files, folders, methods, variables  |  UPPER_CASE → constants
✓  ResearchAgent  ·  research_agent.py  ·  MAX_RETRIES
Intent-driven names
mandatory
Names must describe what something does, not its role in a pattern. Banned suffixes unless no better word exists: Manager, Processor, Handler, Worker.
✗  ResearchManager  ·  DataProcessor
✓  PaperSummarizer  ·  CitationExtractor
2 · Code Structure
One class per file
Each file has exactly one main class. Small private helpers that support only that class may live alongside it, but nothing more.
Encapsulation first
Logic belongs inside classes. Top-level functions only for stateless, reusable utilities that don't belong to any single class.
Vertical breathing room
enforced
Two blank lines between every method. One blank line to separate logically distinct blocks inside a method — treat it like a paragraph break. Don't stack unrelated logic without whitespace.
✓  group → validate → transform → return, each separated by one blank line
✗  40 continuous lines of mixed logic with no breathing room
3 · Folder Structure
If a task spans more than one file, it gets its own folder. Related modules live together — keep the root clean. Folder names follow snake_case and describe the domain, not the pattern (e.g., retrieval/ not utils/).
4 · Documentation
Docstrings — class level
mandatory
Every class gets a docstring. Cover: what it does, what it depends on, and how other classes use it. Be specific about the data flow.
✗  """Handles research."""
✓  """Queries the Semantic Scholar API with a cleaned query string,
    returns a list of Paper objects consumed by CitationRanker."""
Docstrings — method level
Required on any non-trivial method. State inputs (name + type), output (type + meaning), and one line on what it does — not how. Skip docstrings on simple getters, setters, and <10-line obvious methods.
Dependency chain comments
critical
When a class or method hands data to — or relies on — another class, say so explicitly in the docstring. Name the class, name the fields, name the output. Future readers shouldn't have to trace imports to understand the flow.
✓ """Receives a List[Paper] from PaperFetcher, scores each by
   citation_count + recency_weight, returns top-k as RankedResult."""
5 · Inline Comments
Use sparingly — earn every line
enforced
Inline # comments are for logic that looks wrong but is intentional, or where the "why" isn't obvious from the code. Never explain what the code does — only why it does it that way. One line max. No prose.
✗  # loop through papers
✗  # increment counter by 1
✓  # offset by 1 — API pagination is 1-indexed
✓  # intentional: skip abstracts shorter than 50 chars, they're usually metadata
Human tone — not compiler speak
Write comments like a senior dev leaving a note for the next person. Explain the decision, the edge case, the gotcha — not the obvious.
✗  # retry logic
✓  # rate limit hits ~1 in 20 calls at peak — retry up to 3x with backoff
6 · Clean Code
No dead code
Only commit methods you use now or will use in the immediate next task. Speculative code is noise. Delete it — version control remembers.
No stray print statements
Use a logger. A bare print() in committed code is a bug waiting to leak to stdout in production.
Class shape consistency
Within a class, follow this order: __init__ → public methods → private helpers (_name). Public interface at the top — readers shouldn't scroll to find what the class exposes.