"""
Planner Prompt Quality Test Suite

Runs the planner against 12+ diverse test queries to evaluate the
rewritten prompt's ability to generate appropriate query counts
and well-structured research plans.

Outputs:
  - planner/prompt_test_results.json   (raw results)
  - writer/planner_prompt_test_results.md  (formatted report)
"""

import sys
import os
import json
import time
import logging
from datetime import datetime

# ── Path Setup ──
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

from planner.plan import Planner
from graphs.states.subgraph_state import AgentGraphState

# ── Test Queries ──
TEST_QUERIES = [
    {
        "id": 1,
        "domain": "Finance / Factual",
        "complexity": "Simple",
        "expected_range": "1",
        "query": "What is the current price of Bitcoin?",
    },
    {
        "id": 2,
        "domain": "Finance / Two-dimensional",
        "complexity": "Simple",
        "expected_range": "2",
        "query": "What is the price of Bitcoin and what factors are driving it right now?",
    },
    {
        "id": 3,
        "domain": "Coding / Comparison",
        "complexity": "Moderate",
        "expected_range": "3",
        "query": "Compare React and Vue for building interactive dashboards",
    },
    {
        "id": 4,
        "domain": "General / Multi-perspective",
        "complexity": "Moderate",
        "expected_range": "4",
        "query": "Benefits and drawbacks of remote work for employees and companies",
    },
    {
        "id": 5,
        "domain": "Finance / Strategy",
        "complexity": "Moderate-Broad",
        "expected_range": "4-5",
        "query": "What are the best investment strategies for beginners in 2025?",
    },
    {
        "id": 6,
        "domain": "Biology / Technical",
        "complexity": "Broad",
        "expected_range": "4-5",
        "query": "Explain how CRISPR gene editing works and its ethical implications",
    },
    {
        "id": 7,
        "domain": "History",
        "complexity": "Broad",
        "expected_range": "5-6",
        "query": "Tell me about the rise and fall of the Roman Empire",
    },
    {
        "id": 8,
        "domain": "AI / Technical",
        "complexity": "Broad",
        "expected_range": "4-5",
        "query": "How do large language models work and what are their limitations?",
    },
    {
        "id": 9,
        "domain": "News / Current Events",
        "complexity": "Broad",
        "expected_range": "5-7",
        "query": "What are the major developments in the Ukraine-Russia conflict this year?",
    },
    {
        "id": 10,
        "domain": "Science / Comprehensive",
        "complexity": "Very Broad (explicit 'everything')",
        "expected_range": "8-10",
        "query": "Explain everything about quantum computing from basics to current state to future applications",
    },
    {
        "id": 11,
        "domain": "Writing / How-to",
        "complexity": "Moderate",
        "expected_range": "3-5",
        "query": "How do I write a compelling novel? Cover structure, character development, and publishing",
    },
    {
        "id": 12,
        "domain": "General / Definition",
        "complexity": "Simple",
        "expected_range": "1",
        "query": "What is photosynthesis?",
    },
]

# ── Helpers ──


def parse_expected_range(range_str: str) -> tuple[int, int]:
    """Parse '4-5' or '1' into (min, max) tuple."""
    if "-" in range_str:
        parts = range_str.split("-")
        return int(parts[0]), int(parts[1])
    val = int(range_str)
    return val, val


def classify_result(actual: int, expected_min: int, expected_max: int) -> str:
    """Classify actual count vs expected range."""
    if expected_min <= actual <= expected_max:
        return "PASS"
    # Allow ±1 as BORDERLINE
    if (actual == expected_min - 1) or (actual == expected_max + 1):
        return "BORDERLINE"
    return "FAIL"


