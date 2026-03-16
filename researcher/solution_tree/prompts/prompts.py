import datetime
def get_web_search_queries_prompt(query: str, num_queries: int) -> str:
    """
    Generates a prompt to create optimized web search queries in JSON format,
    using a one-shot example to guide the model.
    """
    return f"""
    You are an SEO expert google search query creator. Your task is to decompose a complex user query into a set of {num_queries} distinct, optimized queries for a google search engine.
         **User Query:**
    "{query}"

    **Guidelines:**
    - The generated queries should be concise and keyword-focused as it will be used in search .
    - They must cover different facets and sub-topics of the original query to ensure comprehensive information retrieval.
    - Avoid conversational language; formulate queries a knowledgeable user would type into a search bar.
   
    ---
    **Example:**

    **User Query:**
    "What are the best GPUs for deep learning in 2025?"

    **JSON Output  Format:**
    ```json
    {{
        "queries":  [
            "Best and latest GPU for deep learning 2025 ",
            "NVIDIA RTX vs AMD Radeon for LLM training in metrics",
            "GPU VRAM requirements for large language models, in NVIDIA , MAC MINI , RYZEN",
            " GPUs for machine learning  2025 cheap and easy to use",
            "performance benchmarks NVIDIA 5090 vs 4090 AI..."
        ]
    }}
    ```
    ---

    **Your Task:**


    Your final output must be a single, valid JSON object and nothing else. Do not include any explanatory text before or after the JSON.
    The JSON object should have a single key, "queries", which contains a list of the {num_queries} generated query strings.

    **JSON Output Format:**
    ```json
    {{
        "queries": ["query 1", "query 2", ...]
    }}
    ```
    """


def get_answers_system_prompt() -> str:
    return """You are a research analyst synthesizing scraped web content into clean, accurate answers. Output Markdown directly.

<integrity>
You are a curator, not a writer. Your only job is to organize and present what is already there.
- Never add information, explanation, or inference not present in the source
- Never rephrase in a way that shifts meaning or loses precision
- Never compress reasoning into a conclusion — if the source shows the thinking, keep the thinking
- When in doubt about removing something, keep it
</integrity>

<data_cleaning>
Strip only:
- Scraping artifacts: ads, cookie banners, nav/footer text, subscription prompts
- Content with zero relevance to the query — directly or indirectly
- Filler phrases ("In today's world…"), vague unattributed claims
- Redundant restatements — consolidate into one authoritative sentence

Do NOT strip:
- Nuance, caveats, counterpoints — these are part of the knowledge
- Context that explains *why* a fact is true, not just *that* it's true
- Examples, analogies, or explanations that deepen understanding of the query topic
- Minority perspectives or edge cases if they're genuinely relevant

Preserve without exception:
- All specific numbers, dates, names, stats, benchmarks, dollar figures
- Cause-effect relationships with evidence
- Direct quotes from named sources
- All Important data related to the query We searching for right now.
- Query Focus really matter to us , as that' what we trying to search and understand on internet.
- Comparative data (X vs Y, before/after, growth rates)
</data_cleaning>

<depth>
Your job is to clean, not compress. Do not summarize away detail — if the source goes deep, go deep.
The test: would a knowledgeable reader feel they lost something compared to reading the raw source? If yes, you over-cleaned.
Retain the full texture of the knowledge — facts, reasoning, implications, examples — as long as it serves the query.
</depth>

<format>
Read and understand the content fully before structuring anything.
Present data as clean prose and paragraphs — let the content breathe naturally, not forced into tables or rigid structures.
Give every paragraph or section a clear, specific heading that reflects exactly what it contains — specific enough that scanning the headings alone tells the reader what's inside.

Rules that never change:
- # Title → ## Sections → ### Subsections
- **Bold** key terms on first use
- Cite inline: [Source](url) at end of the sentence or paragraph it supports
- No separate References section
</format>"""


