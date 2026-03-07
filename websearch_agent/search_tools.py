"""
Search tools for the WebSearch Agent.

LangChain @tool functions wrapping Tavily for search and
response skill generation. Image descriptions come from
Tavily API directly (no separate vision call needed).
"""

import json
import logging
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from researcher.scrapers.tavily.tavily_scraper import Tavily
from llms import LlmsHouse
from websearch_agent.web_prompts import (
    QUERY_GENERATION_PROMPT,
    SKILL_GENERATION_PROMPT,
)

logger = logging.getLogger(__name__)


def _format_images(raw_images: list) -> list:
    """
    Normalises Tavily image entries into {url, title, description} dicts.

    Tavily returns images as either plain URL strings or dicts with
    url/title/description keys depending on search depth settings.

    Args:
        raw_images: List of image entries from Tavily response.

    Returns:
        List of normalised image dicts.
    """
    formatted = []
    for img in raw_images:
        if isinstance(img, str):
            formatted.append({"url": img, "title": "", "description": ""})
        elif isinstance(img, dict):
            formatted.append({
                "url": img.get("url", ""),
                "title": img.get("title", ""),
                "description": img.get("description", ""),
            })
    return formatted


def _format_results(raw_results: list, use_raw_content: bool = False) -> list:
    """
    Normalises Tavily result entries into {title, url, content} dicts.

    Args:
        raw_results: List of result dicts from Tavily response.
        use_raw_content: If True, prefer raw_content over content snippet.

    Returns:
        List of normalised result dicts.
    """
    formatted = []
    for r in raw_results:
        content = r.get("content", "")
        if use_raw_content:
            content = r.get("raw_content") or content
        formatted.append({
            "title": r.get("title", "No Title"),
            "url": r.get("url", ""),
            "content": content,
        })
    return formatted


@tool
async def tavily_basic_search(query: str) -> str:
    """Quick web search (1 credit). Returns top 2 results with content snippets + related images with descriptions. Use for simple factual lookups."""
    logger.info(f"[tavily_basic_search] Searching: {query[:60]}")
    try:
        tavily = Tavily(query=query, depth=False, max_result=2)
        images, results = await tavily.basic_search()

        return json.dumps({
            "query": query,
            "images": _format_images(images),
            "results": _format_results(results),
        })
    except Exception as e:
        logger.error(f"[tavily_basic_search] Failed: {e}")
        return json.dumps({"query": query, "images": [], "results": [], "error": str(e)})


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

        return json.dumps({
            "query": query,
            "images": _format_images(images),
            "results": _format_results(results, use_raw_content=True),
        })
    except Exception as e:
        logger.error(f"[tavily_advance_search] Failed: {e}")
        return json.dumps({"query": query, "images": [], "results": [], "error": str(e)})


@tool
async def generate_search_queries(user_query: str, chat_history: str) -> str:
    """Generate 1-3 targeted search queries based on the user's question and conversation history. Use this first to plan what to search for, then execute those queries with the search tools."""
    logger.info(f"[generate_search_queries] Generating queries for: {user_query[:60]}")
    try:
        llm = LlmsHouse.google_model("gemini-2.0-flash", temperature=0.9)
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
        llm = LlmsHouse.google_model("gemini-2.5-flash", temperature=0.8)
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