def run_tests() -> list[dict]:
    """Run all test queries through the planner and collect results."""
    planner = Planner()
    results = []

    total = len(TEST_QUERIES)
    for i, tq in enumerate(TEST_QUERIES, 1):
        qid = tq["id"]
        query = tq["query"]
        domain = tq["domain"]
        complexity = tq["complexity"]
        expected_range = tq["expected_range"]

        print(f"\n{'='*70}")
        print(f"[{i}/{total}] Query #{qid}: {domain}")
        print(f"  User query: {query}")
        print(f"  Expected: {expected_range} queries")
        print(f"{'='*70}")

        state: AgentGraphState = {
            "user_query": query,
            "planner_query": [],
        }

        start_time = time.time()
        try:
            raw_result = planner._generate_plan(state)
            elapsed = time.time() - start_time

            plan_queries = raw_result.get("planner_query", [])
            num_queries = len(plan_queries)

            queries_data = []
            for pq in plan_queries:
                text = pq.get("query", "")
                queries_data.append(
                    {
                        "num": pq.get("query_num", 0),
                        "text": text,
                        "word_count": len(text.split()),
                    }
                )

            exp_min, exp_max = parse_expected_range(expected_range)
            verdict = classify_result(num_queries, exp_min, exp_max)

            result = {
                "query_id": qid,
                "domain": domain,
                "complexity": complexity,
                "expected_range": expected_range,
                "user_query": query,
                "num_queries": num_queries,
                "elapsed_seconds": round(elapsed, 1),
                "verdict": verdict,
                "queries": queries_data,
                "error": None,
            }

            print(f"  ✅ Generated {num_queries} queries in {elapsed:.1f}s — Verdict: {verdict}")
            for qd in queries_data:
                print(f"     Q{qd['num']}: ({qd['word_count']}w) {qd['text'][:100]}...")

        except Exception as e:
            elapsed = time.time() - start_time
            result = {
                "query_id": qid,
                "domain": domain,
                "complexity": complexity,
                "expected_range": expected_range,
                "user_query": query,
                "num_queries": 0,
                "elapsed_seconds": round(elapsed, 1),
                "verdict": "ERROR",
                "queries": [],
                "error": str(e),
            }
            print(f"  ❌ ERROR: {e}")

        results.append(result)

        # Small delay to avoid rate limits
        if i < total:
            time.sleep(2)

    return results