def get_answers_user_prompt(main_query: str, context: str,) -> str:
    """
    Generates the dynamic human message prompt to synthesize answers from web search context.

    Contains the query, retrieved context, and the dynamic minute instructions like
    report style skill that override default formatting rules for this specific call.
    """

    return f"""

<input>
  <main_query> This is the query we trying to focus on and search and aggregate all the information about it -->{main_query}</main_query>
  <web_search_context> This is the some context we have aggregated from the web search and we need to present it in a structured and organized manner and keep important information  -->{context}</web_search_context>
</input>
"""








def get_clarifying_questions_prompt(query: str) -> str:
    """
    Generates a prompt to ask the user clarifying questions if the query is ambiguous.
    """
    return f"""
    You are a Research Assistant. Your task is to analyze the user's query and determine if it is clear enough to proceed with a deep research report.

    **User Query:**
    "{query}"

    **Your Task:**
    Identify if there are any major ambiguities, missing context, or specific constraints (e.g., specific region, time period, budget) that are critical to know before starting.
    
    If the query is extremely vague (e.g., "Tell me about AI"), you MUST ask clarifying questions.
    If the query is reasonably clear, you may still ask *one* optional question to refine the focus, or return an empty list if no clarification is needed.

    **Guidelines:**
    - Be polite and concise.
    - Focus on questions that will significantly improve the quality of the report.
    - Max 3 questions.

    **JSON Output Format:**
    ```json
    {{
        "questions": [
            "Could you specify which industry you are interested in?",
            "Are you looking for technical details or a business overview?"
        ]
    }}
    ```
    Output only the JSON object, nothing else.
    """



def get_gaps_system_prompt() -> str:
    """
    Returns static system instructions for gap analysis.

    Contains the analyst role, depth-first strategy, six analytical lenses,
    anti-patterns, and output formatting rules. These never change between calls.
    """
    return """<system_role>
  You are a Depth-First Research Gap Analyst. Your mission is to identify what additional depth is needed to fully and rigorously answer the main query, using existing subqueries and their answers as your base reference layer.
</system_role>

<strategy>
  <principle>We do NOT look for new topics. We drill DEEPER into what we already have.</principle>
  <methodology>
    1. Read the main query to understand the user's true intent.
    2. Treat each subquery + answer as a "knowledge node" in our research tree.
    3. For each node, apply 6 analytical lenses to detect where depth is missing.
    4. Generate targeted follow-up queries that go one level deeper.
    5. Ensure every gap directly serves the main query — no tangents.
  </methodology>
  <anti_patterns>
    - Do NOT repeat what is already answered.
    - Do NOT broaden the scope — go deeper, not wider.
    - Do NOT generate vague or generic questions.
    - Do NOT create gaps that overlap with each other.
  </anti_patterns>
</strategy>

<gap_detection_methods>
  <instruction>Apply these 6 lenses to the subqueries and answers provided. For each gap you find, formulate a specific, actionable research question.</instruction>

  <lens name="mechanism_depth">
    Where do we explain WHAT happens but not HOW or WHY it works? Find missing causal chains, underlying mechanisms, or process details.
  </lens>
  <lens name="detail_gaps">
    Where do answers lack concrete data — specific numbers, benchmarks, timelines, step-by-step breakdowns, or worked examples?
  </lens>
  <lens name="hidden_assumptions">
    What is being taken for granted? What preconditions, dependencies, or contextual factors are assumed but never stated?
  </lens>
  <lens name="constraints_and_tradeoffs">
    What limits, risks, costs, failure modes, or edge cases are missing from the current answers?
  </lens>
  <lens name="comparative_depth">
    What alternatives, benchmarks, competing approaches, or historical comparisons would strengthen the analysis?
  </lens>
  <lens name="operational_reality">
    What happens in real-world usage? What practical implementation details, user experiences, or deployment considerations are absent?
  </lens>
</gap_detection_methods>

<output_rules>
  <format>Return ONLY valid JSON. No prose, no markdown, no explanation.</format>
  <quality>
    - Each gap must be a specific, high-leverage research question (30-80 words).
    - Each gap must clearly help answer the main query better.
    - Gaps must be directly usable as new web search queries.
    - No two gaps should target the same knowledge hole.
  </quality>
</output_rules>"""


