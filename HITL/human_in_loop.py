"""
Human-in-the-Loop handler for research plan approval.

This module provides HumanPlanReview class that uses LangGraph interrupt
to pause graph execution and collect user approval/feedback for generated plans.
"""

from typing import Dict, Any, List
from langgraph.types import interrupt
from graphs.states.subgraph_state import AgentGraphState


class HumanPlanReview:
    """
    Human-in-the-Loop handler for research plan approval.
    
    Uses LangGraph interrupt mechanism to pause graph execution after planner
    generates a plan. The plan is surfaced via interrupt payload, and when
    resumed with Command(resume=value), the resume value is returned by interrupt().
    """

    def format_plan_display(self, plan_queries: List[Dict]) -> str:
        """
        Formats planner queries into readable display string.

        Args:
            plan_queries: List of PlannerQuery dicts with 'query_num' and 'query'.

        Returns:
            Formatted string showing numbered queries.
        """
        if not plan_queries:
            return "  (No queries generated)"
        
        lines = []
        for item in plan_queries:
            query_num = item.get("query_num", "?")
            query = item.get("query", "")
            lines.append(f"  {query_num}. {query}")
        return "\n".join(lines)

    def _create_interrupt_payload(self, plan_queries: List[Dict], plan_display: str) -> Dict[str, Any]:
        """
        Creates the payload sent with interrupt for review context.

        Args:
            plan_queries: Raw planner query list.
            plan_display: Formatted display string.

        Returns:
            Dict containing message, plan data, and formatted display.
        """
        return {
            "message": "Plan ready for review",
            "plan": plan_queries,
            "plan_display": plan_display
        }

    def review_node(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Node that interrupts for human review and processes resume response.

        Calls interrupt() with plan payload. When graph is resumed with
        Command(resume={"approved": bool, "feedback": str}), interrupt() returns
        that resume value which is used to update state.

        Args:
            state: Current graph state containing planner_query.

        Returns:
            State update with plan_approved and plan_feedback fields.
        """
        plan_queries = state.get("planner_query", [])
        plan_display = self.format_plan_display(plan_queries)
        payload = self._create_interrupt_payload(plan_queries, plan_display)
        
        response = interrupt(payload)
        
        approved = response.get("approved", False)
        feedback = response.get("feedback", "")
        
        return {
            "plan_approved": approved,
            "plan_feedback": feedback
        }


def human_review_node(state: AgentGraphState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for HumanPlanReview.
    
    Instantiates HumanPlanReview and invokes review_node to interrupt
    for plan approval.
    """
    reviewer = HumanPlanReview()
    return reviewer.review_node(state)
