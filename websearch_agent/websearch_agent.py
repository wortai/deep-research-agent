"""
WebSearch Agent node for the DeepResearchAgent graph.

Uses `create_agent` from LangChain with `wrap_tool_call` middleware
that emits TOOL_EXECUTION events via StreamWriter for real-time frontend display.
The agent autonomously chains tools based on user query and chat history.
"""

import logging
import uuid
from typing import Dict, Any, List
from datetime import datetime

from langgraph.types import StreamWriter
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage

from graphs.states.subgraph_state import AgentGraphState
from graphs.events.stream_emitter import get_emitter, StreamEmitter
from websearch_agent.search_tools import ALL_SEARCH_TOOLS
from llms import LlmsHouse

logger = logging.getLogger(__name__)

TOOL_LABELS = {
    "generate_search_queries": "Generating search queries",
    "tavily_basic_search": "Searching",
    "tavily_advance_search": "Concisou Searching",
    "generate_response_skill": "Crafting response vibe",
}

SYSTEM_PROMPT = """You are a web research agent. Search the web to gather information for the user's question.

**Tools:**
- `generate_search_queries` — Generate 1-3 targeted queries from the user question + chat history. Call this first.
- `tavily_basic_search` — Quick search, 1 credit per query. Returns top 2 results with snippets + images with descriptions. Use for simple facts and multiple queries.
- `tavily_advance_search` — Deep search, 2 credits per query (expensive). Returns full raw content + described images. Use ONLY ONCE per request, only when deep detail is needed.
- `generate_response_skill` — Generate formatting/tone instructions for the final response. Pass `user_query` and `search_context` (titles + key content snippets). Call this LAST before stopping.

**Cost-Aware Strategy:**
1. Call `generate_search_queries` first to plan your search.
2. Use `tavily_basic_search` for most queries — it's cheap and returns images with descriptions.
3. Use `tavily_advance_search` at most ONCE if you need in-depth raw content on the most important query.
4. Call `generate_response_skill` as your FINAL tool — include titles, key findings, and short content excerpts so the skill understands the content type.
5. Stop after generating the skill.

Do NOT generate a final answer — just gather results. The response node handles synthesis."""


