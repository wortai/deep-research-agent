"""
Module for solving research queries using LLMs and Web Search.
"""

import json
import logging
import asyncio
from typing import List, Tuple, Dict, Any, Optional

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from llms import LlmsHouse
from researcher.solution_tree.prompts import (
    get_web_search_queries_prompt,
    get_answers_prompt,
    get_gaps_prompt
)
from researcher.web_search import WebSearch
from researcher.solution_tree.utils import dump_query_solution

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Solver:
    """
    Solver class to resolve research queries.
    
    It orchestrates the process of:
    1. Generating web search queries.
    2. Retrieving content from the web.
    3. Analyzing content and identifying gaps.
    """

    def __init__(
        self, 
        query: str, 
        num_web_queries: int = 1, 
        max_web_results: int = 1, 
        num_gaps_per_node: int = 2
    ):
        """
        Initialize the Solver.

        Args:
            query (str): The main research query.
            num_web_queries (int): Number of web search queries to generate.
            max_web_results (int): Maximum number of web results per query.
            num_gaps_per_node (int): Number of gaps to identify per node.
        """
        self.query = query
        self.num_web_queries = num_web_queries
        self.num_gaps_per_node = num_gaps_per_node
        self.max_results = max_web_results

        self.web_search_llm = LlmsHouse.google_model("gemini-2.0-flash")
        self.analysis_llm = LlmsHouse.google_model("gemini-2.0-flash")

    def create_web_search_queries(self) -> List[str]:
        """
        Generate web search queries using the LLM.
        
        Returns:
            List[str]: A list of web search queries.
        """
        parser = JsonOutputParser()
        chain = self.web_search_llm | parser
        prompt = get_web_search_queries_prompt(self.query, self.num_web_queries)
        
        try:
            data = chain.invoke(prompt)
            return data.get("queries", [])
        except OutputParserException as e:
            logger.error(f"Failed to parse web search queries: {e}")
            return []

    async def retrieve_web_content(self, web_search_queries: List[str]) -> List[Dict[str, str]]:
        """
        Retrieve content from web using WebSearch class.
        
        Args:
            web_search_queries (List[str]): List of queries to search for.
            
        Returns:
            List[Dict[str, str]]: List of dicts with 'url' and 'content' keys.
        """
        all_web_content = []
        
        for query in web_search_queries:
            try:
                logger.info(f"Web search: {query}")
                web_search = WebSearch(query=query, max_results=self.max_results)
                results = await web_search.initiate_research()
                logger.info(f"Retrieved {len(results)} results")
                
                if results:
                    for result in results:
                        all_web_content.append({
                            "content": result['content'],
                            "url": result['url']
                        })
            
            except Exception as e:
                logger.error(f"Web search error for '{query}': {e}")
        
        return all_web_content
        
    def analyze_gaps(self, web_content: List[Dict[str, str]]) -> Tuple[str, Dict[str, str], List[str]]:
        """
        Analyzes web search results to answer the main query and identify gaps.
        
        Args:
            web_content (List[Dict[str, str]]): List of dicts with 'url' and 'content' keys.
            
        Returns:
            Tuple[str, Dict[str, str], List[str]]: 
                - The main query.
                - A dictionary of answers.
                - A list of identified gaps (new queries).
        """
        if not web_content:
            logger.warning("No web content to analyze")
            return self.query, {}, []

        context_parts = []
        for item in web_content:
            source_url = item.get('url', 'Unknown Source')
            content = item.get('content', '')
            context_parts.append(f"Source: {source_url}\nContent:\n{content}")

        combined_context = "\n\n---\n\n".join(context_parts)

        answer_prompt = get_answers_prompt(
            main_query=self.query,
            context=combined_context
        )

        parser = JsonOutputParser()
        
        if hasattr(self.analysis_llm, 'max_tokens'):
            analysis_llm_configured = self.analysis_llm.bind(max_tokens=10000)
        else:
            analysis_llm_configured = self.analysis_llm
        
        chain = analysis_llm_configured | parser

        try:
            answers_data = chain.invoke(answer_prompt)
            query_answers = answers_data.get("query_answers", {})

            if self.num_gaps_per_node > 0:
                gaps_prompt = get_gaps_prompt(self.query, query_answers, self.num_gaps_per_node)
                gaps_data = chain.invoke(gaps_prompt)
                gaps = gaps_data.get("gaps", [])
            else:
                gaps = []
            
            return self.query, query_answers, gaps
        except Exception as e:
            logger.error(f"Gap analysis error: {e}")
            return self.query, {}, []

    async def resolve(self) -> Tuple[List[str], Dict[str, str]]:
        """
        Main resolution pipeline using web search.
        Retrieves web content and feeds directly to LLM for analysis.
        
        Returns:
            Tuple[List[str], Dict[str, str]]:
                - List of gaps (new queries).
                - Dictionary of answers.
        """
        web_search_queries = self.create_web_search_queries()
        logger.info(f"Web queries: {web_search_queries}")
        
        web_content = await self.retrieve_web_content(web_search_queries)
        logger.info(f"Retrieved {len(web_content)} content items")
        
        query, answer, gaps = self.analyze_gaps(web_content)

        dump_query_solution(query, answer, filename="query_solutions.md")
        
        logger.info(f"Resolved with {len(gaps)} gaps remaining")

        return gaps, answer

    async def websearch_solver(self) -> Dict[str, Any]:
        """
        Quick websearch using Tavily without full research tree.
        
        Performs direct Tavily search and formats results for
        response_node consumption. Skips research tree and report generation.
        
        Returns:
            Dict with formatted research_review data for state update.
        """
        from researcher.scrapers.tavily.tavily_scraper import Tavily
        
        logger.info(f"[websearch_solver] Quick search for: {self.query[:50]}...")
        
        try:
            tavily = Tavily(query=self.query, max_result=5)
            search_results = await tavily.basic_search()
            
            formatted_results = []
            print(search_results)
            for result in search_results:
                formatted_results.append({
                    "query": self.query,
                    "answer": f"{result.get('url', '')}: {result.get('content', '')}",
                    "parent_query": self.query,
                    "depth": 0
                })
            
            research_review_data = {
                "query": self.query,
                "query_num": 1,
                "raw_research_results": formatted_results,
                "review_feedback": [],
                "current_reviews": [],
                "iteration_count": 0
            }
            
            logger.info(f"[websearch_solver] Found {len(formatted_results)} results")
            
            return {"research_review": [research_review_data]}
            
        except Exception as e:
            logger.error(f"[websearch_solver] Search failed: {e}")
            return {"research_review": []}
