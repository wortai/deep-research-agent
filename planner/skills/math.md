# Mathematics Research Skill

## Identity & Scope
This skill governs research in **mathematics** — the science of structure, pattern, quantity, and logical reasoning. It demands precise notation, rigorous definitions, step-by-step proofs, exact formulas, and deep understanding of which mathematical sub-field a problem belongs to. Activates for any math-related inquiry from basic arithmetic concepts to graduate-level abstract algebra.

---

## Step 1 — Mathematical Field Detection (CRITICAL)
Mathematics has many branches, and each has its own language, tools, and standards. **Before generating any query, identify exactly which field(s) the question belongs to**:

### Pure Mathematics
1. **Algebra** — Groups, rings, fields, vector spaces, modules, Galois theory, representation theory
2. **Analysis** — Real analysis (limits, continuity, integration), complex analysis, functional analysis, measure theory
3. **Topology** — Point-set topology, algebraic topology (homology, homotopy), differential topology, manifolds
4. **Number Theory** — Prime numbers, modular arithmetic, Diophantine equations, algebraic number theory, analytic number theory
5. **Geometry** — Euclidean, non-Euclidean, differential geometry, algebraic geometry, projective geometry
6. **Logic & Foundations** — Set theory, model theory, computability, proof theory, Gödel's theorems
7. **Combinatorics** — Counting, graph theory, extremal combinatorics, Ramsey theory, generating functions

### Applied Mathematics
8. **Linear Algebra** — Matrices, eigenvalues, SVD, least squares, inner product spaces
9. **Differential Equations** — ODE (ordinary), PDE (partial), separation of variables, Fourier methods, numerical methods
10. **Probability & Statistics** — Distributions, Bayes' theorem, hypothesis testing, regression, stochastic processes
11. **Numerical Analysis** — Approximation, interpolation, numerical integration, error analysis, stability
12. **Optimization** — Linear programming, convex optimization, calculus of variations, gradient methods
13. **Discrete Mathematics** — Boolean algebra, recursion, combinatorial optimization, coding theory

### Interdisciplinary
14. **Mathematical Physics** — Variational principles, symmetry groups, tensor analysis, differential forms
15. **Financial Mathematics** — Black-Scholes, stochastic calculus, portfolio theory, risk models
16. **Computational Mathematics** — Algorithm analysis, complexity theory, symbolic computation

**Also determine the sub-topic within the field**: e.g., within Linear Algebra → is this about eigendecomposition, or about solving systems, or about abstract vector spaces?

---

## Step 2 — Notation & Formalism Standards
Mathematics lives in its notation. Queries must account for:

- **Variables**: Use standard conventions (x, y, z for unknowns; a, b, c for constants; n, m, k for integers; f, g, h for functions; α, β, γ for parameters)
- **Set notation**: ℝ (reals), ℤ (integers), ℕ (naturals), ℂ (complex), ∈ (element of), ⊂ (subset)
- **Operators**: ∑ (sum), ∏ (product), ∫ (integral), ∂ (partial derivative), ∇ (gradient/nabla), lim (limit)
- **Logic symbols**: ∀ (for all), ∃ (there exists), ⟹ (implies), ⟺ (if and only if), ¬ (not)
- **Matrix notation**: Boldface or brackets, transpose (Aᵀ), inverse (A⁻¹), determinant (det A or |A|)
- **Theorem-proof structure**: Theorem statement → Proof → QED (or □)

---

## Step 3 — Query Design Through Mathematical Lens

### Foundation Layer
- **Precise definitions**: What are the exact definitions of every object involved? (e.g., "a group is a set G with a binary operation satisfying...")
- **Axiomatic basis**: What axioms/postulates underlie this area? Where does it start?
- **Fundamental theorems**: What are the cornerstone results? (Fundamental Theorem of Calculus, Chinese Remainder Theorem, Spectral Theorem, etc.)
- **Notation and conventions**: What notation does this field use? What are the standard symbols?

### Technique Layer
- **Methods and algorithms**: What are the standard techniques for solving problems in this area?
- **Formulas**: Complete formula statements with all variables defined and conditions specified
- **Worked examples**: Step-by-step solutions showing the method applied to concrete problems
- **Common patterns**: Problem types that appear repeatedly — what approach works for each?

### Depth Layer
- **Proof techniques**: The actual proofs of key theorems — by induction, contradiction, construction, diagram chasing
- **Connections between areas**: How does this connect to other branches? (e.g., algebra ↔ geometry via algebraic geometry)
- **Generalizations**: What happens when you relax assumptions? How does the theory extend?
- **Open problems**: What remains unsolved? (Millennium Prize problems, current research directions)
- **Computational aspects**: How are these concepts implemented in software? (MATLAB, Mathematica, Python/SciPy)

---

## Step 4 — Data Representation
- **Every formula must have all variables defined**: "Let f: ℝ → ℝ be continuous. Then ∫ₐᵇ f(x)dx = F(b) - F(a), where F is any antiderivative of f."
- **Conditions must be stated**: Don't say "the series converges" — say "the series converges for |x| < 1"
- **Step-by-step derivations**: Number each step, state the rule used (e.g., "by the chain rule", "by Cauchy-Schwarz inequality")
- **Equations on their own lines** when complex, with equation numbers for reference
- **Tables for classification**: e.g., types of differential equations, convergence tests, group properties
- **Examples before abstractions**: Show a concrete instance before stating the general theorem
- **Counter-examples**: When a theorem has conditions, show what fails when conditions are removed

---

## Step 5 — Depth Calibration
| User Signal | Response |
|-------------|----------|
| "solve" / "calculate" / "find" | Worked solution with every step shown and method explained |
| "prove" / "show that" / "demonstrate" | Rigorous proof with logical structure and justification at each step |
| "explain" / "what is" / "intuition" | Conceptual explanation with definitions, examples, and geometric/visual intuition |
| "formula" / "equation" | Complete formula with all variables defined, conditions, and domain of validity |
| "practice problems" | Graded problem set with solutions (merge with student_practice skill) |
| Specific theorem named | Full statement, proof, applications, and historical context |
| "difference between" / "compare" | Precise comparison with definitions, examples of each, and where they diverge |

---

## Anti-Patterns
- ✗ Do NOT present formulas without defining all variables and stating conditions
- ✗ Do NOT skip steps in derivations — every logical step must be justified
- ✗ Do NOT confuse definitions with theorems — a definition is chosen, a theorem is proved
- ✗ Do NOT present approximate reasoning where exact reasoning is possible
- ✗ Do NOT ignore edge cases (division by zero, boundary conditions, degenerate cases)
- ✗ Do NOT use informal language where precise mathematical language exists
- ✗ Do NOT conflate different mathematical objects (functions vs. relations, groups vs. rings, convergence types)
- ✗ Do NOT forget that math has many fields — always identify which field first before generating queries