class WebSearchAgent:
    """
    Autonomous web search agent with skill generation.

    Uses create_agent with wrap_tool_call middleware for clean tool execution
    and real-time streaming. Extracts search results, images (from Tavily),
    and response skill from the agent's final message history.
    """

    def __init__(self, emitter: StreamEmitter):
        """
        Build the agent with TOOL_EXECUTION middleware bound to the emitter.

        Args:
            emitter: StreamEmitter for sending tool execution events to frontend.
        """
        self._emitter = emitter
        self._agent = create_agent(
            model=LlmsHouse.google_model("gemini-2.0-flash", temperature=0.3),
            tools=ALL_SEARCH_TOOLS,
            system_prompt=SYSTEM_PROMPT,
            middleware=[self._build_tool_middleware()],
        )

    def _build_tool_middleware(self):
        """
        Creates async wrap_tool_call middleware emitting TOOL_EXECUTION events.

        Emits "running" before tool execution and "completed" after,
        routed through StreamWriter → chunk_router → frontend WebSocket.

        Returns:
            AgentMiddleware wrapping each tool call with event emission.
        """
        emitter = self._emitter

        @wrap_tool_call
        async def emit_tool_status(request, handler):
            tool_name = request.tool_call.get("name", "unknown")
            query_snippet = request.tool_call.get("args", {}).get(
                "query", request.tool_call.get("args", {}).get("user_query", "")
            )[:50]
            label = TOOL_LABELS.get(tool_name, tool_name)
            description = f"{label}: {query_snippet}" if query_snippet else label

            emitter.emit_tool_execution(tool_name, description, status="running")
            result = await handler(request)
            emitter.emit_tool_execution(tool_name, description, status="completed")
            return result

        return emit_tool_status

    async def search(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Invoke the agent and extract search results, images, and skill.

        Args:
            state: AgentGraphState with user_query, chat_messages.

        Returns:
            State update with websearch_results, analyzed_images, response_skill.
        """
        user_query = state.get("user_query", "")
        if not user_query:
            return {"websearch_results": []}

        chat_context = self._format_chat_context(state.get("chat_messages", []))

        result = await self._agent.ainvoke({
            "messages": [{
                "role": "user",
                "content": f"Chat History:\n{chat_context}\n\nCurrent User Question: {user_query}",
            }]
        })

        messages = result.get("messages", [])
        search_outputs = self._extract_search_results(messages)
        analyzed_images = self._extract_images(messages)
        skill = self._extract_skill(messages)

        formatted_results = self._deduplicate_and_format(search_outputs)

        websearch_data = {
            "run_id": state.get("current_run_id", ""),
            "query": user_query,
            "results": formatted_results,
            "timestamp": datetime.now().isoformat(),
        }

        return {
            "websearch_results": [websearch_data],
            "analyzed_images": analyzed_images,
            "response_skill": skill,
        }

    def _format_chat_context(self, chat_messages: List[Dict]) -> str:
        """Formats the last 10 chat_messages into a string for agent context."""
        if not chat_messages:
            return "No prior conversation."
        return "\n".join(
            f"{m.get('role', 'unknown')}: {m.get('content', '')}"
            for m in chat_messages[-10:]
        )

    def _extract_search_results(self, messages: list) -> List[str]:
        """
        Filters ToolMessages containing SEARCH RESULT blocks.

        Args:
            messages: Full message list from the agent's final state.

        Returns:
            List of search result strings from tavily tools.
        """
        return [
            msg.content for msg in messages
            if isinstance(msg, ToolMessage)
            and msg.content
            and "--- SEARCH RESULT" in msg.content
        ]

    def _extract_images(self, messages: list) -> List[Dict]:
        """
        Extracts image data from Tavily's COLLECTED IMAGES blocks.

        Parses TITLE / URL / DESCRIPTION from each IMAGE block,
        generates a UUID per image URL for stable identification.

        Args:
            messages: Full message list from the agent's final state.

        Returns:
            List of {uuid, url, title, description} dicts for state.
        """
        images = []
        seen_urls = set()
        for msg in messages:
            if not isinstance(msg, ToolMessage) or not msg.content:
                continue
            if "COLLECTED IMAGES" not in msg.content:
                continue
            for block in msg.content.split("--- IMAGE"):
                block = block.strip()
                if not block or "COLLECTED" in block:
                    continue
                data = {}
                for line in block.split("\n"):
                    line = line.strip()
                    if line.startswith("TITLE:"):
                        data["title"] = line.split(":", 1)[1].strip()
                    elif line.startswith("URL:"):
                        data["url"] = line.split(":", 1)[1].strip()
                    elif line.startswith("DESCRIPTION:"):
                        data["description"] = line.split(":", 1)[1].strip()
                if data.get("url") and data["url"] not in seen_urls:
                    seen_urls.add(data["url"])
                    data["uuid"] = str(uuid.uuid5(uuid.NAMESPACE_URL, data["url"]))
                    images.append(data)
        return images[:5]

    def _extract_skill(self, messages: list) -> str:
        """
        Extracts the response skill from the last generate_response_skill ToolMessage.

        Walks messages in reverse, returns the first ToolMessage that
        is not a search result and not an image block.

        Args:
            messages: Full message list from the agent's final state.

        Returns:
            Skill instruction string, or empty string if not found.
        """
        for msg in reversed(messages):
            if not isinstance(msg, ToolMessage) or not msg.content:
                continue
            content = msg.content
            if "--- SEARCH RESULT" in content or "COLLECTED IMAGES" in content:
                continue
            if "No results" in content or "Search failed" in content:
                continue
            if len(content) > 50:
                return content
        return ""

    def _deduplicate_and_format(self, raw_outputs: List[str]) -> str:
        """
        Deduplicates search results by URL and re-numbers them.

        Args:
            raw_outputs: List of formatted search result strings from tools.

        Returns:
            Single string with deduplicated, numbered search results.
        """
        seen_urls = set()
        unique_results = []
        result_index = 1

        for output in raw_outputs:
            blocks = output.split("--- SEARCH RESULT")
            for block in blocks:
                if not block.strip() or "COLLECTED IMAGES" in block:
                    continue
                url_line = ""
                for line in block.split("\n"):
                    if line.startswith("SOURCE URL"):
                        url_line = line.split(":", 1)[-1].strip()
                        break
                if url_line and url_line in seen_urls:
                    continue
                if url_line:
                    seen_urls.add(url_line)
                clean_block = block.lstrip(" 0123456789-")
                unique_results.append(
                    f"--- SEARCH RESULT {result_index} ---{clean_block}"
                )
                result_index += 1

        return "\n\n".join(unique_results) if unique_results else "No search results found."


async def websearch_agent_node(state: AgentGraphState, writer: StreamWriter = None) -> Dict[str, Any]:
    """LangGraph node entry point — creates WebSearchAgent and runs search."""
    emitter = get_emitter(writer)
    agent = WebSearchAgent(emitter)
    return await agent.search(state)
