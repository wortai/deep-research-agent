from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from states.state import ResearchReviewData
from reviewer.reviewer import Reviewer
from researcher.gap_questions.run_research import run_research


class Improviser:
    def __init__(self):
        from researcher.gap_questions.llm_client import GeminiLLMClient
        self.llm_client = GeminiLLMClient()
    
    def improve_proposed_research(self, state: ResearchReviewData) -> ResearchReviewData:
        latest_feedback = state["review_feedback"][-1] if state["review_feedback"] else ""
        
        if not latest_feedback:
            return state
        
        current_proposal = state.get("Proposed_Research", "")
        
        all_insights = []
        for finding in state["processed_findings"]:
            all_insights.extend(finding.get("insights", []))
        
        prompt = f"""
You are a research improvement specialist. Enhance the research proposal based on the review feedback.

TOPIC: {state['topic']}

CURRENT PROPOSAL:
{current_proposal if current_proposal else "No current proposal"}

REVIEW FEEDBACK:
{latest_feedback}

AVAILABLE INSIGHTS:
{chr(10).join([f"• {insight}" for insight in all_insights])}

INSTRUCTIONS:
1. Address all points mentioned in the review feedback
2. Create a comprehensive, well-structured research proposal
3. Include all relevant insights in a logical flow
4. Ensure the proposal fully addresses the original topic
5. Make it professional and complete

Create an improved research proposal:"""

        try:
            response = self.llm_client.generate(prompt, context="research_improvement")
            state["Proposed_Research"] = response.strip()
        except Exception as e:
            state["Proposed_Research"] = state.get("Proposed_Research", "") + f"\n\nError: {str(e)}"
        
        return state


class SubResearcherGraph:
    def __init__(self):
        self.reviewer = Reviewer()
        self.improviser = Improviser()
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(ResearchReviewData)
        
        workflow.add_node("research", self._research_node)
        workflow.add_node("review", self._review_node) 
        workflow.add_node("improviser", self._improviser_node)
        workflow.add_node("complete", self._complete_node)
        
        workflow.set_entry_point("research")
        
        workflow.add_edge("research", "review")
        
        workflow.add_conditional_edges(
            "review",
            self._should_improve,
            {
                "improviser": "improviser",
                "complete": "complete"
            }
        )
        
        workflow.add_edge("improviser", "review")
        workflow.add_edge("complete", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _research_node(self, state: ResearchReviewData) -> ResearchReviewData:
        try:
            research_results = run_research(state["topic"])
            
            query_mappings = research_results.get("query_answer_mappings", {})
            
            if not state["processed_findings"]:
                state["processed_findings"] = []
            
            for gap_query, insights in query_mappings.items():
                finding = {
                    "query": gap_query,
                    "insights": insights,
                    "confidence": research_results.get("final_confidence", 0.0),
                    "session_id": research_results.get("session_id", ""),
                    "urls_count": len(research_results.get("urls_accessed", []))
                }
                state["processed_findings"].append(finding)
            
            state["raw_research_results"].append(str(research_results))
            
        except Exception as e:
            state["processed_findings"].append({
                "query": state["topic"],
                "insights": [f"Research failed: {str(e)}"],
                "confidence": 0.0,
                "error": True
            })
        
        return state
    
    def _review_node(self, state: ResearchReviewData) -> ResearchReviewData:
        return self.reviewer.run(state)
    
    def _improviser_node(self, state: ResearchReviewData) -> ResearchReviewData:
        return self.improviser.improve_proposed_research(state)
    
    def _complete_node(self, state: ResearchReviewData) -> ResearchReviewData:
        if not state.get("Proposed_Research"):
            all_insights = []
            for finding in state["processed_findings"]:
                all_insights.extend(finding.get("insights", []))
            
            basic_proposal = f"""# Research Summary: {state['topic']}

## Key Findings
{chr(10).join([f"• {insight}" for insight in all_insights])}

## Conclusion
This research provides insights into {state['topic']} based on comprehensive analysis.
"""
            state["Proposed_Research"] = basic_proposal
        
        return state
    
    def _should_improve(self, state: ResearchReviewData) -> Literal["improviser", "complete"]:
        latest_feedback = state["review_feedback"][-1] if state["review_feedback"] else ""
        
        if latest_feedback and latest_feedback.strip():
            return "improviser"
        else:
            return "complete"
    
    def run(self, topic: str, task_description: str = None) -> ResearchReviewData:
        initial_state: ResearchReviewData = {
            "topic": topic,
            "task_description": task_description or f"Research on: {topic}",
            "raw_research_results": [],
            "processed_findings": [],
            "review_feedback": [],
            "Proposed_Research": ""
        }
        
        config = {"configurable": {"thread_id": f"research_{hash(topic)}"}}
        final_state = self.graph.invoke(initial_state, config)
        
        return final_state


if __name__ == "__main__":
    subgraph = SubResearcherGraph()
    
    result = subgraph.run(
        topic="What are the latest advancements in large language models?",
        task_description="Research recent developments in LLM technology"
    )
    
    print("Final Research Proposal:")
    print(result["Proposed_Research"])
