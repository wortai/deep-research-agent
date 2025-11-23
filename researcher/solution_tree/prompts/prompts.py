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

def get_gap_analysis_prompt(main_query: str, vector_queries: list, context_by_query: dict, num_gaps_per_node: int) -> str:
    """
    Generates a prompt to analyze vector search results, identify gaps, and cite sources.
    """
    # Format the context for each vector query. The context coming from analyze_gaps
    # will now already include the source URLs.
    context_str = ""
    for query in vector_queries:
        context = context_by_query.get(query, "No relevant information found.")
        context_str += f'### Context for: "{query}"\n{context}\n\n'

    return f"""You are a meticulous research analyst. Your task is to analyze the provided context to answer a set of queries and identify any information gaps related to the main query.

    **Main Query:**
    {main_query}

    **Context from Vector Search (with sources):**
    {context_str}

    ---

    **Your Task:**

    Based **only** on the provided context, generate a JSON object with three keys: "main_query", "query_answers", and "gaps".

    1.  **main_query**: The original main query.
    2.  **query_answers**: A dictionary where each key is one of the original vector search queries and the value is a comprehensive, detailed answer synthesized from the provided text.
    3.  **gaps**: A list of new questions that need to be answered to fully resolve the main query.

    **CRITICAL INSTRUCTIONS:**
    - For each answer in the `query_answers` dictionary, you **MUST** cite the sources you used. Append a "**Sources:**" section at the end of each answer, listing all relevant URLs from the context.
    - You **MUST** identify exactly **{num_gaps_per_node}** gaps.

    **Example Output Format:**
    ```json
    {{
    "main_query": "What is Quantum Computing?",
    "query_answers": {{
        "How does a quantum computer differ from a classical computer?": "The retrieved context reveals several key differences... [rest of the comprehensive answer].\\n\\n**Sources:**\\n- [https://example.com/quantum-intro](https://example.com/quantum-intro)\\n- [https://another.edu/qubits-explained](https://another.edu/qubits-explained)"
    }},
    "gaps": [
        "What are the leading quantum computing hardware technologies and companies developing them?"
    ]
    }}
    Now provide your analysis. Output only the JSON object, nothing else.
    
    {{
    "main_query": "{main_query}",
    "query_answers": {{}},
    "gaps": []
    }}
    """