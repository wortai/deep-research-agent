"""
Main Deep Search Planner Agent class
"""
import time
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from researcher.planner.models import SearchPlan, PlanData
from researcher.planner.config import Config
from researcher.planner.query_enhancer import QueryEnhancer
from researcher.planner.plan_generator import PlanGenerator
from researcher.planner.plan_evaluator import PlanEvaluator
from researcher.planner.plan_refiner import PlanRefiner


class DeepSearchPlannerAgent:
    """Main agent class that orchestrates the deep search planning process"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = None):
        """
        Initialize the Deep Search Planner Agent
        
        Args:
            api_key: Google AI API key (if None, loads from environment)
            model_name: Gemini model to use (defaults to Config.DEFAULT_MODEL_NAME)
        """
        # Load API key from environment if not provided
        self.api_key = api_key or Config.get_api_key()
        self.model_name = model_name or Config.DEFAULT_MODEL_NAME
        self.model = None
        self.search_history = []
        
        # Initialize component classes
        self.query_enhancer = None
        self.plan_generator = None
        self.plan_evaluator = None
        self.plan_refiner = None
        
    def load_gemini_model(self) -> bool:
        """
        Load and configure the Gemini model
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            
            # Test the model
            test_response = self.model.generate_content("Test connection")
            if test_response:
                print(f"✅ Gemini model '{self.model_name}' loaded successfully")
                
                # Initialize component classes
                self.query_enhancer = QueryEnhancer(self.model)
                self.plan_generator = PlanGenerator(self.model)
                self.plan_evaluator = PlanEvaluator(self.model)
                self.plan_refiner = PlanRefiner(self.model)
                
                return True
            else:
                print("❌ Failed to load Gemini model")
                return False
                
        except Exception as e:
            print(f"❌ Error loading Gemini model: {str(e)}")
            return False
    
    def enhance_search_query(self, user_query: str) -> str:
        """
        Enhance the user's search query
        
        Args:
            user_query: Original user search query
            
        Returns:
            str: Enhanced search query
        """
        if not self.query_enhancer:
            raise RuntimeError("Model not loaded. Call load_gemini_model() first.")
        
        return self.query_enhancer.enhance_search_query(user_query)
    
    def generate_initial_plan(self, enhanced_query: str, key_topics: Optional[List[str]] = None) -> PlanData:
        """
        Generate initial search plan
        
        Args:
            enhanced_query: The enhanced search query
            key_topics: Optional list of key topics
            
        Returns:
            PlanData: Initial search plan components
        """
        if not self.plan_generator:
            raise RuntimeError("Model not loaded. Call load_gemini_model() first.")
        
        return self.plan_generator.generate_initial_plan(enhanced_query, key_topics)
    
    def ambiguity_finder(self, enhanced_query: str, plan_data: PlanData, max_questions: int = 3) -> Dict[str, Any]:
        """
        Analyze the plan for ambiguities and generate questions to resolve them
        
        Args:
            enhanced_query: The enhanced search query
            plan_data: The search plan data
            max_questions: Maximum number of clarifying questions to generate
            
        Returns:
            Dict: Evaluation results with identified ambiguities and clarifying questions
        """
        if not self.plan_evaluator:
            raise RuntimeError("Model not loaded. Call load_gemini_model() first.")
        
        evaluation = self.plan_evaluator.find_ambiguities(enhanced_query, plan_data, max_questions)
        
        # Convert to dictionary format for backward compatibility
        return {
            "overall_assessment": evaluation.evaluation_summary,
            "strengths": [],
            "weaknesses_and_recommendations": evaluation.actionable_feedback,
            "areas_for_potential_further_clarification": evaluation.areas_for_clarification,
            "decision_points": evaluation.decision_points,
            "clarifying_questions": evaluation.clarifying_questions
        }
    
    def enhance_plan_with_answers(self, plan_data: PlanData, qa_pairs: Dict[str, str]) -> PlanData:
        """
        Generate enhanced plan based on Q&A pairs
        
        Args:
            plan_data: Original plan data
            qa_pairs: Dictionary of questions and answers
            
        Returns:
            PlanData: Enhanced plan data
        """
        if not self.plan_refiner:
            raise RuntimeError("Model not loaded. Call load_gemini_model() first.")
        
        return self.plan_refiner.enhance_plan_with_answers(plan_data, qa_pairs)
    
    def evaluate_plan_quality(self, plan_data: PlanData, enhanced_query: str = "") -> float:
        """
        Evaluate the quality of a search plan using metric-based scoring
        
        Args:
            plan_data: Plan data to evaluate
            enhanced_query: The enhanced query for context
            
        Returns:
            float: Quality score (0-100)
        """
        if not self.plan_evaluator:
            raise RuntimeError("Model not loaded. Call load_gemini_model() first.")
        
        return self.plan_evaluator.evaluate_plan_quality(plan_data, enhanced_query)
    
    def get_last_evaluation_details(self) -> Dict[str, Any]:
        """
        Get the detailed evaluation results from the last plan quality assessment
        
        Returns:
            Dict: Detailed evaluation including metric scores and feedback
        """
        if not self.plan_evaluator:
            return {}
        
        return self.plan_evaluator.get_last_evaluation_details()
    
    def display_evaluation_details(self, evaluation_details: Dict[str, Any] = None) -> None:
        """
        Display detailed evaluation results in a formatted way
        
        Args:
            evaluation_details: Evaluation details dict (uses last evaluation if None)
        """
        if not self.plan_evaluator:
            print("No evaluator available")
            return
        
        self.plan_evaluator.display_evaluation_details(evaluation_details)
    
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
        if not self.plan_refiner:
            raise RuntimeError("Model not loaded. Call load_gemini_model() first.")
        
        return self.plan_refiner.refine_plan(plan_data, evaluation_details, enhanced_query)
    
    def apply_manual_refinements(self, plan_data: PlanData, manual_feedback: List[str]) -> PlanData:
        """
        Apply manual refinements to a plan based on user-provided feedback
        
        Args:
            plan_data: Current plan data
            manual_feedback: List of manual feedback items
            
        Returns:
            PlanData: Refined plan data
        """
        if not self.plan_refiner:
            raise RuntimeError("Model not loaded. Call load_gemini_model() first.")
        
        return self.plan_refiner.apply_manual_refinements(plan_data, manual_feedback)
    
    def execute_planning_cycle(self, user_query: str, qa_pairs: Optional[Dict[str, str]] = None,
                             max_iterations: int = 3, top_n: int = 2) -> List[SearchPlan]:
        """
        Execute a complete planning cycle
        
        Args:
            user_query: Original user search query
            qa_pairs: Optional Q&A pairs for enhancement
            max_iterations: Number of refinement iterations
            top_n: Number of top plans to return
            
        Returns:
            List[SearchPlan]: Top N search plans sorted by quality
        """
        if not self.model:
            raise RuntimeError("Model not loaded. Call load_gemini_model() first.")
        
        print(f"🚀 Starting planning cycle for: '{user_query}'")
        
        # Step 1: Enhance query
        enhanced_query = self.enhance_search_query(user_query)
        
        # Step 2: Generate initial plan
        current_plan_data = self.generate_initial_plan(enhanced_query)
        
        # Step 3: Enhance with answers if provided
        if qa_pairs:
            current_plan_data = self.enhance_plan_with_answers(current_plan_data, qa_pairs)
        
        # Step 4: Iterative refinement
        all_plans = []
        
        for iteration in range(max_iterations):
            print(f"\n--- ITERATION {iteration + 1}/{max_iterations} ---")
            
            # Evaluate current plan
            quality_score = self.evaluate_plan_quality(current_plan_data, enhanced_query)
            evaluation_details = self.get_last_evaluation_details()
            
            # Create SearchPlan object
            search_plan = SearchPlan(
                query=user_query,
                enhanced_query=enhanced_query,
                plan_steps=current_plan_data.search_steps,
                decision_points=[],  # Could be populated from evaluation if needed
                clarifying_questions=[],  # Could be populated if needed
                quality_score=quality_score,
                iteration=iteration + 1,
                timestamp=time.time()
            )
            
            all_plans.append(search_plan)
            
            # Show detailed evaluation for current iteration
            if evaluation_details:
                self.display_evaluation_details(evaluation_details)
            
            # Refine plan for next iteration (except last)
            if iteration < max_iterations - 1:
                current_plan_data = self.refine_plan(current_plan_data, evaluation_details, enhanced_query)
        
        # Sort by quality score and return top N
        all_plans.sort(key=lambda x: x.quality_score, reverse=True)
        top_plans = all_plans[:top_n]
        
        print(f"\n🎉 Planning cycle complete! Generated {len(all_plans)} plan iterations")
        print(f"🏆 Returning top {len(top_plans)} plans")
        
        return top_plans
    
    def display_plan(self, search_plan: SearchPlan) -> None:
        """
        Display a search plan in a formatted way
        
        Args:
            search_plan: SearchPlan object to display
        """
        print(f"\n{'='*60}")
        print(f"📋 SEARCH PLAN (Iteration {search_plan.iteration}) - Score: {search_plan.quality_score:.1f}/100")
        print(f"{'='*60}")
        print(f"🔍 Original Query: {search_plan.query}")
        print(f"✨ Enhanced Query: {search_plan.enhanced_query}")
        
        print(f"\n📋 Plan Steps:")
        for i, step in enumerate(search_plan.plan_steps, 1):
            print(f"   {i}. {step}")
        
        if search_plan.decision_points:
            print(f"\n🤔 Decision Points:")
            for i, point in enumerate(search_plan.decision_points, 1):
                print(f"   {i}. {point}")
        
        if search_plan.clarifying_questions:
            print(f"\n❓ Clarifying Questions:")
            for i, question in enumerate(search_plan.clarifying_questions, 1):
                print(f"   {i}. {question}")
        
        print(f"{'='*60}")