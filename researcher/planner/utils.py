"""
Utility functions and parsers for the Deep Search Planner Agent
"""
import json
import re
from typing import Dict, List, Any, Optional
from researcher.planner.models import PlanData, PlanEvaluation
from researcher.planner.config import Config, REQUIRED_PLAN_KEYS


class ResponseParser:
    """Utility class for parsing AI model responses"""
    
    @staticmethod
    def clean_json_response(response_text: str) -> str:
        """Clean response text to extract JSON"""
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        return response_text.strip()
    
    @staticmethod
    def extract_enhanced_query(response_text: str) -> str:
        """Extract the Enhanced Query from the LLM response"""
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for the Enhanced Query line
            if line.startswith('**Enhanced Query:**'):
                enhanced_query = line.replace('**Enhanced Query:**', '').strip()
                if enhanced_query:
                    return enhanced_query
            # Alternative formats the LLM might use
            elif 'enhanced query:' in line.lower():
                parts = line.split(':')
                if len(parts) > 1:
                    enhanced_query = ':'.join(parts[1:]).strip()
                    if enhanced_query:
                        return enhanced_query
        
        # Fallback: look for the first substantial sentence
        for line in lines:
            line = line.strip()
            if len(line) > 50 and line.endswith('.'):
                return line
        
        # Ultimate fallback: return first non-empty line
        for line in lines:
            line = line.strip()
            if line and len(line) > 20:
                return line
        
        # If all else fails, return a generic enhancement
        return f"Comprehensive analysis and investigation of {response_text[:100].strip()}"
    
    @staticmethod
    def parse_initial_plan_response(response_text: str, enhanced_query: str) -> PlanData:
        """Parse the structured initial plan response"""
        plan_data = PlanData(
            search_steps=[],
            key_areas=[],
            information_sources=[],
            search_strategies=[],
            success_metrics=[]
        )
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect phases (e.g., "### 1. Phase 1:")
            if line.startswith('###') and 'Phase' in line:
                current_section = 'phases'
                phase_title = line.replace('###', '').strip()
                if phase_title:
                    plan_data.search_steps.append(phase_title)
                continue
            
            # Detect keywords section
            elif 'Initial Keywords' in line or 'Keywords for Broad Searches' in line:
                current_section = 'keywords'
                continue
            
            # Detect decision points section
            elif 'Decision Points' in line or 'Ambiguities' in line:
                current_section = 'decision_points'
                continue
            
            # Extract content based on current section
            if current_section == 'phases':
                if '**Objective:**' in line:
                    objective = line.replace('**Objective:**', '').strip()
                    if objective:
                        plan_data.key_areas.append(objective)
                
                elif line.startswith('*') and any(keyword in line.lower() for keyword in 
                    ['literature', 'database', 'report', 'interview', 'survey', 'search']):
                    activity = line.lstrip('* ').strip()
                    if 'database' in activity.lower() or 'report' in activity.lower():
                        plan_data.information_sources.append(activity)
                    else:
                        plan_data.search_strategies.append(activity)
            
            elif current_section == 'keywords':
                if line.startswith('*') or line.startswith('-'):
                    keyword = line.lstrip('*- ').strip().strip('"\'')
                    if keyword and len(keyword) > 3:
                        plan_data.search_strategies.append(f"Search for: {keyword}")
            
            elif current_section == 'decision_points':
                if line.startswith('*') or line.startswith('-'):
                    decision_point = line.lstrip('*- ').strip()
                    if decision_point:
                        plan_data.success_metrics.append(f"Clarify: {decision_point}")
        
        # Ensure we have at least some content
        if not plan_data.search_steps:
            plan_data.search_steps = [
                "Phase 1: Foundational Understanding & Overview",
                "Phase 2: Deep Dive into Core Components", 
                "Phase 3: Analysis of Impacts & Challenges"
            ]
        
        if not plan_data.key_areas:
            plan_data.key_areas = [
                "Establish broad understanding of the research topic",
                "Gather detailed information on core components",
                "Analyze implications and challenges"
            ]
        
        if not plan_data.information_sources:
            plan_data.information_sources = [
                "Academic databases and peer-reviewed journals",
                "Industry reports and governmental publications",
                "Expert interviews and case studies"
            ]
        
        if not plan_data.search_strategies:
            plan_data.search_strategies = [
                "Systematic literature review approach",
                "Progressive refinement from broad to specific",
                "Multi-source validation and cross-referencing"
            ]
        
        if not plan_data.success_metrics:
            plan_data.success_metrics = [
                "Comprehensive coverage of all key topics",
                "Quality and credibility of sources identified",
                "Clear identification of research gaps and ambiguities"
            ]
        
        return plan_data
    
    @staticmethod
    def parse_evaluation_response(response_text: str, max_questions: int) -> PlanEvaluation:
        """Parse evaluation response into PlanEvaluation object"""
        try:
            cleaned_response = ResponseParser.clean_json_response(response_text)
            evaluation_data = json.loads(cleaned_response)
            
            # Validate required keys and provide defaults
            required_keys = ['overall_assessment', 'strengths', 'weaknesses_and_recommendations', 
                           'areas_for_potential_further_clarification', 'generated_questions']
            for key in required_keys:
                if key not in evaluation_data:
                    if key == 'overall_assessment':
                        evaluation_data[key] = "Plan evaluation completed."
                    else:
                        evaluation_data[key] = []
            
            # Extract decision points/ambiguities
            decision_points = []
            
            # Extract from weaknesses and recommendations
            for weakness_item in evaluation_data.get('weaknesses_and_recommendations', []):
                if isinstance(weakness_item, dict):
                    weakness = weakness_item.get('weakness', '')
                    if weakness:
                        decision_points.append(weakness)
                elif isinstance(weakness_item, str):
                    decision_points.append(weakness_item)
            
            # Extract from areas for clarification
            for clarification in evaluation_data.get('areas_for_potential_further_clarification', []):
                if isinstance(clarification, str):
                    decision_points.append(clarification)
            
            # Extract all clarifying questions into a single list
            all_questions = []
            all_questions.extend(evaluation_data.get('generated_questions', []))
            
            # Get questions from weaknesses_and_recommendations
            for weakness_item in evaluation_data.get('weaknesses_and_recommendations', []):
                if isinstance(weakness_item, dict):
                    questions = weakness_item.get('clarifying_questions', [])
                    if isinstance(questions, list):
                        all_questions.extend(questions)
                    elif isinstance(questions, str):
                        all_questions.append(questions)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_questions = []
            for question in all_questions:
                if question not in seen:
                    seen.add(question)
                    unique_questions.append(question)
            
            # Limit to max_questions
            final_questions = evaluation_data.get('generated_questions', [])[:max_questions]
            
            if len(final_questions) < max_questions:
                additional_needed = max_questions - len(final_questions)
                for question in unique_questions:
                    if question not in final_questions:
                        final_questions.append(question)
                        additional_needed -= 1
                        if additional_needed == 0:
                            break
            
            final_questions = final_questions[:max_questions]
            
            return PlanEvaluation(
                overall_score=0.0,  # This will be set elsewhere
                metric_scores={},
                evaluation_summary=evaluation_data.get('overall_assessment', ''),
                actionable_feedback=evaluation_data.get('weaknesses_and_recommendations', []),
                areas_for_clarification=evaluation_data.get('areas_for_potential_further_clarification', []),
                decision_points=decision_points,
                clarifying_questions=final_questions
            )
            
        except json.JSONDecodeError:
            return ResponseParser.parse_evaluation_fallback(response_text, max_questions)
    
    @staticmethod
    def parse_evaluation_fallback(response_text: str, max_questions: int) -> PlanEvaluation:
        """Fallback parser for evaluation responses that aren't valid JSON"""
        decision_points = []
        clarifying_questions = []
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            line_lower = line.lower()
            if 'question' in line_lower:
                current_section = 'questions'
            elif 'weakness' in line_lower or 'recommendation' in line_lower:
                current_section = 'weaknesses'
            elif 'clarification' in line_lower or 'ambiguit' in line_lower:
                current_section = 'clarifications'
            
            # Extract content
            if current_section and (line.startswith(('-', '•', '*')) or line[0].isdigit() or '?' in line):
                cleaned_line = line.lstrip('-•*0123456789. ').strip()
                if cleaned_line and len(cleaned_line) > 10:
                    if current_section == 'questions':
                        if '?' in cleaned_line and len(clarifying_questions) < max_questions:
                            clarifying_questions.append(cleaned_line)
                    else:
                        decision_points.append(cleaned_line)
        
        # Ensure we have some content
        if not decision_points:
            decision_points = [
                "Plan scope and objectives need clarification",
                "Research methodology requires more specificity",
                "Success criteria and metrics need definition"
            ]
        
        # Generate simple questions if none found
        if not clarifying_questions:
            clarifying_questions = Config.DEFAULT_SIMPLE_QUESTIONS[:max_questions]
        
        return PlanEvaluation(
            overall_score=0.0,
            metric_scores={},
            evaluation_summary="Plan requires further analysis and refinement",
            actionable_feedback=[],
            areas_for_clarification=[],
            decision_points=decision_points,
            clarifying_questions=clarifying_questions
        )
    
    @staticmethod
    def parse_plan_response(response_text: str) -> Dict[str, Any]:
        """Parse a plan response into dictionary format"""
        try:
            cleaned_response = ResponseParser.clean_json_response(response_text)
            plan_dict = json.loads(cleaned_response)
            
            # Validate structure and provide defaults
            for key in REQUIRED_PLAN_KEYS:
                if key not in plan_dict:
                    plan_dict[key] = []
            
            return plan_dict
            
        except json.JSONDecodeError:
            return ResponseParser.parse_plan_fallback(response_text)
    
    @staticmethod
    def parse_plan_fallback(response_text: str) -> Dict[str, Any]:
        """Fallback parser for plan responses that aren't valid JSON"""
        plan_dict = {key: [] for key in REQUIRED_PLAN_KEYS}
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            line_lower = line.lower()
            for key in REQUIRED_PLAN_KEYS:
                if key.replace('_', ' ') in line_lower:
                    current_section = key
                    break
            
            # Extract content
            if current_section and (line.startswith(('-', '•', '*')) or line[0].isdigit()):
                cleaned_line = line.lstrip('-•*0123456789. ').strip().strip('"\'')
                if cleaned_line and len(cleaned_line) > 10:
                    plan_dict[current_section].append(cleaned_line)
        
        # Ensure we have some content
        for key in REQUIRED_PLAN_KEYS:
            if not plan_dict[key]:
                plan_dict[key] = [f"Default {key.replace('_', ' ')} item"]
        
        return plan_dict