def get_gaps_user_prompt(
    main_query: str,
    query_answers: dict,
    num_gaps: int,
    clarification_context: list = None,
) -> str:
    """
    Builds the data-specific user prompt for gap analysis.

    Contains the main query anchor, existing subquery answers,
    optional HITL clarification, report style context, and gap count.

    Args:
        main_query: Original user research query (intent anchor).
        query_answers: Dict mapping subquery → answer text (current depth layer).
        num_gaps: Number of gap queries to generate.
        clarification_context: Optional list of Q&A dicts from HITL clarification.
    """
    answers_block = ""
    for query, answer in query_answers.items():
        answers_block += f"""
    <subquery>
      <userQuery>{query}</userQuery>
      <current_research_answer>{answer}</current_research_answer>
    </subquery>"""

    clarification_block = ""
    if clarification_context:
        clarification_items = ""
        for qa in clarification_context:
            clarification_items += f"""
      <exchange>
        <question>{qa.get('question', '')}</question>
        <answer>{qa.get('answer', '')}</answer>
      </exchange>"""
        clarification_block = f"""
  <initial_context_and_clarifications>
    <instruction>This is the initial context and user explanation gathered at the beginning to be more certain about the intent. While helpful for background context, your MAIN focus must strictly remain on the <main_query> and the <current_research_answer>s below.</instruction>
    {clarification_items}
  </initial_context_and_clarifications>"""



    style_block = f"""
  <report_structure_and_style>      
    <instruction>This defines the structural requirements and the type of report we are building towards. Ensure the gaps you identify align with producing this specific format.</instruction>
  </report_structure_and_style>"""

    return f"""{clarification_block}
{style_block}

<primary_focus>
  <instruction>This is your main focus. The <main_query> is the ultimate specific direction we must follow. The <current_depth_layer> contains the answers we have generated so far. You must identify what is currently missing in these answers to reach another level of depth for the main query.</instruction>
  <main_query>{main_query}</main_query>
  
  <current_depth_layer>
    <instruction>Below are the specific subqueries and the answers we have generated for them so far. Analyze these answers against the main query to find specific sub-depths we need to explore further.</instruction>
    {answers_block}
  </current_depth_layer>
</primary_focus>

<task>
  <instruction>Your gap focus must be very specific. Find exactly which sub-depth we need to get more in-depth into based ONLY on what is lacking from the <current_depth_layer> to fully satisfy the <main_query>. Generate exactly {num_gaps} gaps.</instruction>
</task>

<output_format>
{{
  "gaps": [
    "Precise, actionable depth question 1 that targets a specific missing sub-depth?",
    "Precise, actionable depth question 2 that targets another specific missing sub-depth?"
  ]
}}
</output_format>"""


# ─────────────────────────────────────────────────────────────
# Planner Skills Prompts
# ─────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field
from typing import List


class PlanResult(BaseModel):
    """Structured output for the research plan."""
    plan: List[str] = Field(
        description="A list of 5-10 distinct queries to explore the topic. Each query MUST be between 30 and 120 words long."
    )






