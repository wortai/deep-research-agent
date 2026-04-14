#!/usr/bin/env python3
"""
Planner test with 50 realistic user queries across diverse domains.
Calls get_enhanced_plan_prompt, generates plans, and saves results to test_plan.md.
"""

import os
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, "/Users/choclate/Desktop/WORT/deep-research-agent")

from dotenv import load_dotenv

load_dotenv("/Users/choclate/Desktop/WORT/deep-research-agent/.env")

import importlib.util

prompts_path = "/Users/choclate/Desktop/WORT/deep-research-agent/researcher/solution_tree/prompts/prompts.py"
spec = importlib.util.spec_from_file_location("prompts_direct", prompts_path)
prompts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompts)

get_enhanced_plan_prompt = prompts.get_enhanced_plan_prompt
PlanResult = prompts.PlanResult

TEST_QUERIES = [
    {
        "id": 1,
        "domain": "Finance/Investment",
        "query": "I'm 28 years old and just started my first real job making about 75k a year. I want to start investing but I have no idea where to begin. Should I go with index funds or try picking individual stocks? Also is it too early to think about retirement accounts like a 401k or Roth IRA?",
    },
    {
        "id": 2,
        "domain": "Coding/Web Development",
        "query": "I've been learning Python for about 6 months and I want to transition into web development. Should I learn Django or FastAPI for building backend APIs? I eventually want to build a SaaS product so I need something that scales well and is maintainable long term.",
    },
    {
        "id": 3,
        "domain": "Health/Nutrition",
        "query": "I've been feeling really sluggish and tired all the time for the past few months despite sleeping 7-8 hours. My diet is pretty bad honestly, mostly takeout and fast food. What are the most impactful dietary changes I can make to improve my energy levels throughout the day?",
    },
    {
        "id": 4,
        "domain": "Physics",
        "query": "Can someone explain quantum entanglement in a way that actually makes sense? I keep reading that measuring one particle instantly affects another one far away but that sounds like faster than light communication which shouldn't be possible. What's really going on here?",
    },
    {
        "id": 5,
        "domain": "Cooking/Technique",
        "query": "I want to learn how to properly cook steak at home like a restaurant quality sear. I've tried a few times but it always turns out either overcooked or lacking a good crust. What's the best method, pan searing with butter or reverse sear in the oven first?",
    },
    {
        "id": 6,
        "domain": "AI/Technology",
        "query": "I keep hearing about AI agents and how they're going to change everything in 2025 and 2026. What exactly are AI agents, how are they different from regular chatbots like ChatGPT, and what are the most useful things people are actually building with them right now?",
    },
    {
        "id": 7,
        "domain": "Biology/Genetics",
        "query": "How does CRISPR gene editing actually work at the molecular level? I understand it can cut DNA but how does it know where to cut and how do scientists control what changes get made? Also what are the current real world applications beyond just lab experiments?",
    },
    {
        "id": 8,
        "domain": "Art/History",
        "query": "Why is modern art so controversial? I went to a contemporary art museum recently and honestly I couldn't tell the difference between some of the art and random objects. What's the history behind the modern art movement and what should I actually be looking for to appreciate it?",
    },
    {
        "id": 9,
        "domain": "News/Geopolitics",
        "query": "What's actually happening with the US-China trade tensions right now in 2026? I see headlines about tariffs and semiconductor restrictions but I don't really understand the full picture. How does this affect regular consumers and what's the likely outcome?",
    },
    {
        "id": 10,
        "domain": "Math/Education",
        "query": "I'm struggling to understand calculus, specifically the concept of limits and derivatives. Every resource I find either goes way too deep into proofs or just gives me formulas to memorize. Can someone explain what derivatives actually mean conceptually and why they matter in real life?",
    },
    {
        "id": 11,
        "domain": "Niche/Urban Planning",
        "query": "Why do some cities feel walkable and pleasant while others feel like they were designed exclusively for cars? I'm curious about the urban planning principles that make cities like Amsterdam or Tokyo so pedestrian friendly compared to most American cities.",
    },
    {
        "id": 12,
        "domain": "Finance/Crypto",
        "query": "Is Bitcoin still a good investment in 2026 or has the ship sailed? I missed the early days and now I'm wondering if putting a small portion of my savings into crypto makes sense. What are the actual use cases beyond speculation that justify Bitcoin's value?",
    },
    {
        "id": 13,
        "domain": "Coding/DevOps",
        "query": "I'm a junior developer and I keep hearing about Docker and Kubernetes but I don't really understand what problems they solve. My apps run fine locally. Can someone explain what containerization is, why companies use it, and how I should start learning it practically?",
    },
    {
        "id": 14,
        "domain": "Health/Mental Health",
        "query": "I've been dealing with anxiety for a while now and therapy is too expensive for me. What are evidence-based techniques I can practice on my own to manage daily anxiety? I've heard about CBT and mindfulness but I don't really know where to start with either.",
    },
    {
        "id": 15,
        "domain": "STEM/Space",
        "query": "What's the current status of SpaceX's Starship program and when is NASA actually planning to send astronauts back to the Moon under the Artemis program? Also how does Starship compare to the SLS rocket in terms of capability and cost?",
    },
    {
        "id": 16,
        "domain": "Cooking/Cuisine",
        "query": "I want to learn how to cook authentic Thai food at home. What are the essential ingredients I need to stock up on, and what are 3-4 beginner-friendly Thai dishes I should master first? I live near an Asian grocery store so I can get most ingredients.",
    },
    {
        "id": 17,
        "domain": "Biology/Evolution",
        "query": "How do new species actually form? I understand natural selection favors certain traits but I don't understand how one species splits into two separate ones that can't interbreed. What's the evidence for speciation and how long does the process typically take?",
    },
    {
        "id": 18,
        "domain": "Art/Music",
        "query": "I want to learn music production as a hobby, making beats and electronic music. What software should I start with, Ableton or FL Studio? And what basic music theory do I actually need to know to start making decent sounding tracks without spending years studying?",
    },
    {
        "id": 19,
        "domain": "General/Productivity",
        "query": "I have a terrible habit of procrastinating on everything important. I'll spend hours on my phone instead of doing work that matters. What actually works to overcome chronic procrastination? Not generic advice like 'just do it' but real strategies backed by psychology research.",
    },
    {
        "id": 20,
        "domain": "Physics/Cosmology",
        "query": "What happened before the Big Bang? I know time itself started with the Big Bang but that answer feels like a cop-out. What do current theories in physics and cosmology say about what existed before our universe, if anything? Are multiverse theories taken seriously?",
    },
    {
        "id": 21,
        "domain": "Investment/Real Estate",
        "query": "Is buying a house still a better financial decision than renting in 2026 given the current interest rates and housing market? I live in a mid-size US city and I'm trying to decide if I should keep renting or buy my first property. What factors should I consider?",
    },
    {
        "id": 22,
        "domain": "Coding/Machine Learning",
        "query": "I want to get into machine learning but I'm overwhelmed by all the options. Should I start with Andrew Ng's courses, fast.ai, or just build projects and learn as I go? How much math do I realistically need to know before I can build useful ML models?",
    },
    {
        "id": 23,
        "domain": "Health/Fitness",
        "query": "I'm a complete beginner to strength training. I want to build muscle and get stronger but the gym is intimidating and I don't want to hire a personal trainer. What's a simple beginner workout routine I can follow 3 days a week, and how do I know if I'm progressing?",
    },
    {
        "id": 24,
        "domain": "Niche/Psychology",
        "query": "Why do people believe in conspiracy theories even when presented with strong evidence against them? I'm not trying to mock anyone, I genuinely want to understand the psychology behind it. What cognitive biases and social factors drive conspiracy thinking?",
    },
    {
        "id": 25,
        "domain": "Finance/Taxes",
        "query": "I just started freelancing full time after years of being a W2 employee. What do I need to know about quarterly estimated taxes, self-employment tax, and legitimate business deductions? I want to minimize my tax burden legally without getting in trouble with the IRS.",
    },
    {
        "id": 26,
        "domain": "News/Climate",
        "query": "What are the most promising carbon capture and climate mitigation technologies being developed right now? I'm skeptical that planting trees alone can solve climate change. What are the realistic technological solutions and how close are we to deploying them at scale?",
    },
    {
        "id": 27,
        "domain": "Math/Statistics",
        "query": "I keep seeing studies reported in the news saying things like 'X increases risk of Y by 50%' but then I find out the actual numbers are tiny. How should I properly interpret statistical claims and scientific studies as a non-expert? What are common statistical tricks to watch out for?",
    },
    {
        "id": 28,
        "domain": "Art/Photography",
        "query": "I want to get into photography as a serious hobby. Should I start with a mirrorless camera or is my smartphone good enough for learning the basics? What are the fundamental concepts I should master first, and what's a reasonable budget for beginner gear?",
    },
    {
        "id": 29,
        "domain": "STEM/Materials Science",
        "query": "What are the latest breakthroughs in battery technology? I keep seeing headlines about solid-state batteries and new lithium alternatives but it seems like nothing actually reaches consumers. What's the realistic timeline for next-generation batteries in EVs and phones?",
    },
    {
        "id": 30,
        "domain": "Cooking/Meal Prep",
        "query": "I work long hours and end up ordering delivery most nights which is destroying my budget. How do I meal prep efficiently for a full work week? I need practical strategies, not just recipes. How do I plan, shop, and cook 5 days of lunches and dinners on a Sunday?",
    },
    {
        "id": 31,
        "domain": "Health/Sleep",
        "query": "My sleep quality has been terrible lately. I fall asleep fine but I wake up at 3 or 4 AM and can't get back to sleep. What does the science say about improving sleep maintenance? Are supplements like melatonin or magnesium actually helpful or is it mostly about sleep hygiene?",
    },
    {
        "id": 32,
        "domain": "General/Education",
        "query": "Is a master's degree still worth it in 2026 or is the job market shifting towards skills and experience over formal education? I'm considering going back to school for computer science but I'm not sure if the time and cost justify the career benefits anymore.",
    },
    {
        "id": 33,
        "domain": "Coding/Security",
        "query": "How do websites and apps actually get hacked? Not looking to learn anything malicious, I just want to understand the most common vulnerability types like SQL injection, XSS, and phishing so I can protect my own web applications. What security practices should every developer follow?",
    },
    {
        "id": 34,
        "domain": "Biology/Neuroscience",
        "query": "How does memory actually work in the brain? I find it fascinating that I can remember a song from 15 years ago but forget what I had for lunch yesterday. What's the difference between short-term and long-term memory, and why does the brain decide to keep or discard certain information?",
    },
    {
        "id": 35,
        "domain": "Niche/Philosophy",
        "query": "What is the hard problem of consciousness and why haven't neuroscientists and philosophers been able to solve it? I've read that we can explain how the brain processes information but not why it feels like something to be conscious. What are the leading theories about this?",
    },
    {
        "id": 36,
        "domain": "Finance/Stock Market",
        "query": "What's driving the stock market in 2026? I see the S&P 500 is at record highs but I also read warnings about a potential crash. What economic indicators should I actually pay attention to, and is market timing ever a good strategy or should I just keep dollar cost averaging?",
    },
    {
        "id": 37,
        "domain": "Physics/Quantum Computing",
        "query": "Is quantum computing actually going to break internet encryption like some articles claim? How far are we from practical quantum computers and what would the implications be for cybersecurity? Also what's the difference between a quantum computer and a regular supercomputer?",
    },
    {
        "id": 38,
        "domain": "Art/Film",
        "query": "I want to understand why certain films are considered masterpieces while others with bigger budgets are forgettable. What are the key elements of cinematography, pacing, and storytelling that separate a great film from an average one? Any resources for learning film analysis?",
    },
    {
        "id": 39,
        "domain": "Health/Gut Microbiome",
        "query": "I keep reading that gut health affects everything from your mood to your immune system. How legit is the science behind the gut-brain connection and the microbiome? What dietary changes and probiotics are actually supported by research versus just being marketing hype?",
    },
    {
        "id": 40,
        "domain": "General/Career",
        "query": "I've been at the same company for 4 years and I feel stuck. My salary has barely increased despite good performance reviews. Is it true that job hopping every 2-3 years is the best way to increase your salary, or does loyalty to one company still have value?",
    },
    {
        "id": 41,
        "domain": "Coding/Open Source",
        "query": "How do I start contributing to open source projects? I'm a decent Python developer but I look at big projects on GitHub and feel totally lost. Where do I find beginner-friendly issues, how does the PR process work, and how do I get maintainers to actually review my contributions?",
    },
    {
        "id": 42,
        "domain": "STEM/Renewable Energy",
        "query": "Can the world actually run on 100% renewable energy or is that unrealistic? What are the biggest technical challenges with solar and wind, specifically around energy storage and grid stability? How are countries like Germany and Denmark handling these issues?",
    },
    {
        "id": 43,
        "domain": "Cooking/Fermentation",
        "query": "I want to start making my own sourdough bread from scratch. How do I create and maintain a sourdough starter, and what's the basic process from start to finish? I don't have any fancy equipment, just a regular home oven. What are the most common mistakes beginners make?",
    },
    {
        "id": 44,
        "domain": "News/AI Regulation",
        "query": "What's happening with AI regulation globally? I know the EU passed the AI Act but what about the US and other countries? Are there actual enforceable rules around AI development or is it mostly voluntary guidelines? How are tech companies responding to all this?",
    },
    {
        "id": 45,
        "domain": "Math/Cryptography",
        "query": "How does end-to-end encryption actually work in apps like WhatsApp and Signal? I understand the basic idea that messages are scrambled but how do two phones agree on a secret key without anyone intercepting it? What's the math behind public key cryptography?",
    },
    {
        "id": 46,
        "domain": "Niche/Mycology",
        "query": "I've been getting interested in mushroom foraging and cultivation. What are the safest mushrooms for beginners to identify in the wild, and what equipment do I need to start growing gourmet mushrooms at home? Also how big is the legal risk of misidentification?",
    },
    {
        "id": 47,
        "domain": "Investment/ETFs",
        "query": "I have about 10k saved up and I want to invest it in ETFs for long term growth. Should I just put it all in VOO or should I diversify across different ETFs like international and bond funds? What's a good simple portfolio allocation for someone who doesn't want to actively manage things?",
    },
    {
        "id": 48,
        "domain": "General/Travel",
        "query": "I want to take a 3-week trip through Japan but I have no idea how to plan it. What's the best route to see both Tokyo and Kyoto, how does the rail pass work, and what's a realistic daily budget? I'm interested in both tourist highlights and off-the-beaten-path experiences.",
    },
    {
        "id": 49,
        "domain": "Health/Longevity",
        "query": "What does the latest research actually say about extending human lifespan and healthspan? I see a lot of hype around NMN, resveratrol, and intermittent fasting for anti-aging. Which of these interventions have solid evidence behind them and which are mostly speculation at this point?",
    },
    {
        "id": 50,
        "domain": "Coding/System Design",
        "query": "I have a technical interview coming up that includes a system design round. How should I approach designing a large-scale system like a chat application or a URL shortener? What are the key concepts I need to understand like load balancing, caching, and database sharding?",
    },
]


