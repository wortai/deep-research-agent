"""
Plan evaluation functionality for the Deep Search Planner Agent
"""
import json
from typing import Dict, Any
import google.generativeai as genai
from researcher.planner.models import PlanData, PlanEvaluation
from researcher.planner.prompts import Prompts
from researcher.planner.utils import ResponseParser, ScoreExtractor
from researcher.planner.config import Config


class PlanEvaluator:
    """Handles plan evaluation and quality assessment using AI models"""
    
    def __init__(self, model: genai.GenerativeModel):
        """
        Initialize the PlanEvaluator
        
        Args:
            model: Configured Gemini model instance
        """
        self.model = model
        self._last_evaluation_details = {}
    
    def find_ambiguities(self, enhanced_query: str, plan_data: PlanData, max_questions: int = 3) -> PlanEvaluation:
        """
        Analyze the plan for ambiguities and generate questions to resolve them
        
        Args:
            enhanced_query: The enhanced search query
            plan_data: The search plan data
            max_questions: Maximum number of clarifying questions to generate
            
        Returns:
            PlanEvaluation: Evaluation results with identified ambiguities and clarifying questions
        """
        # Format the prompt with the plan data and max questions
        formatted_prompt = Prompts.EVALUATE_PLAN_QUALITY.format(
            enhanced_query=enhanced_query,
            max_questions=max_questions,
            search_steps=json.dumps(plan_data.search_steps, indent=4),
            key_areas=json.dumps(plan_data.key_areas, indent=4),
            information_sources=json.dumps(plan_data.information_sources, indent=4),
            search_strategies=json.dumps(plan_data.search_strategies, indent=4),
            success_metrics=json.dumps(plan_data.success_metrics, indent=4)
        )
        
        try:
            response = self.model.generate_content(formatted_prompt)
            response_text = response.text.strip()
            
            evaluation_result = ResponseParser.parse_evaluation_response(response_text, max_questions)
            
            print(f"🤔 Identified {len(evaluation_result.decision_points)} decision points and ambiguities")
            print(f"❓ Generated {len(evaluation_result.clarifying_questions)} simple clarifying questions")
            return evaluation_result
                
        except Exception as e:
            print(f"❌ Error in ambiguity finder: {str(e)}")
            return PlanEvaluation(
                overall_score=0.0,
                metric_scores={},
                evaluation_summary="Error occurred during evaluation",
                actionable_feedback=[],
                areas_for_clarification=[],
                decision_points=[],
                clarifying_questions=Config.DEFAULT_SIMPLE_QUESTIONS[:max_questions]
            )
    
    def evaluate_plan_quality(self, plan_data: PlanData, enhanced_query: str = "") -> float:
        """
        Evaluate the quality of a search plan using metric-based scoring
        
        Args:
            plan_data: Plan data to evaluate
            enhanced_query: The enhanced query for context
            
        Returns:
            float: Quality score (0-100)
        """
        # Format the prompt with the plan data
        formatted_prompt = Prompts.EVALUATE_PLAN_QUALITY_SCORED.format(
            enhanced_query=enhanced_query,
            search_steps=json.dumps(plan_data.search_steps, indent=4),
            key_areas=json.dumps(plan_data.key_areas, indent=4),
            information_sources=json.dumps(plan_data.information_sources, indent=4),
            search_strategies=json.dumps(plan_data.search_strategies, indent=4),
            success_metrics=json.dumps(plan_data.success_metrics, indent=4)
        )
        
        try:
            response = self.model.generate_content(formatted_prompt)
            response_text = response.text.strip()
            
            # Clean response - remove markdown code blocks if present
            response_text = ResponseParser.clean_json_response(response_text)
            
            try:
                evaluation = json.loads(response_text)
                overall_score = evaluation.get('overall_score', 0)
                
                # Validate score range (should be 1-10, convert to 0-100)
                if overall_score <= 10:
                    overall_score = overall_score * 10  # Convert 1-10 scale to 0-100
                elif overall_score > 100:
                    overall_score = min(overall_score, 100)  # Cap at 100
                
                # Store detailed evaluation for potential use
                self._last_evaluation_details = evaluation
                
                print(f"📊 Plan quality score: {overall_score:.1f}/100")
                
                # Print metric breakdown if available
                if 'metric_scores' in evaluation:
                    metrics = evaluation['metric_scores']
                    print(f"   📋 Completeness: {metrics.get('completeness', 0)}/10")
                    print(f"   🔍 Clarity: {metrics.get('clarity_specificity', 0)}/10")
                    print(f"   🔄 Logical Flow: {metrics.get('logical_flow_cohesion', 0)}/10")
                    print(f"   ✅ Feasibility: {metrics.get('feasibility_realism', 0)}/10")
                    print(f"   🎯 Relevance: {metrics.get('keyword_relevance_breadth', 0)}/10")
                
                return overall_score
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing failed in evaluation: {str(e)}")
                print(f"Raw response: {response_text[:200]}...")
                # Fallback: try to extract a numeric score
                overall_score = ScoreExtractor.extract_numeric_score(response_text)
                print(f"📊 Plan quality score (fallback): {overall_score:.1f}/100")
                return overall_score
                
        except Exception as e:
            print(f"❌ Error evaluating plan quality: {str(e)}")
            return 50.0  # Default middle score
    
    def get_last_evaluation_details(self) -> Dict[str, Any]:
        """
        Get the detailed evaluation results from the last plan quality assessment
        
        Returns:
            Dict: Detailed evaluation including metric scores and feedback
        """
        return self._last_evaluation_details
    
    def display_evaluation_details(self, evaluation_details: Dict[str, Any] = None) -> None:
        """
        Display detailed evaluation results in a formatted way
        
        Args:
            evaluation_details: Evaluation details dict (uses last evaluation if None)
        """
        if evaluation_details is None:
            evaluation_details = self.get_last_evaluation_details()
        
        if not evaluation_details:
            print("No evaluation details available")
            return
        
        print(f"\n{'='*60}")
        print(f"📊 DETAILED PLAN EVALUATION")
        print(f"{'='*60}")
        
        # Overall score
        overall_score = evaluation_details.get('overall_score', 0)
        print(f"🎯 Overall Score: {overall_score:.1f}/10 ({overall_score*10:.1f}/100)")
        
        # Metric breakdown
        if 'metric_scores' in evaluation_details:
            print(f"\n📋 METRIC BREAKDOWN:")
            metrics = evaluation_details['metric_scores']
            metric_names = {
                'completeness': 'Completeness (25%)',
                'clarity_specificity': 'Clarity & Specificity (20%)',
                'logical_flow_cohesion': 'Logical Flow & Cohesion (20%)',
                'feasibility_realism': 'Feasibility & Realism (15%)',
                'keyword_relevance_breadth': 'Keyword Relevance & Breadth (20%)'
            }
            
            for key, name in metric_names.items():
                score = metrics.get(key, 0)
                bars = '█' * int(score) + '░' * (10 - int(score))
                print(f"   {name}: {score}/10 [{bars}]")
        
        # Summary
        if 'evaluation_summary' in evaluation_details:
            print(f"\n💭 SUMMARY:")
            print(f"   {evaluation_details['evaluation_summary']}")
        
        # Actionable feedback
        if 'actionable_feedback' in evaluation_details:
            feedback = evaluation_details['actionable_feedback']
            if feedback:
                print(f"\n🔧 ACTIONABLE FEEDBACK:")
                for i, item in enumerate(feedback, 1):
                    print(f"   {i}. {item}")
        
        print(f"{'='*60}")