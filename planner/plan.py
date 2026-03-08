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
    get_plan_prompt,
    get_clarifying_questions_prompt,
    get_clarification_prompt,
    get_skill_selection_prompt,
    get_enhanced_plan_prompt,
    get_report_style_prompt,
    SkillSelectionResult,
    PlanResult
)
from graphs.states.subgraph_state import AgentGraphState, PlannerQuery, MemoryContext
from graphs.events.frontend_events import create_event, EventType, PhaseType
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
        
        Args:
            memory_facade: Optional MemoryFacade for context retrieval.
        """
        self.llm = LlmsHouse.google_model("gemini-2.5-flash")
        self._memory = memory_facade
        self._skills_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "skills"
        )

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

    def _generate_plan(self, state: AgentGraphState, writer: StreamWriter = None) -> Dict[str, Any]:
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

        context_prompt = self._build_context_prompt(state)

        
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

        # Use skill-enhanced planning if skills were selected
        selected_skills = state.get("selected_skills", [])
        clarification_answers = state.get("clarification_answers", [])

        if selected_skills:
            skill_contents = self._load_available_skills()
            merged_instructions = "\n\n".join(
                f"=== SKILL: {s} ===\n{skill_contents[s]}"
                for s in selected_skills if s in skill_contents
            )
            prompt = get_enhanced_plan_prompt(
                query=complete_query,
                skill_instructions=merged_instructions,
                clarification_context=clarification_answers
            
            )
            logger.info(f"Using skill-enhanced plan with skills: {selected_skills}")
        else:
            prompt = get_plan_prompt(complete_query)
            logger.info("Using standard plan prompt (no skills selected)")

        def _to_numbered_queries(plan_list: list) -> list:
            """Convert plain query list to PlannerQuery format with query_num."""
            return [{"query_num": i + 1, "query": q} for i, q in enumerate(plan_list)]

        logger.info(f"Generating plan for query: {query[:100]}...")

        try:
            structured_llm = self.llm.with_structured_output(PlanResult)
            result = structured_llm.invoke(prompt)
            
            plan = result.plan
            logger.info(f"Generated plan with {len(plan)} steps.")
            numbered_plan = _to_numbered_queries(plan)
            plan_content = "Research Plan:\n" + "\n".join([f"{q['query_num']}. {q['query']}" for q in numbered_plan])
            
            plan_message = {
                "message_id": str(uuid.uuid4()),
                "role": "assistant",
                "content": plan_content,
                "timestamp": datetime.now().isoformat(),
                "tool_calls": None,
                "tool_results": None,
                "message_type": "plan",
                "metadata": {"raw_plan": plan, "skills_used": selected_skills}
            }
            
            return {
                "planner_query": numbered_plan,
                "chat_messages": [plan_message]
            }

        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            return {"planner_query": _to_numbered_queries([query])}

    def _load_available_skills(self) -> Dict[str, str]:
        """
        Reads all .md skill files from the planner/skills/ directory.

        Returns:
            Dict mapping skill filename (e.g. 'coding_tech.md') to
            the full markdown content of that file.
        """
        skills = {}
        if not os.path.isdir(self._skills_dir):
            logger.warning(f"[Planner] Skills directory not found: {self._skills_dir}")
            return skills

        for filename in sorted(os.listdir(self._skills_dir)):
            if filename.endswith(".md"):
                filepath = os.path.join(self._skills_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    skills[filename] = f.read()

        logger.info(f"[Planner] Loaded {len(skills)} research skills: {list(skills.keys())}")
        return skills

    def _select_skills(self, state: AgentGraphState, writer: StreamWriter = None) -> Dict[str, Any]:
        """
        Uses LLM with structured output to select 1-4 skills for the query.

        Reads user_query and clarification_answers from state, loads all
        available skills, invokes get_skill_selection_prompt with
        SkillSelectionResult structured output, and returns selected filenames.
        Emits SKILL_SELECTION_COMPLETED event via StreamWriter.

        Args:
            state: Current state containing user_query and clarification_answers.
            writer: Optional StreamWriter for emitting frontend events.

        Returns:
            State update with 'selected_skills' list of filenames.
        """
        user_query = state.get("user_query", "")
        clarification_answers = state.get("clarification_answers", [])
        available_skills = self._load_available_skills()

        if not available_skills:
            logger.warning("[Planner] No skills available, skipping selection")
            return {"selected_skills": []}

        if writer:
            writer(create_event(
                EventType.PLANNER_PROGRESS,
                PhaseType.PLANNING,
                payload={"message": "Analyzing query to select research skills..."}
            ))

        prompt = get_skill_selection_prompt(
            user_query=user_query,
            clarification_context=clarification_answers,
            available_skills=available_skills
        )

        try:
            structured_llm = self.llm.with_structured_output(SkillSelectionResult)
            result = structured_llm.invoke(prompt)

            valid_skills = [
                s for s in result.selected_skills
                if s in available_skills
            ][:4]

            if not valid_skills:
                logger.warning("[Planner] LLM returned no valid skill names, using general_academic.md")
                valid_skills = ["general_academic.md"]

            logger.info(f"[Planner] Selected skills: {valid_skills} — Reasoning: {result.reasoning}")

            if writer:
                skill_labels = [s.replace('.md', '').replace('_', ' ').title() for s in valid_skills]
                writer(create_event(
                    EventType.SKILL_SELECTION_COMPLETED,
                    PhaseType.PLANNING,
                    payload={
                        "skills": valid_skills,
                        "skill_labels": skill_labels,
                        "reasoning": result.reasoning
                    }
                ))

            return {"selected_skills": valid_skills}

        except Exception as e:
            logger.error(f"[Planner] Skill selection failed: {e}")
            return {"selected_skills": ["general_academic.md"]}

    def generate_clarification_questions(self, state: AgentGraphState, writer: StreamWriter = None) -> List[str]:
        """
        Generates clarification questions using LLM without interruption.

        Invokes get_clarification_prompt, gets 2-3 questions and returns them.
        Emits CLARIFICATION_STARTED event via StreamWriter.
        """
        user_query = state.get("user_query", "")
        previous_answers = state.get("clarification_answers", [])
        loop_count = state.get("clarification_loop_count", 0)

        if writer:
            writer(create_event(
                EventType.CLARIFICATION_STARTED,
                PhaseType.CLARIFYING,
                payload={"message": "Analyzing research deep context...", "loop_number": loop_count + 1}
            ))

        prompt = get_clarification_prompt(
            user_query=user_query,
            previous_answers=previous_answers,
            loop_number=loop_count + 1
        )

        from pydantic import BaseModel, Field
        from typing import List

        class ClarificationResult(BaseModel):
            needs_more_clarification: bool = Field(description="Whether clarification from the user is needed.")
            questions: List[str] = Field(description="List of clarification questions to ask.")

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
        to apply targeted edits. Concatenates report_body_sections
        for LLM context, then returns updated sections.
        
        Args:
            state: State with edit_instructions and current report sections.
            
        Returns:
            State update with modified report sections.
        """
        edit_instructions = state.get("edit_instructions", "")
        if not edit_instructions:
            logger.warning("[Editor] No edit instructions provided")
            return {}
        
        body_sections = state.get("report_body_sections", [])
        combined_body = "\n\n".join(
            s.get("section_content", "") for s in sorted(body_sections, key=lambda s: s.get("section_order", 0))
        )
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
{combined_body}

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
            
            for key in ["report_abstract", "report_introduction", "report_conclusion"]:
                if result.get(key) and result[key] != "null":
                    updates[key] = result[key]
            
            if result.get("report_body") and result["report_body"] != "null":
                import uuid as _uuid
                updates["report_body_sections"] = [{
                    "section_id": str(_uuid.uuid4()),
                    "section_order": 1,
                    "section_content": result["report_body"]
                }]
            
            logger.info(f"[Editor] Applied edits to {len(updates)} sections")
            return updates
            
        except Exception as e:
            logger.error(f"[Editor] Error applying edits: {e}")
            return {}


