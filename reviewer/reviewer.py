"""
Reviewer class for LangGraph - evaluates research and provides feedback.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from researcher.gap_questions.llm_client import GeminiLLMClient
import logging
load_dotenv()

class Reviewer:
    """
    Reviewer class that evaluates research results and provides feedback.
    Follows LangGraph pattern where state is passed as parameters.
    """
    
    def __init__(self):
        """Initialize the Reviewer with LLM client using llm_client.py file Nishant made 
        --In future we need global LLM choosing file and So on prompting LLM file  --
        """
        try:
            self.llm_client = GeminiLLMClient()
        except Exception as e:
            raise Exception(f"Failed to initialize LLM client: {e}")
    



    def review_research(self, state: Dict[str, Any]) -> Dict[str, Any]:
            
            try:
                # Get processed findings from state
                processed_findings = state.get("processed_findings", [])
                topic = state.get("topic", "")
                # Get previous review feedback
                previous_review_feedback = state.get("review_feedback", [])

                if not processed_findings:
                    state["review_feedback"].append("Disapproved: No processed findings to review.")
                    return state

                # Get the last feedback if it exists
                last_feedback = previous_review_feedback[-1] if previous_review_feedback else "None"

                # Create one Big string Research we conducted,  for review
                research_summary = self._create_research_summary(processed_findings)

                # Create review prompt
                prompt = f"""
    You are a research quality reviewer. Analyze the research findings and determine if they adequately answer the research question.

    RESEARCH TOPIC: {topic}

    PREVIOUS FEEDBACK:
    {last_feedback}

    CURRENT FINDINGS:
    {research_summary}

    EVALUATION CRITERIA:
    1. Completeness: Does the research fully address the topic?
    2. Depth: Are the insights substantive and detailed?
    3. Coverage: Are important aspects missing?
    4. Responsiveness: Have previous feedback points been addressed?

    INSTRUCTIONS:
    - If research is comprehensive and complete, and previous feedback is addressed, respond with: "APPROVED"
    - If research needs improvement, provide specific feedback on what's missing or what needs further investigation, referencing previous feedback if applicable.
    - Be specific about gaps or areas needing deeper investigation.

    Your response:"""

                response = self.llm_client.generate(prompt, context="research_review")

    
                if "APPROVED" in response.upper():
                    feedback = "APPROVED"  
                else:
                    feedback = response.strip()
                return {"review_feedback": [feedback]}


            except Exception as e:
                logging.error("Review failed", exc_info=True)
                raise RuntimeError("Review failed. Please check logs for details.") from e





    def _create_research_summary(self, processed_findings: List[Dict]) -> str:
        """
        Generates a formatted summary string from a list of processed research findings.
        Each finding includes the original query and its associated insights, presented in a numbered list.
        The summary is structured for easy review, with clear separation between findings.

        """
        summary_parts = []
        for i, finding in enumerate(processed_findings, 1):
            query = finding.get("query", "Unknown query")
            insights = finding.get("insights", [])
            summary_parts.append(f"\nFinding {i}: {query}")
            summary_parts.append(f"Insights ({len(insights)}):")
            for j, insight in enumerate(insights, 1):
                summary_parts.append(f"  {j}. {insight}")
            summary_parts.append("-" * 40)
        return "\n".join(summary_parts)
    


    def run(self, state: Dict[str, Any]):
        """
        Entry point for LangGraph node. Processes the state and returns the updated state.
        In LangGraph, each node function should return the (possibly updated) state dictionary.
        """
        return self.review_research(state)










# Example usage for testing
if __name__ == "__main__":

    
    # Test state
    test_state = {
        "topic": "AI advancements",
        "task_description": "Research AI developments",
        "raw_research_results": [],
        "processed_findings": [
            {
                "query": "What are the latest breakthroughs in artificial intelligence as of 2024?",
                "insights": [
                    "OpenAI released GPT-4, a large multimodal model capable of processing both text and images, demonstrating significant improvements in reasoning and contextual understanding.",
                    "Major progress in computer vision includes self-supervised learning techniques, enabling models to learn from unlabeled data and outperform previous benchmarks on image classification and object detection.",
                    "Reinforcement learning has been successfully applied to robotics, allowing robots to learn complex tasks in simulation and transfer those skills to real-world environments.",
                    "AI safety research has advanced, with new methods for interpretability and alignment, helping ensure that AI systems behave as intended and can be audited for fairness and bias.",
                    "Multimodal AI systems, which integrate text, vision, and audio, are now capable of generating coherent content across different media and understanding context in a more human-like manner."
                ]
            }
        ],
        "review_feedback": [],
        "Proposed_Research": ""
    }
    
    reviewer = Reviewer()
    updated_state = reviewer.run(test_state)
    
    print("Review Feedback:", updated_state["review_feedback"])
