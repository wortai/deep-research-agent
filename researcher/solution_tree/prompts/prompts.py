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

def get_vector_search_queries_prompt(query: str, num_queries: int) -> str:
    """
    Generates a prompt to create queries for a vector store search in JSON format,
    using a one-shot example to guide the model.
    """
    return f"""
    You are an AI assistant specializing in semantic retrieval for a vector database. Your task is to rephrase a user's query into {num_queries} distinct questions or declarative statements that are optimized for vector similarity search.

    **Guidelines:**
    - The generated queries should capture the underlying intent and concepts of the original query.
    - They should be phrased as if you are searching for text chunks that would directly answer or contain that specific information.
    - Focus on concepts and full sentences rather than just keywords.

    ---
    **Example:**

    **User Query:**
    "Tell me about Reinforcement Learning from Human Feedback (RLHF) and how it's used to align large language models."

    **JSON Output Format:**
    ```json
    {{
        "queries": [
            "What is Reinforcement Learning from Human Feedback (RLHF)?",
            "How does the reward model in RLHF work?",
            "What are the steps involved in the RLHF training process?",
            "How is RLHF used to improve the safety and alignment of LLMs?",
            "What are the limitations or challenges of using RLHF?"
        ]
    }}
    ```
    ---

    **Your Task:**

    **User Query:**
    "{query}"

    Your final output must be a single, valid JSON object and nothing else. Do not include any explanatory text before or after the JSON.
    The JSON object should have a single key, "queries", which contains a list of the {num_queries} generated query strings.

    **JSON Output Format:**
    ```json
    {{
        "queries": ["What is the process for X?", "Explain the relationship between Y and Z.", ...]
    }}
    ```
    """

