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

def get_answers_prompt(main_query: str, context: str) -> str:
    """Generates a prompt to synthesize answers from web search context with adaptive formatting and inline citations."""
    return f"""You are an expert research analyst specializing in presenting information clearly and effectively. Your task is to synthesize a comprehensive, well-structured answer from the provided context.

**Main Query:**
{main_query}

**Context from Web Search (with sources):**
{context}

---

**Your Task:**

Generate a JSON object with two keys: "main_query" and "query_answers".

1. **main_query**: The original main query (unchanged).
2. **query_answers**: A dictionary where the key is the main query and the value is a comprehensive answer in **Markdown format**.

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


- Format: `[🔗](URL)` - the emoji itself becomes the clickable link
- Place citations at the end of the sentence or paragraph they support
- If multiple sources support a paragraph, include multiple citation links: `[🔗](URL1) [🔗](URL2)`
- DO NOT create a separate "Sources" section at the end
- Ensure the JSON is valid (properly escaped quotes, newlines as `\\n`)


**Quality Standards:**

- **Accuracy**: Keep all numbers, dates, names, and facts exactly as stated in the context
- **Comprehensiveness**: Cover all relevant aspects of the query found in the context and in depth 
- **Clarity**: Use clear, concise language; avoid jargon unless necessary
- **Completeness**: Ensure the answer can stand alone without needing additional context
- **Relevance**: Focus strictly on answering the main query




** CONTEXT RULE **
- Strictly Don't Try to Summarize the Context , Instead Try to get in the depth 
- Don't Loose the Details of the context 
- Don't make it shorter or way longer than the context 
- Don't Try to give short summary answer of the query , instead try to get in the depth 
- Don't Make answer vague , it has to be clear and getting in depths to explain


**Example Output Format:**
```json
{{
    
    "query_answers": {{
        "{main_query}": "# Understanding Machine Learning Basics\\n\\nMachine learning is a subset of artificial intelligence that enables systems to learn from data. [🔗](https://example.com/ml-intro)\\n\\n## Types of Machine Learning\\n\\n### Supervised Learning\\n\\nSupervised learning uses labeled datasets to train algorithms. Common applications include classification and regression tasks. [🔗](https://example.com/supervised)\\n\\n### Unsupervised Learning\\n\\nThis approach finds hidden patterns in unlabeled data. [🔗](https://example.com/unsupervised)\\n\\n## Comparison of Approaches\\n\\n| Feature | Supervised | Unsupervised |\\n|---------|-----------|--------------|\\n| Data Type | Labeled | Unlabeled |\\n| Use Case | Prediction | Pattern Discovery |\\n| Complexity | Lower | Higher |\\n\\n[🔗](https://example.com/comparison)\\n\\n## Key Takeaways\\n\\n- Machine learning automates decision-making processes [🔗](https://example.com/benefits)\\n- Different approaches suit different problem types [🔗](https://example.com/selection)\\n- Training data quality is critical for success [🔗](https://example.com/data-quality)"
    }}
}}
```


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

Generate a JSON object with one key: "plan".

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



def get_gaps_prompt(main_query: str, query_answers: dict, num_gaps: int) -> str:
    """
    Generates a depth-focused research gap prompt.
    Main query = user intent anchor.
    Subqueries + answers = current depth state.
    Output = next-level depth probes.
    """

    answers_str = ""
    for query, answer in query_answers.items():
        answers_str += f'### Subquery: "{query}"\nCurrent Answer:\n{answer}\n\n'

    return f"""
You are a **Depth-First Research Analyst Agent**.

Your mission is to determine what *additional depth* is needed to fully and rigorously answer the **Main Query**, using the **Subqueries and their Answers as your base reference layer**.

---

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

{
  "gaps": [
    "Precise, actionable depth question 1?",
    "Precise, actionable depth question 2?",
    ...
  ]
}
"""