def planner_node(state: AgentGraphState, writer: StreamWriter = None) -> Dict[str, Any]:
    """
    LangGraph node wrapper for Planner.
    
    Reads user_query and memory_context from state, generates
    planner_query (list of research queries) using context-aware planning.
    """
    planner = Planner()
    return planner._generate_plan(state, writer)


def clarification_node(state: AgentGraphState, writer: StreamWriter = None) -> Dict[str, Any]:
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

    user_response = interrupt({
        "type": "clarification",
        "questions": questions,
        "loop_number": loop_count + 1,
    })

    answers_raw = user_response.get("answers", {})

    new_qa_pairs: list = []
    if isinstance(answers_raw, dict):
        for q, a in answers_raw.items():
            new_qa_pairs.append({"question": q, "answer": a})
    elif isinstance(answers_raw, list):
        for i, a in enumerate(answers_raw):
            q = questions[i] if i < len(questions) else f"Question {i+1}"
            new_qa_pairs.append({"question": q, "answer": a})

    logger.info(
        f"[Planner] Clarification round {loop_count + 1}: "
        f"collected {len(new_qa_pairs)} answers"
    )

    summary_lines = [f"Q: {p['question']} → A: {p['answer']}" for p in new_qa_pairs]
    clarification_msg = {
        "message_id": str(uuid.uuid4()),
        "role": "system",
        "content": f"[User clarified (round {loop_count + 1})]\n" + "\n".join(summary_lines),
        "timestamp": datetime.now().isoformat(),
        "metadata": {"message_type": "clarification", "round": loop_count + 1},
    }

    return {
        "clarification_answers": new_qa_pairs,
        "clarification_loop_count": loop_count + 1,
        "clarification_questions": [],
        "chat_messages": [clarification_msg],
    }