def get_answers_prompt(main_query: str, context: str, report_style_skill: str = "") -> str:
    """Generates a prompt to synthesize answers from web search context with adaptive formatting and inline citations.
    
    Args:
        main_query: The research question to answer.
        context: Combined web search results with source URLs.
        report_style_skill: Optional LLM-generated style directive for report formatting.
    """
    style_block = ""
    if report_style_skill:
        style_block = f"""

=== REPORT STYLE DIRECTIVE (HIGHEST PRIORITY) ===
The following style directive was generated from the user's preferences and must be followed for ALL formatting decisions. It OVERRIDES the default formatting guidelines below whenever they conflict.
But keep the structure of the Hiearchy of the report as it is
{report_style_skill}

=== END STYLE DIRECTIVE ===
"""
    return f"""You are an expert research analyst specializing in presenting information clearly and effectively. Your task is to synthesize a comprehensive, well-structured answer from the provided context.
{style_block}

**Main Query:**
{main_query}

**Context from Web Search (with sources):**
{context}

---

**Your Task:**

Write a comprehensive answer in **Markdown format** directly. DO NOT wrap your answer in JSON.

---

**FORMATTING GUIDELINES:**

**Analyze the query and context first** to determine the optimal presentation format:

- **Comparative queries** (e.g., "X vs Y", "differences between"): Use comparison tables or side-by-side analysis
- **Step-by-step processes** (e.g., "how to", "steps to"): Use numbered lists with detailed explanations
- **Multiple items/options** (e.g., "top 10", "best practices"): Use bullet points with subsections
- **Quantitative data** (e.g., statistics, metrics, pricing): Use tables or structured data presentations
- **Definitions/explanations**: Use clear headings with paragraphs and subparagraphs
- **Historical/chronological**: Use timeline format or chronologically ordered sections
- **Mixed content**: Combine multiple formats as appropriate




- ** Just Numbered data like creating a Question If User trying to create a Question sheet to Practiced**


- ** CLEANING OF UNECESSARY DATA **
- We need to ignore the data that's not necessary and only adds repetition and noise.
- Don't add too much new information that's not present in the context.
- Your focus should be Precision and Accuracy and Completeness of the answer in Answering not in the length of the answer.
- Our Answers Should be based on what Part/angle/perspective of the Main query  our Context from websearch trying to ask is trying to answer
- Quality Over Quantity
- It doesn't has to answer the whole main query at all , just answer the specific part of main query is trying to focus well


**Structure Requirements:**

1. **Main Heading (H1)**: Start with a clear, relevant title using `# Title`

2. **Body Content**: Organized into logical sections with:
   - `## Section Headings` for major topics
   - `### Subsection Headings` for subtopics
   - Tables (use Markdown table syntax) for comparative data
   - Bullet points (`-` or `*`) for lists
   - Numbered lists (`1.`, `2.`) for sequential steps
   - **Bold** for emphasis on key terms
   - *Italic* for secondary emphasis
3 **Inline Citations**: After each statement/paragraph that uses information from a source, add the 🔗 emoji as a hyperlink to the source URL: `[🔗](https://example.com)`


**Citation Rules:**

- Format: `[source name](URL)` - the emoji itself becomes the clickable link
- Place citations at the end of the sentence or paragraph they support
- If multiple sources support a paragraph, include multiple citation links: `[🔗](URL1) [🔗](URL2)`
- DO NOT create a separate "Sources" section at the end


**Quality Standards:**

- **Accuracy**: Keep all numbers, dates, names, and facts exactly as stated in the context
- **Comprehensiveness**: Cover all relevant aspects of the query found in the context and in depth 
- **Clarity**: Use clear, concise language; avoid jargon unless necessary
- **Completeness**: Ensure the answer can stand alone without needing additional context
- **Relevance**: Focus strictly on answering the main query but only from the context provided




** CONTEXT RULE **
- Strictly Don't Try to Summarize the Context , Instead Try to get in the depth 
- Don't Loose the Details of the context 
- Don't make it shorter or way longer than the context 
- Don't Try to give short summary answer of the query , instead try to get in the depth 
- Don't Make answer vague , it has to be clear and getting in depths to explain


**Example Output Format:**
# Understanding Machine Learning Basics

Machine learning is a subset of artificial intelligence that enables systems to learn from data. [🔗](https://example.com/ml-intro)

## Types of Machine Learning

### Supervised Learning

Supervised learning uses labeled datasets to train algorithms. Common applications include classification and regression tasks. [🔗](https://example.com/supervised)

### Unsupervised Learning

This approach finds hidden patterns in unlabeled data. [🔗](https://example.com/unsupervised)

## Comparison of Approaches

| Feature | Supervised | Unsupervised |
|---------|-----------|--------------|
| Data Type | Labeled | Unlabeled |
| Use Case | Prediction | Pattern Discovery |
| Complexity | Lower | Higher |

[Machine Learning](https://example.com/comparison)

## Key Takeaways

- Machine learning automates decision-making processes [Machine Learning-deeplearning](https://example.com/benefits)
- Different approaches suit different problem types [GeeksforGeeks](https://example.com/selection)
- Training data quality is critical for success [Towards Data Science ](https://example.com/data-quality)
"""
def get_plan_prompt(query: str) -> str:
    """
    Generates a prompt to create a comprehensive, hierarchical research plan with progressive depth.
    """
    return f"""You are an expert Research Strategist specializing in designing comprehensive, hierarchical investigation plans. Your goal is to create a structured research blueprint that builds knowledge progressively.

**User Query:**
"{query}"

---

**Your Task:**
Generate a structured research plan.

**PLANNING METHODOLOGY:**

**Phase 1: Query Analysis**
- Identify the core subject and scope
- Determine what foundational knowledge is needed first
- Map out the logical progression from basics to advanced insights
- Identify distinct aspects that need separate investigation

**Phase 2: Hierarchical Structure Design**

Create a research plan that follows this progression:

**Level 1 - Foundation (Queries 1-3):**
- **Query 1**: Broad contextual overview - What is the subject? Why does it matter? Current landscape
- **Query 2**: Core mechanisms/fundamentals - How does it work? Key components? Basic principles
- **Query 3**: Historical context & evolution - Background, trajectory, major milestones

**Level 2 - Deep Dive (Queries 4-6):**
- **Query 4**: Specific dimensions of the topic (e.g., financial performance, technical capabilities, market position)
- **Query 5**: Comparative analysis, challenges, opportunities, or specialized aspects

**Level 3 - Advanced Insights (Queries 6-8):**
- **Query 6-7**: Expert perspectives, emerging trends, future implications
- **Query 8**: Synthesis query - connecting themes, implications, or forward-looking analysis

**QUERY DESIGN PRINCIPLES:**

1. **Independence**: Each query must be self-contained and searchable independently
2. **Distinctness**: No two queries should return substantially overlapping information
3. **Specificity**: Each query targets a specific aspect, angle, or dimension
4. **Progressive Depth**: Later queries assume knowledge from earlier ones and go deeper
5. **Completeness**: Together, queries should cover all critical aspects of the user's question
6. **Searchability**: Phrased to work well with search engines (clear keywords, proper scope)
7. **Density**: Queries should be detailed and comprehensive, utilizing the full word limit to capture nuanced aspects

**CRITICAL RULES:**

✓ **DO:**
- Start broad, then progressively narrow and deepen
- Each query explores a DISTINCT dimension (financial vs technical vs market vs competitive, etc.)
- Make queries specific enough to avoid generic results
- Include time-specific elements when relevant (e.g., "2025", "recent", "latest")
- Cover both quantitative data and qualitative insights
- Progress from "what/who" → "how/why" → "so what/what's next"
- Pack queries with specific details, metrics, and dimensions to investigate
- Include multiple related sub-aspects within each query to maximize information density

✗ **DON'T:**
- Create redundant queries that would return similar information
- End with overview/summary queries (end with depth instead)
- Make queries too vague ("tell me about X")
- Ignore important dimensions mentioned in the user query
- Create linear queries that just repeat the same question differently
- Waste the word limit with generic phrases

**QUERY FORMULATION GUIDELINES:**

- **Length**: Each query should be 30-120 words (dense, detailed, and comprehensive)
- **Format**: Natural search phrases with multiple dimensions and specific angles
- **Keywords**: Include specific terms, metrics, time periods, and dimensions that will yield targeted results
- **Scope**: Include multiple related sub-questions within each query to maximize coverage
- **Density**: Pack each query with specific aspects to investigate - don't be minimalist

**EXAMPLE STRUCTURE** (for "What is NVIDIA's performance in 2025?"):
```json
{{
    "plan": [
        "1. NVIDIA comprehensive business overview 2025 including complete breakdown of revenue streams from data center GPUs, gaming graphics cards, professional visualization, automotive and embedded systems, along with current market capitalization, total employee count, geographic revenue distribution, major product lines like H100 and B100 AI accelerators, and overall company positioning in semiconductor industry",
        
        "2. GPU architecture and AI chip technology use by NVIDIA deep dive covering Hopper and Blackwell architecture specifications, tensor core capabilities, memory bandwidth and capacity, CUDA core counts, power efficiency metrics, manufacturing process nodes from TSMC, technological advantages over competitors in AI training and inference workloads, and specific performance benchmarks",
        
        "3. NVIDIA historical financial evolution from graphics card company origins through cryptocurrency mining boom impact, acquisition of Mellanox Technologies, ARM acquisition attempt and regulatory rejection, transformation into AI chip leader, stock splits history, and major strategic pivots that shaped current 2025 business model",
        
        "4. Quarterly earnings analysis of NVIDIA Q4 2024 and Q1 2025 including detailed revenue figures by business segment, gross profit margins, operating expenses, net income, earnings per share, year-over-year growth rates, guidance for upcoming quarters, analyst estimates versus actual performance, and management commentary on results",
        
        "5. Data center business performance metrics of NVIDIA in 2025 covering AI accelerator sales volume, cloud service provider partnerships with AWS Microsoft Azure Google Cloud, enterprise AI deployment trends, market share in AI training versus inference chips, average selling prices, supply constraints or capacity expansions, and major customer wins or losses",
        
        "6.  Stock market performance 2025 including share price movement year-to-date, 52-week highs and lows, price-to-earnings ratio, institutional investor holdings changes, analyst price targets and rating upgrades or downgrades, trading volume patterns, inclusion in major indices, and investor sentiment indicators from earnings calls",
        
        "7. NVIDIA competitive landscape analysis versus AMD MI300 series, Intel Gaudi accelerators, custom AI chips from Google TPU Amazon Trainium Microsoft Maia, comparing performance benchmarks, market share data, pricing strategies, customer preference trends, software ecosystem advantages CUDA versus ROCm, and partnership announcements that affect competitive positioning",
        
        "8.  Supply chain (NVIDIA) analysis 2025 including TSMC manufacturing capacity allocation, CoWoS advanced packaging constraints, HBM memory supply from SK Hynix and Samsung, geopolitical risks from Taiwan tensions, US export restrictions on China sales impact, alternative supplier development, and supply-demand balance affecting ability to fulfill orders",
        
        "9. NVIDIA future growth trajectory and AI industry outlook covering projections for data center GPU market expansion through 2027, emerging applications in autonomous vehicles robotics, next-generation architecture roadmap beyond Blackwell, potential new market entries, analyst long-term revenue and earnings growth estimates, and secular AI adoption trends",
        
        "10. Eegulatory challenges and strategic risks NVIDIA might face including antitrust scrutiny from regulators worldwide, customer concentration risk with major cloud providers, potential for customers developing in-house alternatives, geopolitical export control impacts, IP litigation concerns, and market saturation risks as AI infrastructure buildout matures"
    ]
}}
```

**ADAPTATION GUIDELINES:**

Adjust your plan based on query type:

- **Company/Performance queries**: Foundation → Financials → Market Position → Competition → Future Outlook
- **Technical topics**: Definition → Core Concepts → Applications → Advanced Techniques → Future Trends
- **Comparative queries**: Individual overviews → Direct comparisons → Use cases → Expert opinions
- **How-to queries**: Basics → Step-by-step → Advanced techniques → Common issues → Best practices
- **Market/Industry queries**: Overview → Key players → Trends → Challenges → Predictions

**OUTPUT REQUIREMENTS:**

- Generate 5-10 queries (use fewer for simple topics, more for complex ones)
- Each query should be detailed and dense (15-120 words max )shouldn't go upto 120 if not necessary, covering multiple related dimensions
- Output **ONLY** the JSON object - no explanations, no markdown fences
- Number each query clearly: "1. ...", "2. ...", etc.
- Ensure proper JSON formatting (escaped quotes if needed)

**QUALITY CHECKLIST:**

Before finalizing, verify:
- [ ] Does each query target a DISTINCT aspect with multiple dimensions?
- [ ] Does the plan progress from foundational to advanced?
- [ ] Are queries dense and detailed, utilizing the word limit effectively?
- [ ] Would these queries, collectively, fully answer the user's question?
- [ ] Are queries specific enough to avoid generic web results?
- [ ] Is there no significant redundancy between queries?
- [ ] Does the final query provide depth, not just summary?
- [ ] Does each query pack in multiple related sub-aspects to maximize information gathering?

Output only the JSON object.
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



def get_gaps_prompt(main_query: str, query_answers: dict, num_gaps: int, clarification_context: list = None, report_style_skill: str = "") -> str:
    """
    Generates a depth-focused research gap prompt.
    Main query = user intent anchor.
    Subqueries + answers = current depth state.
    Output = next-level depth probes.
    Incorporates user clarification to find style-aware and intent-aligned gaps.

    Args:
        main_query: Original user research query.
        query_answers: Dict mapping subquery → answer text.
        num_gaps: Number of gaps to generate.
        clarification_context: Optional list of Q&A dicts from HITL clarification.
        report_style_skill: Optional style directive for format-aware gap detection.
    """

    answers_str = ""
    for query, answer in query_answers.items():
        answers_str += f'### Subquery: "{query}"\nCurrent Answer:\n{answer}\n\n'

    clarification_block = ""
    if clarification_context:
        clarification_block = "\n### 🗣️ User Clarifications (from HITL)\nThe user provided the following additional context about their intent:\n"
        for qa in clarification_context:
            clarification_block += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\n"
        clarification_block += "\nUse these clarifications to find gaps that align with what the user ACTUALLY wants.\n"

    style_block = ""
    if report_style_skill:
        style_block = f"\n### 📐 Report Style Context\nThe final report will be formatted as:\n{report_style_skill[:300]}\n\nConsider what gaps are relevant for THIS type of output.\n"

    return f"""
