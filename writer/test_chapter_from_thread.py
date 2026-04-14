"""
Test: Generate chapters from real thread checkpoint data.

Extracts ResearchReview data from a specific thread's LangGraph checkpoint,
runs the full Writer pipeline (outline -> design -> chapter bodies),
evaluates output quality, and runs an LLM observer to critique whether
the prompt instructions were actually followed.

Usage:
    cd deep-research-agent
    python -m writer.test_chapter_from_thread
"""

import sys
import os
import json
import re
import asyncio
import logging
from datetime import datetime

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_server_root = os.path.join(os.path.dirname(_project_root), "server")
_parent_root = os.path.dirname(_project_root)  # WORT/

sys.path.insert(0, _project_root)
sys.path.insert(0, _server_root)
sys.path.insert(0, _parent_root)

from dotenv import load_dotenv

env_path = os.path.join(_project_root, ".env")
load_dotenv(env_path, override=False)

from memory.memory_facade import MemoryFacade
from writer.report_writer import Writer
from llms import LlmsHouse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

THREAD_ID = "a534c345-468d-4970-881a-2a51d19c3735"
OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), f"test_output_thread_{THREAD_ID[:8]}"
)


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


async def read_thread_state(thread_id: str) -> dict:
    db_uri = os.getenv("DATABASE_URL")
    if not db_uri:
        raise RuntimeError("DATABASE_URL not set in environment")

    logger.info(f"Connecting to database for thread: {thread_id}")
    facade = MemoryFacade(db_uri)
    await facade.initialize()

    # Inline checkpoint reading (avoids importing server package)
    config = {"configurable": {"thread_id": thread_id}}
    checkpoint_tuple = await facade.checkpointer.aget_tuple(config)

    if not checkpoint_tuple or not checkpoint_tuple.checkpoint:
        raise RuntimeError(f"No checkpoint found for thread: {thread_id}")

    channel_values = checkpoint_tuple.checkpoint.get("channel_values", {})
    if not channel_values:
        raise RuntimeError(f"Empty channel_values for thread: {thread_id}")

    await facade.shutdown()
    return channel_values


