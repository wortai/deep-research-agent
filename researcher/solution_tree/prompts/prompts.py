def get_web_search_queries_prompt(query: str, num_queries: int) -> str:
    """
    Generates a prompt to create optimized web search queries in JSON format,
    using a one-shot example to guide the model.
    """
    return f"""
    You are an expert search query creator. Your task is to decompose a complex user query into a set of {num_queries} distinct, optimized queries for a standard web search engine like Google.

    **Guidelines:**
    - The generated queries should be concise and keyword-focused.
    - They must cover different facets and sub-topics of the original query to ensure comprehensive information retrieval.
    - Avoid conversational language; formulate queries a knowledgeable user would type into a search bar.

    ---
    **Example:**

    **User Query:**
    "What are the best GPUs for deep learning in 2025, considering performance, price, and memory for training large language models?"

    **JSON Output Format:**
    ```json
    {{
        "queries": [
            "best GPU for deep learning 2025",
            "NVIDIA RTX vs AMD Radeon for LLM training",
            "GPU VRAM requirements for large language models",
            "budget GPUs for machine learning 2025",
            "performance benchmarks NVIDIA 5090 vs 4090 AI"
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

def get_gap_analysis_prompt(main_query: str, vector_queries: list, context_by_query: dict) -> str:
    """
    Generates a prompt to analyze vector search results and identify remaining gaps.
    
    Args:
        main_query: The main user query
        vector_queries: List of vector search queries used
        context_by_query: Dict mapping each vector query to its retrieved context
    """
    
    # Format the context for each vector query
    query_context_sections = []
    for query in vector_queries:
        context = context_by_query.get(query, "No relevant information found.")
        query_context_sections.append(f"""
**Vector Query:** "{query}"
**Retrieved Context:**
{context}
""")
    
    all_contexts = "\n---\n".join(query_context_sections)
    
    return f"""You are a precise and thorough analyst. Your task is to evaluate whether the retrieved information from a vector database is sufficient to answer the main query.

**Main Query:** "{main_query}"

**Vector Search Queries Used:**
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(vector_queries)])}

**Retrieved Information for Each Vector Query:**
{all_contexts}

---

**Your Task:**

1. **Evaluate each vector search query**: For each query, provide a COMPREHENSIVE and DETAILED answer using ALL relevant information from the retrieved context. 
   - Include ALL key points, facts, and details from the context
   - Synthesize information from multiple sources if available
   - Provide explanations, examples, and specifics mentioned in the context
   - Each answer should be 3-5 sentences minimum, or longer if the context warrants it
   - If information is insufficient, explain exactly what is present and what is missing

2. **Identify gaps**: Determine what critical information is still missing to fully answer the main query. These gaps should be:
   - Specific and actionable
   - Formulated as web search queries that would retrieve the missing information
   - Not already covered in the retrieved context
   - Essential to answering the main query completely

**Important Rules:**
- Base your analysis ONLY on the retrieved context provided
- DO NOT summarize or truncate answers - use ALL relevant information from the context
- Be thorough and comprehensive in your answers
- Do not hallucinate or invent information beyond what's in the context
- If a vector query cannot be fully answered from the context, provide what IS available and note what's missing

**Example Output Format:**
```json
{{
  "main_query": "What is Quantum Computing?",
  "query_answers": {{
    "What are the fundamental principles of quantum computing?": "Based on the retrieved context, quantum computing is built on four fundamental principles from quantum mechanics. First, superposition allows qubits to exist in multiple states simultaneously, representing combinations of all possible configurations. Second, entanglement enables qubits to correlate their states with other qubits, creating intrinsic links where measuring one qubit immediately reveals information about others. Third, interference is the computational engine, where probability amplitudes can build upon each other or cancel out, amplifying desired outcomes while eliminating others. Fourth, decoherence is the process where quantum states collapse, which must be carefully managed to maintain quantum behavior. These principles work together to enable quantum computers to solve problems that are intractable for classical computers.",
    "How does a quantum computer differ from a classical computer?": "The retrieved context reveals several key differences between quantum and classical computers. Classical computers use bits that store either 0 or 1 and process information sequentially using binary code. In contrast, quantum computers use qubits that can exist in superposition - simultaneously representing 0, 1, or weighted combinations of both states. While classical computers must explore solution spaces sequentially, quantum computers can process multiple possibilities in parallel through superposition and interference. The context also indicates that quantum computers excel at specific complex problems like molecular simulation and optimization, whereas classical computers remain superior for most everyday computing tasks. Additionally, quantum computers require extreme operating conditions, including temperatures near absolute zero for superconducting qubits, while classical computers operate at room temperature."
  }},
  "gaps": [
    "What are the current practical applications of quantum computing in industry as of 2025?",
    "What is the timeline for quantum computing to become commercially viable for general use?",
    "What are the leading quantum computing hardware technologies and companies developing them?"
  ]
}}
```

---

**Now provide your analysis:**

Your output must be a single valid JSON object with exactly three keys:
1. "main_query" (string): The main query
2. "query_answers" (object): Each vector query as a key with its DETAILED, COMPREHENSIVE answer as the value
3. "gaps" (array): List of specific web search queries for missing information

**CRITICAL: Make your answers to each query as detailed and comprehensive as possible using ALL available information from the context. Do not truncate or summarize unnecessarily.**

Output only the JSON object, nothing else.
```json
{{
  "main_query": "",
  "query_answers": {{}},
  "gaps": []
}}
```
"""