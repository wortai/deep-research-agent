"""
Plan refinement functionality for the Deep Search Planner Agent
"""
import json
from typing import Dict, List, Any
import google.generativeai as genai
from researcher.planner.models import PlanData
from researcher.planner.prompts import Prompts
from researcher.planner.utils import ResponseParser


class PlanRefiner:
    """Handles plan refinement and enhancement using AI models"""
    
    def __init__(self, model: genai.GenerativeModel):
        """
        Initialize the PlanRefiner
        
        Args:
            model: Configured Gemini model instance
        """
        self.model = model
    
    def enhance_plan_with_answers(self, plan_data: PlanData, qa_pairs: Dict[str, str]) -> PlanData:
        """
        Generate enhanced plan based on Q&A pairs
        
        Args:
            plan_data: Original plan data
            qa_pairs: Dictionary of questions and answers
            
        Returns:
            PlanData: Enhanced plan data
        """
        # Format Q&A pairs for the prompt
        qa_text = ""
        if qa_pairs:
            qa_text = "\n".join(f"Q: {q}\nA: {a}\n" for q, a in qa_pairs.items())
        else:
            qa_text = "No specific clarifications provided."
        
        enhancement_prompt = Prompts.ENHANCE_PLAN_WITH_ANSWERS.format(
            plan_data=json.dumps(plan_data.to_dict(), indent=2),
            qa_text=qa_text
        )
        
        try:
            response = self.model.generate_content(enhancement_prompt)
            response_text = response.text.strip()
            
            enhanced_plan_dict = ResponseParser.parse_plan_response(response_text)
            enhanced_plan = PlanData.from_dict(enhanced_plan_dict)
            
            print(f"🔄 Plan enhanced with {len(qa_pairs)} clarifications")
            return enhanced_plan
            
        except Exception as e:
            print(f"❌ Error enhancing plan: {str(e)}")
            return plan_data
    
    def refine_plan(self, plan_data: PlanData, evaluation_details: Dict[str, Any], 
                    enhanced_query: str = "") -> PlanData:
        """
        Refine the plan based on evaluation feedback and quality assessment
        
        Args:
            plan_data: Current plan data
            evaluation_details: Detailed evaluation results with feedback
            enhanced_query: The enhanced query for context
            
        Returns:
            PlanData: Refined plan data
        """
        # Format the prompt with the plan data and evaluation
        formatted_prompt = Prompts.REFINE_PLAN.format(
            enhanced_query=enhanced_query,
            search_steps=json.dumps(plan_data.search_steps, indent=4),
            key_areas=json.dumps(plan_data.key_areas, indent=4),
            information_sources=json.dumps(plan_data.information_sources, indent=4),
            search_strategies=json.dumps(plan_data.search_strategies, indent=4),
            success_metrics=json.dumps(plan_data.success_metrics, indent=4),
            plan_evaluation=json.dumps(evaluation_details, indent=4)
        )
        
        try:
            response = self.model.generate_content(formatted_prompt)
            response_text = response.text.strip()
            
            refined_plan_dict = ResponseParser.parse_plan_response(response_text)
            refined_plan = PlanData.from_dict(refined_plan_dict)
            
            # Log improvements made
            self._log_refinement_improvements(plan_data, refined_plan, evaluation_details)
            
            print(f"🔧 Plan refined based on evaluation feedback")
            return refined_plan
                
        except Exception as e:
            print(f"❌ Error refining plan: {str(e)}")
            return plan_data
    
    def apply_manual_refinements(self, plan_data: PlanData, manual_feedback: List[str]) -> PlanData:
        """
        Apply manual refinements to a plan based on user-provided feedback
        
        Args:
            plan_data: Current plan data
            manual_feedback: List of manual feedback items
            
        Returns:
            PlanData: Refined plan data
        """
        # Create a mock evaluation structure for manual feedback
        mock_evaluation = {
            "overall_score": 7.0,
            "actionable_feedback": manual_feedback,
            "areas_for_potential_further_clarification": [],
            "evaluation_summary": "Manual refinement requested"
        }
        
        print(f"🔧 Applying {len(manual_feedback)} manual refinements...")
        return self.refine_plan(plan_data, mock_evaluation)
    
    def _log_refinement_improvements(self, original_plan: PlanData, 
                                refined_plan: PlanData, 
                                evaluation_details: Dict[str, Any]) -> None:
        """
        Log the improvements made during refinement
        
        Args:
            original_plan: Original plan data
            refined_plan: Refined plan data
            evaluation_details: Evaluation details that guided refinement
        """
        print(f"📈 REFINEMENT IMPROVEMENTS:")
        
        # Count improvements in each section
        improvements = {}
        plan_attributes = ['search_steps', 'key_areas', 'information_sources', 'search_strategies', 'success_metrics']
        
        for attr in plan_attributes:
            original_items = getattr(original_plan, attr, [])
            refined_items = getattr(refined_plan, attr, [])
            
            original_count = len(original_items)
            refined_count = len(refined_items)
            
            if refined_count > original_count:
                improvements[attr] = refined_count - original_count
            
            # Check for enhanced content (longer descriptions)
            original_content = ' '.join(original_items)
            refined_content = ' '.join(refined_items)
            if len(refined_content) > len(original_content) * 1.1:  # 10% more content
                improvements[f"{attr}_enhanced"] = True
        
        # Display improvements
        section_names = {
            'search_steps': 'Search Steps',
            'key_areas': 'Key Areas', 
            'information_sources': 'Information Sources',
            'search_strategies': 'Search Strategies',
            'success_metrics': 'Success Metrics'
        }
        
        for key, improvement in improvements.items():
            if key.endswith('_enhanced'):
                section = key.replace('_enhanced', '')
                print(f"   ✨ Enhanced {section_names.get(section, section)} with more detailed content")
            else:
                print(f"   ➕ Added {improvement} new items to {section_names.get(key, key)}")
        
        # Show which feedback was addressed
        feedback_count = len(evaluation_details.get('actionable_feedback', []))
        if feedback_count > 0:
            print(f"   🎯 Addressed {feedback_count} actionable feedback items")