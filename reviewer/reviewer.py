"""
Module for reviewing research content.

The Reviewer analyzes completed research content (Q&A pairs) and
generates synthesis questions to identify gaps and areas needing
deeper exploration.
"""

import logging
from typing import List, Dict, Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from llms import LlmsHouse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Reviewer:
    """
    Generates review questions based on research content.
    
    Analyzes Q&A pairs from research and produces synthesis questions
    that identify gaps, themes, and areas needing further exploration.
    
    Dependencies:
        - LlmsHouse: Provides the LLM for generating review queries.
    """

    def __init__(self, num_review_queries: int = 3):
        """
        Initialize the Reviewer.

        Args:
            num_review_queries: Number of synthesis questions to generate.
        """
        self.num_review_queries = num_review_queries
        self.review_llm = LlmsHouse.google_model("gemini-2.0-flash")

    def _build_review_prompt(self, original_query: str, content_summary: str) -> str:
        """
        Build the prompt for generating review queries.

        Args:
            original_query: The original research question.
            content_summary: Formatted string of existing Q&A pairs.

        Returns:
            A prompt string for the LLM.
        """
        return f"""
You are a meticulous Senior Research Analyst. Your task is to review research content and generate Reviews Based on the query and Research Content.
But you need to understand , that if the topic needs the reviews or not. Check what things are missing , If the Topic is fully answered that mention in queries.
Make sure it only should answer the Original Query.

**Original Query:**
{original_query}

**Research Content:**
---
{content_summary}
---

**Your Task:**
Generate **{self.num_review_queries}** or empty list  deep-level review questions that:
- The size of Review query depends on the how depth you think the reseaarch is missing and required for the topic  to answer  
- Synthesize and connect the existing findings that exists in content summary 
- Identify key themes and Gaps in the research that missing that not completely present to answer original query 
- Give the Genuine reviews that guide what research is missing , what to discuss more in depth , what is half information . 
- To discuss what is missing you can mention name of topics , subtopics ,  sub-subtopics .
-  Reviews 100% should be related to the original query and not jumping on random topics .
- And then mention then Generate the Review Queries that ask questions about the missing parts of the research and be Precise about query and thing.

**Output Format:**
Provide valid JSON with a single key "review_queries" containing a list of {self.num_review_queries} questions.

Example:
{{
    "review_queries": [
        "What are the main trade-offs identified  across this specific ____ topic?",
        "How do the different aspects of this ___ relate to each other?",
        "What are the practical implications of these findings?"
    ]
}}


**If you think the research is complete and no more reviews are needed, return an empty list.** 

Example:
{{
    "review_queries": []
}}
"""

    def _format_content_as_summary(self, content: List[Dict[str, Any]]) -> str:
        """
        Format a content dictionary into a readable summary string.

        Args:
            content: List of dictionaries with "query" and "answer" keys.

        Returns:
            Formatted string with all Q&A pairs.
        """
        if not content:
            return "No content available."

        formatted_parts = []
        for entry in content:
            formatted_parts.append(f"Sub Query that we trying to answer: {entry['query']}")
            formatted_parts.append(f"Answer we got so far for above query: {entry['answer']}\n")
        return "\n".join(formatted_parts)

    def generate_reviews(self, original_query: str, content: List[Dict[str, Any]]) -> List[str]:
        """
        Generate review questions based on research content.

        Analyzes the provided Q&A content and produces synthesis questions
        that will guide further research exploration.

        Args:
            original_query: The original research question.
            content: List of dictionaries with "query" and "answer" keys from research.

        Returns:
            List of review query strings. Empty list if generation fails.
        """
        content_summary = self._format_content_as_summary(content)
        prompt = self._build_review_prompt(original_query, content_summary)

        parser = JsonOutputParser()
        chain = self.review_llm | parser

        try:
            response = chain.invoke(prompt)
            review_queries = response.get("review_queries", [])
            logger.info(f"Generated {len(review_queries)} review queries: {review_queries}")
            return review_queries
        except OutputParserException as e:
            logger.error(f"Failed to parse JSON from reviewer LLM: {e}")
            return []
        except Exception as e:
            logger.error(f"Error during review query generation: {e}")
            return []