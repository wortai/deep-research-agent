#!/usr/bin/env python3
"""
Standalone test script for planner prompt - uses direct API calls.
"""

import os
import sys
import json
from datetime import datetime

# Add project root
sys.path.insert(0, "/Users/choclate/Desktop/WORT/deep-research-agent")

# Load env
from dotenv import load_dotenv

load_dotenv("/Users/choclate/Desktop/WORT/deep-research-agent/.env")

# Import prompts directly
import importlib.util

prompts_path = "/Users/choclate/Desktop/WORT/deep-research-agent/researcher/solution_tree/prompts/prompts.py"
spec = importlib.util.spec_from_file_location("prompts_direct", prompts_path)
prompts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompts)

get_enhanced_plan_prompt = prompts.get_enhanced_plan_prompt
PlanResult = prompts.PlanResult

# Test queries
DEMO_QUERIES = [
    {
        "id": 1,
        "domain": "Finance/Fact",
        "query": "What is the current price of Bitcoin?",
    },
    {
        "id": 2,
        "domain": "Coding/Comparison",
        "query": "Compare React and Vue for building dashboards",
    },
    {
        "id": 3,
        "domain": "AI/Technical",
        "query": "How do large language models work and what are their limitations?",
    },
    {
        "id": 4,
        "domain": "History",
        "query": "Tell me about the rise and fall of the Roman Empire",
    },
    {
        "id": 5,
        "domain": "Finance/Strategy",
        "query": "What are the best investment strategies for beginners in 2025?",
    },
    {
        "id": 6,
        "domain": "Biology/Ethics",
        "query": "Explain how CRISPR gene editing works and its ethical implications",
    },
    {
        "id": 7,
        "domain": "News/Current",
        "query": "What are the major developments in the Ukraine-Russia conflict this year?",
    },
    {
        "id": 8,
        "domain": "Science/Comprehensive",
        "query": "Explain everything about quantum computing — from basics to current state to future applications",
    },
    {
        "id": 9,
        "domain": "General/Business",
        "query": "What are the benefits and drawbacks of remote work for employees and companies?",
    },
    {
        "id": 10,
        "domain": "Writing/How-to",
        "query": "How do I write a compelling novel? Cover structure, character development, and publishing",
    },
]


def count_words(text):
    return len(text.strip().split())


def run_tests():
    print("🚀 Starting Planner Prompt Test...\n")

    # Initialize LLM
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ No API key found!")
        return

    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=1.25)
    structured_llm = llm.with_structured_output(PlanResult)
    print("✅ LLM initialized\n")

    results = []

    for demo in DEMO_QUERIES:
        print(f"Test #{demo['id']}: {demo['domain']}")
        print(f"Query: {demo['query']}")

        try:
            prompt = get_enhanced_plan_prompt(
                query=demo["query"], skill_instructions="", clarification_context=[]
            )

            result = structured_llm.invoke(prompt)
            plan = result.plan

            print(f"  Generated {len(plan)} queries:")

            for i, q in enumerate(plan):
                wc = count_words(q)
                status = "✅" if 20 <= wc <= 100 else "❌"
                print(f"    {i + 1}. [{wc} words] {status} {q[:80]}...")

            # Analysis
            num_ok = len(plan) >= 1 and len(plan) <= 10
            words_ok = all(20 <= count_words(q) <= 100 for q in plan)

            results.append(
                {
                    "id": demo["id"],
                    "domain": demo["domain"],
                    "query": demo["query"],
                    "num_generated": len(plan),
                    "word_counts": [count_words(q) for q in plan],
                    "num_ok": num_ok,
                    "words_ok": words_ok,
                    "plan": plan,
                }
            )

            if num_ok and words_ok:
                print("  ✅ PASS\n")
            else:
                print("  ❌ FAIL\n")

        except Exception as e:
            print(f"  ❌ Error: {e}\n")
            results.append({"id": demo["id"], "error": str(e)})

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r.get("num_ok") and r.get("words_ok"))
    total = len([r for r in results if "error" not in r])

    print(f"Passed: {passed}/{total}")

    # Save results
    with open(
        "/Users/choclate/Desktop/WORT/deep-research-agent/tests/planner_results.json",
        "w",
    ) as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to tests/planner_results.json")


if __name__ == "__main__":
    run_tests()