You are a **Depth-First Research Analyst Agent**.

Your mission is to determine what *additional depth* is needed to fully and rigorously answer the **Main Query**, using the **Subqueries and their Answers as your base reference layer**.

---
{clarification_block}
{style_block}
### 🧭 Anchors

**Main Query (User Intent Anchor):**  
{main_query}

**Current Depth Layer (What We Already Know):**  
{answers_str}

---

### 🎯 Your Objective

Generate exactly **{num_gaps}** research gaps that:

• Stay aligned with the *Main Query*  
• Go *deeper into the subqueries and their answers*  
• Uncover missing mechanisms, assumptions, limits, or technical details  
• Lead to stronger, more complete understanding of the topic  
• Can be directly used as new search queries

---

### 🔎 How to Go Deeper

Use the subqueries + answers as your base and ask:

1. **Mechanism Depth** – Where do we explain *what*, but not *how / why*?
2. **Detail Gaps** – What parts lack concrete data, steps, or examples?
3. **Hidden Assumptions** – What is being taken for granted?
4. **Constraints & Tradeoffs** – What limits, risks, or costs are missing?
5. **Comparative Depth** – What alternatives or benchmarks are missing?
6. **Operational Reality** – What happens in real-world usage?

---

### 🧱 Output Rules

• Return ONLY valid JSON  
• No prose, no markdown  
• Each gap must be a **specific, high-leverage research question**  
• Do NOT repeat what is already answered  
• Each gap must clearly help answer the *Main Query better*

