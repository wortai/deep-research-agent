# Coding & Technology Skill

## Identity & Scope
This skill governs research involving **programming, software engineering, frameworks, tools, system design, and technology documentation**. It activates when the user wants to understand code, learn a language/framework, debug a problem, design a system, or explore technical architecture. This skill understands that every coding query lives within a specific ecosystem and the research must be tailored accordingly.

---

## Step 1 — Technology Stack Detection
Before planning, identify the exact technical coordinates:

### Language / Runtime
- **Web Frontend**: JavaScript, TypeScript, HTML/CSS, WebAssembly
- **Web Backend**: Python, Node.js, Go, Rust, Java, C#, Ruby, PHP
- **Mobile**: Swift (iOS), Kotlin (Android), Dart (Flutter), React Native
- **Systems**: C, C++, Rust, Go
- **Data / ML**: Python (NumPy, Pandas, PyTorch, TensorFlow), R, Julia
- **Scripting**: Bash, PowerShell, Python, Perl
- **Database**: SQL (PostgreSQL, MySQL), NoSQL (MongoDB, Redis, DynamoDB), GraphQL

### Framework / Library
Detect the specific framework: React, Next.js, Vue, Angular, Django, FastAPI, Flask, Spring Boot, Express, LangChain, LangGraph, etc.

### Problem Type
1. **Learning** — "How does X work?" / "Teach me Y" / "What is Z?"
2. **Implementation** — "How to build X" / "Code for Y"
3. **Debugging** — "Error when X" / "Why does Y fail?"
4. **Architecture** — "How to design X" / "Best practices for Y"
5. **Comparison** — "X vs Y" / "Which framework for Z?"
6. **Documentation** — "API reference for X" / "Configuration options"

---

## Step 2 — Source Prioritization
Code research demands authoritative, version-specific sources:
- **Official documentation** (docs.python.org, react.dev, developer.mozilla.org) — ALWAYS prioritize
- **GitHub repositories** — Source code, issues, discussions, release notes
- **Language specifications** — ECMAScript spec, Python PEP documents, Rust RFC
- **Stack Overflow** — Verified answers with high vote counts (check recency)
- **Technical blogs from core teams** — Official engineering blogs (React Blog, Rust Blog, Go Blog)
- **Conference talks** — PyCon, JSConf, GopherCon, RustConf presentations
- **Technical books** — O'Reilly, Manning, Pragmatic Programmers

**Version matters**: Always target the specific version the user is working with. A React 18 answer is wrong for React 19.

---

## Step 3 — Query Design Through Coding Lens

### Foundation Layer
- **Concept understanding**: What is this technology? What problem does it solve? How does it work internally?
- **Setup and configuration**: How to install, configure, and get a running development environment?
- **Core API**: What are the fundamental functions/classes/methods? What are the signatures and return types?

### Implementation Layer
- **Working code examples**: Complete, runnable code snippets (not fragments)
- **Common patterns**: Design patterns, idiomatic usage, community conventions
- **Edge cases**: Error handling, boundary conditions, performance implications

### Advanced Layer
- **Architecture decisions**: When to use this vs. alternatives? Trade-offs and limitations
- **Performance optimization**: Profiling techniques, bottleneck identification, optimization strategies
- **Production considerations**: Deployment, monitoring, scaling, security best practices

---

## Step 4 — Data Representation
- **ALWAYS include code blocks** with proper language tags (```python, ```typescript, etc.)
- **Show complete, runnable examples** — not isolated snippets missing imports or context
- **Include input/output examples** for functions and APIs
- **Use tables for comparisons** (feature matrix, performance benchmarks)
- **Terminal commands must include the shell** (bash, zsh, cmd)
- **Version numbers must be explicit** — "Python 3.12", "React 19.1", "PostgreSQL 16"
- **Error messages should be shown verbatim** when discussing debugging

---

## Step 5 — Depth Calibration
| User Signal | Response |
|-------------|----------|
| "how to" / "tutorial" | Step-by-step guide with complete code examples |
| "explain" / "how does this work" | Conceptual deep-dive with internal architecture |
| "best practice" / "production" | Architecture-level guidance with trade-off analysis |
| "error" / "bug" / "doesn't work" | Debugging-focused with common causes and solutions |
| "vs" / "compare" / "which" | Side-by-side comparison with decision framework |
| Specific library/API named | Documentation-quality API reference with usage examples |
| "cheat sheet" / "reference" | Dense code reference card (merge with student_practice skill) |

---

## Anti-Patterns
- ✗ Do NOT provide code without specifying the language and version
- ✗ Do NOT show incomplete snippets — always include imports, setup, and context
- ✗ Do NOT recommend deprecated APIs or outdated practices
- ✗ Do NOT ignore error handling in examples — real code needs error management
- ✗ Do NOT mix framework-specific code with vanilla code without labeling
- ✗ Do NOT assume the user's operating system — be explicit (macOS, Linux, Windows)
- ✗ Do NOT present untested code patterns as "best practices"
