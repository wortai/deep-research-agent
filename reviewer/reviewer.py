"""
Reviewer class for LangGraph - evaluates research and provides feedback.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import LLM client from gap_questions
from researcher.gap_questions.llm_client import GeminiLLMClient

load_dotenv()


class Reviewer:
    """
    Reviewer class that evaluates research results and provides feedback.
    Follows LangGraph pattern where state is passed as parameters.
    """
    
    def __init__(self):
        """Initialize the Reviewer with LLM client."""
        try:
            self.llm_client = GeminiLLMClient()
        except Exception as e:
            raise Exception(f"Failed to initialize LLM client: {e}")
    
    def review_research(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review the research findings and provide feedback.
        
        Args:
            state: ResearchReviewData state containing processed_findings
            
        Returns:
            Updated state with review_feedback
        """
        try:
            # Get processed findings from state
            processed_findings = state.get("processed_findings", [])
            topic = state.get("topic", "")
            
            if not processed_findings:
                state["review_feedback"].append("No research findings to review")
                return state
            
            # Create research summary for review
            research_summary = self._create_research_summary(processed_findings)
            
            # Create review prompt
            prompt = f"""
You are a research quality reviewer. Analyze the research findings and determine if they adequately answer the research question.

RESEARCH TOPIC: {topic}

CURRENT FINDINGS:
{research_summary}

EVALUATION CRITERIA:
1. Completeness: Does the research fully address the topic?
2. Depth: Are the insights substantive and detailed?
3. Coverage: Are important aspects missing?

INSTRUCTIONS:
- If research is comprehensive and complete, respond with: "APPROVED"
- If research needs improvement, provide specific feedback on what's missing
- Be specific about gaps or areas needing deeper investigation

Your response:"""

            response = self.llm_client.generate(prompt, context="research_review")
            
            # Process response
            if "APPROVED" in response.upper():
                feedback = ""  # No feedback needed
            else:
                feedback = response.strip()
            
            # Update state
            state["review_feedback"].append(feedback)
            
            return state
            
        except Exception as e:
            error_msg = f"Review failed: {str(e)}"
            state["review_feedback"].append(error_msg)
            return state
    
    def _create_research_summary(self, processed_findings: List[Dict]) -> str:
        """
        Create a summary of research findings for review.
        
        Args:
            processed_findings: List of processed findings from state
            
        Returns:
            Formatted research summary string
        """
        summary_parts = []
        
        for i, finding in enumerate(processed_findings, 1):
            query = finding.get("query", "Unknown query")
            insights = finding.get("insights", [])
            
            summary_parts.append(f"\nFinding {i}: {query}")
            summary_parts.append(f"Insights ({len(insights)}):")
            
            for j, insight in enumerate(insights[:3], 1):  # Show max 3 insights
                summary_parts.append(f"  {j}. {insight}")
            
            if len(insights) > 3:
                summary_parts.append(f"  ... and {len(insights) - 3} more insights")
            
            summary_parts.append("-" * 40)
        
        return "\n".join(summary_parts)
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to run the reviewer process - for LangGraph node.
        
        Args:
            state: ResearchReviewData state
            
        Returns:
            Updated state with review feedback
        """
        return self.review_research(state)


# Example usage for testing
if __name__ == "__main__":
    from states.state import ResearchReviewData
    
    # Test state
    test_state = {
        "topic": "AI advancements",
        "task_description": "Research AI developments",
        "raw_research_results": [],
        "processed_findings": [
            {
                "query": "Latest AI breakthroughs",
                "insights": ["GPT-4 breakthrough", "Computer vision improvements"]
            }
        ],
        "review_feedback": [],
        "Proposed_Research": ""
    }
    
    reviewer = Reviewer()
    updated_state = reviewer.run(test_state)
    
    print("Review Feedback:", updated_state["review_feedback"])