def count_words(text):
    return len(text.strip().split())


def classify_intent(query: str) -> str:
    q = query.lower()
    if any(p in q for p in ["what is", "who is", "current", "define", "what's"]):
        if "vs" in q or "compare" in q or "difference" in q:
            return "Comparative"
        return "Lookup"
    if any(p in q for p in ["why does", "what causes", "how did", "what led"]):
        return "Causal"
    if any(p in q for p in ["how does", "explain", "walk me", "actually work"]):
        return "Mechanistic"
    if any(p in q for p in ["vs", "compare", "difference", "which is better", "or is"]):
        return "Comparative"
    if any(
        p in q for p in ["pros and cons", "should i", "worth it", "good or", "legit"]
    ):
        return "Evaluative"
    if any(
        p in q
        for p in [
            "everything about",
            "complete guide",
            "a to z",
            "from scratch",
            "all aspects",
        ]
    ):
        return "Comprehensive"
    if any(
        p in q
        for p in [
            "how do i",
            "best approach",
            "step by step",
            "how to",
            "start",
            "learn",
            "begin",
        ]
    ):
        return "Strategic"
    if any(p in q for p in ["tell me about", "overview", "want to understand"]):
        return "Exploratory"
    return "Exploratory"


def run_tests():
    print("=" * 70)
    print("PLANNER TEST - 50 DIVERSE USER QUERIES")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: No API key found!")
        return

    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=1.25)
    structured_llm = llm.with_structured_output(PlanResult)
    print("LLM initialized (gemini-2.0-flash)\n")

    results = []
    total = len(TEST_QUERIES)

    for idx, test_case in enumerate(TEST_QUERIES):
        qid = test_case["id"]
        domain = test_case["domain"]
        query = test_case["query"]
        intent = classify_intent(query)
        query_wc = count_words(query)

        print(f"[{idx + 1}/{total}] ID={qid} | {domain} | Intent: {intent}")
        print(f"  Query ({query_wc}w): {query[:90]}...")

        try:
            prompt = get_enhanced_plan_prompt(
                query=query, skill_instructions="", clarification_context=[]
            )

            result = structured_llm.invoke(prompt)
            plan = result.plan

            word_counts = [count_words(q) for q in plan]
            in_range = sum(1 for wc in word_counts if 20 <= wc <= 100)
            all_in_range = in_range == len(plan)
            count_ok = 1 <= len(plan) <= 10

            print(
                f"  -> {len(plan)} queries | Word range: {min(word_counts)}-{max(word_counts)} | In-range: {in_range}/{len(plan)}"
            )

            results.append(
                {
                    "id": qid,
                    "domain": domain,
                    "intent": intent,
                    "query": query,
                    "query_word_count": query_wc,
                    "num_generated": len(plan),
                    "word_counts": word_counts,
                    "count_ok": count_ok,
                    "words_ok": all_in_range,
                    "in_range_count": in_range,
                    "plan": plan,
                    "error": None,
                }
            )

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append(
                {
                    "id": qid,
                    "domain": domain,
                    "intent": intent,
                    "query": query,
                    "query_word_count": query_wc,
                    "error": str(e),
                }
            )

        time.sleep(1)

    # ── Generate Markdown Report ──
    md_lines = []
    md_lines.append("# Planner Test Report — 50 Diverse User Queries")
    md_lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_lines.append(f"**Model:** gemini-2.0-flash | **Temperature:** 1.25")
    md_lines.append(f"**Total queries tested:** {total}")
    md_lines.append("")

    # Summary statistics
    successful = [r for r in results if r.get("error") is None]
    failed = [r for r in results if r.get("error") is not None]
    count_ok = [r for r in successful if r.get("count_ok")]
    words_ok = [r for r in successful if r.get("words_ok")]
    all_pass = [r for r in successful if r.get("count_ok") and r.get("words_ok")]

    md_lines.append("## Summary")
    md_lines.append("")
    md_lines.append(f"| Metric | Value |")
    md_lines.append(f"|---|---|")
    md_lines.append(f"| Total queries | {total} |")
    md_lines.append(f"| Successful | {len(successful)} |")
    md_lines.append(f"| Errors | {len(failed)} |")
    md_lines.append(f"| Count in range (1-10) | {len(count_ok)}/{len(successful)} |")
    md_lines.append(f"| All words 20-100 | {len(words_ok)}/{len(successful)} |")
    md_lines.append(f"| Fully passing | {len(all_pass)}/{len(successful)} |")

    if successful:
        avg_queries = sum(r["num_generated"] for r in successful) / len(successful)
        all_word_counts = [wc for r in successful for wc in r["word_counts"]]
        avg_word_count = (
            sum(all_word_counts) / len(all_word_counts) if all_word_counts else 0
        )
        min_wc = min(all_word_counts) if all_word_counts else 0
        max_wc = max(all_word_counts) if all_word_counts else 0
        md_lines.append(f"| Avg plan queries | {avg_queries:.1f} |")
        md_lines.append(f"| Avg query word count | {avg_word_count:.1f} |")
        md_lines.append(f"| Min query word count | {min_wc} |")
        md_lines.append(f"| Max query word count | {max_wc} |")

    # Distribution by query count
    md_lines.append("")
    md_lines.append("## Plan Size Distribution")
    md_lines.append("")
    md_lines.append("| # Queries in Plan | Count |")
    md_lines.append("|---|---|")
    from collections import Counter

    size_counts = Counter(r["num_generated"] for r in successful)
    for size in sorted(size_counts.keys()):
        md_lines.append(f"| {size} | {size_counts[size]} |")

    # Distribution by intent type
    md_lines.append("")
    md_lines.append("## Intent Type Distribution")
    md_lines.append("")
    md_lines.append("| Intent | Count | Avg Plan Size |")
    md_lines.append("|---|---|---|")
    intent_groups = {}
    for r in successful:
        intent = r["intent"]
        intent_groups.setdefault(intent, []).append(r)
    for intent in sorted(intent_groups.keys()):
        grp = intent_groups[intent]
        avg_sz = sum(r["num_generated"] for r in grp) / len(grp)
        md_lines.append(f"| {intent} | {len(grp)} | {avg_sz:.1f} |")

    # Domain breakdown
    md_lines.append("")
    md_lines.append("## Domain Breakdown")
    md_lines.append("")
    md_lines.append("| Domain | Count | Avg Plan Size | All Words OK |")
    md_lines.append("|---|---|---|---|")
    domain_groups = {}
    for r in successful:
        domain_groups.setdefault(r["domain"], []).append(r)
    for domain in sorted(domain_groups.keys()):
        grp = domain_groups[domain]
        avg_sz = sum(r["num_generated"] for r in grp) / len(grp)
        w_ok = sum(1 for r in grp if r["words_ok"])
        md_lines.append(f"| {domain} | {len(grp)} | {avg_sz:.1f} | {w_ok}/{len(grp)} |")

    # Errors
    if failed:
        md_lines.append("")
        md_lines.append("## Errors")
        md_lines.append("")
        for r in failed:
            md_lines.append(f"- **ID {r['id']}** ({r['domain']}): {r['error']}")

    # Detailed results per query
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## Detailed Results")
    md_lines.append("")

    for r in results:
        status = (
            "PASS"
            if r.get("count_ok") and r.get("words_ok")
            else ("ERROR" if r.get("error") else "FAIL")
        )
        emoji = {"PASS": "✅", "FAIL": "⚠️", "ERROR": "❌"}[status]

        md_lines.append(f"### {emoji} Query #{r['id']} — {r['domain']} [{r['intent']}]")
        md_lines.append("")
        md_lines.append(f"> **User Query** ({r.get('query_word_count', '?')} words):")
        md_lines.append(f"> {r['query']}")
        md_lines.append("")

        if r.get("error"):
            md_lines.append(f"**Error:** {r['error']}")
            md_lines.append("")
            continue

        md_lines.append(f"**Plan Size:** {r['num_generated']} queries")
        md_lines.append(
            f"**Word Counts:** {r['word_counts']} (range: {min(r['word_counts'])}-{max(r['word_counts'])})"
        )
        md_lines.append(
            f"**Words in 20-100 range:** {r['in_range_count']}/{r['num_generated']}"
        )
        md_lines.append("")

        for i, q in enumerate(r["plan"]):
            wc = count_words(q)
            mark = "✅" if 20 <= wc <= 100 else "❌"
            md_lines.append(f"**{i + 1}.** [{wc}w {mark}] {q}")
            md_lines.append("")

        md_lines.append("---")
        md_lines.append("")

    report_text = "\n".join(md_lines)
    output_path = "/Users/choclate/Desktop/WORT/deep-research-agent/tests/test_plan.md"
    with open(output_path, "w") as f:
        f.write(report_text)

    # Also save raw JSON
    json_path = (
        "/Users/choclate/Desktop/WORT/deep-research-agent/tests/test_plan_results.json"
    )
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)
    print(f"Pass: {len(all_pass)}/{len(successful)}")
    print(f"Results: {output_path}")
    print(f"JSON:    {json_path}")


if __name__ == "__main__":
    run_tests()
