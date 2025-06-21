#!/usr/bin/env python3
"""
Intelligent Research Planning Module

This module generates follow-up questions to synthesize robust research plans.
It identifies ambiguities, generates clarifying questions, and refines plans iteratively.

Input: User query (str)
Output: Follow-up questions + refined execution plan

Features:
- Decision point detection
- Multi-type question generation  
- Iterative plan refinement
- Quality evaluation
- LangGraph state management
"""

import asyncio
import json
import logging
import uuid
import os
from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass
from enum import Enum

# Environment variables
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

# Google Gemini imports
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Disable LangSmith tracing to avoid threading errors
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuestionType(Enum):
    CLARIFICATION = "clarification"
    CONSTRAINT = "constraint" 
    PREFERENCE = "preference"
    CONTEXT = "context"
    SCOPE = "scope"
    METHODOLOGY = "methodology"

@dataclass
class ResearchStep:
    id: str
    description: str
    dependencies: List[str]
    tools_needed: List[str]
    expected_output: str
    confidence: float
    ambiguity_score: float

@dataclass
class FollowUpQuestion:
    question: str
    question_type: QuestionType
    related_step_ids: List[str]
    priority: int  # 1-5, 5 being highest
    rationale: str

@dataclass
class DecisionPoint:
    step_id: str
    decision_description: str
    options: List[str]
    criteria_needed: List[str]
    impact_scope: str

class PlanningState(TypedDict):
    user_query: str
    initial_plan: List[ResearchStep]
    decision_points: List[DecisionPoint]
    follow_up_questions: List[FollowUpQuestion]
    refined_plan: List[ResearchStep]
    plan_quality_score: float
    iteration_count: int
    max_iterations: int

