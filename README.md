<div align="center">

<picture>
  <img src="./assets/wortlogo.png" alt="WORT" width="140" />
</picture>

# WORT Research Agent

**Parallel research engine with editable, citation backed reports.**

[![License: MIT](https://img.shields.io/badge/License-MIT-1A3C2B?style=flat-square&labelColor=1A3C2B&color=9EFFBF)](#license)
[![Built with LangGraph](https://img.shields.io/badge/Built_with-LangGraph-1A3C2B?style=flat-square&labelColor=1A3C2B&color=FF8C69)](#architecture)
[![Open Source](https://img.shields.io/badge/Open-Source-1A3C2B?style=flat-square&labelColor=1A3C2B&color=9EFFBF)](#contributing)

<br/>

*Every tool I tried returned one output and closed the door. No refinement loop, no going back.*  
*Research is iterative. The tools weren't. So I built WORT.*

</div>

<br/>

<div align="center" style="background: linear-gradient(135deg, #1A3C2B, #2A5C42); padding: 30px; border-radius: 16px;">
  <img src="./assets/WortHomepage.png" alt="WORT Homepage" width="92%" style="border-radius: 10px; box-shadow: 0 12px 40px rgba(0,0,0,0.4);" />
</div>

<br/>

<div style="font-family: 'JetBrains Mono', monospace;">

## What is WORT

WORT is an open source AI research agent that fundamentally rethinks how we extract knowledge from the internet. Instead of relying on a single model call to produce a generic summary, WORT spawns **parallel sub agents** that independently traverse the web using a **Breadth First Search (BFS)** strategy. Each agent researches one dimension of your query while a **Reviewer agent** continuously evaluates the quality of findings, identifies gaps, and reroutes depth until the research is genuinely complete.

The output is not a wall of AI generated text. It is a **fully styled, editable HTML report** with inline citations, images, and design themes chosen dynamically to match the tone of your query. You can continue editing any section of the report with AI assistance, directly in the document viewer.

WORT was built solo over three months in New York City with a focused constraint: **extract maximum quality from the cheapest available models.** That tradeoff forced better architecture at every layer.

<br/>

---

<br/>

## Three Intelligence Modes

WORT ships with three distinct modes, each designed for a different depth of research.

<br/>

### `01` Web Search · Fast Intel

The fastest path to accurate, cited answers. Web Search is built for questions where you need real time data, not a pre trained knowledge cutoff. Every single line in the response is backed by a source, nothing is hallucinated, and relevant images and illustrations are pulled directly from search results.

<div align="center" style="background: linear-gradient(135deg, #1A3C2B, #244E38); padding: 28px; border-radius: 14px;">
  <img src="./assets/websearchchat.png" alt="Web Search in action showing cited responses" width="92%" style="border-radius: 8px; box-shadow: 0 10px 35px rgba(0,0,0,0.35);" />
</div>

<br/>

**How it works under the hood:**

The `WebSearchAgent` is an autonomous agent that chains research tools in sequence based on the user's intent. It does not follow a fixed script. The LLM reasons about which tools to invoke, in what order, and how deep to go.

```
Step 1 → Query Analysis       Analyze the user query + full chat history to produce
                                1 to 3 targeted, SEO optimized research queries

Step 2 → Web Retrieval         Execute queries across the web, returning top results
                                with content snippets + described images

Step 3 → Deep Extraction       (Optional) Pull full raw page content on the most
                                critical query for thorough source analysis

Step 4 → Response Styling      Generate tone and formatting instructions so the
                                final answer matches the "vibe" of your question

Step 5 → Cited Synthesis       Compose the final response with inline [source] labels
                                that map to verifiable URLs
```

Every response includes a **citation map** linking each source label to the exact URL it came from. Relevant images with descriptions are pulled directly from search results and embedded in the answer. The agent retains full conversation context so follow up questions feel natural and continuous.

```python
# The agent autonomously decides which tools to call and in what order.
# No hardcoded pipeline — the LLM reasons about the best strategy per query.

self._agent = create_agent(
    model=LlmsHouse.grok_model("grok-4-1-fast-reasoning", temperature=0.5),
    tools=ALL_SEARCH_TOOLS,
    system_prompt=SYSTEM_PROMPT,
    middleware=[self._build_tool_middleware()],  # Real time streaming to frontend
)
```

<br/>

---

<br/>

### `02` Deep Research · Synthesis Engine

This is the core of WORT. Deep Research is designed for questions that cannot be answered by a single search. It handles topics that require multiple perspectives, comparative analysis, and iterative depth: exam cheatsheets, investment reports, system design breakdowns, full domain explorations.

<div align="center" style="background: linear-gradient(135deg, #FF8C69, #e07a5a); padding: 28px; border-radius: 14px;">
  <img src="./assets/Deepresearch.png" alt="Deep Research report with styled HTML output" width="92%" style="border-radius: 8px; box-shadow: 0 10px 35px rgba(0,0,0,0.3);" />
</div>

<br/>

**How it works:**

When you submit a query, Deep Research moves through five distinct phases. Each phase feeds into the next, and you stay in control at every checkpoint.

<br/>

**Phase 1 — Clarification.** Before any research begins, WORT asks clarifying questions to understand your actual intent. It probes for scope, depth, and the specific angles you care about. This can loop up to three rounds, and the system only moves forward once it has a clear understanding of what you are looking for.

**Phase 2 — Planning.** Your query gets decomposed into a structured research plan: a set of independent sub queries, each targeting a different dimension of the topic. WORT remembers your past conversations and preferences, so plans are personalized. You get to **review, revise, or approve** this plan before any research starts.

<div align="center" style="background: linear-gradient(135deg, #9EFFBF, #7adfa0); padding: 24px; border-radius: 14px;">
  <img src="./assets/allocateDynamicNumberofAgents.png" alt="Dynamic allocation of parallel research agents" width="55%" style="border-radius: 8px; box-shadow: 0 8px 30px rgba(0,0,0,0.15);" />
</div>

<br/>

**Phase 3 — Parallel BFS Research.** This is where the real depth comes from. Each sub query from the plan spawns its own dedicated research agent, and all agents run simultaneously. Inside each agent, research follows a **Breadth First Search tree**. The agent starts with the question, searches the web, produces an answer, and then identifies what is still missing. Each gap becomes a new branch in the tree, which gets researched at the next level down. Sibling branches at the same depth are all explored in parallel.

```
                        ┌─────────────────────────────┐
                        │      Initial Query           │
                        │  "How do neural networks     │
                        │       learn?"                │
                        └──────────┬──────────────────┘
                                   │
                    ┌──────────────┼──────────────────┐
                    ▼              ▼                   ▼
              ┌──────────┐  ┌──────────┐        ┌──────────┐
              │  Gap 1   │  │  Gap 2   │        │  Gap 3   │
              │Backprop  │  │Gradient  │        │Loss      │
              │mechanics │  │descent   │        │functions │
              └────┬─────┘  └────┬─────┘        └────┬─────┘
                   │             │                    │
              ┌────┴────┐  ┌────┴────┐          ┌────┴────┐
              ▼         ▼  ▼         ▼          ▼         ▼
           Sub-gap   Sub-gap  Sub-gap  Sub-gap  Sub-gap  Sub-gap
```

You control how deep this tree goes through the **analysis level** you select:

| Level  | Tree Depth | Review Cycles | Best For |
|--------|-----------|---------------|----------|
| `LOW`  | 2         | 2             | Quick overviews, study guides |
| `MID`  | 2         | 3             | Balanced depth with thorough review |
| `HIGH` | 3         | 2             | Maximum depth, technical deep dives |

<br/>

<div align="center" style="background: linear-gradient(135deg, #1A3C2B, #163626); padding: 28px; border-radius: 14px;">
  <img src="./assets/parallel research.png" alt="Parallel research agents working simultaneously" width="92%" style="border-radius: 8px; box-shadow: 0 10px 35px rgba(0,0,0,0.4);" />
</div>

<br/>

**Phase 4 — Reviewer Loop.** Once the initial research is done, a Reviewer agent steps in and reads through everything that was collected. It acts like a senior analyst: it flags what is genuinely missing, what was only half explained, and what needs more depth. The Reviewer generates follow up questions, those questions get resolved through additional research, and then the Reviewer checks again. This **research → review → resolve** loop continues until the Reviewer is satisfied that no real gaps remain.

**Phase 5 — Report Writing.** The Writer takes everything and produces a **fully styled HTML report**. First it builds an outline with chapters, an abstract, introduction, and conclusion. Then a design system selects a visual theme that matches the tone of your topic (scientific papers get clean minimalist layouts, business reports get corporate styling, creative topics get bold editorial formatting). Each chapter is generated in parallel using the selected design, so the entire report looks visually consistent. After the report is generated, you can **edit any section directly** using the built in editor. Select a section, give it a rewrite instruction, and only that section gets regenerated while the rest stays untouched.

<br/>

---

<br/>

### `03` Extreme Research · The Final Sandbox

Extreme Research represents the next frontier. It spins up a **secure live Virtual Machine** to execute real code, browse the web identically like a human, and analyze deeply technical research that requires computation. It creates dynamic simulations and visualizations directly in chat and can output any file format from PDFs to presentations.

<div align="center" style="background: linear-gradient(135deg, #FF8C69, #d47758); padding: 28px; border-radius: 14px;">
  <img src="./assets/ExtermeResearchFeature.png" alt="Extreme Research with VM and code execution" width="92%" style="border-radius: 8px; box-shadow: 0 10px 35px rgba(0,0,0,0.3);" />
</div>

> **🚧 Coming Soon:** Extreme Research is actively in development. The architecture is designed and the VM integration is being built. This mode will be available in a future release.

<br/>

---

<br/>

## Architecture

The entire system is orchestrated as a **LangGraph state machine** with conditional routing, interrupt/resume support for human in the loop checkpoints, and parallel subgraph invocation.

<div align="center" style="background: #F7F7F5; padding: 20px; border: 1px solid rgba(58,58,56,0.12); border-radius: 2px;">
  <img src="./assets/architecture.svg" alt="WORT System Architecture" width="100%" />
</div>

<br/>

---

<br/>

## What You Can Actually Build With This

WORT produces real, usable output. Here are scenarios where it genuinely shines, along with example prompts you could run right now.

<br/>

**📚 Exam Prep and Study Guides**

You have a midterm in three days and six chapters to cover. Instead of reading everything, you tell WORT exactly what you need and it builds a focused cheatsheet that covers the material from multiple angles.

```
→  "Create a comprehensive cheatsheet on Backpropagation covering chain rule
    derivations, gradient flow, vanishing gradients, and practical tips for
    tuning learning rates. Include worked examples."
```

With `LOW` depth, you get a clean single pass summary. Set it to `HIGH` and it will produce the kind of granular breakdown that textbooks spread across entire chapters, complete with visual structure and section editing.

<br/>

**🎯 Interview and Presentation Prep**

You are walking into a meeting about a domain you have never touched. WORT researches the space from multiple perspectives and gives you a report you can read in 15 minutes and sound like you have been studying for weeks.

```
→  "I have a product manager interview at a fintech startup. Build me a
    deep brief on the current state of embedded finance, key players,
    regulatory challenges, and where the market is heading in 2026."
```

The editable report means you can rewrite any section until it matches your talking points perfectly.

<br/>

**📊 Business and Market Analysis**

The parallel agent architecture is naturally suited for comparative research. Each sub agent simultaneously covers a different dimension of the analysis.

```
→  "Compare Notion, Obsidian, and Coda as knowledge management platforms.
    Cover pricing, feature depth, collaboration capabilities, API ecosystem,
    and enterprise adoption. Include recent funding and market position."
```

```
→  "Analyze the electric vehicle battery supply chain. Cover lithium sourcing,
    manufacturing bottlenecks, geopolitical risks, and emerging solid state
    alternatives. Focus on investment implications for 2026."
```

<br/>

**🏗️ System Design and Technical Deep Dives**

The BFS approach naturally maps to how technical topics branch. Ask about microservices and the tree automatically expands into load balancing, service discovery, data consistency, observability, and deployment strategies.

```
→  "Explain the complete architecture of a distributed rate limiter. Cover
    token bucket vs sliding window, Redis vs in memory approaches, race
    conditions, and how companies like Stripe and Cloudflare implement theirs."
```

<br/>

**🔬 Cited, Trustworthy Research**

Every response in Web Search mode is fully cited. Deep Research reports include source URLs for every claim. Nothing is hallucinated. This is research you can actually verify and share with confidence.

```
→  "What are the latest clinical findings on GLP-1 receptor agonists for
    weight management? Include specific trial data, side effect profiles,
    and how they compare to surgical interventions."
```

<br/>

**🎨 Beautiful, Presentation Ready Reports**

WORT does not produce walls of plain text. Reports are fully styled HTML documents with design themes dynamically chosen to match your content domain. Scientific topics get clean minimalist layouts. Creative briefs get bold editorial styling. Everything is editable after generation.

```
→  "Write a comprehensive report on the history and cultural impact of
    Studio Ghibli films. Cover animation philosophy, recurring themes,
    global reception, and influence on modern animation."
```

<br/>

---

<br/>

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for the frontend)
- API keys for LLM providers (Grok/xAI, Google Gemini, DeepSeek, and optionally OpenAI/Anthropic)
- Web search API keys (see `.env.example`)
- PostgreSQL (optional, for persistent memory)

### Installation

```bash
# Clone the repository
git clone https://github.com/madhvantyagi/WORT.git
cd WORT/deep-research-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the `deep-research-agent/` directory:

```env
GROK_API_KEY=your_xai_api_key
GOOGLE_API_KEY=your_gemini_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
SEARCH_API_KEY=your_search_api_key
DATABASE_URL=postgresql://user:pass@localhost:5432/wort  # optional
```

### Running

```bash
# Start the research agent
python graphs/deep_research_agent.py "Your research query here"

# Or start the full stack with the frontend
cd ../FrontEnd/wort-ai-core
npm install
npm run dev
```

<br/>

---

<br/>

## Contributing

WORT is fully open source. The core research engine, the agent logic, the prompt architecture, everything is public, verifiable, and improvable. Built to be seen, forked, and made better by anyone who cares about research as much as I do.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

<br/>

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

<br/>

---

<div align="center">

<br/>

Built with obsession by [**Madhvan Tyagi**](https://github.com/madhvantyagi) · NYC · 2026

<br/>

*Intelligence should be transparent. WORT is.*

</div>
