"""
Planner Prompt Regression Test — Iteration 2

Focused re-test after targeted fix for definition queries.
Tests:
  - The previously-failing "What is photosynthesis?" (run twice for consistency)
  - Additional definition queries (gravity, machine learning, blockchain)
  - Regression spot-checks for queries that were passing in iteration 1

Total: 9 test runs
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

# ── Test Queries (9 runs total) ──
TEST_QUERIES = [
    # ── Definition queries (the fix target) ──
    {
        "id": "A1",
        "category": "Definition Fix",
        "label": "Photosynthesis (run 1)",
        "expected_range": "1",
        "query": "What is photosynthesis?",
    },
    {
        "id": "A2",
        "category": "Definition Fix",
        "label": "Photosynthesis (run 2)",
        "expected_range": "1",
        "query": "What is photosynthesis?",
    },
    {
        "id": "A3",
        "category": "Definition Fix",
        "label": "Gravity",
        "expected_range": "1",
        "query": "What is gravity?",
    },
    {
        "id": "A4",
        "category": "Definition Fix",
        "label": "Machine Learning",
        "expected_range": "1",
        "query": "What is machine learning?",
    },
    {
        "id": "A5",
        "category": "Definition Fix",
        "label": "Blockchain (imperative)",
        "expected_range": "1",
        "query": "Define blockchain",
    },
    # ── Regression spot-checks ──
    {
        "id": "R1",
        "category": "Regression",
        "label": "Bitcoin price",
        "expected_range": "1",
        "query": "What is the current price of Bitcoin?",
    },
    {
        "id": "R2",
        "category": "Regression",
        "label": "React vs Vue",
        "expected_range": "3",
        "query": "Compare React and Vue for building interactive dashboards",
    },
    {
        "id": "R3",
        "category": "Regression",
        "label": "CRISPR + ethics",
        "expected_range": "4-5",
        "query": "Explain how CRISPR gene editing works and its ethical implications",
    },
    {
        "id": "R4",
        "category": "Regression",
        "label": "Investment strategies",
        "expected_range": "4-5",
        "query": "What are the best investment strategies for beginners in 2025?",
    },
    {
        "id": "R5",
        "category": "Regression",
        "label": "Quantum computing (comprehensive)",
        "expected_range": "8-10",
        "query": "Explain everything about quantum computing from basics to current state to future applications",
    },
]

# ── Helpers ──


def parse_expected_range(range_str: str) -> tuple:
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
    if (actual == expected_min - 1) or (actual == expected_max + 1):
        return "BORDERLINE"
    return "FAIL"


def run_tests() -> list:
    """Run all test queries through the planner and collect results."""
    planner = Planner()
    results = []

    total = len(TEST_QUERIES)
    for i, tq in enumerate(TEST_QUERIES, 1):
        qid = tq["id"]
        query = tq["query"]
        category = tq["category"]
        label = tq["label"]
        expected_range = tq["expected_range"]

        print(f"\n{'='*70}")
        print(f"[{i}/{total}] {qid} ({category}): {label}")
        print(f"  User query: {query}")
        print(f"  Expected: {expected_range} queries")
        print(f"{'='*70}")

        state = {
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
                "category": category,
                "label": label,
                "expected_range": expected_range,
                "user_query": query,
                "num_queries": num_queries,
                "elapsed_seconds": round(elapsed, 1),
                "verdict": verdict,
                "queries": queries_data,
                "error": None,
            }

            status_icon = "✅" if verdict == "PASS" else ("⚠️" if verdict == "BORDERLINE" else "❌")
            print(f"  {status_icon} Generated {num_queries} queries in {elapsed:.1f}s — Verdict: {verdict}")
            for qd in queries_data:
                print(f"     Q{qd['num']}: ({qd['word_count']}w) {qd['text'][:120]}...")

        except Exception as e:
            elapsed = time.time() - start_time
            result = {
                "query_id": qid,
                "category": category,
                "label": label,
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


def generate_iteration2_appendix(results: list) -> str:
    """Generate the markdown appendix to append to the existing report."""
    lines = []

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Iteration 2: Post-Fix Regression Test")
    lines.append("")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("**Changes:** Added definition-query anti-patterns and pre-output self-test to planner prompt")
    lines.append("")
    lines.append("### Results Summary")
    lines.append("")
    lines.append("| # | Query | Expected | Actual | Verdict |")
    lines.append("|---|-------|----------|--------|---------|")

    for r in results:
        escaped_query = r["user_query"].replace("|", "\\|")
        if r["query_id"] == "A2":
            label = f"{escaped_query} (run 2)"
        else:
            label = escaped_query
        lines.append(
            f"| {r['query_id']} | {label} | {r['expected_range']} | {r['num_queries']} | {r['verdict']} |"
        )
    lines.append("")

    # ── Verdict counts ──
    verdicts = {"PASS": 0, "FAIL": 0, "BORDERLINE": 0, "ERROR": 0}
    for r in results:
        verdicts[r["verdict"]] += 1

    # ── Analysis ──
    lines.append("### Analysis")
    lines.append("")

    # Definition fix analysis
    definition_results = [r for r in results if r["category"] == "Definition Fix"]
    definition_passes = [r for r in definition_results if r["verdict"] == "PASS"]
    definition_failures = [r for r in definition_results if r["verdict"] != "PASS"]

    lines.append(f"**Definition query fix ({len(definition_results)} tests):**")
    if len(definition_passes) == len(definition_results):
        lines.append("- ✅ All definition queries now correctly generate exactly 1 query.")
    else:
        lines.append(f"- ❌ {len(definition_failures)}/{len(definition_results)} definition queries still fail:")
        for r in definition_failures:
            exp_min, exp_max = parse_expected_range(r["expected_range"])
            lines.append(
                f"  - **{r['label']}**: Got {r['num_queries']}, expected {exp_min}-{exp_max}"
            )
    lines.append("")

    # Regression analysis
    regression_results = [r for r in results if r["category"] == "Regression"]
    regression_passes = [r for r in regression_results if r["verdict"] == "PASS"]
    regression_failures = [r for r in regression_results if r["verdict"] != "PASS"]

    lines.append(f"**Regression check ({len(regression_results)} tests):**")
    if len(regression_passes) == len(regression_results):
        lines.append("- ✅ No regressions detected. All previously-passing queries still pass.")
    else:
        lines.append(f"- ❌ {len(regression_failures)} regression(s) detected:")
        for r in regression_failures:
            exp_min, exp_max = parse_expected_range(r["expected_range"])
            lines.append(
                f"  - **{r['label']}**: Got {r['num_queries']}, expected {exp_min}-{exp_max} — {r['verdict']}"
            )
    lines.append("")

    # Overall
    total_pass = verdicts["PASS"]
    total = len(results)
    pass_rate = total_pass / total * 100 if total else 0

    lines.append(f"**Overall pass rate:** {pass_rate:.0f}% ({total_pass}/{total})")
    lines.append("")

    # ── Detailed results per query ──
    lines.append("### Detailed Query Output")
    lines.append("")

    for r in results:
        lines.append(f"#### {r['query_id']}: {r['label']} ({r['category']})")
        lines.append("")
        lines.append(f"- **User Query:** _{r['user_query']}_")
        lines.append(f"- **Expected:** {r['expected_range']}")
        lines.append(f"- **Actual:** {r['num_queries']}")
        lines.append(f"- **Verdict:** **{r['verdict']}**")
        lines.append(f"- **Elapsed:** {r['elapsed_seconds']}s")

        if r["error"]:
            lines.append(f"- **Error:** {r['error']}")
        else:
            lines.append("")
            lines.append("| # | Query Text | Words |")
            lines.append("|---|-----------|-------|")
            for q in r["queries"]:
                escaped = q["text"].replace("|", "\\|")
                lines.append(f"| {q['num']} | {escaped} | {q['word_count']} |")
        lines.append("")

    # ── Final Verdict ──
    lines.append("### Final Verdict")
    lines.append("")

    definition_all_pass = len(definition_passes) == len(definition_results)
    no_regressions = len(regression_passes) == len(regression_results)

    if definition_all_pass and no_regressions:
        lines.append("**APPROVED** ✅")
        lines.append("")
        lines.append("The targeted fix for definition queries is working correctly:")
        lines.append("- All 5 definition query tests generate exactly 1 query as expected")
        lines.append("- All 5 regression spot-checks pass with no regressions")
        lines.append("- The prompt is production-ready")
    elif definition_all_pass and not no_regressions:
        lines.append("**NEEDS MORE ITERATION** ⚠️")
        lines.append("")
        lines.append("- Definition fix is working ✅")
        lines.append(f"- But {len(regression_failures)} regression(s) detected ❌")
        lines.append("- Must investigate and fix regressions before approval")
    elif not definition_all_pass and no_regressions:
        lines.append("**NEEDS MORE ITERATION** ⚠️")
        lines.append("")
        lines.append(f"- Definition fix partially working: {len(definition_passes)}/{len(definition_results)} pass")
        lines.append("- No regressions detected ✅")
        lines.append("- Need stronger anti-patterns for definition queries")
    else:
        lines.append("**NEEDS MORE ITERATION** ❌")
        lines.append("")
        lines.append(f"- Definition fix not fully working: {len(definition_passes)}/{len(definition_results)} pass")
        lines.append(f"- {len(regression_failures)} regression(s) detected")
        lines.append("- Requires both fix reinforcement and regression investigation")
    lines.append("")

    return "\n".join(lines)


# ── Main ──
if __name__ == "__main__":
    print("=" * 70)
    print("  PLANNER PROMPT REGRESSION TEST — ITERATION 2")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Total test runs: {len(TEST_QUERIES)}")
    print("=" * 70)

    results = run_tests()

    # Save raw JSON
    json_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "regression_test_results.json",
    )
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n📄 JSON results saved to: {json_path}")

    # Append markdown to existing report
    md_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "writer",
        "planner_prompt_test_results.md",
    )
    md_path = os.path.abspath(md_path)

    appendix = generate_iteration2_appendix(results)

    with open(md_path, "a", encoding="utf-8") as f:
        f.write(appendix)
    print(f"📝 Markdown appendix appended to: {md_path}")

    # Print final summary
    verdicts = {"PASS": 0, "FAIL": 0, "BORDERLINE": 0, "ERROR": 0}
    for r in results:
        verdicts[r["verdict"]] += 1

    print("\n" + "=" * 70)
    print("  FINAL SUMMARY — ITERATION 2")
    print("=" * 70)

    # Definition queries
    def_results = [r for r in results if r["category"] == "Definition Fix"]
    def_pass = sum(1 for r in def_results if r["verdict"] == "PASS")
    print(f"\n  Definition Fix: {def_pass}/{len(def_results)} PASS")
    for r in def_results:
        icon = "✅" if r["verdict"] == "PASS" else "❌"
        print(f"    {icon} {r['label']}: {r['num_queries']} query/queries (expected {r['expected_range']})")

    # Regression
    reg_results = [r for r in results if r["category"] == "Regression"]
    reg_pass = sum(1 for r in reg_results if r["verdict"] == "PASS")
    print(f"\n  Regression Check: {reg_pass}/{len(reg_results)} PASS")
    for r in reg_results:
        icon = "✅" if r["verdict"] == "PASS" else "❌"
        print(f"    {icon} {r['label']}: {r['num_queries']} query/queries (expected {r['expected_range']})")

    print(f"\n  Overall: {verdicts['PASS']}/{len(results)} PASS")
    for v in ["PASS", "BORDERLINE", "FAIL", "ERROR"]:
        if verdicts[v] > 0:
            print(f"    {v}: {verdicts[v]}")
    print("=" * 70)
