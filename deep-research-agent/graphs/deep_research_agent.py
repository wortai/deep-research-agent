"""
Deep Research Agent - Main LangGraph.

This module implements DeepResearchAgent class that orchestrates:
1. Router Node: Uses search_mode and context to route workflow
2. Planner Node: Generates research queries from user input
3. Human Review Node: Pauses for user approval of the plan
4. Parallel Research: Invokes researcher-reviewer subgraph for each query
5. Writer Node: Aggregates research and generates final report sections
6. Response Node: Composes final response for frontend

Supports short-term (conversation) and long-term (semantic) memory
through the MemoryFacade integration.
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional

from langgraph.graph import StateGraph, END
from langgraph.types import Command
import uuid
from datetime import datetime

from graphs.states.subgraph_state import (
    AgentGraphState,
    ResearchReviewData,
    MemoryContext,
)
from graphs.subgraphs.researcher_reviewer_subgraph import (
    build_researcher_reviewer_subgraph,
)
from planner.plan import planner_node, clarification_node, human_clarification_node
from planner.query_validator import MAX_PLAN_QUERIES
from editor.editor_node import editor_node
from writer.report_writer import writer_node
from HITL.human_in_loop import human_review_node, HumanPlanReview
from router.intent_router import router_node
from response.response_composer import response_node
from websearch_agent import websearch_agent_node
from memory import MemoryFacade
from memory.memory_compactor import memory_node

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepResearchAgent:
    """
    Main agent orchestrating the deep research workflow.

    Coordinates planner, human review, parallel research, and report writing
    through a LangGraph state machine with interrupt/resume support.
    """

    def __init__(
        self, db_uri: Optional[str] = None, memory: Optional[MemoryFacade] = None
    ):
        """
        Initialize agent with memory system and build the compiled graph.

        Args:
            db_uri: PostgreSQL connection string for memory persistence.
            memory: Optional existing MemoryFacade instance for shared state.
        """
        self._db_uri = db_uri or os.getenv("DATABASE_URL")

        # Use provided memory or create new one (which handles DB or in-memory)
        self._memory = memory or MemoryFacade(self._db_uri)
        self._checkpointer = self._memory.checkpointer

        self._graph = self._build_graph()
        self._plan_formatter = HumanPlanReview()

    def _build_graph(self) -> StateGraph:
        """
        Builds the LangGraph workflow with all nodes and edges.

        Flow:
            router_node → [search_mode routing]
                ├── websearch → websearch_agent → response_node → END
                └── deepsearch/extremesearch → clarification_node ⟲(max 2) → planner_node → human_review_node → parallel_research_node → writer_node → response_node → END

        Returns:
            Compiled StateGraph with checkpointer for interrupt/resume.
        """
        workflow = StateGraph(AgentGraphState)

        workflow.add_node("router_node", router_node)
        workflow.add_node("clarification_node", clarification_node)
        workflow.add_node("human_clarification_node", human_clarification_node)
        workflow.add_node("planner_node", planner_node)
        workflow.add_node("editor_node", editor_node)
        workflow.add_node("websearch_agent", websearch_agent_node)
        workflow.add_node("writer_node", writer_node)
        workflow.add_node("response_node", response_node)
        workflow.add_node("memory_node", memory_node)
        workflow.add_node("parallel_research_node", self._parallel_research_node)
        workflow.add_node("human_review_node", human_review_node)

        workflow.set_entry_point("router_node")

        workflow.add_conditional_edges(
            "router_node",
            self._route_by_mode,
            {
                "websearch": "websearch_agent",
                "deepsearch": "clarification_node",
                "extremesearch": "clarification_node",
                "edit": "editor_node",
            },
        )

        workflow.add_edge("websearch_agent", "response_node")

        # Clarification loop: loops back up to 2 times, then proceeds to skill selection
        workflow.add_conditional_edges(
            "clarification_node",
            self._route_after_clarification,
            {
                "human_clarification_node": "human_clarification_node",
                "planner_node": "planner_node",
            },
        )

        # After human clarification, go back to clarification node to see if we need more
        workflow.add_edge("human_clarification_node", "clarification_node")

        workflow.add_edge("planner_node", "human_review_node")
        workflow.add_conditional_edges(
            "human_review_node",
            self._route_after_review,
            {
                "parallel_research_node": "parallel_research_node",
                "planner_node": "planner_node",
            },
        )
        workflow.add_edge("parallel_research_node", "writer_node")
        workflow.add_edge("writer_node", "response_node")
        workflow.add_edge("editor_node", "response_node")

        workflow.add_edge("response_node", "memory_node")
        workflow.add_edge("memory_node", END)

        return workflow.compile(checkpointer=self._checkpointer)

    def _route_by_mode(self, state: AgentGraphState) -> str:
        """
        Routes based on normalized search_mode from router_node.

        Returns:
            Next node for web/deep/extreme/edit orchestration.
        """
        mode = state.get("search_mode", "deepsearch")
        if mode not in {"websearch", "deepsearch", "extremesearch", "edit"}:
            return "deepsearch"
        return mode

    def _route_after_clarification(self, state: AgentGraphState) -> str:
        """
        Routes after a clarification round.

        If the user explicitly skipped clarification, proceeds directly
        to planner_node. Otherwise continues looping to
        human_clarification_node if under the 2-loop max and the LLM
        indicated more clarification is needed (by providing questions).

        Returns:
            'human_clarification_node' to ask user, or 'planner_node' to proceed.
        """
        # Explicit skip takes priority over everything
        if state.get("skip_clarification", False):
            return "planner_node"

        loop_count = state.get("clarification_loop_count", 0)
        questions = state.get("clarification_questions", [])

        if loop_count < 2 and questions:
            return "human_clarification_node"

        return "planner_node"

    def _route_after_review(self, state: AgentGraphState) -> str:
        """
        Routes based on plan approval status.

        Returns:
            'parallel_research_node' if approved, 'planner_node' if feedback needed.
        """
        if state.get("plan_approved", False):
            return "parallel_research_node"
        return "planner_node"

    async def _parallel_research_node(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Invokes researcher-reviewer subgraph in parallel for each planner query.

        Takes planner_query list from state, creates one subgraph invocation per query,
        executes all in parallel using asyncio.gather, and accumulates results.

        The active analysis_level is resolved to concrete (depth, max_reviews) values
        and injected into every subgraph initial state so the researcher and reviewer
        nodes behave according to the user-selected mode.

        Args:
            state: Current state containing planner_query list and analysis_level.

        Returns:
            State update with research_review list populated.
        """
        queries = state.get("planner_query", [])

        if not queries:
            logger.warning("[parallel_research_node] No queries from planner")
            return {"research_review": []}

        if len(queries) > MAX_PLAN_QUERIES:
            raise ValueError(
                f"[parallel_research_node] BLOCKED: plan contains {len(queries)} queries "
                f"which exceeds the hard limit of {MAX_PLAN_QUERIES}. "
                "The QueryValidator should have caught this earlier."
            )

        subgraph = build_researcher_reviewer_subgraph()

        current_run_id = state.get("current_run_id", "")
        analysis_level = state.get("analysis_level", "low")

        # Map analysis_level to concrete research parameters.
        # Defined locally — the mapping is only meaningful here where subgraphs
        # are spawned, so it doesn't belong as a class-level constant.
        level_params = {
            "low": {"depth": 2, "max_reviews": 2},
            "mid": {"depth": 2, "max_reviews": 3},
            "high": {"depth": 3, "max_reviews": 2},
        }
        params = level_params.get(analysis_level, level_params["low"])

        logger.info(
            f"[parallel_research_node] analysis_level={analysis_level!r} → "
            f"depth={params['depth']}, max_reviews={params['max_reviews']} "
            f"for {len(queries)} queries"
        )

        async def invoke_subgraph(planner_query: dict) -> ResearchReviewData:
            """Invoke subgraph for a single query with analysis parameters injected."""
            query = planner_query["query"]
            query_num = planner_query["query_num"]

            initial_state = {
                "query": query,
                "query_num": query_num,
                "run_id": current_run_id,
                "raw_research_results": [],
                "review_feedback": [],
                "current_reviews": [],
                "iteration_count": 0,
                "logs": [],
                "clarification_context": state.get("clarification_answers", []),
                "depth": params["depth"],
                "max_reviews": params["max_reviews"],
            }
            result = await subgraph.ainvoke(initial_state)
            return result

        tasks = [invoke_subgraph(q) for q in queries]
        results = await asyncio.gather(*tasks)

        return {"research_review": list(results)}

    # -------------------------------------------------------------------------
    # State factory helpers
    # -------------------------------------------------------------------------

    def _create_initial_state(
        self,
        user_query: str,
        search_mode: str = "deepsearch",
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None,
        analysis_level: str = "low",
        api_keys: Optional[Dict[str, str]] = None,
        model_selections: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Creates initial state dictionary for graph invocation.

        Args:
            user_query: The research question to investigate.
            search_mode: Search mode from frontend (websearch/deepsearch/extremesearch).
            thread_id: Optional conversation thread ID. Auto-generated if None.
            user_id: Optional user ID for long-term memory. Defaults to 'default_user'.
            analysis_level: Deep analysis intensity ('low', 'mid', or 'high').

        Returns:
            Initial state with all fields set to defaults including memory context.
        """
        new_message = {
            "message_id": str(uuid.uuid4()),
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat(),
        }

        normalized_mode = self._normalize_search_mode(search_mode)
        safe_level = (analysis_level or "low").strip().lower()
        if safe_level not in {"low", "mid", "high"}:
            safe_level = "low"

        return {
            "thread_id": thread_id or str(uuid.uuid4()),
            "user_id": user_id or "00000000-0000-0000-0000-000000000000",
            "chat_messages": [new_message],
            "memory_context": MemoryContext(
                semantic_memories=[], user_profile=None, conversation_summary=None
            ),
            "user_query": user_query,
            "current_run_id": str(uuid.uuid4()),
            "search_mode": normalized_mode,
            "analysis_level": safe_level,
            "router_thinking": "",
            "improve_in_response": "",
            "total_agents": 0,
            "completed_agents": 0,
            "total_research_steps": 0,
            "completed_research_steps": 0,
            "current_phase": "routing",
            "planner_query": [],
            "clarification_questions": [],
            "clarification_answers": [],
            "clarification_loop_count": 0,
            "skip_clarification": False,
            "plan_feedback": "",
            "plan_approved": False,
            "research_review": [],
            "reports": [],
            "websearch_results": [],
            "final_response": "",
            "api_keys": api_keys or {},
            "model_selections": model_selections or {},
        }

    def _create_update_state(
        self,
        user_query: str,
        search_mode: str,
        thread_id: str,
        user_id: str = "00000000-0000-0000-0000-000000000000",
        analysis_level: str = "low",
        api_keys: Optional[Dict[str, str]] = None,
        model_selections: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Creates a partial state update for existing threads.

        Only updates fields that change per-turn, preserving report_body_sections
        and other accumulated data across follow-up questions.
        """
        new_message = {
            "message_id": str(uuid.uuid4()),
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat(),
        }

        normalized_mode = self._normalize_search_mode(search_mode)
        safe_level = (analysis_level or "low").strip().lower()
        if safe_level not in {"low", "mid", "high"}:
            safe_level = "low"

        return {
            "user_query": user_query,
            "current_run_id": str(uuid.uuid4()),
            "search_mode": normalized_mode,
            "analysis_level": safe_level,
            "chat_messages": [new_message],  # Appends due to operator.add
            "current_phase": "routing",  # Reset phase for new turn
            "user_id": user_id,
            "improve_in_response": "",
            "api_keys": api_keys or {},
            "model_selections": model_selections or {},
        }

    @staticmethod
    def _normalize_search_mode(search_mode: str) -> str:
        """Normalizes frontend mode strings to supported graph values."""
        normalized = (search_mode or "").strip().lower()
        if normalized in {"websearch", "web"}:
            return "websearch"
        if normalized in {"extremesearch", "extreme_search", "extreme"}:
            return "extremesearch"
        if normalized == "edit":
            return "edit"
        return "deepsearch"

    async def run(
        self,
        user_query: str,
        search_mode: str = "deepsearch",
        thread_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute deep research with HITL interrupt loop.

        Handles the interrupt/resume cycle for plan approval. When graph
        hits interrupt at human_review_node, displays plan via terminal and
        resumes with Command(resume=value).

        Args:
            user_query: The research question to investigate.
            search_mode: Search mode (default: deepsearch).
            thread_id: Optional existing thread ID for memory.

        Returns:
            Final state containing report content and metadata.
        """
        thread_id = thread_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = self._create_initial_state(
            user_query, search_mode=search_mode, thread_id=thread_id
        )

        # logger.info(f"[run] Starting research for: {user_query}")

        # Check if state exists to decide between Init vs Update
        current_state = await self._graph.aget_state(config)
        state_exists = bool(current_state.values)

        if state_exists:
            # logger.info(f"[run] Thread {thread_id} exists - updating state")
            initial_state = self._create_update_state(
                user_query, search_mode=search_mode, thread_id=thread_id
            )
        else:
            # logger.info(f"[run] Thread {thread_id} new - initializing full state")
            initial_state = self._create_initial_state(
                user_query, search_mode=search_mode, thread_id=thread_id
            )

        if self._memory:
            await self._memory.initialize()

            # Populate memory context for the planner
            memory_context = await self._memory.get_context_for_planner(
                thread_id=thread_id,
                user_id=initial_state["user_id"],
                current_query=user_query,
                search_mode=initial_state.get("search_mode", "deepsearch"),
            )
            initial_state["memory_context"] = memory_context

        result = await self._graph.ainvoke(initial_state, config=config)

        while "__interrupt__" in result:
            interrupt_data = result["__interrupt__"]
            if interrupt_data:
                plan_display = self._display_plan_for_terminal(interrupt_data)
                resume_value = self._get_terminal_approval(plan_display)
                result = await self._graph.ainvoke(
                    Command(resume=resume_value), config=config
                )
            else:
                break

        # logger.info("[run] Research complete")
        return result


async def run_deep_research(
    user_query: str,
    search_mode: str = "deepsearch",
    thread_id: Optional[str] = None,
    memory: Optional[MemoryFacade] = None,
) -> Dict[str, Any]:
    """
    Convenience function to execute deep research.

    Args:
        user_query: Research question.
        search_mode: Search mode.
        thread_id: Optional thread ID for memory.
        memory: Optional shared memory instance.

    Returns:
        Final state containing report content.
    """
    agent = DeepResearchAgent(memory=memory)
    return await agent.run(user_query, search_mode, thread_id)


if __name__ == "__main__":
    import sys
    import os
    from datetime import datetime

    async def main():
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
        else:
            query = "How Neural Networks works"

        # Example of persistent thread with shared memory
        thread_id = str(uuid.uuid4())
        print(f"Starting research with thread_id: {thread_id}")

        # Create shared memory instance
        memory = MemoryFacade()
        await memory.initialize()

        # First turn
        result = await run_deep_research(query, "deepsearch", thread_id, memory)

        # Simulate follow-up in same thread (memory persistence)
        # follow_up = await run_deep_research("What about transformers?", "follow_up", thread_id, memory)

        report_markdown = format_report_markdown(result, query)

    asyncio.run(main())
