import logging

def dump_query_solution(query: str, answer_dict: dict, filename: str = "query_solutions.md"):
    """
    Appends a query and its structured solution to a markdown document.
    """
    try:
        # --- THIS IS THE KEY UPDATE ---
        # Start building the Markdown content
        content = f"\n\n## Query\n{query}\n\n## Solution\n"
        
        if isinstance(answer_dict, dict):
            # Format the dictionary into a readable list of Q&A pairs
            for sub_query, answer_text in answer_dict.items():
                content += f"#### {sub_query}\n{answer_text}\n\n"
        else:
            # Fallback for plain string answers if they ever occur
            content += f"{str(answer_dict)}\n"

        content += "\n---\n"
        # --- END OF UPDATE ---
        
        # Append to file with UTF-8 encoding
        with open(filename, "a", encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"Query and solution appended to {filename}")
        
    except Exception as e:
        logging.error(f"Failed to dump query solution to {filename}: {e}")