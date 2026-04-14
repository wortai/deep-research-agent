"""
Planner Node for LangGraph Agent.

This module implements the Planner class which analyzes user queries,
uses memory context for informed planning, and generates structured
research plans or clarifying questions.
"""

from typing import Dict, Any, List, Optional
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from langgraph.types import StreamWriter, interrupt
from llms.llms import LlmsHouse
from researcher.solution_tree.prompts.prompts import (
    get_clarifying_questions_prompt,
    get_clarification_prompt,
    get_enhanced_plan_prompt,
    PlanResult,
)
from graphs.states.subgraph_state import AgentGraphState, PlannerQuery, MemoryContext
from graphs.events.frontend_events import create_event, EventType, PhaseType
from planner.query_validator import QueryValidator
from utils.errors import LLMCatchError
import logging
import uuid
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Planner:
    """
    Planner Node that uses memory context for informed plan generation.

    Responsibilities:
    1. Generate step-by-step research plans using user query and memory context.
    2. Ask clarifying questions when query is ambiguous.
    3. Request feedback on specific topics from user.
    """

    def __init__(self, memory_facade: Optional[Any] = None):
        """
        Initialize the Planner with LLM and optional memory facade.
        """
        self.llm = LlmsHouse.grok_model("grok-4-1-fast-reasoning", temperature=1.25)
        self.fallback_llm = LlmsHouse.get_fallback_model(temperature=1.25)

    def _build_chat_memory(self, state: AgentGraphState) -> str:
        """
        Builds context string from long-term memory and recent conversation history.

        Long-term memory (user profile + semantic memories) comes from
        state['memory_context'], populated upstream by MemoryFacade.get_context_for_planner
        which performs semantic search with cross-encoder reranking.

        Short-term memory is the last 10 chat_messages from state, providing
        immediate conversational context without overwhelming the prompt.

        Args:
            state: Current state containing memory_context and chat_messages.

        Returns:
            Formatted context string or empty string if no context available.
        """
        MAX_RECENT_MESSAGES = 10
        sections = []

        memory_context = state.get("memory_context")
        if memory_context:
            user_profile = memory_context.get("user_profile")
            if user_profile:
                profile_items = [f"{k}: {v}" for k, v in user_profile.items()]
                sections.append(f"[User Profile]\n{', '.join(profile_items)}")

            semantic_memories = memory_context.get("semantic_memories", [])
            if semantic_memories:
                memory_lines = [
                    f"- {m.get('content', '')}"
                    for m in semantic_memories
                    if m.get("content")
                ]
                if memory_lines:
                    sections.append("[Relevant Memories]\n" + "\n".join(memory_lines))

            conversation_summary = memory_context.get("conversation_summary")
            if conversation_summary:
                sections.append(f"[Conversation Summary]\n{conversation_summary}")

        chat_messages = state.get("chat_messages", [])
        recent_messages = chat_messages[-MAX_RECENT_MESSAGES:] if chat_messages else []
        if recent_messages:
            formatted_msgs = []
            for msg in recent_messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if content and role in ("user", "assistant"):
                    formatted_msgs.append(f"  {role}: {content[:300]}")
            if formatted_msgs:
                sections.append("[Recent Conversation]\n" + "\n".join(formatted_msgs))

        if not sections:
            return ""

        return "\n\n".join(sections)

    def _generate_plan(
        self, state: AgentGraphState, writer: StreamWriter = None
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive research plan using query and memory context.

        Incorporates user's memory context (preferences, past research, profile)
        to generate more personalized and relevant research plans.
        If plan_feedback is present (from HITL rejection), incorporates
        feedback for refined plan generation.

        Args:
            state: Current state containing user_query and memory_context.
            writer: Optional LangGraph writer for streaming events.

        Returns:
            State update with 'planner_query' list populated.
        """
        query = state.get("user_query")
        if not query:
            logger.warning("User query not found in state.")
            return {"planner_query": []}

        context_prompt = self._build_chat_memory(state)

        plan_feedback = state.get("plan_feedback", "")

        if plan_feedback:
            complete_query = (
                f"User Original Query: {query}\n\n"
                f"Plan Generated Before Feedback: {state.get('planner_query', [])}\n\n"
                f"[User Feedback on Previous Plan]:\n{plan_feedback}\n\n"
                f"CRITICAL INSTRUCTION REGARDING FEEDBACK: Formulate the queries EXACTLY as the user requested in the feedback above. If the user provided a single query, return EXACTLY 1 query. If they provided a list, return exactly that list without splitting it further."
            )
            logger.info(f"Regenerating plan with user feedback: {plan_feedback}")
        else:
            complete_query = query

        if context_prompt:
            complete_query = f"{context_prompt}\n\n[User Query]\n{complete_query}"

        clarification_answers = state.get("clarification_answers", [])

        prompt = get_enhanced_plan_prompt(
            query=complete_query,
            skill_instructions="",
            clarification_context=clarification_answers,
        )
        logger.info("Using standard plan prompt")

        validator = QueryValidator()

        def _to_numbered_queries(plan_list: list) -> list:
            return [{"query_num": i + 1, "query": q} for i, q in enumerate(plan_list)]

        def _build_state_update(raw_plan: list) -> Dict[str, Any]:
            validated = validator.validate_and_fix(raw_plan, query)
            numbered = _to_numbered_queries(validated)
            plan_content = "Tasks:\n\n" + "\n\n".join(
                f"Agent_{q['query_num'] // 10}_{q['query_num'] % 10} Subagent's task: {q['query']}"
                for q in numbered
            )
            plan_message = {
                "message_id": str(uuid.uuid4()),
                "role": "assistant",
                "content": plan_content,
                "timestamp": datetime.now().isoformat(),
                "tool_calls": None,
                "tool_results": None,
                "message_type": "plan",
                "metadata": {"raw_plan": validated},
            }
            return {"planner_query": numbered, "chat_messages": [plan_message]}

        logger.info(f"Generating plan for query: {query[:100]}...")

        try:
            structured_llm = self.llm.with_structured_output(PlanResult)
            result = structured_llm.invoke(prompt)
            logger.info(f"Generated plan with {len(result.plan)} steps.")
            return _build_state_update(result.plan)

        except Exception as e:
            logger.error(f"Error generating plan: {e}")

            if self.fallback_llm:
                try:
                    logger.info("[Planner] Retrying plan generation with fallback model")
                    structured_llm = self.fallback_llm.with_structured_output(PlanResult)
                    result = structured_llm.invoke(prompt)
                    logger.info(f"Generated plan with fallback ({len(result.plan)} steps).")
                    return _build_state_update(result.plan)
                except Exception as fb_err:
                    error_msg = f"[Planner] Fallback plan generation also failed: {fb_err}"
                    logger.error(error_msg)
                    raise LLMCatchError(
                        message=error_msg,
                        error_details="Both main and fallback LLM failed to generate a valid plan."
                    )

            # If no fallback llm exists
            error_msg = f"Error generating plan: {e}"
            raise LLMCatchError(message=error_msg, error_details="Main LLM failed and no fallback available.")

    def generate_clarification_questions(
        self, state: AgentGraphState, writer: StreamWriter = None
    ) -> List[str]:
        """
        Generates clarification questions using LLM without interruption.

        Invokes get_clarification_prompt, gets 2-3 questions and returns them.
        Emits CLARIFICATION_STARTED event via StreamWriter.
        """
        user_query = state.get("user_query", "")
        previous_answers = state.get("clarification_answers", [])
        loop_count = state.get("clarification_loop_count", 0)
        context_prompt = self._build_chat_memory(state)

        contextual_query = user_query
        if context_prompt:
            contextual_query = f"{context_prompt}\n\n[User Query]\n{user_query}"

        if writer:
            writer(
                create_event(
                    EventType.CLARIFICATION_STARTED,
                    PhaseType.CLARIFYING,
                    payload={
                        "message": "Analyzing research deep context...",
                        "loop_number": loop_count + 1,
                    },
                )
            )

        prompt = get_clarification_prompt(
            user_query=contextual_query,
            previous_answers=previous_answers,
            loop_number=loop_count + 1,
        )

        from pydantic import BaseModel, Field
        from typing import List

        class ClarificationResult(BaseModel):
            needs_more_clarification: bool = Field(
                description="Whether clarification from the user is needed."
            )
            questions: List[str] = Field(
                description="List of clarification questions to ask."
            )

        try:
            structured_llm = self.llm.with_structured_output(ClarificationResult)
            result = structured_llm.invoke(prompt)

            questions = result.questions
            needs_more = result.needs_more_clarification

            if not questions or not needs_more:
                logger.info("[Planner] No clarification needed, proceeding")
                return []

            return questions

        except Exception as e:
            logger.error(f"[Planner] Clarification generation failed: {e}")

            if self.fallback_llm:
                try:
                    logger.info("[Planner] Retrying clarification with fallback model")
                    structured_llm = self.fallback_llm.with_structured_output(
                        ClarificationResult
                    )
                    result = structured_llm.invoke(prompt)
                    questions = result.questions
                    needs_more = result.needs_more_clarification
                    if not questions or not needs_more:
                        logger.info(
                            "[Planner] Fallback: no clarification needed, proceeding"
                        )
                        return []
                    return questions
                except Exception as fb_err:
                    logger.error(
                        f"[Planner] Fallback clarification also failed: {fb_err}"
                    )

            return []

    def request_feedback(self, state: AgentGraphState, topic: str) -> Dict[str, Any]:
        """
        Generates a feedback request for user on a specific topic.

        Used when the planner needs user input on a specific aspect
        of the research plan or query interpretation.

        Args:
            state: Current state.
            topic: The topic or aspect to request feedback on.

        Returns:
            Dict with 'feedback_request' containing the formatted request.
        """
        query = state.get("user_query", "")

        prompt = f"""Given the user's research query: "{query}"

Generate a clear, concise feedback request about: {topic}

The request should:
1. Be specific about what input is needed
2. Explain why this input would help the research
3. Provide 2-3 example options if applicable

Return JSON with:
- "feedback_topic": brief topic name
- "feedback_question": the question to ask
- "options": list of suggested options (can be empty)
"""

        try:
            result = self.chain.invoke(prompt)
            logger.info(f"Generated feedback request for topic: {topic}")
            return {
                "feedback_request": {
                    "topic": result.get("feedback_topic", topic),
                    "question": result.get(
                        "feedback_question", f"Please provide feedback on: {topic}"
                    ),
                    "options": result.get("options", []),
                }
            }
        except Exception as e:
            logger.error(f"Error generating feedback request: {e}")
            return {
                "feedback_request": {
                    "topic": topic,
                    "question": f"Please provide feedback on: {topic}",
                    "options": [],
                }
            }

    def validate_plan_scope(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Validates if the generated plan scope is appropriate.

        Checks if the plan is too broad, too narrow, or well-scoped
        for the user's query and available context.

        Args:
            state: Current state with planner_query.

        Returns:
            Dict with 'scope_valid' bool and 'scope_feedback' string.
        """
        plan_queries = state.get("planner_query", [])
        query = state.get("user_query", "")

        if not plan_queries:
            return {"scope_valid": False, "scope_feedback": "No plan generated"}

        num_queries = len(plan_queries)

        if num_queries > 15:
            return {
                "scope_valid": False,
                "scope_feedback": f"Plan has {num_queries} queries, consider narrowing scope",
            }
        elif num_queries < 2:
            return {
                "scope_valid": False,
                "scope_feedback": "Plan may be too narrow, consider expanding research areas",
            }

        return {"scope_valid": True, "scope_feedback": "Plan scope is appropriate"}


def planner_node(state: AgentGraphState, writer: StreamWriter = None) -> Dict[str, Any]:
    """
    LangGraph node wrapper for Planner.

    Reads user_query and memory_context from state, generates
    planner_query (list of research queries) using context-aware planning.
    """
    planner = Planner()
    return planner._generate_plan(state, writer)


def clarification_node(
    state: AgentGraphState, writer: StreamWriter = None
) -> Dict[str, Any]:
    """
    LangGraph node wrapper for Clarification Generation.

    Generates mindset-probing questions and saves them to state.
    """
    planner = Planner()
    questions = planner.generate_clarification_questions(state, writer)
    return {"clarification_questions": questions}


def human_clarification_node(state: AgentGraphState) -> Dict[str, Any]:
    """
    Node that interrupts for human clarification and processes answers.

    After collecting answers, appends a compact system message to
    chat_messages summarising the clarification exchange so downstream
    nodes and future turns retain this context.
    """
    loop_count = state.get("clarification_loop_count", 0)
    questions = state.get("clarification_questions", [])

    if not questions:
        return {"clarification_loop_count": loop_count + 1}

    print("\n-------------------------------------------")
    print(f"CLARIFICATION QUESTIONS (Round {loop_count + 1}):")
    for idx, q in enumerate(questions):
        print(f"  {idx + 1}. {q}")
    print("-------------------------------------------\n")

    user_response = interrupt(
        {
            "type": "clarification",
            "questions": questions,
            "loop_number": loop_count + 1,
        }
    )

    answers_raw = user_response.get("answers", {})

    new_qa_pairs: list = []
    if isinstance(answers_raw, dict):
        for q, a in answers_raw.items():
            new_qa_pairs.append({"question": q, "answer": a})
    elif isinstance(answers_raw, list):
        for i, a in enumerate(answers_raw):
            q = questions[i] if i < len(questions) else f"Question {i + 1}"
            new_qa_pairs.append({"question": q, "answer": a})

    logger.info(
        f"[Planner] Clarification round {loop_count + 1}: "
        f"collected {len(new_qa_pairs)} answers"
    )

    summary_lines = [f"Q: {p['question']} → A: {p['answer']}" for p in new_qa_pairs]
    clarification_msg = {
        "message_id": str(uuid.uuid4()),
        "role": "system",
        "content": f"[User clarified (round {loop_count + 1})]\n"
        + "\n".join(summary_lines),
        "timestamp": datetime.now().isoformat(),
        "metadata": {"message_type": "clarification", "round": loop_count + 1},
    }

    return {
        "clarification_answers": new_qa_pairs,
        "clarification_loop_count": loop_count + 1,
        "clarification_questions": [],
        "chat_messages": [clarification_msg],
    }
