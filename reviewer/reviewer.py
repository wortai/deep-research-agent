import logging
import asyncio
from typing import List, Dict, Any
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from llms import LlmsHouse
from researcher.solution_tree.main import Solver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReviewNode:
    """Represents a review query to be resolved by the Solver."""
    def __init__(self, query: str):
        self.query = query
        self.answer = None

class Reviewer:
    """
    A Reviewer that analyzes completed research content and generates review queries.
    Each review query is resolved through the Solver to produce enriched content.
    """
    def __init__(self, num_review_queries: int = 3, collection_name: str = "research-documents"):
        """
        Initializes the Reviewer.

        Args:
            num_review_queries: The number of review queries to generate.
            collection_name: Vector store collection to use for Solver resolution.
        """
        self.num_review_queries = num_review_queries
        self.collection_name = collection_name
        # Use the same LLM as solution_tree
        self.review_llm = LlmsHouse.google_model("gemini-2.0-flash-001")

    def _get_review_prompt(self, original_query: str, content_summary: str) -> str:
        """Creates the prompt for the reviewer LLM."""
        return f"""
You are a meticulous Senior Research Analyst. Your task is to review research content and generate high-level synthesis questions.

**Original Query:**
{original_query}

**Research Content:**
---
{content_summary}
---

**Your Task:**
Generate **{self.num_review_queries}** high-level review questions that:
- Synthesize and connect the existing findings
- Identify key themes and implications
- Guide comprehensive understanding of the topic
- Fill any remaining conceptual gaps

**Output Format:**
Provide valid JSON with a single key "review_queries" containing a list of {self.num_review_queries} questions.

Example:
{{
    "review_queries": [
        "What are the main trade-offs identified across all findings?",
        "How do the different aspects relate to each other?",
        "What are the practical implications of these findings?"
    ]
}}
"""

    def _format_content(self, content: Dict[str, Any]) -> str:
        """Formats content dictionary into a readable summary."""
        if not content:
            return "No content available."

        formatted_parts = []
        for query, answer in content.items():
            formatted_parts.append(f"Q: {query}")
            formatted_parts.append(f"A: {answer}\n")
        return "\n".join(formatted_parts)

    def _generate_review_queries(self, original_query: str, content: Dict[str, Any]) -> List[str]:
        """
        Generates review queries based on research content.

        Args:
            original_query: The original research query
            content: Dictionary of query-answer pairs from resolve()

        Returns:
            List of review queries
        """
        logging.info("Generating review queries...")

        content_summary = self._format_content(content)
        prompt = self._get_review_prompt(original_query, content_summary)

        parser = JsonOutputParser()
        chain = self.review_llm | parser

        try:
            response = chain.invoke(prompt)
            review_queries = response.get("review_queries", [])
            logging.info(f"Generated {len(review_queries)} review queries")
            return review_queries
        except OutputParserException as e:
            logging.error(f"Error parsing JSON from reviewer LLM: {e}")
            return []
        except Exception as e:
            logging.error(f"Error during review query generation: {e}")
            return []

    async def _resolve_review_node(self, review_node: ReviewNode, node_index: int, total_nodes: int) -> None:
        """
        Resolves a single review query using Solver with vector-only search (no web scraping).

        Args:
            review_node: ReviewNode to resolve
            node_index: Index of this node (for logging)
            total_nodes: Total number of nodes (for logging)
        """
        logging.info(f"[{node_index}/{total_nodes}] Resolving review query: {review_node.query}")

        solver = Solver(
            query=review_node.query,
            num_web_queries=0,      # OPTIMIZED: Skip web scraping (vector store already populated)
            num_vector_queries=5,   # INCREASED: More semantic searches in existing vector store
            max_web_results=0,      # No web results needed
            collection_name=self.collection_name,
            num_gaps_per_node=0     # No gaps - only resolve the query
        )

        try:
            _, answer = await solver.resolve()  # gaps will be empty (num_gaps_per_node=0)
            review_node.answer = answer
            logging.info(f"[{node_index}/{total_nodes}] Successfully resolved review query")
        except Exception as e:
            logging.error(f"[{node_index}/{total_nodes}] Error resolving review query '{review_node.query}': {e}")
            review_node.answer = {}

    async def review_and_enrich(self, original_query: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method: Generates review queries and enriches content with their resolutions.

        Args:
            original_query: The original research query
            content: Dictionary of query-answer pairs from Solver.resolve()

        Returns:
            Enriched content dictionary with original + review query-answer pairs
        """
        logging.info("=" * 60)
        logging.info("STARTING REVIEW PROCESS")
        logging.info("=" * 60)

        # Step 1: Generate review queries
        review_queries = self._generate_review_queries(original_query, content)

        if not review_queries:
            logging.warning("No review queries generated. Returning original content.")
            return content

        # Step 2: Create ReviewNodes
        review_nodes = [ReviewNode(query=q) for q in review_queries]

        # Step 3: Resolve all review queries IN PARALLEL (optimized for speed)
        logging.info(f"Resolving {len(review_nodes)} review queries in parallel...")

        tasks = [
            self._resolve_review_node(review_node, i+1, len(review_nodes))
            for i, review_node in enumerate(review_nodes)
        ]

        await asyncio.gather(*tasks)

        logging.info(f"All {len(review_nodes)} review queries resolved")

        # Step 4: Merge original content with review answers
        enriched_content = content.copy()

        for review_node in review_nodes:
            if review_node.answer:
                # Merge review answers into enriched content
                enriched_content.update(review_node.answer)

        logging.info("=" * 60)
        logging.info(f"REVIEW COMPLETE - Added {len(review_nodes)} review insights")
        logging.info("=" * 60)

        return enriched_content

if __name__ == '__main__':
    async def main():
        # Simulated content from Solver.resolve()
        original_query = "What are the key differences between Python async/await and threading?"

        mock_content = {
            "How does async/await work in Python?":
                "Async/await in Python enables cooperative multitasking using coroutines...\n\n**Sources:**\n- https://docs.python.org/3/library/asyncio.html",

            "What are the performance characteristics of threading?":
                "Threading in Python uses OS-level threads but is limited by the GIL...\n\n**Sources:**\n- https://realpython.com/python-gil"
        }

        print("=" * 60)
        print("INITIAL CONTENT FROM SOLVER")
        print("=" * 60)
        for q, a in mock_content.items():
            print(f"\nQ: {q}")
            print(f"A: {a[:100]}...")

        # Initialize Reviewer with 2 review queries
        reviewer = Reviewer(num_review_queries=2)

        # Run review and enrichment
        enriched_content = await reviewer.review_and_enrich(original_query, mock_content)

        print("\n" + "=" * 60)
        print("ENRICHED CONTENT AFTER REVIEW")
        print("=" * 60)
        print(f"Original content items: {len(mock_content)}")
        print(f"Enriched content items: {len(enriched_content)}")
        print(f"New insights added: {len(enriched_content) - len(mock_content)}")

        print("\n" + "=" * 60)
        print("ALL QUERY-ANSWER PAIRS")
        print("=" * 60)
        for i, (query, answer) in enumerate(enriched_content.items(), 1):
            print(f"\n[{i}] Q: {query}")
            print(f"    A: {answer[:150]}...")

    asyncio.run(main())