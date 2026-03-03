# Academic Research Skill

## Identity & Scope
This skill governs research that demands scholarly rigor. It applies when the user's query touches education, science, theory, or any topic best addressed through university-level sources, peer-reviewed literature, and authoritative textbooks.

---

## Step 1 — Field Detection
Before generating a single query, determine:
1. **Which academic discipline** does this belong to? (e.g., Computer Science, Biology, Economics, Psychology, Linguistics, Engineering, Political Science)
2. **Which sub-field** within that discipline? (e.g., within CS → Machine Learning → Reinforcement Learning → Multi-Agent RL)
3. **What academic level** is implied? (introductory undergraduate → advanced undergraduate → graduate → research frontier)
4. **Is this theoretical or applied?** Pure theory demands different sources than applied/engineering work.

Use the user query and any clarification context to make these determinations. If ambiguous, default to a moderate (upper undergraduate) level with both theoretical and applied angles.

---

## Step 2 — Source Prioritization
Queries generated under this skill must be designed to surface:
- **Peer-reviewed journal papers** (IEEE, ACM, Nature, Science, Springer, Elsevier)
- **University course materials** and lecture notes from top institutions (MIT OCW, Stanford, Oxford)
- **Authoritative textbooks** and their authors (e.g., "Cormen et al." for algorithms, "Griffiths" for electrodynamics)
- **Survey papers and meta-analyses** that consolidate knowledge
- **Reputable preprint servers** when cutting-edge is needed (arXiv, SSRN, bioRxiv)
- **Conference proceedings** from top-tier venues (NeurIPS, ICML, CVPR, CHI, SIGMOD)

Avoid: blog posts (unless from verified academics), social media opinions, marketing material, non-peer-reviewed claims.

---

## Step 3 — Query Design Through Academic Lens
Each query should be structured to elicit scholarly-quality information:

### Foundation Layer (Queries 1–3)
- **Definitional precision**: Start with exact definitions, taxonomies, and classifications used in the field
- **Theoretical foundations**: What models, frameworks, or theories underpin this topic?
- **Historical evolution**: Who are the seminal authors? What are the landmark papers? How has the field's understanding evolved?

### Depth Layer (Queries 4–6)
- **Methodological detail**: What methodologies are standard in this area? What experimental designs, proof techniques, or analytical frameworks?
- **Current state of the art**: What do the most recent papers say? What are the open problems?
- **Comparative analysis**: How do competing theories/approaches compare? What does the evidence favor?

### Advanced Layer (Queries 7+)
- **Critical analysis**: What are the limitations, criticisms, and ongoing debates?
- **Interdisciplinary connections**: How does this area connect to adjacent fields?
- **Research gaps**: What remains unsolved? Where is active investigation happening?

---

## Step 4 — Data Representation
- Prefer structured taxonomies (categorized lists) over flat summaries
- Include author names, publication years, and institution affiliations when possible
- Use formal terminology native to the discipline
- Reference specific theorems, algorithms, models, or frameworks by their canonical names
- When citing competing viewpoints, attribute them to specific researchers or schools of thought

---

## Step 5 — Depth Calibration
| User Signal | Depth Response |
|-------------|---------------|
| "explain" / "what is" / "basics" | Undergraduate textbook level, definitions + worked examples |
| "how does" / "mechanism" / "deep dive" | Graduate level, full theoretical derivation + empirical evidence |
| "latest" / "state of the art" / "2025" | Research frontier, recent papers, open problems |
| "compare" / "vs" / "differences" | Systematic literature review style, tabulated comparisons |
| Specific author/paper mentioned | Research-level, citation network analysis |

---

## Anti-Patterns
- ✗ Do NOT generate vague queries like "research on topic X"
- ✗ Do NOT mix multiple unrelated sub-fields in a single query
- ✗ Do NOT prioritize recency over accuracy for established topics
- ✗ Do NOT ignore the hierarchical structure of academic knowledge (foundations before advanced)
- ✗ Do NOT generate queries that would primarily return commercial/marketing content