---

### 📦 JSON Output Format

{{
  "gaps": [
    "Precise, actionable depth question 1?",
    "Precise, actionable depth question 2?",
    ...
  ]
}}
"""


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


class SkillSelectionResult(BaseModel):
    """Structured output for selecting 1-4 research skills."""
    selected_skills: List[str] = Field(
        description="List of 1 to 4 skill filenames (e.g. ['coding_tech.md', 'general_academic.md']). Must be exact filenames from the provided available skills list."
    )
    reasoning: str = Field(
        description="Brief explanation of why these specific skills were selected and how they complement each other for this query."
    )


def get_clarification_prompt(
    user_query: str,
    previous_answers: list,
    loop_number: int
) -> str:
    """
    Generates a prompt for the HITL clarification step.

    Produces exactly 1-3 genuine, mindset-probing questions that try to understand
    the user's research angle, depth expectations, and focus areas.
    Avoids repeating questions already answered.

    Args:
        user_query: Original user research query.
        previous_answers: List of dicts with 'question' and 'answer' keys
                          from earlier clarification rounds.
        loop_number: Current clarification round (1-3).

    Returns:
        Prompt string for the LLM.
    """
    previous_context = ""
    if previous_answers:
        previous_context = "\n\nPREVIOUS CLARIFICATION (do NOT repeat these questions):\n"
        for qa in previous_answers:
            previous_context += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\n\n"

    return f"""You are a Research Strategist preparing to build a comprehensive research plan. Before planning, you need to deeply understand the user's intent.

