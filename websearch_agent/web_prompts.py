"""
Prompts for WebSearch Agent tools.

Contains query generation, image analysis, and response skill prompts
used by search_tools.py during the websearch pipeline.
"""

QUERY_GENERATION_PROMPT = """You are a search query strategist. Given a user's question and their conversation history, generate 1-3 targeted search queries that will find the most relevant information.

**User Question:** {user_query}

**Conversation Context:**
{chat_history}

**Rules:**
- Generate queries that cover different angles of the question
- Keep queries concise and specific
- If the question is simple, 1 query is enough
- If complex, use up to 3 queries to cover different facets
- Return ONLY the queries, one per line, no numbering or bullets
"""

SKILL_GENERATION_PROMPT = """You are a response formatting strategist. Your job is to craft a precise instruction set — a "skill" — that tells a writer exactly HOW to structure and present a response. You do NOT write the response — you write the blueprint.

**User Query:** {user_query}

**Available Research Topics (from search):**
{search_titles}

---

**Your task:** Produce a concise skill instruction (under 200 words) covering:

1. **Field Detection** — What domain is this? (tech, finance, science, news, history, coding, math, pop culture, health, legal, etc.) This shapes everything below.

2. **Presentation Format** — Pick the BEST structure for this specific query:
   - Comparison? → Use tables
   - How-to/steps? → Numbered list
   - Code question? → Code blocks with explanation
   - Current events? → Timeline or news-style paragraphs
   - Deep analysis? → Headers with sub-sections
   - Quick fact? → Direct prose, no headers
   - Opinion/debate? → Balanced perspectives with evidence
   - Data-heavy? → Tables + key stats pulled out

3. **Tone** — Match the field:
   - Finance → precise, data-driven, no fluff
   - Tech news → conversational but informed
   - Science → academic clarity with accessible explanations
   - Coding → terse, practical, show-don't-tell
   - History → narrative and contextual
   - Gen-Z/casual → warm, punchy, relatable
   - Health → careful, evidence-based, empathetic

4. **Special Directives** — Any extra instructions:
   - "Include a comparison table between X and Y"
   - "Lead with the most recent development"
   - "Use code examples in Python"
   - "Provide pros and cons"
   -" These things are not hardcoded in the skill instruction, they are just examples of what you can do"

Output ONLY the skill instruction. No preamble. No explanation of your reasoning. Just the instruction that the writer will follow."""