def save_json(results: list[dict], path: str):
    """Save raw results to JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n📄 JSON results saved to: {path}")


def generate_markdown_report(results: list[dict], path: str):
    """Generate a detailed Markdown report."""
    lines: list[str] = []

    lines.append("# Planner Prompt Quality Test Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Model:** grok-4-1-fast-reasoning (via Planner class)")
    lines.append(f"**Total test queries:** {len(results)}")
    lines.append("")

    # ── Summary ──
    verdicts = {"PASS": 0, "FAIL": 0, "BORDERLINE": 0, "ERROR": 0}
    for r in results:
        verdicts[r["verdict"]] += 1

    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Verdict | Count |")
    lines.append("|---------|-------|")
    for v in ["PASS", "BORDERLINE", "FAIL", "ERROR"]:
        lines.append(f"| {v} | {verdicts[v]} |")
    lines.append("")

    total_queries_generated = sum(r["num_queries"] for r in results)
    avg_queries = total_queries_generated / len(results) if results else 0
    lines.append(f"- **Total queries generated across all tests:** {total_queries_generated}")
    lines.append(f"- **Average queries per test:** {avg_queries:.1f}")
    lines.append("")

    # ── Detailed Results Per Query ──
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Results")
    lines.append("")

    for r in results:
        qid = r["query_id"]
        lines.append(f"### Query #{qid}: {r['domain']}")
        lines.append("")
        lines.append(f"**Complexity:** {r['complexity']}  ")
        lines.append(f"**User Query:** _{r['user_query']}_  ")
        lines.append(f"**Expected Range:** {r['expected_range']}  ")
        lines.append(f"**Actual Count:** {r['num_queries']}  ")
        lines.append(f"**Verdict:** **{r['verdict']}**  ")
        lines.append(f"**Elapsed:** {r['elapsed_seconds']}s  ")

        if r["error"]:
            lines.append(f"**Error:** {r['error']}  ")
            lines.append("")
            continue

        lines.append("")
        lines.append("| # | Query | Words |")
        lines.append("|---|-------|-------|")
        for q in r["queries"]:
            # Escape pipe characters in query text for markdown table
            escaped_text = q["text"].replace("|", "\\|")
            lines.append(f"| {q['num']} | {escaped_text} | {q['word_count']} |")
        lines.append("")

        # ── Analysis notes ──
        exp_min, exp_max = parse_expected_range(r["expected_range"])
        actual = r["num_queries"]
        notes = []

        if r["verdict"] == "PASS":
            notes.append("Query count within expected range.")
        elif r["verdict"] == "BORDERLINE":
            if actual < exp_min:
                notes.append(
                    f"Under-generating by 1: got {actual}, expected {exp_min}-{exp_max}."
                )
            else:
                notes.append(
                    f"Over-generating by 1: got {actual}, expected {exp_min}-{exp_max}."
                )
        elif r["verdict"] == "FAIL":
            if actual < exp_min:
                notes.append(
                    f"Significant under-generation: got {actual}, expected {exp_min}-{exp_max}."
                )
            else:
                notes.append(
                    f"Significant over-generation: got {actual}, expected {exp_min}-{exp_max}."
                )

        # Check query word counts
        short_queries = [q for q in r["queries"] if q["word_count"] < 20]
        long_queries = [q for q in r["queries"] if q["word_count"] > 100]
        if short_queries:
            notes.append(
                f"{len(short_queries)} query/queries below 20-word minimum."
            )
        if long_queries:
            notes.append(
                f"{len(long_queries)} query/queries above 100-word maximum."
            )

        # Check independence
        if actual > 1:
            query_texts = [q["text"].lower() for q in r["queries"]]
            overlap_found = False
            for idx_a in range(len(query_texts)):
                for idx_b in range(idx_a + 1, len(query_texts)):
                    # Simple overlap check: do they share >50% of meaningful words?
                    words_a = set(query_texts[idx_a].split()) - {
                        "the", "a", "an", "and", "or", "of", "in", "to", "for",
                        "is", "are", "what", "how", "with", "that", "this",
                    }
                    words_b = set(query_texts[idx_b].split()) - {
                        "the", "a", "an", "and", "or", "of", "in", "to", "for",
                        "is", "are", "what", "how", "with", "that", "this",
                    }
                    if words_a and words_b:
                        overlap = len(words_a & words_b) / min(len(words_a), len(words_b))
                        if overlap > 0.6:
                            overlap_found = True
                            break
                if overlap_found:
                    break
            if overlap_found:
                notes.append("Potential overlap detected between queries.")
            else:
                notes.append("Queries appear independent (low keyword overlap).")

        # Check progression
        if actual >= 3:
            notes.append(
                "Progressive ordering should go: foundation → mechanism → application → analysis → future."
            )

        if notes:
            lines.append("**Analysis Notes:**")
            for note in notes:
                lines.append(f"- {note}")
            lines.append("")

    # ── Comparison with Baseline ──
    lines.append("---")
    lines.append("")
    lines.append("## Comparison with Baseline (Old Prompt)")
    lines.append("")

    baseline_path = os.path.join(
        os.path.dirname(__file__), "..", "planner_test_results.json"
    )
    baseline_path = os.path.abspath(baseline_path)

    if os.path.exists(baseline_path):
        with open(baseline_path, "r") as f:
            baseline = json.load(f)

        lines.append(
            "| Query | Domain | Baseline | New Prompt | Expected | Δ | Improvement? |"
        )
        lines.append(
            "|-------|--------|----------|------------|----------|---|-------------|"
        )

        # Map baseline by domain (approximate match)
        baseline_by_domain = {}
        for b in baseline:
            baseline_by_domain[b.get("domain", "")] = b

        for r in results:
            # Try to find matching baseline
            domain_key = r["domain"]
            baseline_match = baseline_by_domain.get(domain_key)

            if baseline_match:
                b_count = baseline_match["num_queries"]
                n_count = r["num_queries"]
                delta = n_count - b_count
                exp_min, exp_max = parse_expected_range(r["expected_range"])
                improved = ""
                # Check if closer to expected range
                if r["verdict"] == "PASS":
                    improved = "✅ YES"
                elif abs(delta) > 0:
                    if b_count > exp_max and n_count <= exp_max:
                        improved = "✅ YES (less over-gen)"
                    elif b_count < exp_min and n_count >= exp_min:
                        improved = "✅ YES (less under-gen)"
                    elif n_count > b_count and b_count < exp_min:
                        improved = "⚠️ PARTIAL"
                    elif n_count < b_count and b_count > exp_max:
                        improved = "⚠️ PARTIAL"
                    else:
                        improved = "❌ NO"
                else:
                    improved = "➖ SAME"

                lines.append(
                    f"| #{r['query_id']} | {r['domain']} | {b_count} | {n_count} | {r['expected_range']} | {delta:+d} | {improved} |"
                )
            else:
                lines.append(
                    f"| #{r['query_id']} | {r['domain']} | N/A | {r['num_queries']} | {r['expected_range']} | — | — |"
                )
        lines.append("")
    else:
        lines.append("_Baseline file `planner_test_results.json` not found. Skipping comparison._")
        lines.append("")

    # ── Overall Assessment ──
    lines.append("---")
    lines.append("")
    lines.append("## Overall Assessment")
    lines.append("")

    pass_rate = verdicts["PASS"] / len(results) * 100 if results else 0
    acceptable_rate = (verdicts["PASS"] + verdicts["BORDERLINE"]) / len(results) * 100 if results else 0

    lines.append(f"- **Pass rate:** {pass_rate:.0f}% ({verdicts['PASS']}/{len(results)})")
    lines.append(
        f"- **Acceptable rate (PASS + BORDERLINE):** {acceptable_rate:.0f}% "
        f"({verdicts['PASS'] + verdicts['BORDERLINE']}/{len(results)})"
    )
    lines.append("")

    # Identify over-generation patterns
    over_gen = [
        r for r in results
        if r["verdict"] in ("FAIL", "BORDERLINE")
        and r["num_queries"] > parse_expected_range(r["expected_range"])[1]
    ]
    under_gen = [
        r for r in results
        if r["verdict"] in ("FAIL", "BORDERLINE")
        and r["num_queries"] < parse_expected_range(r["expected_range"])[0]
    ]

    if over_gen:
        lines.append("### Over-Generation Issues")
        lines.append("")
        for r in over_gen:
            exp_min, exp_max = parse_expected_range(r["expected_range"])
            lines.append(
                f"- **#{r['query_id']}** ({r['domain']}): "
                f"Got {r['num_queries']}, expected {exp_min}-{exp_max} — "
                f"_{r['user_query'][:80]}_"
            )
        lines.append("")

    if under_gen:
        lines.append("### Under-Generation Issues")
        lines.append("")
        for r in under_gen:
            exp_min, exp_max = parse_expected_range(r["expected_range"])
            lines.append(
                f"- **#{r['query_id']}** ({r['domain']}): "
                f"Got {r['num_queries']}, expected {exp_min}-{exp_max} — "
                f"_{r['user_query'][:80]}_"
            )
        lines.append("")

    # Recommendations
    lines.append("### Recommendations")
    lines.append("")

    if pass_rate >= 80:
        lines.append("✅ **The prompt is performing well overall.** Minor adjustments may help edge cases.")
    elif pass_rate >= 50:
        lines.append("⚠️ **The prompt has moderate issues.** Targeted fixes needed for specific query types.")
    else:
        lines.append("❌ **The prompt has significant issues.** Major revisions may be required.")

    lines.append("")

    if over_gen:
        lines.append(
            "1. **For over-generation:** The prompt's anti-pattern section may need stronger language "
            "or additional examples for the specific domains that are over-generating. "
            "Consider adding domain-specific examples in the count decision framework."
        )
    if under_gen:
        lines.append(
            "2. **For under-generation:** Ensure the prompt's framework clearly distinguishes "
            "between simple factual lookups and multi-dimensional queries. "
            "Some queries may need the prompt to recognize implicit dimensions."
        )
    lines.append(
        "3. **Query quality:** Check that generated queries meet the 20-100 word requirement "
        "and maintain independence between queries."
    )
    lines.append(
        "4. **Progressive ordering:** Verify that queries follow the foundation → mechanism → "
        "application → analysis → future progression pattern."
    )
    lines.append("")

    # Write file
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"📝 Markdown report saved to: {path}")


# ── Main ──
if __name__ == "__main__":
    print("=" * 70)
    print("  PLANNER PROMPT QUALITY TEST SUITE")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = run_tests()

    # Save JSON
    json_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "prompt_test_results.json",
    )
    save_json(results, json_path)

    # Generate Markdown report
    md_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "writer",
        "planner_prompt_test_results.md",
    )
    md_path = os.path.abspath(md_path)
    generate_markdown_report(results, md_path)

    # Print final summary
    verdicts = {"PASS": 0, "FAIL": 0, "BORDERLINE": 0, "ERROR": 0}
    for r in results:
        verdicts[r["verdict"]] += 1

    print("\n" + "=" * 70)
    print("  FINAL SUMMARY")
    print("=" * 70)
    for v in ["PASS", "BORDERLINE", "FAIL", "ERROR"]:
        if verdicts[v] > 0:
            print(f"  {v}: {verdicts[v]}")
    print(f"  Total: {len(results)}")
    print("=" * 70)