def make_serializable(obj):
    if isinstance(obj, dict):
        return {str(k): make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    return str(obj)


def save_raw_state(state: dict):
    path = os.path.join(OUTPUT_DIR, "01_raw_state.json")
    with open(path, "w") as f:
        json.dump(make_serializable(state), f, indent=2, default=str)
    logger.info(f"Raw state saved to: {path}")


def print_state_summary(state: dict):
    print("\n" + "=" * 80)
    print("STATE SUMMARY")
    print("=" * 80)
    print(f"  user_query:       {state.get('user_query', 'N/A')[:120]}")
    print(f"  current_run_id:   {state.get('current_run_id', 'N/A')}")

    planner = state.get("planner_query", [])
    print(f"  planner_queries:  {len(planner)}")
    for pq in planner:
        print(f"    #{pq.get('query_num', '?')}: {pq.get('query', '')[:80]}")

    reviews = state.get("research_review", [])
    print(f"  research_reviews: {len(reviews)}")
    for r in reviews:
        q = r.get("query", "")[:80]
        n = len(r.get("raw_research_results", []))
        print(
            f"    query_num={r.get('query_num', '?')} run={r.get('run_id', '?')[:8]} results={n} query={q}"
        )

    reports = state.get("reports", [])
    print(f"  existing_reports: {len(reports)}")
    print(f"  search_mode:      {state.get('search_mode', 'N/A')}")
    print(f"  intent_type:      {state.get('intent_type', 'N/A')}")
    print(f"  analysis_level:   {state.get('analysis_level', 'N/A')}")
    print("=" * 80 + "\n")


def build_mock_state(state: dict) -> dict:
    return {
        "user_query": state.get("user_query", ""),
        "current_run_id": state.get("current_run_id", ""),
        "planner_query": state.get("planner_query", []),
        "research_review": state.get("research_review", []),
    }


def evaluate_chapter_html(html_content: str, chapter_heading: str) -> dict:
    results = {
        "chapter_heading": chapter_heading,
        "html_length": len(html_content),
        "metrics": {},
        "issues": [],
        "warnings": [],
        "passes": [],
    }

    has_report_chapter = '<div class="report-chapter">' in html_content
    has_report_page = '<div class="report-page">' in html_content
    page_count = html_content.count('<div class="report-page">')

    results["metrics"]["has_report_chapter"] = has_report_chapter
    results["metrics"]["has_report_page"] = has_report_page
    results["metrics"]["page_count"] = page_count

    if not has_report_chapter:
        results["issues"].append("MISSING: <div class='report-chapter'> wrapper")
    if not has_report_page:
        results["issues"].append("MISSING: <div class='report-page'> containers")
    if page_count < 2:
        results["issues"].append(f"FAIL: Only {page_count} page(s), minimum is 2")
    else:
        results["passes"].append(f"OK: {page_count} report-page containers")

    svg_count = html_content.count("<svg")
    results["metrics"]["svg_count"] = svg_count
    if svg_count > 0:
        svg_with_title = html_content.count("<title>")
        svg_with_desc = html_content.count("<desc>")
        if svg_with_title < svg_count:
            results["warnings"].append(
                f"{svg_count - svg_with_title} SVG(s) missing <title>"
            )
        if svg_with_desc < svg_count:
            results["warnings"].append(
                f"{svg_count - svg_with_desc} SVG(s) missing <desc>"
            )
        svg_with_viewbox = html_content.count("viewBox=")
        if svg_with_viewbox < svg_count:
            results["warnings"].append(
                f"{svg_count - svg_with_viewbox} SVG(s) missing viewBox"
            )
        results["passes"].append(f"OK: {svg_count} SVG element(s)")

    has_charts_css = 'class="charts-css' in html_content
    results["metrics"]["has_charts_css"] = has_charts_css
    table_count = html_content.count("<table")
    results["metrics"]["table_count"] = table_count
    inline_style_count = html_content.count('style="')
    results["metrics"]["inline_style_count"] = inline_style_count
    if inline_style_count < 5:
        results["warnings"].append(
            f"Only {inline_style_count} inline styles - may not follow design instructions"
        )

    link_count = html_content.count("<a href=")
    results["metrics"]["citation_count"] = link_count
    if link_count == 0:
        results["warnings"].append("No citations/links found")
    else:
        results["passes"].append(f"OK: {link_count} citation(s)")

    open_divs = html_content.count("<div")
    close_divs = html_content.count("</div>")
    if open_divs != close_divs:
        results["issues"].append(
            f"MISMATCH: {open_divs} opening <div> vs {close_divs} closing </div>"
        )
    else:
        results["passes"].append(f"OK: All divs properly closed ({open_divs} pairs)")

    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", html_content, re.DOTALL)
    total_words = sum(len(p.split()) for p in paragraphs)
    results["metrics"]["paragraph_count"] = len(paragraphs)
    results["metrics"]["total_words"] = total_words
    if total_words < 300:
        results["issues"].append(f"LOW CONTENT: Only {total_words} words in paragraphs")
    elif total_words < 600:
        results["warnings"].append(
            f"LOW CONTENT: {total_words} words - may not fill pages"
        )
    else:
        results["passes"].append(f"OK: {total_words} words of prose content")

    visual_types = []
    if svg_count > 0:
        visual_types.append("SVG")
    if has_charts_css:
        visual_types.append("Charts.css")
    if table_count > 0:
        visual_types.append("Table")
    if link_count > 0:
        visual_types.append("Citation")
    if html_content.count("<blockquote") > 0:
        visual_types.append("Blockquote")
    if html_content.count("<details") > 0:
        visual_types.append("Collapsible")
    results["metrics"]["visual_types"] = visual_types
    if len(visual_types) <= 1 and total_words > 200:
        results["warnings"].append(
            f"LOW VISUAL VARIETY: Only {len(visual_types)} visual type(s)"
        )
    elif len(visual_types) >= 2:
        results["passes"].append(
            f"OK: {len(visual_types)} visual types: {', '.join(visual_types)}"
        )

    if table_count >= 3:
        results["warnings"].append(
            f"POSSIBLE REPETITION: {table_count} tables - consider varying"
        )

    return results


async def observer_critique(
    html_content: str,
    design_instructions: str,
    chapter_heading: str,
    user_query: str,
) -> dict:
    model = LlmsHouse().google_model("gemini-2.5-flash")

    prompt = f"""You are a quality auditor for HTML report chapters. A chapter was generated by an AI following strict instructions. Your job is to check whether the instructions were actually followed.

CHAPTER HEADING: {chapter_heading}
USER QUERY: {user_query}

DESIGN INSTRUCTIONS GIVEN TO THE GENERATOR:
{design_instructions[:3000] if design_instructions else "No design instructions provided."}

GENERATED HTML (truncated to first 8000 chars):
{html_content[:8000]}

Evaluate the following criteria. For each, answer PASS or FAIL with a brief explanation:

1. STRUCTURE: Does the HTML have a <div class="report-chapter"> wrapper containing only <div class="report-page"> children? Are all elements inside report-page containers?

2. PAGE COUNT: Are there at least 2 report-page containers?

3. DESIGN COMPLIANCE: Do the colors (hex values), font families, and font sizes match the design instructions? Check inline styles.

4. VISUAL VARIETY: Does the chapter use a mix of presentation formats (prose, tables, charts, SVG, blockquotes, callouts) rather than repeating one pattern?

5. CONTENT DEPTH: Is the content exhaustive and detailed, or does it feel summarized/superficial? Should be at least 600 words of prose.

6. CITATIONS: Are there inline <a href> citation links? At least 3 required.

7. SVG STANDARDS: If SVGs exist, do they have viewBox, <title>, <desc>? Are they wrapped in overflow-x:auto?

8. REPORT TYPE MATCH: Does the visual style match the report type implied by the design instructions?

9. NO ANTI-PATTERNS: No invented content, no section_id markers, no unclosed tags, no repeated visual pattern 3+ times?

10. OVERALL QUALITY: Would a human reader find this chapter professional and informative?

Respond in this exact JSON format (no markdown fences):
{{
  "criteria": [
    {{"name": "Structure", "verdict": "PASS|FAIL", "detail": "brief explanation"}},
    {{"name": "Page Count", "verdict": "PASS|FAIL", "detail": "brief explanation"}},
    {{"name": "Design Compliance", "verdict": "PASS|FAIL", "detail": "brief explanation"}},
    {{"name": "Visual Variety", "verdict": "PASS|FAIL", "detail": "brief explanation"}},
    {{"name": "Content Depth", "verdict": "PASS|FAIL", "detail": "brief explanation"}},
    {{"name": "Citations", "verdict": "PASS|FAIL", "detail": "brief explanation"}},
    {{"name": "SVG Standards", "verdict": "PASS|FAIL", "detail": "brief explanation"}},
    {{"name": "Report Type Match", "verdict": "PASS|FAIL", "detail": "brief explanation"}},
    {{"name": "No Anti-Patterns", "verdict": "PASS|FAIL", "detail": "brief explanation"}},
    {{"name": "Overall Quality", "verdict": "PASS|FAIL", "detail": "brief explanation"}}
  ],
  "pass_count": 0,
  "fail_count": 0,
  "summary": "One paragraph overall assessment."
}}"""

    try:
        response = await model.ainvoke(prompt)
        raw_text = response.content if hasattr(response, "content") else str(response)

        code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw_text, re.DOTALL)
        if code_block:
            return json.loads(code_block.group(1).strip())

        brace_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if brace_match:
            return json.loads(brace_match.group(0))

        return {"error": "Could not parse observer response", "raw": raw_text[:2000]}
    except Exception as e:
        return {"error": str(e)}