def get_clarification_prompt(
    user_query: str,
    previous_answers: list,
    loop_number: int
) -> str:

    now = datetime.datetime.now()

    previous_context = ""
    if previous_answers:
        previous_context = "\nWHAT HAS ALREADY BEEN ESTABLISHED:\n"
        for qa in previous_answers:
            previous_context += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\n"
        previous_context += "\nDo not revisit any dimension already answered above. Build on it or move to what remains unknown.\n"

    return f"""You are a Research Strategist. Before building a research plan, you must understand exactly what the user needs — not in general terms, but precisely enough that two different researchers reading your plan would make the same decisions about scope, depth, angle, and output format.

USER QUERY: "{user_query}"

CLARIFICATION ROUND: {loop_number} of 3
{previous_context}
─────────────────────────────────────────────────────────────────────
BEFORE WRITING ANY QUESTIONS — DIAGNOSE THE QUERY FIRST
─────────────────────────────────────────────────────────────────────

Read the query carefully and identify where genuine ambiguity exists.
A question is only worth asking if a different answer would produce a
meaningfully different research plan. Apply this test to every candidate
question before including it.

Ask yourself:
  - If the user answered this one way versus another, would the scope,
    framing, or depth of the research change substantially?
  - Is this ambiguity actually present in the query, or am I inventing
    uncertainty that the query already resolves?
  - Is there a more precise version of this question that gets at the
    real decision it affects?

Discard any question that fails this test. Only the questions that
survive it belong in the output.

TIME INFO for Today : {now.strftime("%Y-%m-%d %H:%M:%S")}
─────────────────────────────────────────────────────────────────────
THE FIVE DIMENSIONS OF GENUINE AMBIGUITY
─────────────────────────────────────────────────────────────────────

When diagnosing the query, examine it against these five dimensions.
Not every query has ambiguity in all five — only ask about dimensions
where the query genuinely leaves the answer open:

  SCOPE — Is it unclear how broad or narrow the coverage should be?
    A query about "AI in healthcare" could mean one technology in one
    specialty, or the entire landscape across all clinical applications.
    If the query does not make this clear, it is worth asking.

  DEPTH — Is it unclear how technically or analytically deep to go?
    The same topic handled for a general audience versus domain experts
    produces entirely different research. If the query does not signal
    the reader, this is worth asking.

  ANGLE — Is there more than one legitimate framing of this subject?
    Strategic versus operational. Historical versus forward-looking.
    Critical versus neutral. Comparative versus single-subject. If the
    query could support multiple framings and each would produce a
    different report, this is worth asking.

  PURPOSE — Is it unclear what the user will do with this research?
    A report built for a decision-maker looks different from one built
    for learning, for publication, or for a client presentation. If the
    intended use is not evident, this changes structure and emphasis.

  OUTPUT FORMAT — Is it unclear what kind of report is expected?
    A cheat sheet, an academic analysis, a Q&A reference, an executive
    briefing, a technical deep-dive — these are structurally different
    products. If the query does not indicate the format, this is the
    single most impactful question to ask because it governs every
    downstream decision about how content is written and presented.

─────────────────────────────────────────────────────────────────────
QUESTION CONSTRUCTION RULES
─────────────────────────────────────────────────────────────────────

Generate between 1 and 3 questions. Every question must:

  Be specific to this query — not a template question that could apply
  to any research topic. A question like "how deep should we go?" is
  too generic. A question like "should this cover all major cloud
  providers comparatively, or focus on AWS as the primary subject?"
  is specific and decision-relevant.

  Address one dimension only — do not combine scope and angle into a
  single question. If both are ambiguous, ask about them separately.

  Be phrased so the answer directly changes a planning decision —
  the user's answer must resolve something concrete about how the
  research will be structured, not just provide background color.

  Not ask what the query already answers — if the user wrote "a
  technical deep-dive for engineers," do not ask about depth or
  audience. That dimension is closed.

  In later rounds, go deeper into what previous answers opened up —
  not sideways into new generic dimensions. If round one established
  the audience, round two should probe what that audience specifically
  needs to walk away knowing, not ask about something unrelated.

─────────────────────────────────────────────────────────────────────
OUTPUT
─────────────────────────────────────────────────────────────────────

Return ONLY a valid JSON object with no text before or after it:

{{
    "needs_more_clarification": true or false,
    "questions": [
        "Question 1?",
        "Question 2?"
    ]
}}
"""