class IntelligentResearchPlanner:
    """
    Intelligent Research Planning Module using LangGraph and Google Gemini
    """
    
    def __init__(self, gemini_api_key: str, model_name: str = "models/gemini-1.5-pro-latest"):
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        
        # List available models for debugging
        try:
            available_models = list(genai.list_models())
            generative_models = [m.name for m in available_models if 'generateContent' in m.supported_generation_methods]
            logger.info(f"Available generative models: {generative_models[:5]}")
        except Exception as e:
            logger.warning(f"Could not list models: {e}")
        
        # Try to use the specified model
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Successfully initialized model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize model {model_name}: {e}")
            raise
        
        # Safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Memory for state management
        self.memory = MemorySaver()
        
        # Build the planning graph
        self.planner = self._build_planning_graph()
    
    def _build_planning_graph(self) -> StateGraph:
        """Build the LangGraph planning workflow"""
        
        workflow = StateGraph(PlanningState)
        
        # Add nodes
        workflow.add_node("generate_initial_plan", self._generate_initial_plan_node)
        workflow.add_node("analyze_decision_points", self._analyze_decision_points_node)
        workflow.add_node("generate_questions", self._generate_questions_node)
        workflow.add_node("evaluate_plan_quality", self._evaluate_plan_quality_node)
        workflow.add_node("refine_plan", self._refine_plan_node)
        
        # Add edges
        workflow.add_edge(START, "generate_initial_plan")
        workflow.add_edge("generate_initial_plan", "analyze_decision_points")
        workflow.add_edge("analyze_decision_points", "generate_questions")
        workflow.add_edge("generate_questions", "evaluate_plan_quality")
        
        # Conditional edge for iteration
        workflow.add_conditional_edges(
            "evaluate_plan_quality",
            self._should_continue_refining,
            {
                "continue": "refine_plan",
                "finish": END
            }
        )
        workflow.add_edge("refine_plan", "analyze_decision_points")
        
        return workflow.compile(checkpointer=self.memory)
    
    async def _generate_initial_plan_node(self, state: PlanningState) -> PlanningState:
        """Generate initial research plan from user query"""
        logger.info("🎯 Generating initial research plan...")
        
        user_query = state["user_query"]
        
        prompt = f"""
        You are an expert research planner. Given a user's research query, create a detailed research plan.
        
        User Query: {user_query}
        
        Create a research plan with the following structure:
        - Break down into 4-8 specific research steps
        - For each step, identify:
          * Clear description of what to do
          * Dependencies on other steps
          * Tools/methods needed
          * Expected output
          * Confidence level (0-1)
          * Ambiguity score (0-1, higher = more ambiguous)
        
        Return as JSON in this format:
        {{
            "steps": [
                {{
                    "id": "step_1",
                    "description": "...",
                    "dependencies": ["step_0"],
                    "tools_needed": ["arxiv_search", "web_search"],
                    "expected_output": "...",
                    "confidence": 0.8,
                    "ambiguity_score": 0.3
                }}
            ]
        }}
        
        Focus on creating actionable, specific steps while identifying areas of uncertainty.
        """
        
        try:
            response = await self._call_gemini_async(prompt)
            
            # Clean the response to extract JSON
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()
            
            plan_data = json.loads(response_clean)
            
            # Convert to ResearchStep objects
            initial_plan = []
            for step_data in plan_data["steps"]:
                step = ResearchStep(
                    id=step_data["id"],
                    description=step_data["description"], 
                    dependencies=step_data["dependencies"],
                    tools_needed=step_data["tools_needed"],
                    expected_output=step_data["expected_output"],
                    confidence=step_data["confidence"],
                    ambiguity_score=step_data["ambiguity_score"]
                )
                initial_plan.append(step)
            
            state["initial_plan"] = initial_plan
            state["iteration_count"] = 1
            state["max_iterations"] = 3
            
            logger.info(f"Generated initial plan with {len(initial_plan)} steps")
            
        except Exception as e:
            logger.error(f"Error generating initial plan: {e}")
            # Create a fallback plan
            fallback_step = ResearchStep(
                id="step_1",
                description=f"Research the topic: {user_query}",
                dependencies=[],
                tools_needed=["web_search"],
                expected_output="Basic understanding of the topic",
                confidence=0.5,
                ambiguity_score=0.8
            )
            state["initial_plan"] = [fallback_step]
            state["iteration_count"] = 1
            state["max_iterations"] = 3
        
        return state
    
    async def _analyze_decision_points_node(self, state: PlanningState) -> PlanningState:
        """Analyze plan to identify decision points and ambiguities"""
        logger.info("🔍 Analyzing decision points...")
        
        current_plan = state.get("refined_plan")
        if not current_plan:
            current_plan = state["initial_plan"]
        
        # Debug: Log plan details
        logger.info(f"Analyzing {len(current_plan)} steps")
        for step in current_plan:
            logger.info(f"Step {step.id}: confidence={step.confidence:.2f}, ambiguity={step.ambiguity_score:.2f}")
        
        # Find high-ambiguity steps and decision points
        decision_points = []
        
        for step in current_plan:
            if step.ambiguity_score > 0.5 or step.confidence < 0.7:
                logger.info(f"Step {step.id} needs decision point analysis (ambiguity={step.ambiguity_score:.2f}, confidence={step.confidence:.2f})")
                
                prompt = f"""
                Analyze this research step for decision points and ambiguities:
                
                Step: {step.description}
                Tools needed: {step.tools_needed}
                Expected output: {step.expected_output}
                Ambiguity score: {step.ambiguity_score}
                Confidence: {step.confidence}
                
                Identify:
                1. What specific decisions need to be made?
                2. What are the alternative approaches?
                3. What criteria are needed to choose?
                4. What additional context is required?
                
                Return as JSON:
                {{
                    "decision_description": "...",
                    "options": ["option1", "option2"],
                    "criteria_needed": ["criterion1", "criterion2"],
                    "impact_scope": "high"
                }}
                """
                
                try:
                    response = await self._call_gemini_async(prompt)
                    
                    # Clean JSON response
                    response_clean = response.strip()
                    if response_clean.startswith("```json"):
                        response_clean = response_clean[7:]
                    if response_clean.endswith("```"):
                        response_clean = response_clean[:-3]
                    response_clean = response_clean.strip()
                    
                    decision_data = json.loads(response_clean)
                    
                    decision_point = DecisionPoint(
                        step_id=step.id,
                        decision_description=decision_data["decision_description"],
                        options=decision_data["options"],
                        criteria_needed=decision_data["criteria_needed"],
                        impact_scope=decision_data["impact_scope"]
                    )
                    decision_points.append(decision_point)
                    logger.info(f"Created decision point for step {step.id}")
                    
                except Exception as e:
                    logger.warning(f"Error analyzing step {step.id}: {e}")
                    # Create a fallback decision point
                    decision_point = DecisionPoint(
                        step_id=step.id,
                        decision_description=f"How to best approach: {step.description}",
                        options=["approach_1", "approach_2"],
                        criteria_needed=["clarity", "feasibility"],
                        impact_scope="medium"
                    )
                    decision_points.append(decision_point)
                    logger.info(f"Created fallback decision point for step {step.id}")
        
        state["decision_points"] = decision_points
        logger.info(f"Identified {len(decision_points)} decision points")
        
        return state
    
    async def _generate_questions_node(self, state: PlanningState) -> PlanningState:
        """Generate follow-up questions to resolve decision points"""
        logger.info("❓ Generating follow-up questions...")
        
        decision_points = state["decision_points"]
        follow_up_questions = []
        
        for dp in decision_points:
            prompt = f"""
            Generate follow-up questions to resolve this research decision point:
            
            Decision: {dp.decision_description}
            Options: {dp.options}
            Criteria needed: {dp.criteria_needed}
            Impact: {dp.impact_scope}
            
            Generate 2-3 specific, actionable questions that would help resolve this decision.
            Questions should be:
            - Specific and answerable
            - Focused on the most critical ambiguities
            - Designed to improve plan quality
            
            Return as JSON:
            {{
                "questions": [
                    {{
                        "question": "...",
                        "type": "clarification",
                        "priority": 4,
                        "rationale": "..."
                    }}
                ]
            }}
            
            Valid types: clarification, constraint, preference, context, scope, methodology
            Priority: 1-5 (5 = highest)
            """
            
            try:
                response = await self._call_gemini_async(prompt)
                
                # Clean JSON response
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean[7:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                response_clean = response_clean.strip()
                
                questions_data = json.loads(response_clean)
                
                for q_data in questions_data["questions"]:
                    question = FollowUpQuestion(
                        question=q_data["question"],
                        question_type=QuestionType(q_data["type"]),
                        related_step_ids=[dp.step_id],
                        priority=q_data["priority"],
                        rationale=q_data["rationale"]
                    )
                    follow_up_questions.append(question)
                    
            except Exception as e:
                logger.warning(f"Error generating questions for {dp.step_id}: {e}")
                # Create fallback question
                question = FollowUpQuestion(
                    question=f"What is the best approach for {dp.decision_description}?",
                    question_type=QuestionType.CLARIFICATION,
                    related_step_ids=[dp.step_id],
                    priority=3,
                    rationale="Need clarification on approach"
                )
                follow_up_questions.append(question)
        
        # Sort by priority (highest first)
        follow_up_questions.sort(key=lambda x: x.priority, reverse=True)
        
        state["follow_up_questions"] = follow_up_questions
        logger.info(f"Generated {len(follow_up_questions)} follow-up questions")
        
        return state
    
    async def _evaluate_plan_quality_node(self, state: PlanningState) -> PlanningState:
        """Evaluate the quality of the current plan"""
        logger.info("📊 Evaluating plan quality...")
        
        current_plan = state.get("refined_plan")
        if not current_plan:
            current_plan = state["initial_plan"]
        
        if not current_plan:
            state["plan_quality_score"] = 0.0
            logger.warning("No plan to evaluate")
            return state
        
        # Calculate quality metrics
        total_confidence = sum(step.confidence for step in current_plan)
        avg_confidence = total_confidence / len(current_plan)
        
        total_ambiguity = sum(step.ambiguity_score for step in current_plan)
        avg_ambiguity = total_ambiguity / len(current_plan)
        
        # Quality score (higher is better)
        quality_score = (avg_confidence * 0.6) + ((1 - avg_ambiguity) * 0.4)
        
        state["plan_quality_score"] = quality_score
        logger.info(f"Plan quality score: {quality_score:.2f} (avg_confidence: {avg_confidence:.2f}, avg_ambiguity: {avg_ambiguity:.2f})")
        
        return state
    
    def _should_continue_refining(self, state: PlanningState) -> str:
        """Decide whether to continue refining the plan"""
        quality_score = state["plan_quality_score"]
        iteration_count = state["iteration_count"]
        max_iterations = state["max_iterations"]
        
        logger.info(f"Quality check: score={quality_score:.2f}, iteration={iteration_count}/{max_iterations}")
        
        # Continue if quality is low and we haven't exceeded max iterations
        if quality_score < 0.8 and iteration_count < max_iterations:
            logger.info("Continuing refinement...")
            return "continue"
        else:
            logger.info("Finishing refinement...")
            return "finish"
    
    async def _refine_plan_node(self, state: PlanningState) -> PlanningState:
        """Refine the plan based on generated questions"""
        logger.info("🔧 Refining research plan...")
        
        current_plan = state.get("refined_plan", state["initial_plan"])
        questions = state["follow_up_questions"]
        
        # Group questions by related steps
        questions_by_step = {}
        for q in questions:
            for step_id in q.related_step_ids:
                if step_id not in questions_by_step:
                    questions_by_step[step_id] = []
                questions_by_step[step_id].append(q)
        
        refined_plan = []
        
        for step in current_plan:
            if step.id in questions_by_step:
                # Refine this step based on questions
                related_questions = questions_by_step[step.id]
                questions_text = "\n".join([f"- {q.question} ({q.rationale})" for q in related_questions])
                
                prompt = f"""
                Refine this research step based on the following clarifying questions:
                
                Original Step:
                Description: {step.description}
                Tools: {step.tools_needed}
                Expected Output: {step.expected_output}
                
                Questions to Address:
                {questions_text}
                
                Create a refined version that:
                1. Addresses the questions raised
                2. Is more specific and actionable
                3. Reduces ambiguity
                4. Maintains feasibility
                
                Return as JSON:
                {{
                    "description": "...",
                    "tools_needed": ["..."],
                    "expected_output": "...",
                    "confidence": 0.9,
                    "ambiguity_score": 0.2
                }}
                """
                
                try:
                    response = await self._call_gemini_async(prompt)
                    
                    # Clean JSON response
                    response_clean = response.strip()
                    if response_clean.startswith("```json"):
                        response_clean = response_clean[7:]
                    if response_clean.endswith("```"):
                        response_clean = response_clean[:-3]
                    response_clean = response_clean.strip()
                    
                    refined_data = json.loads(response_clean)
                    
                    refined_step = ResearchStep(
                        id=step.id,
                        description=refined_data["description"],
                        dependencies=step.dependencies,
                        tools_needed=refined_data["tools_needed"],
                        expected_output=refined_data["expected_output"],
                        confidence=refined_data["confidence"],
                        ambiguity_score=refined_data["ambiguity_score"]
                    )
                    refined_plan.append(refined_step)
                    
                except Exception as e:
                    logger.warning(f"Error refining step {step.id}: {e}")
                    # Improve step manually
                    refined_step = ResearchStep(
                        id=step.id,
                        description=f"Enhanced: {step.description}",
                        dependencies=step.dependencies,
                        tools_needed=step.tools_needed,
                        expected_output=step.expected_output,
                        confidence=min(step.confidence + 0.1, 1.0),
                        ambiguity_score=max(step.ambiguity_score - 0.1, 0.0)
                    )
                    refined_plan.append(refined_step)
            else:
                refined_plan.append(step)  # No changes needed
        
        state["refined_plan"] = refined_plan
        state["iteration_count"] += 1
        
        logger.info(f"Plan refined (iteration {state['iteration_count']})")
        
        return state
    
    async def _call_gemini_async(self, prompt: str) -> str:
        """Async wrapper for Gemini API calls"""
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            # Check if response was blocked
            if not response.text:
                if hasattr(response, 'prompt_feedback'):
                    logger.warning(f"Response blocked: {response.prompt_feedback}")
                return "Error: Response was blocked by safety filters"
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Return a more helpful error message
            if "404" in str(e):
                return "Error: Model not found. Please check available models."
            elif "safety" in str(e).lower():
                return "Error: Content blocked by safety filters."
            else:
                raise
    
    async def generate_research_plan(self, user_query: str, thread_id: str = None) -> Dict[str, Any]:
        """
        Main method to generate research plan with follow-up questions
        
        Args:
            user_query: The user's research question
            thread_id: Optional thread ID for conversation tracking
            
        Returns:
            Dict containing refined plan and follow-up questions
        """
        logger.info(f"🚀 Starting research planning for: '{user_query}'")
        
        # Generate thread_id if not provided
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        initial_state = {
            "user_query": user_query,
            "initial_plan": [],
            "decision_points": [],
            "follow_up_questions": [],
            "refined_plan": [],
            "plan_quality_score": 0.0,
            "iteration_count": 0,
            "max_iterations": 3
        }
        
        # Configuration with thread_id (required for checkpointer)
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            final_state = await self.planner.ainvoke(initial_state, config=config)
            
            # Convert to serializable format
            final_plan = final_state.get("refined_plan")
            if not final_plan:
                final_plan = final_state.get("initial_plan", [])
            
            result = {
                "success": True,
                "user_query": user_query,
                "thread_id": thread_id,
                "final_plan": [
                    {
                        "id": step.id,
                        "description": step.description,
                        "dependencies": step.dependencies,
                        "tools_needed": step.tools_needed,
                        "expected_output": step.expected_output,
                        "confidence": step.confidence,
                        "ambiguity_score": step.ambiguity_score
                    }
                    for step in final_plan
                ],
                "follow_up_questions": [
                    {
                        "question": q.question,
                        "type": q.question_type.value,
                        "priority": q.priority,
                        "rationale": q.rationale,
                        "related_steps": q.related_step_ids
                    }
                    for q in final_state["follow_up_questions"]
                ],
                "plan_quality_score": final_state["plan_quality_score"],
                "iterations_completed": final_state["iteration_count"],
                "decision_points_resolved": len(final_state["decision_points"])
            }
            
            logger.info(f"✅ Research planning completed successfully")
            logger.info(f"📊 Plan quality: {result['plan_quality_score']:.2f}")
            logger.info(f"❓ Follow-up questions: {len(result['follow_up_questions'])}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in research planning: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "user_query": user_query,
                "thread_id": thread_id
            }

# Utility function to check available models
async def check_available_models(api_key: str):
    """Check what Gemini models are available"""
    try:
        genai.configure(api_key=api_key)
        models = list(genai.list_models())
        
        print("🔍 Available Gemini Models:")
        print("-" * 40)
        
        generative_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                generative_models.append(model.name)
                print(f"✅ {model.name}")
        
        if not generative_models:
            print("❌ No generative models found")
        
        # Return the actual model names, not just the last part
        return generative_models
        
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return []

# Updated main function with proper model selection
async def main():
    """Test the research planning module"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get Gemini API key from environment variable
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if not GEMINI_API_KEY:
        print("⚠️  Please set GEMINI_API_KEY in your .env file")
        print("Create a .env file with:")
        print("GEMINI_API_KEY=your_actual_gemini_api_key_here")
        return
    
    # Check available models first
    print("🔍 Checking available Gemini models...")
    available_models = await check_available_models(GEMINI_API_KEY)
    
    if not available_models:
        print("❌ No compatible models found. Please check your API key.")
        return
    
    # Find the best available model (prefer newer versions)
    preferred_models = [
        "models/gemini-1.5-pro-latest",
        "models/gemini-1.5-pro-001", 
        "models/gemini-1.0-pro-latest",
        "models/gemini-1.0-pro"
    ]
    
    model_to_use = None
    for preferred in preferred_models:
        if preferred in available_models:
            model_to_use = preferred
            break
    
    # If none of the preferred models found, use the first available
    if not model_to_use:
        model_to_use = available_models[0]
    
    print(f"🚀 Using model: {model_to_use}")
    
    try:
        planner = IntelligentResearchPlanner(GEMINI_API_KEY, model_name=model_to_use)
    except Exception as e:
        print(f"❌ Error initializing planner: {e}")
        return
    
    # Test queries
    test_queries = [
        "How do transformers work and what are their limitations?",
        "What are the best practices for fine-tuning large language models?",
        "Compare different approaches to multi-agent systems in AI"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"🎯 PLANNING FOR: {query}")
        print('='*80)
        
        # Generate unique thread_id for each query
        thread_id = str(uuid.uuid4())
        
        result = await planner.generate_research_plan(query, thread_id)
        
        if result["success"]:
            print(f"✅ SUCCESS")
            print(f"🆔 Thread ID: {result['thread_id']}")
            print(f"📊 Plan Quality: {result['plan_quality_score']:.2f}")
            print(f"🔄 Iterations: {result['iterations_completed']}")
            
            print(f"\n📋 FINAL RESEARCH PLAN:")
            for i, step in enumerate(result["final_plan"], 1):
                print(f"{i}. {step['description']}")
                print(f"   Tools: {', '.join(step['tools_needed'])}")
                print(f"   Confidence: {step['confidence']:.2f}")
                print()
            
            print(f"❓ FOLLOW-UP QUESTIONS:")
            for i, q in enumerate(result["follow_up_questions"], 1):
                print(f"{i}. [{q['type'].upper()}] {q['question']}")
                print(f"   Priority: {q['priority']}/5")
                print(f"   Rationale: {q['rationale']}")
                print()
        
        else:
            print(f"❌ ERROR: {result['error']}")
        
        # Small delay between tests
        await asyncio.sleep(2)

# Updated quick test function
async def quick_test():
    """Quick test with one query"""
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if not GEMINI_API_KEY:
        print("⚠️  Please set GEMINI_API_KEY in your .env file")
        return
    
    # Check available models
    print("🔍 Checking available models...")
    available_models = await check_available_models(GEMINI_API_KEY)
    
    if not available_models:
        print("❌ No compatible models found")
        return
    
    # Select best available model
    preferred_models = [
        "models/gemini-1.5-pro-latest",
        "models/gemini-1.5-pro-001", 
        "models/gemini-1.0-pro-latest",
        "models/gemini-1.0-pro"
    ]
    
    model_to_use = None
    for preferred in preferred_models:
        if preferred in available_models:
            model_to_use = preferred
            break
    
    if not model_to_use:
        model_to_use = available_models[0]
    
    print(f"🚀 Using model: {model_to_use}")
    
    try:
        planner = IntelligentResearchPlanner(GEMINI_API_KEY, model_name=model_to_use)
    except Exception as e:
        print(f"❌ Error initializing planner: {e}")
        return
    
    test_query = "How do transformers work and what are their limitations?"
    print(f"🎯 Testing: {test_query}")
    
    result = await planner.generate_research_plan(test_query)
    
    if result["success"]:
        print("✅ SUCCESS!")
        print(f"📊 Plan quality: {result['plan_quality_score']:.2f}")
        print(f"📋 Steps: {len(result['final_plan'])}")
        print(f"❓ Questions: {len(result['follow_up_questions'])}")
        
        # Show first few steps
        print("\n📋 Sample steps:")
        for step in result["final_plan"][:3]:
            print(f"- {step['description']}")
        
        # Show first few questions
        print("\n❓ Sample questions:")
        for q in result["follow_up_questions"][:3]:
            print(f"- {q['question']}")
            
    else:
        print(f"❌ ERROR: {result['error']}")

if __name__ == "__main__":
    print("🎯 Research Planning Module")
    print("Choose an option:")
    print("1. Quick test (1 query)")
    print("2. Full test (3 queries)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(quick_test())
    elif choice == "2":
        asyncio.run(main())
    else:
        print("Invalid choice. Running quick test by default.")
        asyncio.run(quick_test())