async def main():
    ensure_output_dir()

    print("=" * 80)
    print("CHAPTER GENERATION TEST FROM REAL THREAD DATA")
    print(f"Thread: {THREAD_ID}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 80)

    # Step 1: Read thread state
    print("\n[Step 1] Reading thread checkpoint from database...")
    state = await read_thread_state(THREAD_ID)
    save_raw_state(state)
    print_state_summary(state)

    user_query = state.get("user_query", "")
    if not user_query:
        print("WARNING: No user_query found. Aborting.")
        return

    research_reviews = state.get("research_review", [])
    if not research_reviews:
        print("WARNING: No research_review data found. Aborting.")
        return

    # Step 2: Save extracted research data
    print("\n[Step 2] Saving extracted research data...")
    research_path = os.path.join(OUTPUT_DIR, "02_research_review.json")
    with open(research_path, "w") as f:
        json.dump(make_serializable(research_reviews), f, indent=2, default=str)

    planner_queries = state.get("planner_query", [])
    planner_path = os.path.join(OUTPUT_DIR, "03_planner_queries.json")
    with open(planner_path, "w") as f:
        json.dump(planner_queries, f, indent=2, default=str)

    # Step 3: Run Writer pipeline
    print("\n[Step 3] Running Writer pipeline (outline -> design -> chapters)...")
    mock_state = build_mock_state(state)
    writer = Writer(emitter=None)
    result = await writer.run(mock_state)

    print(f"\n  TOC HTML length: {len(result.get('table_of_contents', ''))}")
    print(f"  Body sections:  {len(result.get('report_body_sections', []))}")
    print(f"  Design instr.:  {len(result.get('design_instructions', ''))}")

    # Step 4: Save outputs
    print("\n[Step 4] Saving outputs...")
    design_instructions = result.get("design_instructions", "")
    design_path = os.path.join(OUTPUT_DIR, "04_design_instructions.txt")
    with open(design_path, "w") as f:
        f.write(f"Thread: {THREAD_ID}\nUser Query: {user_query}\n{'=' * 80}\n\n")
        f.write(design_instructions)
    print(f"  Design instructions: {design_path}")

    toc_path = os.path.join(OUTPUT_DIR, "05_toc.html")
    with open(toc_path, "w") as f:
        f.write(result.get("table_of_contents", ""))
    print(f"  Table of contents: {toc_path}")

    all_evaluations = []
    all_observations = []
    body_sections = result.get("report_body_sections", [])

    for idx, section in enumerate(body_sections):
        order = section.get("section_order", idx)
        content = section.get("section_content", "")
        section_id = section.get("section_id", f"section-{idx}")

        safe_filename = f"06_chapter_{order:02d}_{section_id[:8]}.html"
        html_path = os.path.join(OUTPUT_DIR, safe_filename)
        with open(html_path, "w") as f:
            f.write(content)
        print(f"  Chapter {order}: {html_path} ({len(content)} chars)")

        eval_result = evaluate_chapter_html(content, f"Section {order}")
        eval_result["file"] = safe_filename
        eval_result["section_order"] = order
        all_evaluations.append(eval_result)

        print(f"    Pages: {eval_result['metrics'].get('page_count', 0)}")
        print(f"    Words: {eval_result['metrics'].get('total_words', 0)}")
        print(f"    SVGs: {eval_result['metrics'].get('svg_count', 0)}")
        print(f"    Citations: {eval_result['metrics'].get('citation_count', 0)}")
        for p in eval_result["passes"]:
            print(f"      PASS: {p}")
        for w in eval_result["warnings"]:
            print(f"      WARN: {w}")
        for i in eval_result["issues"]:
            print(f"      FAIL: {i}")

    # Step 5: Save evaluations
    print("\n[Step 5] Saving evaluations...")
    eval_path = os.path.join(OUTPUT_DIR, "07_evaluations.json")
    with open(eval_path, "w") as f:
        json.dump(all_evaluations, f, indent=2, default=str)
    print(f"  Evaluations: {eval_path}")

    # Step 6: Observer agent
    print("\n[Step 6] Running LLM observer agent on each chapter...")
    for idx, section in enumerate(body_sections):
        order = section.get("section_order", idx)
        content = section.get("section_content", "")
        if not content:
            continue

        print(f"\n  Observing Chapter {order}...")
        observation = await observer_critique(
            html_content=content,
            design_instructions=design_instructions,
            chapter_heading=f"Section {order}",
            user_query=user_query,
        )
        observation["section_order"] = order
        all_observations.append(observation)

        if "error" in observation:
            print(f"    ERROR: {observation['error']}")
        else:
            pass_c = observation.get("pass_count", 0)
            fail_c = observation.get("fail_count", 0)
            print(f"    Observer: {pass_c} PASS / {fail_c} FAIL")
            print(f"    Summary: {observation.get('summary', '')[:200]}")
            for c in observation.get("criteria", []):
                m = "PASS" if c["verdict"] == "PASS" else "FAIL"
                print(f"      [{m}] {c['name']}: {c.get('detail', '')[:80]}")

    obs_path = os.path.join(OUTPUT_DIR, "08_observer_critique.json")
    with open(obs_path, "w") as f:
        json.dump(all_observations, f, indent=2, default=str)
    print(f"\n  Observer critiques: {obs_path}")

    # Step 7: Combined report
    print("\n[Step 7] Building combined report HTML...")
    full_html_path = os.path.join(OUTPUT_DIR, "09_full_report.html")
    with open(full_html_path, "w") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write('<meta charset="utf-8">\n')
        f.write(
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        )
        f.write(f"<title>Test Report - Thread {THREAD_ID[:8]}</title>\n")
        f.write("<style>\n")
        f.write(
            "  body { background: #f5f5f5; font-family: system-ui; padding: 20px; }\n"
        )
        f.write(
            "  .report-page { background: white; max-width: 800px; margin: 20px auto; padding: 3rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }\n"
        )
        f.write("  .report-chapter { margin-bottom: 40px; }\n")
        f.write("</style>\n")
        f.write("</head>\n<body>\n")
        f.write(f"<h1>Test Report for Thread {THREAD_ID[:8]}</h1>\n")
        f.write(f"<p>User Query: {user_query}</p>\n<hr>\n")
        for section in body_sections:
            f.write(section.get("section_content", ""))
            f.write("\n\n")
        f.write("</body>\n</html>")
    print(f"  Full report: {full_html_path}")

    # Final Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Thread:             {THREAD_ID}")
    print(f"User Query:         {user_query[:100]}")
    print(f"Planner Queries:    {len(planner_queries)}")
    print(f"Research Reviews:   {len(research_reviews)}")
    print(f"Chapters Generated: {len(body_sections)}")
    print(f"Design Instr. Len:  {len(design_instructions)}")

    tp = sum(len(e.get("passes", [])) for e in all_evaluations)
    tw = sum(len(e.get("warnings", [])) for e in all_evaluations)
    tf = sum(len(e.get("issues", [])) for e in all_evaluations)
    op = sum(o.get("pass_count", 0) for o in all_observations)
    of_ = sum(o.get("fail_count", 0) for o in all_observations)

    print(f"\nEval:    {tp} passes, {tw} warnings, {tf} issues")
    print(f"Observer: {op} PASS, {of_} FAIL")
    print(f"\nAll outputs: {OUTPUT_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