def skill_selection_node(state: AgentGraphState, writer: StreamWriter = None) -> Dict[str, Any]:
    """
    LangGraph node wrapper for research skill selection.

    Uses structured LLM output to pick 1-4 domain-specific skills
    based on user query and accumulated clarification context.
    """
    planner = Planner()
    return planner._select_skills(state, writer)


def report_style_node(state: AgentGraphState, writer: StreamWriter = None) -> Dict[str, Any]:
    """
    LangGraph node wrapper for report style generation.

    Generates a report style directive from user query, clarification answers,
    and selected skills. Stored in report_style_skill state field and used by
    all downstream prompts (answers, gaps, outline, chapters, CSS).
    """
    user_query = state.get("user_query", "")
    clarification_answers = state.get("clarification_answers", [])
    selected_skills = state.get("selected_skills", [])

    if writer:
        writer(create_event(
            EventType.PLANNER_PROGRESS,
            PhaseType.PLANNING,
            payload={"message": "Determining report style and formatting..."}
        ))

    prompt = get_report_style_prompt(
        user_query=user_query,
        clarification_answers=clarification_answers,
        selected_skill_names=selected_skills
    )

    try:
        llm = LlmsHouse.google_model("gemini-2.5-flash")
        response = llm.invoke(prompt)
        style_directive = response.content if hasattr(response, 'content') else str(response)
        logger.info(f"[ReportStyle] Generated style directive ({len(style_directive)} chars)")
        return {"report_style_skill": style_directive.strip()}
    except Exception as e:
        logger.error(f"[ReportStyle] Style generation failed: {e}")
        return {"report_style_skill": ""}


def editor_node(state: AgentGraphState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for report editing.
    
    Reads edit_instructions and current report sections,
    applies targeted edits using LLM.
    """
    planner = Planner()
    return planner.editor(state)

