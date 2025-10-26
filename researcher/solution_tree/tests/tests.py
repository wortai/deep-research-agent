import asyncio
from researcher.solution_tree import Solver

solver = Solver("What is Quantum Computing?", num_web_queries=5)

# Dump Any Output to a file
def file_dump(content, filename="output_dump.txt"):
    with open(filename, "w") as f:
        f.write(str(content))
    return

def test_web_queries():
    web_queries = solver.create_web_search_queries()
    file_dump(web_queries, "web_search_queries_response.txt")
    return web_queries

async def test_retrieve_store_content(queries):
    all_web_content = await solver.retrieve_store_content(queries)
    file_dump(all_web_content, "web_search_content.txt")
    return all_web_content

def test_vector_search_queries():
    vector_queries = solver.create_vector_search_queries()
    file_dump(vector_queries, "vector_search_queries_response.txt")
    return vector_queries

def test_analyze_gaps(vector_queries):
    main_query, query_answers, gaps = solver.analyze_gaps(vector_queries)
    
    # Build formatted output
    lines = [
        "\n" + "="*100,
        " QUERY ANALYSIS RESULTS ".center(100, "="),
        "="*100,
        "\n📝 MAIN QUERY:",
        "-"*100,
        main_query,
        "\n\n✅ VECTOR QUERY ANSWERS:",
        "-"*100
    ]
    
    # Add each query-answer pair
    if query_answers:
        for i, (query, answer) in enumerate(query_answers.items(), 1):
            lines.append(f"\n  [{i}] Query: {query}")
            lines.append(f"      Answer: {answer}")
    else:
        lines.append("\n  No query answers available")
    
    # Add gaps section
    lines.extend([
        "\n\n🔍 IDENTIFIED GAPS (Web Search Needed):",
        "-"*100
    ])
    
    if gaps:
        for i, gap in enumerate(gaps, 1):
            lines.append(f"\n  [{i}] {gap}")
    else:
        lines.append("\n  ✓ No gaps - all information available in vector store")
    
    lines.append("\n" + "="*100 + "\n")
    
    # Join and display
    output = "\n".join(str(line) for line in lines)
    print(output)
    
    # Save to file
    file_dump(output, "gaps_analysis.txt")
    print("💾 Saved to gaps_analysis.txt\n")


if __name__ == "__main__":
    # Test 1: Web Queries generation (PASS)
    # web_queries = test_web_queries()
    
    # Test 2: Web Content Retrieval (PASS) + Vector Store Upload (FAIL)
    # web_content = asyncio.run(test_retrieve_store_content(['quantum computing explained', 'principles of quantum mechanics']))

    # Test 3: Vector Queries generation (PASS)
    # vector_queries = test_vector_search_queries()

    # Test 4: Analyze Gaps
    # ['What are the fundamental principles of quantum computing?', 'How does a quantum computer differ from a classical computer?', 'What are the potential applications of quantum computing?', 'What are the current limitations and challenges in building and using quantum computers?', 'Explain the concepts of qubits, superposition, and entanglement in quantum computing.']
    test_analyze_gaps(['What are the fundamental principles of quantum computing?', 'How does a quantum computer differ from a classical computer?', 'What are the potential applications of quantum computing?', 'What are the current limitations and challenges in building and using quantum computers?', 'Explain the concepts of qubits, superposition, and entanglement in quantum computing.'])
    