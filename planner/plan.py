"""
Planner Node for LangGraph Agent.

This module implements the Planner class which analyzes user queries,
uses memory context for informed planning, and generates structured
research plans or clarifying questions.
"""

from typing import Dict, Any, List, Optional
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llms.llms import LlmsHouse
from researcher.solution_tree.prompts.prompts import get_plan_prompt, get_clarifying_questions_prompt
from graphs.states.subgraph_state import AgentGraphState, PlannerQuery, MemoryContext
import logging

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
        
        Args:
            memory_facade: Optional MemoryFacade for context retrieval.
        """
        self.llm = LlmsHouse.google_model("gemini-2.5-flash")
        self.parser = JsonOutputParser()
        self.chain = self.llm | self.parser
        self._memory = memory_facade

    def _build_context_prompt(self, state: AgentGraphState) -> str:
        """
        Builds context string from memory_context for LLM prompt.
        
        Formats semantic memories, user profile, and conversation summary
        into a readable context block for the planning prompt.
        
        Args:
            state: Current state containing memory_context.
            
        Returns:
            Formatted context string or empty string if no context.
        """
        memory_context = state.get("memory_context")
        if not memory_context:
            return ""
            
        sections = []
        
        user_profile = memory_context.get("user_profile")
        if user_profile:
            profile_items = [f"{k}: {v}" for k, v in user_profile.items()]
            sections.append(f"[User Profile]\n{', '.join(profile_items)}")
            
        semantic_memories = memory_context.get("semantic_memories", [])
        if semantic_memories:
            memory_lines = [f"- {m.get('content', '')}" for m in semantic_memories if m.get('content')]
            if memory_lines:
                sections.append("[Known User Facts]\n" + "\n".join(memory_lines))
                
        conversation_summary = memory_context.get("conversation_summary")
        if conversation_summary:
            sections.append(f"[Previous Context]\n{conversation_summary}")
            
        if not sections:
            return ""
            
        return "\n\n".join(sections)

    def _generate_plan(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Generates a comprehensive research plan using query and memory context.
        
        Incorporates user's memory context (preferences, past research, profile)
        to generate more personalized and relevant research plans.
        If plan_feedback is present (from HITL rejection), incorporates
        feedback for refined plan generation.
        
        Args:
            state: Current state containing user_query and memory_context.
            
        Returns:
            State update with 'planner_query' list populated.
        """
        query = state.get("user_query")
        if not query:
            logger.warning("User query not found in state.")
            return {"planner_query": []}

        context_prompt = self._build_context_prompt(state)
        
        plan_feedback = state.get("plan_feedback", "")
        
        if plan_feedback:
            complete_query = (
                f"User Original Query: {query}\n\n"
                f"Plan Generated Before Feedback: {state.get('planner_query', [])}\n\n"
                f"[User Feedback on Previous Plan]:\n{plan_feedback}"
            )
            logger.info(f"Regenerating plan with user feedback: {plan_feedback}")
        else:
            complete_query = query
            
        if context_prompt:
            complete_query = f"{context_prompt}\n\n[User Query]\n{complete_query}"

        def _to_numbered_queries(plan_list: list) -> list:
            """Convert plain query list to PlannerQuery format with query_num."""
            return [{"query_num": i + 1, "query": q} for i, q in enumerate(plan_list)]

        logger.info(f"Generating plan for query: {query[:100]}...")
        prompt = get_plan_prompt(complete_query)

        try:
            result = self.chain.invoke(prompt)
            plan = result.get("plan", [])
            logger.info(f"Generated plan with {len(plan)} steps.")
            return {"planner_query": _to_numbered_queries(plan)}

        except OutputParserException as e:
            logger.error(f"Failed to parse plan: {e}")
            return {"planner_query": _to_numbered_queries([query])}
        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            return {"planner_query": _to_numbered_queries([query])}

    def ask_question(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Generates clarifying questions for ambiguous queries.
        
        Uses memory context to avoid asking about known user preferences.
        Returns questions that can be presented to user via HITL interrupt.
        
        Args:
            state: Current state containing user_query and memory_context.
            
        Returns:
            Dict with 'clarifying_questions' list of question strings.
        """
        query = state.get("user_query", "")
        if not query:
            return {"clarifying_questions": []}
            
        context_prompt = self._build_context_prompt(state)
        
        prompt_query = query
        if context_prompt:
            prompt_query = f"{context_prompt}\n\n[User Query]\n{query}"
            
        prompt = get_clarifying_questions_prompt(prompt_query)
        
        try:
            result = self.chain.invoke(prompt)
            questions = result.get("questions", [])
            
            if not questions and result.get("ask_question") == "no":
                return {"clarifying_questions": [], "needs_clarification": False}
                
            logger.info(f"Generated {len(questions)} clarifying questions")
            return {"clarifying_questions": questions, "needs_clarification": len(questions) > 0}
            
        except Exception as e:
            logger.error(f"Error generating clarifying questions: {e}")
            return {"clarifying_questions": [], "needs_clarification": False}

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
                    "question": result.get("feedback_question", f"Please provide feedback on: {topic}"),
                    "options": result.get("options", [])
                }
            }
        except Exception as e:
            logger.error(f"Error generating feedback request: {e}")
            return {
                "feedback_request": {
                    "topic": topic,
                    "question": f"Please provide feedback on: {topic}",
                    "options": []
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
                "scope_feedback": f"Plan has {num_queries} queries, consider narrowing scope"
            }
        elif num_queries < 2:
            return {
                "scope_valid": False, 
                "scope_feedback": "Plan may be too narrow, consider expanding research areas"
            }
            
        return {"scope_valid": True, "scope_feedback": "Plan scope is appropriate"}

    def editor(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Edits existing report based on user instructions.
        
        Reads edit_instructions and current report sections, uses LLM
        to apply targeted edits. Skips research phase and goes directly
        to publisher after editing.
        
        Args:
            state: State with edit_instructions and current report sections.
            
        Returns:
            State update with modified report sections.
        """
        edit_instructions = state.get("edit_instructions", "")
        if not edit_instructions:
            logger.warning("[Editor] No edit instructions provided")
            return {}
        
        report_body = state.get("report_body", "")
        report_abstract = state.get("report_abstract", "")
        report_introduction = state.get("report_introduction", "")
        report_conclusion = state.get("report_conclusion", "")
        
        prompt = f"""You are editing an existing research report.

## Edit Instructions
{edit_instructions}

## Current Report Sections

### Abstract
{report_abstract}

### Introduction
{report_introduction}

### Body
{report_body}

### Conclusion
{report_conclusion}

Apply the requested edits to the appropriate sections. Return JSON with only the sections that need changes:
{{
    "report_abstract": "updated abstract or null if no changes",
    "report_introduction": "updated intro or null if no changes",
    "report_body": "updated body or null if no changes",
    "report_conclusion": "updated conclusion or null if no changes"
}}
"""
        
        try:
            result = self.chain.invoke(prompt)
            updates = {}
            
            for key in ["report_abstract", "report_introduction", "report_body", "report_conclusion"]:
                if result.get(key) and result[key] != "null":
                    updates[key] = result[key]
            
            logger.info(f"[Editor] Applied edits to {len(updates)} sections")
            return updates
            
        except Exception as e:
            logger.error(f"[Editor] Error applying edits: {e}")
            return {}


def planner_node(state: AgentGraphState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for Planner.
    
    Reads user_query and memory_context from state, generates
    planner_query (list of research queries) using context-aware planning.
    """
    planner = Planner()
    return planner._generate_plan(state)


def editor_node(state: AgentGraphState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for report editing.
    
    Reads edit_instructions and current report sections,
    applies targeted edits using LLM.
    """
    planner = Planner()
    return planner.editor(state)