class ScoreExtractor:
    """Utility class for extracting and normalizing scores"""
    
    @staticmethod
    def extract_numeric_score(response_text: str) -> float:
        """Extract numeric score from response text"""
        scores = re.findall(r'\d+\.?\d*', response_text)
        if scores:
            overall_score = float(scores[-1])
            # Normalize to 0-100 range
            if overall_score <= 10:
                overall_score *= 10
            elif overall_score > 100:
                overall_score = min(overall_score, 100)
            return overall_score
        return 50.0  # Default middle score


class PlanFormatter:
    """Utility class for formatting and displaying plans"""
    
    @staticmethod
    def format_plan_display(plan_data: PlanData, title: str = "Search Plan") -> str:
        """Format plan data for display"""
        output = [f"\n{'='*60}", f"{title.upper()}", f"{'='*60}"]
        
        sections = [
            ("🔍 Search Steps", plan_data.search_steps),
            ("🎯 Key Areas", plan_data.key_areas),
            ("📚 Information Sources", plan_data.information_sources),
            ("🔎 Search Strategies", plan_data.search_strategies),
            ("✅ Success Metrics", plan_data.success_metrics)
        ]
        
        for section_title, items in sections:
            output.append(f"\n{section_title}:")
            for i, item in enumerate(items, 1):
                output.append(f"   {i}. {item}")
        
        output.append(f"{'='*60}")
        return '\n'.join(output)
    
    @staticmethod
    def format_evaluation_display(evaluation: PlanEvaluation, overall_score: float) -> str:
        """Format evaluation results for display"""
        output = [f"\n{'='*60}", "📊 DETAILED PLAN EVALUATION", f"{'='*60}"]
        
        # Overall score
        output.append(f"🎯 Overall Score: {overall_score:.1f}/100")
        
        # Metric breakdown
        if evaluation.metric_scores:
            output.append(f"\n📋 METRIC BREAKDOWN:")
            metric_names = {
                'completeness': 'Completeness (25%)',
                'clarity_specificity': 'Clarity & Specificity (20%)',
                'logical_flow_cohesion': 'Logical Flow & Cohesion (20%)',
                'feasibility_realism': 'Feasibility & Realism (15%)',
                'keyword_relevance_breadth': 'Keyword Relevance & Breadth (20%)'
            }
            
            for key, name in metric_names.items():
                score = evaluation.metric_scores.get(key, 0)
                bars = '█' * int(score) + '░' * (10 - int(score))
                output.append(f"   {name}: {score}/10 [{bars}]")
        
        # Summary
        if evaluation.evaluation_summary:
            output.append(f"\n💭 SUMMARY:")
            output.append(f"   {evaluation.evaluation_summary}")
        
        # Actionable feedback
        if evaluation.actionable_feedback:
            output.append(f"\n🔧 ACTIONABLE FEEDBACK:")
            for i, item in enumerate(evaluation.actionable_feedback, 1):
                feedback_text = item if isinstance(item, str) else item.get('weakness', str(item))
                output.append(f"   {i}. {feedback_text}")
        
        output.append(f"{'='*60}")
        return '\n'.join(output)