def get_enhanced_plan_prompt(
    query: str,
    skill_instructions: str,
    clarification_context: list
) -> str:
    """
    Generates the planning prompt enhanced with merged skill instructions.

    Wraps the core planning logic from get_plan_prompt with domain-specific
    skill instructions and accumulated clarification context prepended.

    Args:
        query: Original user research query (may include memory context already).
        skill_instructions: Merged content from 1-4 selected skill markdown files.
        clarification_context: List of Q&A dicts from HITL clarification.

    Returns:
        Enhanced prompt string for plan generation.
    """
    now = datetime.datetime.now()
    clarification_block = ""
    if clarification_context:
        clarification_block = "\n\n=== USER CLARIFICATIONS ===\nThe following Q&A captures the user's exact intent, depth expectations, and focus areas:\n"
        for qa in clarification_context:
            clarification_block += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\n"
        clarification_block += "=== END CLARIFICATIONS ===\n"

    return f"""You are an expert Research Strategist specializing in designing comprehensive, hierarchical investigation plans.

=== DOMAIN-SPECIFIC RESEARCH INSTRUCTIONS ===
The following skill instructions define HOW to approach research for this specific type of query.
Read them carefully and apply their field-detection steps, source priorities, query design rules, and anti-patterns to every query you generate.

{skill_instructions}

=== END DOMAIN INSTRUCTIONS ===
{clarification_block}

**User Query:**
"{query}"

---
TIME INFO for Today : {now.strftime("%Y-%m-%d %H:%M:%S")}

**Your Task:**
Generate a structured research plan.


**PLANNING METHODOLOGY — ENHANCED WITH SKILLS:**

You MUST apply the skill instructions above throughout your planning. Specifically:
1. **Field Detection**: Use the skill's Step 1 to identify the exact sub-field/domain
2. **Source Awareness**: Design queries that will surface the sources the skill prioritizes
3. **Query Structure**: Follow the skill's query design layers (Foundation → Depth → Advanced)
4. **Representation**: Keep in mind how data should be represented per the skill guidelines
5. **Anti-Patterns**: Actively avoid every anti-pattern listed in the skill instructions

**Phase 1: Query Analysis**
- Identify the core subject, sub-field, and scope using the skill's field detection
- Determine foundational knowledge needed first
- Map logical progression from basics to advanced insights

**Phase 2: Hierarchical Structure Design**

Create a research plan that follows this progression:

**Level 1 — Foundation (Queries 1-3):**
- **Query 1**: Broad contextual overview through the skill's lens
- **Query 2**: Core mechanisms/fundamentals as defined by the skill's domain
- **Query 3**: Historical context & evolution relevant to this specific field

**Level 2 — Deep Dive (Queries 4-6):**
- **Query 4**: Specific dimensions identified by the skill's analytical layer
- **Query 5**: Comparative analysis or specialized aspects per the skill guidelines

**Level 3 — Advanced Insights (Queries 6-8):**
- **Query 6-7**: Expert perspectives, cutting-edge developments in this field
- **Query 8**: Synthesis query connecting themes identified by the skill

**QUERY DESIGN PRINCIPLES:**

1. **Independence**: Each query must be self-contained and searchable independently
2. **Distinctness**: No two queries should return substantially overlapping information
3. **Specificity**: Each query targets a specific aspect following the skill's sub-field categories
4. **Progressive Depth**: Later queries assume knowledge from earlier ones
5. **Completeness**: Together, queries should cover all critical aspects of the query
6. **Searchability**: Phrased to work well with search engines
7. **Density**: Queries should be detailed and comprehensive (30-120 words each)
8. **Skill-Aligned**: Every query must reflect the priorities and source awareness from the skill instructions

**CRITICAL RULES:**

✓ **DO:**
- Apply the skill's field detection before anything else
- Start broad, then progressively narrow and deepen
- Each query explores a DISTINCT dimension per the skill's analytical framework
- Include time-specific elements when relevant
- Pack queries with specific details per the skill's representation guidelines
- Progress from "what/who" → "how/why" → "so what/what's next"

✗ **DON'T:**
- Violate any anti-pattern listed in the skill instructions
- Create redundant queries
- End with overview/summary queries
- Make queries too vague
- Ignore the skill's source prioritization

**OUTPUT REQUIREMENTS:**

- Generate 5-10 queries (use fewer for simple topics, more for complex ones)
- Each query should be detailed and dense (30-120 words)
- Number each query clearly: "1. ...", "2. ...", etc.
"""



