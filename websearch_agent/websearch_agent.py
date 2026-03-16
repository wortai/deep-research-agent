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
    "tavily_advance_search": "Deep searching",
    "generate_response_skill": "Crafting response vibe",
}

SYSTEM_PROMPT = """You are a web research agent. Search the web to gather information for the user's question.

**Tools:**
- `generate_search_queries` — Generate 1-3 targeted queries from the user question + chat history. Call this first.
    - We need to analyze the user query and chat history to understand what the user is asking for.
    - Then generate good SEO search queries that give us good URLs about the specific topic the user is asking for.
    - These queries should be 15 to 60 words max and each query should cover different angles of the subject.
    - Remember, we have to get the best URLs using these queries.
- `tavily_basic_search` — Quick search, 1 credit per query. Returns top 2 results with snippets + images with descriptions. Use for simple facts and multiple queries.
- `tavily_advance_search` — Deep search, 2 credits per query (expensive). Returns full raw content + described images. Use only when deep detail is needed.
- `generate_response_skill` — Generate formatting/tone instructions for the final response. Pass `user_query` and `search_context` (titles + key content snippets). Call this LAST before stopping.

**Instructions**
STEP 1. Call `generate_search_queries` first to generate queries to USE in Step 2.
STEP 2. Call `tavily_basic_search` using the generated queries to gather information.
- You can skip step 3 if you have enough information from step 2.
STEP 3. Use `tavily_advance_search` at most once if you need in-depth raw content on the most important query.
STEP 4. Call `generate_response_skill` as your FINAL tool — include titles, key findings, and short content excerpts so the skill understands the content type.
STEP 5. Stop after generating the skill.

Do NOT generate a final text answer summarizing the information — just execute tools to gather results. The response node handles synthesis."""


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
            model=LlmsHouse.grok_model(
                model_name= "grok-4-1-fast-reasoning",
                temperature=0.5,
            ),
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
            State update with websearch_results, response_skill.
        """
        user_query = state.get("user_query", "")
        if not user_query:
            return {"websearch_results": []}

        chat_context = self._format_chat_context(state.get("chat_messages", []))
        memory_context = self._format_memory_context(state.get("memory_context", {}))
        improve_instruction = self._normalize_improve_instruction(
            state.get("improve_in_response", "")
        )

        result = await self._agent.ainvoke({
            "messages": [{
                "role": "user",
                "content": (
                    f"Long-Term Memory Context:\n{memory_context}\n\n"
                    f"Chat History:\n{chat_context}\n\n"
                    f"Current User Question: {user_query}\n\n"
                    f"Improve_in_response instruction:\n{improve_instruction}"
                ),
            }]
        })

        messages = result.get("messages", [])
        structured_results, all_images = self._parse_search_results(messages)
        skill = self._extract_skill(messages)

        websearch_data = {
            "run_id": state.get("current_run_id", ""),
            "query": user_query,
            "results": structured_results,
            "images": all_images,
            "timestamp": datetime.now().isoformat(),
        }

        return {
            "websearch_results": [websearch_data],
            "analyzed_images": [],
            "response_skill": skill,
        }

    def _extract_skill(self, messages: list) -> str:
        """
        Extracts the response skill from the last generate_response_skill ToolMessage.
        """
        for msg in reversed(messages):
            if not isinstance(msg, ToolMessage) or not msg.content:
                continue
            content = msg.content
            if "error" in content.lower() or "failed" in content.lower():
                continue
            # We can detect skill by length or specific markers.
            # Assuming it's typically a longer descriptive string not formatted as JSON.
            if len(content) > 50 and not content.strip().startswith("["):
                return content
        return ""

    def _format_chat_context(self, chat_messages: List[Dict]) -> str:
        """Formats the last 10 chat_messages into a string for agent context."""
        if not chat_messages:
            return "No prior conversation."
        return "\n".join(
            f"{m.get('role', 'unknown')}: {m.get('content', '')}"
            for m in chat_messages[-10:]
        )

    @staticmethod
    def _format_memory_context(memory_context: Dict[str, Any]) -> str:
        """
        Formats concise long-term memory snippets for websearch planning.
        """
        if not memory_context:
            return "No long-term memory context."

        semantic_memories = memory_context.get("semantic_memories", [])[:2]
        user_profile = memory_context.get("user_profile") or {}

        parts: List[str] = []
        if semantic_memories:
            parts.append("Top related memories:")
            for idx, memory in enumerate(semantic_memories, start=1):
                content = memory.get("content", "").strip()
                mtype = memory.get("type", "fact")
                if content:
                    parts.append(f"{idx}. [{mtype}] {content}")

        if user_profile:
            profile_text = ", ".join(f"{k}: {v}" for k, v in user_profile.items())
            parts.append(f"User profile: {profile_text}")

        if not parts:
            return "No long-term memory context."
        return "\n".join(parts)

    @staticmethod
    def _normalize_improve_instruction(instruction: str) -> str:
        """
        Provides a stable improvement instruction for the websearch agent.
        """
        text = (instruction or "").strip()
        if not text:
            return "No need to improve in response, we are doing good."
        return text

    def _parse_search_results(self, messages: list):
        """
        Parses JSON search results from ToolMessages.

        Each search tool returns {query, images, results}. This collects
        results (deduplicated by URL) and all top-level images.

        Returns:
            Tuple of (unique_results, all_images).
        """
        unique_results = []
        all_images = []
        seen_urls = set()
        seen_image_urls = set()

        import json

        for msg in messages:
            if not isinstance(msg, ToolMessage) or not msg.content:
                continue

            try:
                data = json.loads(msg.content)
                if not isinstance(data, dict) or "results" not in data:
                    continue

                for item in data.get("results", []):
                    url = item.get("url")
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    unique_results.append({
                        "title": item.get("title", "No Title"),
                        "url": url,
                        "content": item.get("content", ""),
                    })

                for img in data.get("images", []):
                    img_url = img.get("url", "")
                    if img_url and img_url not in seen_image_urls:
                        seen_image_urls.add(img_url)
                        all_images.append(img)

            except json.JSONDecodeError:
                continue

        return unique_results, all_images


async def websearch_agent_node(state: AgentGraphState, writer: StreamWriter = None) -> Dict[str, Any]:
    """LangGraph node entry point — creates WebSearchAgent and runs search."""
    emitter = get_emitter(writer)
    agent = WebSearchAgent(emitter)
    return await agent.search(state)