USER QUERY: "{user_query}"

CLARIFICATION ROUND: {loop_number} of 3
{previous_context}
YOUR TASK:
Generate exactly 1 to 3 genuine questions that will help you understand:

1. **Research Angle** — Which perspective or lens does the user want? (theoretical vs. practical, academic vs. industry, historical vs. contemporary)
2. **Depth Expectations** — How deep should the research go? (surface overview, intermediate understanding, expert-level deep dive)
3. **Focus Area** — Which specific aspects of the topic matter most? (if the topic has multiple facets, which one to prioritize)
4. **Clarity on Ambiguities** — Any part of the query that could be interpreted multiple ways
5. **Style** — How should we present the report? (academic, Q&A, cheat sheet style, difficulty level, etc.)

QUESTION QUALITY RULES:
- IMPORTANT: You MUST generate at least 1 question. NEVER assume the query is perfectly clear, especially regarding the 'Style' of the final report.
- Limit to maximum 3 questions.
- Questions must be SPECIFIC to this query, not generic filler.
- Questions should uncover the user's MINDSET and research goals.
- If previous answers already covered an area, go DEEPER into unexplored angles.
- Each question should genuinely change how you would plan the research.
- Do NOT ask obvious questions the query already answers.

OUTPUT RULES:
Return ONLY a valid JSON object:
{{
    "needs_more_clarification": true,
    "questions": [
        "Question 1?",
        "Question 2?"
    ]
}}
"""


def get_skill_selection_prompt(
    user_query: str,
    clarification_context: list,
    available_skills: dict
) -> str:
    """
    Generates a prompt to select 1-4 research skills based on query analysis.

    The LLM analyzes the user query and clarification answers to determine
    which domain-specific skills should be merged for optimal research planning.

    Args:
        user_query: Original user research query.
        clarification_context: List of Q&A dicts from HITL clarification.
        available_skills: Dict mapping filename to file content preview.

    Returns:
        Prompt string for the LLM (used with structured output SkillSelectionResult).
    """
    clarification_text = ""
    if clarification_context:
        clarification_text = "\nCLARIFICATION CONTEXT (user's answers about their intent):\n"
        for qa in clarification_context:
            clarification_text += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\n"

    # Concise identity map so the LLM understands each skill's purpose
    skill_identities = {
        "general_academic.md": "Scholarly research — peer-reviewed papers, university-level depth, textbook rigor. "
            "Detects academic discipline & sub-field (CS, Biology, Economics…). Prioritizes journals, surveys, conference proceedings. "
            "Builds queries from definitions → methodology → state of the art → critical analysis.",
        "general_student_practice.md": "Practice sheets, cheat sheets, flashcards, exam & interview prep. "
            "Detects format (cheat sheet vs problem set vs exam sim), field, and difficulty level. "
            "Structures by topic → difficulty progression → worked solutions with answer keys.",
        "philosophy.md": "Philosophical inquiry — ethics, metaphysics, epistemology, political philosophy, aesthetics. "
            "Identifies branch (ethics, logic, existentialism…) and key thinkers (Kant, Nietzsche, Rawls…). "
            "Uses dialectical structure: thesis → arguments → objections → replies. Demands primary source citations.",
        "finance_corporate.md": "Finance & markets — equity research, macro economics, corporate analysis, personal finance. "
            "Detects financial domain (equity, fixed income, macro, crypto…). Prioritizes SEC filings, Bloomberg data, analyst reports. "
            "Builds queries targeting specific metrics, valuations, and risk analysis.",
        "news_journalism.md": "Current events & breaking news — recency-first, multi-source fact-checking. "
            "Detects news category (breaking, analysis, political, industry). Requires wire services (AP, Reuters) and tier-1 outlets. "
            "Timestamps all events, attributes every claim to sources, flags conflicting reports.",
        "history.md": "Historical research — primary sources, chronological analysis, historiographical debate. "
            "Detects time period (Ancient → Contemporary) and geographic region. Distinguishes primary vs secondary sources. "
            "Examines causes, perspectives, legacy, and revisionist interpretations.",
        "coding_tech.md": "Programming & technology — code, frameworks, system design, debugging, documentation. "
            "Detects language, framework, and problem type (learning, implementation, debugging, architecture). "
            "Requires version-specific official docs, complete runnable code examples, and error handling.",
        "physics.md": "Physics — classical mechanics to quantum field theory, experimental & theoretical. "
            "Detects sub-field (QM, EM, thermodynamics, astrophysics…). Demands mathematical rigor with proper notation and SI units. "
            "Covers governing laws, derivations, experimental verification, and open problems.",
        "math.md": "Mathematics — pure & applied, proofs, formulas, equations, notation-aware. "
            "Detects exact field (algebra, analysis, topology, number theory, probability, differential equations…). "
            "Requires precise definitions, step-by-step proofs, all variables defined, and conditions stated. "
            "Identifies sub-topic before generating any query.",
    }

    skills_list = "\nAVAILABLE RESEARCH SKILLS:\n"
    for filename in available_skills:
        identity = skill_identities.get(filename, available_skills[filename][:200])
        skills_list += f"\n**{filename}**: {identity}\n"

    return f"""You are a Research Skills Router. Your task is to analyze the user's research query and select the BEST combination of domain-specific research skills.

