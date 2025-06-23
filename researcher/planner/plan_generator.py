"""
Plan generation functionality for the Deep Search Planner Agent
"""
from typing import List, Optional
import google.generativeai as genai
from researcher.planner.models import PlanData
from researcher.planner.prompts import Prompts
from researcher.planner.utils import ResponseParser


class PlanGenerator:
    """Handles initial plan generation using AI models"""
    
    def __init__(self, model: genai.GenerativeModel):
        """
        Initialize the PlanGenerator
        
        Args:
            model: Configured Gemini model instance
        """
        self.model = model
    
    def generate_initial_plan(self, enhanced_query: str, key_topics: Optional[List[str]] = None) -> PlanData:
        """
        Generate initial search plan using the specialized prompt
        
        Args:
            enhanced_query: The enhanced search query
            key_topics: Optional list of key topics (if not provided, will be extracted)
            
        Returns:
            PlanData: Initial search plan components
        """
        # Format key topics for the prompt
        if key_topics:
            key_topics_text = "\n".join(f"* {topic}" for topic in key_topics)
        else:
            key_topics_text = "* [Key topics to be derived from the enhanced query]"
        
        # Format the prompt with the enhanced query and key topics
        planning_prompt = Prompts.GENERATE_INITIAL_PLAN.format(
            enhanced_query=enhanced_query,
            key_topics=key_topics_text
        )
        
        try:
            response = self.model.generate_content(planning_prompt)
            response_text = response.text.strip()
            
            # Parse the structured response into plan components
            plan_data = ResponseParser.parse_initial_plan_response(response_text, enhanced_query)
            
            print(f"📋 Initial plan generated with {len(plan_data.search_steps)} phases")
            return plan_data
            
        except Exception as e:
            print(f"❌ Error generating initial plan: {str(e)}")
            return PlanData(
                search_steps=[],
                key_areas=[],
                information_sources=[],
                search_strategies=[],
                success_metrics=[]
            )