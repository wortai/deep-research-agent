"""
Deep Research Agent - Main LangGraph.

This module implements DeepResearchAgent class that orchestrates:
1. Router Node: Classifies intent and routes to appropriate workflow
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
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
import uuid
from datetime import datetime

from graphs.states.subgraph_state import AgentGraphState, ResearchReviewData, MemoryContext
from graphs.subgraphs.researcher_reviewer_subgraph import build_researcher_reviewer_subgraph
from graphs.events.frontend_events import create_event, EventType, PhaseType
from planner.plan import planner_node, editor_node
from writer.report_writer import writer_node
from HITL.human_in_loop import human_review_node, HumanPlanReview
from memory import MemoryFacade
from router.intent_router import router_node
from response.response_composer import response_node
from researcher.solution_tree.query_sol_ans import Solver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepResearchAgent:
    """
    Main agent orchestrating the deep research workflow.
    
    Coordinates planner, human review, parallel research, and report writing
    through a LangGraph state machine with interrupt/resume support.
    """

    def __init__(self, db_uri: Optional[str] = None, memory: Optional[MemoryFacade] = None):
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
            router_node → [intent routing]
                ├── websearch → parallel_solver_node → response_node → END
                ├── deepsearch/extremesearch → planner_node → human_review_node → parallel_research_node → writer_node → response_node → END
                ├── follow_up/off_topic → response_node → END
                └── edit → editor_node → response_node → END

        Returns:
            Compiled StateGraph with checkpointer for interrupt/resume.
        """
        workflow = StateGraph(AgentGraphState)

        workflow.add_node("router_node", router_node)
        workflow.add_node("planner_node", planner_node)
        workflow.add_node("editor_node", editor_node)
        workflow.add_node("human_review_node", human_review_node)
        workflow.add_node("parallel_research_node", self._parallel_research_node)
        workflow.add_node("parallel_solver_node", self._parallel_solver_node)
        workflow.add_node("writer_node", writer_node)
        workflow.add_node("response_node", response_node)

        workflow.set_entry_point("router_node")
        
        workflow.add_conditional_edges(
            "router_node",
            self._route_by_intent,
            {
                "websearch": "parallel_solver_node",
                "deepsearch": "planner_node",
                "extremesearch": "planner_node",
                "follow_up": "response_node",
                "edit": "editor_node",
                "clarification": "planner_node",
                "off_topic": "response_node",
            }
        )
        
        workflow.add_edge("parallel_solver_node", "response_node")
        
        workflow.add_edge("planner_node", "human_review_node")
        workflow.add_conditional_edges(
            "human_review_node",
            self._route_after_review,
            {
                "parallel_research_node": "parallel_research_node",
                "planner_node": "planner_node"
            }
        )
        workflow.add_edge("parallel_research_node", "writer_node")
        workflow.add_edge("writer_node", "response_node")
        
        workflow.add_edge("editor_node", "response_node")
        
        workflow.add_edge("response_node", END)

        return workflow.compile(checkpointer=self._checkpointer)

    def _route_by_intent(self, state: AgentGraphState) -> str:
        """
        Routes based on classified intent from router_node.

        Returns:
            Node name to route to based on intent_type.
        """
        intent = state.get("intent_type", "deepsearch")
        logger.info(f"[_route_by_intent] Routing to: {intent}")
        return intent

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

        Args:
            state: Current state containing planner_query list.

        Returns:
            State update with research_review list populated.
        """
        queries = state.get("planner_query", [])

        if not queries:
            logger.warning("[parallel_research_node] No queries from planner")
            return {"research_review": []}

        logger.info(f"[parallel_research_node] Starting parallel research for {len(queries)} queries")

        subgraph = build_researcher_reviewer_subgraph()

        async def invoke_subgraph(planner_query: dict) -> ResearchReviewData:
            """Invoke subgraph for a single query with query_num tracking."""
            query = planner_query["query"]
            query_num = planner_query["query_num"]

            initial_state = {
                "query": query,
                "query_num": query_num,
                "raw_research_results": [],
                "review_feedback": [],
                "current_reviews": [],
                "iteration_count": 0,
                "logs": []
            }
            result = await subgraph.ainvoke(initial_state)
            logger.info(f"[parallel_research_node] Completed research for query #{query_num}: {query[:50]}...")
            return result

        tasks = [invoke_subgraph(q) for q in queries]
        results = await asyncio.gather(*tasks)

        logger.info(f"[parallel_research_node] All {len(results)} research tasks complete")
        
        all_logs = []
        for res in results:
            if "logs" in res:
                all_logs.extend(res["logs"])
        
        # Sort logs by timestamp to keep them in order (optional but good)
        all_logs.sort(key=lambda x: x.get("timestamp", ""))

        return {"research_review": list(results), "chat_messages": all_logs}

    async def _parallel_solver_node(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Quick websearch using Solver.websearch_solver for websearch mode.

        Args:
            state: Current state containing user_query.

        Returns:
            State update with research_review populated from Tavily results.
        """
        user_query = state.get("user_query", "")
        
        if not user_query:
            logger.warning("[_parallel_solver_node] No user query provided")
            return {"research_review": []}
        
        logger.info(f"[_parallel_solver_node] Starting websearch for: {user_query[:50]}...")
        
        solver = Solver(query=user_query)
        return await solver.websearch_solver()



    def _create_initial_state(
        self, 
        user_query: str,
        search_mode: str = "deepsearch",
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates initial state dictionary for graph invocation.
        
        Args:
            user_query: The research question to investigate.
            search_mode: Search mode from frontend (websearch/deepsearch/extremesearch).
            thread_id: Optional conversation thread ID. Auto-generated if None.
            user_id: Optional user ID for long-term memory. Defaults to 'default_user'.
            
        Returns:
            Initial state with all fields set to defaults including memory context.
        """
        # Create new user message
        new_message = {
            "message_id": str(uuid.uuid4()),
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "thread_id": thread_id or str(uuid.uuid4()),
            "user_id": user_id or "default_user",
            "chat_messages": [new_message],
            "memory_context": MemoryContext(
                semantic_memories=[],
                user_profile=None,
                conversation_summary=None
            ),
            "user_query": user_query,
            "search_mode": search_mode,
            "intent_type": "",
            "total_agents": 0,
            "completed_agents": 0,
            "total_research_steps": 0,
            "completed_research_steps": 0,
            "current_phase": "routing",
            "planner_query": [],
            "plan_feedback": "",
            "plan_approved": False,
            "research_review": [],
            "report_table_of_contents": "",
            "report_abstract": "",
            "report_introduction": "",
            "report_body_sections": [],
            "report_conclusion": "",
            "report_methodology": "",
            "final_response": "",
            "edit_instructions": None
        }

    def _create_update_state(
        self,
        user_query: str,
        search_mode: str,
        thread_id: str,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Creates a partial state update for existing threads.
        Only updates fields that change per-turn, preserving report_body_sections/etc.
        """
        new_message = {
            "message_id": str(uuid.uuid4()),
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "user_query": user_query,
            "search_mode": search_mode,
            "chat_messages": [new_message], # Appends due to operator.add
            "intent_type": "", # Reset intent for new turn
            "current_phase": "routing", # Reset phase
            "user_id": user_id,
            # DO NOT reset report_body_sections, report_abstract, etc. here
        }

    async def run(
        self, 
        user_query: str, 
        search_mode: str = "deepsearch",
        thread_id: Optional[str] = None
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
            user_query, 
            search_mode=search_mode,
            thread_id=thread_id
        ) 

        logger.info(f"[run] Starting research for: {user_query}")
        
        # Check if state exists to decide between Init vs Update
        current_state = await self._graph.get_state(config)
        state_exists = bool(current_state.values)

        if state_exists:
            logger.info(f"[run] Thread {thread_id} exists - updating state")
            initial_state = self._create_update_state(
                user_query, 
                search_mode=search_mode, 
                thread_id=thread_id
            )
        else:
            logger.info(f"[run] Thread {thread_id} new - initializing full state")
            initial_state = self._create_initial_state(
                user_query, 
                search_mode=search_mode, 
                thread_id=thread_id
            )
        
        if self._memory:
            await self._memory.initialize()
            
            # Populate memory context for the planner
            memory_context = await self._memory.get_context_for_planner(
                thread_id=thread_id,
                user_id=initial_state["user_id"],
                current_query=user_query
            )
            initial_state["memory_context"] = memory_context
            
        result = await self._graph.ainvoke(initial_state, config=config)

        while "__interrupt__" in result:
            interrupt_data = result["__interrupt__"]
            if interrupt_data:
                plan_display = self._display_plan_for_terminal(interrupt_data)
                resume_value = self._get_terminal_approval(plan_display)
                result = await self._graph.ainvoke(Command(resume=resume_value), config=config)
            else:
                break

        logger.info("[run] Research complete")
        return result





async def run_deep_research(
    user_query: str, 
    search_mode: str = "deepsearch",
    thread_id: Optional[str] = None,
    memory: Optional[MemoryFacade] = None
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

    def format_report_markdown(result: Dict[str, Any], query: str) -> str:
        """Format the research result as a complete markdown report."""
        lines = []
        lines.append(f"# Research Report: {query}\n")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        lines.append("---\n")

        if result.get('report_abstract'):
            lines.append("## Abstract\n")
            lines.append(f"{result['report_abstract']}\n")
            lines.append("---\n")

        if result.get('report_introduction'):
            lines.append("## Introduction\n")
            lines.append(f"{result['report_introduction']}\n")
            lines.append("---\n")

        # Report Body (chapters and subchapters)
        body_sections = result.get('report_body_sections', [])
        for section in sorted(body_sections, key=lambda s: s.get('section_order', 0)):
            lines.append(f"{section.get('section_content', '')}\n")
        if body_sections:
            lines.append("---\n")

        if result.get('report_conclusion'):
            lines.append(f"{result['report_conclusion']}\n")

        return "\n".join(lines)

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
        result = await run_deep_research(query, "websearch", thread_id, memory)
        
        # Simulate follow-up in same thread (memory persistence)
        # follow_up = await run_deep_research("What about transformers?", "follow_up", thread_id, memory)

        report_markdown = format_report_markdown(result, query)

        output_dir = "reports"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_query = "".join(c if c.isalnum() or c == ' ' else '_' for c in query[:50]).strip().replace(' ', '_')
        file_path = f"{output_dir}/{timestamp}_{safe_query}.md"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_markdown)

        print("\n" + "=" * 80)
        print("RESEARCH COMPLETE")
        print("=" * 80)
        print(f"\n📊 Stats:")
        print(f"   - Planner Queries: {len(result.get('planner_query', []))}")
        print(f"   - Research Reviews: {len(result.get('research_review', []))}")
        print(f"   - Report Body Sections: {len(result.get('report_body_sections', []))}")
        print(f"\n📄 Report saved to: {file_path}")
        print("\n" + "=" * 80)
        if result.get('report_body_sections'):
            print("\n" + "=" * 80)
            print("FULL REPORT")
            print("=" * 80 + "\n")
            print(report_markdown)
        else:
            print("\n" + "=" * 80)
            print("SEARCH COMPLETE")
            print("=" * 80 + "\n")

    asyncio.run(main())