USER QUERY: "{user_query}"
{clarification_text}
{skills_list}

YOUR TASK:
Select between 1 and 4 skills that, when combined, will produce the most effective research plan for this query.

SELECTION LOGIC:
- Select the PRIMARY skill that matches the core domain of the query
- Add SECONDARY skills if the query spans multiple domains
- Consider skill combinations that complement each other:
  • "Learn leetcode problems" → coding_tech.md + general_academic.md
  • "SQL cheat sheet" → coding_tech.md + general_student_practice.md
  • "Latest Tesla stock analysis" → finance_corporate.md + news_journalism.md
  • "History of quantum mechanics" → physics.md + history.md
  • "Nietzsche's influence on modern ethics" → philosophy.md + history.md
  • "Practice calculus problems" → math.md + general_student_practice.md

RULES:
- Minimum 1 skill, maximum 4 skills
- Selected skills must be exact filenames from the available list
- If the query clearly belongs to one domain, selecting just 1 skill is correct
- Only add additional skills if they genuinely add a distinct research dimension
- The reasoning should explain how the skills work together
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


def get_report_style_prompt(
    user_query: str,
    clarification_answers: list,
    selected_skill_names: list
) -> str:
    """
    Generates a prompt that produces a report style directive.

    The LLM analyzes user intent (from clarification answers), query nature,
    and selected research skills to generate a concise presentation contract
    that dictates how every section, chapter, and visual element should look.

    Args:
        user_query: Original user research query.
        clarification_answers: List of Q&A dicts from HITL clarification.
        selected_skill_names: List of selected skill filenames.

    Returns:
        Prompt string for the LLM to produce the style directive text.
    """
    clarification_block = ""
    if clarification_answers:
        clarification_block = "\nUSER CLARIFICATIONS (their exact intent, depth, and format preferences):\n"
        for qa in clarification_answers:
            clarification_block += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\n"

    skills_block = ", ".join(selected_skill_names) if selected_skill_names else "general_academic.md"

    return f"""You are a Report Style Architect. Your task is to produce a REPORT STYLE DIRECTIVE — a concise contract (200-400 words) that tells every downstream prompt exactly how to format, structure, and present the research output.

USER QUERY: "{user_query}"
{clarification_block}
SELECTED RESEARCH SKILLS: {skills_block}

---

YOUR TASK: Generate a REPORT STYLE DIRECTIVE that covers ALL of the following:

1. **REPORT TYPE** — Name the report format explicitly:
   - Academic paper (abstract, literature review, methodology, analysis, conclusion)
   - Practice sheet / Question bank (numbered questions, difficulty levels, answer keys)
   - Cheat sheet (condensed, high-density bullet points, tables, one-page reference)
   - Financial briefing (executive summary, metrics, risk analysis, charts)
   - Technical documentation (code examples, API references, step-by-step guides)
   - News analysis (timeline, multi-source attribution, conflicting reports)
   - Comparative analysis (feature matrices, side-by-side tables, pros/cons)
   - Tutorial / How-to guide (sequential steps, examples, common mistakes)
   - Or any other format that fits the query best

2. **SECTION FORMATTING RULES** — For each section of the report, specify:
   - What markdown elements to prioritize (tables, numbered lists, code blocks, blockquotes, bullet points, paragraphs)
   - Heading depth (H1, H2, H3 usage patterns)
   - Content density (concise vs. in-depth)
   - Whether sections should have sub-questions, examples, worked solutions, or comparisons
   - Most important this part as it completely change how each section looks it can turn into research report to practice sheet to questions and answers to practice to Coding/Techincal documentation , Financial analysis report , News analysis report , Historical in depth analysis report , Comparative analysis report , 

3. **STRUCTURAL CONVENTIONS**:
   - Should the report have chapters? Or flat sections?
   - Does it need an abstract/introduction/conclusion, or just content?
   - How should citations appear? (inline 🔗, footnotes, or reference list)
   - Are there recurring patterns? (e.g., "every topic gets a definition → explanation → example → practice question")

4. **PRESENTATION NOTES**:
   - Tone (academic, conversational, technical, concise)
   - Target audience (student, researcher, professional, general)
   - Visual density (minimal text with heavy tables, or narrative-heavy with few tables)

5. **EMPHASIS ON USER PREFERENCES**:
   - If the user said "practice sheet" or "cheat sheet" or "just questions" in clarification → that OVERRIDES everything else
   - User's stated preferences for format/style are THE HIGHEST PRIORITY

OUTPUT: Write the directive as a clear, structured text block. NO JSON. Plain text with markdown formatting (bold, bullet points). This text will be injected verbatim into other prompts.
"""

