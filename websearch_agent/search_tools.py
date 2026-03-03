"""
Search tools for the WebSearch Agent.

LangChain @tool functions wrapping Tavily for search and
response skill generation. Image descriptions come from
Tavily API directly (no separate vision call needed).
"""

import logging
import uuid
from typing import List
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from researcher.scrapers.tavily.tavily_scraper import Tavily
from llms import LlmsHouse
from websearch_agent.web_prompts import (
    QUERY_GENERATION_PROMPT,
    SKILL_GENERATION_PROMPT,
)

logger = logging.getLogger(__name__)

SEARCH_RESULT_TEMPLATE = (
    "--- SEARCH RESULT {index} ---\n"
    "SOURCE TITLE: {title}\n"
    "SOURCE URL BELONGS TO EXTRACTED CONTENT : {url}\n"
    "EXTRACTED CONTENT:\n{content}\n"
    "--------------------------------------------------------\n"
)

IMAGE_BLOCK_TEMPLATE = (
    "--- IMAGE {index} ---\n"
    "TITLE: {title}\n"
    "URL: {url}\n"
    "DESCRIPTION: {description}\n"
    "--------------------------------------------------------\n"
)


@tool
async def tavily_basic_search(query: str) -> str:
    """Quick web search (1 credit). Returns top 2 results with content snippets + any related images with descriptions. Use for simple factual lookups."""
    logger.info(f"[tavily_basic_search] Searching: {query[:60]}")
    try:
        tavily = Tavily(query=query, depth=False, max_result=2)
        images, results = await tavily.basic_search()
        if not results:
            return f"No results found for: {query}"

        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(SEARCH_RESULT_TEMPLATE.format(
                index=i,
                title=result.get("title", "No Title"),
                url=result.get("url", "No URL"),
                content=result.get("content", "No Content"),
            ))

        if images:
            formatted.append("\n--- COLLECTED IMAGES ---")
            for i, img in enumerate(images[:3], 1):
                if isinstance(img, dict):
                    formatted.append(IMAGE_BLOCK_TEMPLATE.format(
                        index=i,
                        title=img.get("title", ""),
                        url=img.get("url", ""),
                        description=img.get("description", "No description"),
                    ))

        return "\n\n".join(formatted)
    except Exception as e:
        logger.error(f"[tavily_basic_search] Failed: {e}")
        return f"Search failed for: {query}. Error: {str(e)}"


@tool
async def tavily_advance_search(query: str) -> str:
    """Deep web search (2 credits — use sparingly, max once per request). Returns top 2 results with full raw content + described images. Use for complex or detailed topics."""
    logger.info(f"[tavily_advance_search] Deep searching: {query[:60]}")
    try:
        tavily = Tavily(
            query=query, depth=True, max_result=2,
            include_raw_content=True, include_images=True,
        )
        images, results = await tavily.advance_search()
        if not results:
            return f"No results found for: {query}"

        formatted = []
        for i, result in enumerate(results, 1):
            content = result.get("raw_content") or result.get("content", "No Content")
            formatted.append(SEARCH_RESULT_TEMPLATE.format(
                index=i,
                title=result.get("title", "No Title"),
                url=result.get("url", "No URL"),
                content=content,
            ))

        if images:
            formatted.append("\n--- COLLECTED IMAGES ---")
            for i, img in enumerate(images[:3], 1):
                if isinstance(img, dict):
                    formatted.append(IMAGE_BLOCK_TEMPLATE.format(
                        index=i,
                        title=img.get("title", ""),
                        url=img.get("url", ""),
                        description=img.get("description", "No description"),
                    ))

        return "\n\n".join(formatted)
    except Exception as e:
        logger.error(f"[tavily_advance_search] Failed: {e}")
        return f"Deep search failed for: {query}. Error: {str(e)}"


@tool
async def generate_search_queries(user_query: str, chat_history: str) -> str:
    """Generate 1-3 targeted search queries based on the user's question and conversation history. Use this first to plan what to search for, then execute the generated queries with the search tools."""
    logger.info(f"[generate_search_queries] Generating queries for: {user_query[:60]}")
    try:
        llm = LlmsHouse.google_model("gemini-2.0-flash", temperature=0.3)
        prompt = QUERY_GENERATION_PROMPT.format(
            user_query=user_query,
            chat_history=chat_history or "No prior conversation.",
        )
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
        logger.info(f"[generate_search_queries] Generated {len(queries)} queries: {queries}")
        return "\n".join(queries)
    except Exception as e:
        logger.error(f"[generate_search_queries] Failed: {e}")
        return user_query


@tool
async def generate_response_skill(user_query: str, search_context: str) -> str:
    """Generate a response skill — precise formatting and tone instructions tailored to the user's query and the research found. Pass the user_query and a summary of search results (titles + key content snippets). Call this as your LAST tool before stopping."""
    logger.info(f"[generate_response_skill] Generating skill for: {user_query[:60]}")
    try:
        llm = LlmsHouse.google_model("gemini-2.5-flash", temperature=0.4)
        prompt = SKILL_GENERATION_PROMPT.format(
            user_query=user_query,
            search_titles=search_context or "No context available.",
        )
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        skill = response.content.strip()
        logger.info(f"[generate_response_skill] Skill generated ({len(skill)} chars)")
        return skill
    except Exception as e:
        logger.error(f"[generate_response_skill] Failed: {e}")
        return "Use clear prose with bold key facts. Lead with the direct answer."


ALL_SEARCH_TOOLS = [
    tavily_basic_search,
    tavily_advance_search,
    generate_search_queries,
    generate_response_skill,
]
