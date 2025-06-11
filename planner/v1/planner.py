import google.generativeai as genai
import json
import time
import os
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class SearchPlan:
    """Represents a search plan with its components and metadata"""
    query: str
    enhanced_query: str
    plan_steps: List[str]
    decision_points: List[str]
    clarifying_questions: List[str]
    quality_score: float
    iteration: int
    timestamp: float

class DeepSearchPlannerAgent:
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-pro"):
        """
        Initialize the Deep Search Planner Agent
        
        Args:
            api_key: Google AI API key (if None, loads from GOOGLE_API_KEY env var)
            model_name: Gemini model to use
        """
        # Load API key from environment if not provided
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided either as parameter or GOOGLE_API_KEY environment variable")
            
        self.model_name = model_name
        self.model = None
        self.search_history = []
        
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
                return True
            else:
                print("❌ Failed to load Gemini model")
                return False
                
        except Exception as e:
            print(f"❌ Error loading Gemini model: {str(e)}")
            return False
    
    def enhance_search_query(self, user_query: str) -> str:
        """
        Enhance the user's search query using the specialized prompt
        
        Args:
            user_query: Original user search query
            
        Returns:
            str: Enhanced search query
        """
        prompt_for_enhance_search_query = """
    **System Message:** You are an expert Research Strategist AI. Your primary function is to deconstruct a user's initial, often vague, search query and reformulate it into a sophisticated, structured, and comprehensive query. This output will be used by another AI to generate a detailed research plan. Your adherence to the user's original topic is paramount.

    ---

    **User Message:**

    Your task is to take the user's search query and enhance it. The enhancement must clarify the user's intent and break down the topic into its core logical pillars for investigation.

    **Follow these steps:**
    1.  **Analyze:** Deeply analyze the provided `[User Query]` to identify the core subject and implied areas of interest. Your analysis must be confined to the scope of the query.
    2.  **Synthesize:** Create a single, concise, and highly descriptive **"Enhanced Query"**. This sentence should act as a master title for a comprehensive research project that is directly based on the user's query.
    3.  **Decompose:** Break down the Enhanced Query into a list of **"Key Topics"**. These topics should be the primary themes or sub-questions directly derivable from the user's query.

    **Crucial Constraints:**
    * **Stay Strictly On Topic:** Do not add any new information, concepts, or facts that are not directly implied by the `[User Query]`. Your role is to structure the existing topic, not to add your own knowledge to it.
    * **No Fabrication:** Do not invent details or go off on tangents. The output must be a direct, logical expansion of the original query.
    * **No Plan Generation:** DO NOT generate the research plan itself or any prose beyond the "Enhanced Query" and "Key Topics".
    * **Strict Formatting:** Your output must strictly follow the format shown in the examples.

    ---

    **Example 1: Technology / Health**

    `[User Query]`: "AI in healthcare"

    **Your Output:**
    **Enhanced Query:** An in-depth analysis of the application, ethical implications, and future trajectory of Artificial Intelligence in the healthcare sector, focusing on diagnostics, drug discovery, and patient care personalization.
    **Key Topics:**
    * AI-powered medical imaging and diagnostics (e.g., radiology, pathology).
    * Machine learning models for drug discovery and clinical trial optimization.
    * Ethical considerations, bias, and patient data privacy in medical AI.
    * Regulatory landscape and FDA approval for AI-based medical devices.
    * Personalized treatment plans and predictive health analytics.

    ---

    **Example 2: Business / Logistics**

    `[User Query]`: "supply chain issues"

    **Your Output:**
    **Enhanced Query:** A comprehensive investigation into the causes, impacts, and strategic solutions for recent global supply chain disruptions, examining vulnerabilities from the perspectives of logistics, technology, and geopolitics.
    **Key Topics:**
    * Impact of the COVID-19 pandemic on global logistics and manufacturing.
    * Geopolitical factors (e.g., trade wars, conflicts) affecting supply routes.
    * Technological solutions for supply chain resilience (e.g., blockchain, AI forecasting).
    * The shift from "just-in-time" to "just-in-case" inventory strategies.
    * Labor shortages and their effect on transportation and warehousing.

    ---

    **Example 3: Environmental Science**

    `[User Query]`: "microplastics in ocean"

    **Your Output:**
    **Enhanced Query:** An investigation into the sources, distribution, and ecological impact of microplastic pollution in marine environments, and an evaluation of potential mitigation strategies and technological solutions.
    **Key Topics:**
    * Primary and secondary sources of microplastic pollution.
    * Bioaccumulation of microplastics in the marine food web.
    * Verified impacts on marine biodiversity and specific ecosystem health markers.
    * Current and emerging technologies for filtering and removing microplastics from water.
    * International policies and treaties aimed at reducing plastic pollution.

    ---

    **Example 4: Finance / Economics**

    `[User Query]`: "cryptocurrency regulation"

    **Your Output:**
    **Enhanced Query:** A global analysis of the current regulatory frameworks and future policy directions for cryptocurrencies and digital assets, focusing on investor protection, financial stability, and anti-money laundering (AML) concerns.
    **Key Topics:**
    * Comparative regulatory approaches in major economic blocs (e.g., USA, EU, East Asia).
    * The role of central banks and the parallel development of CBDCs.
    * Taxation policies for cryptocurrency capital gains and transactions.
    * KYC/AML compliance challenges for centralized and decentralized exchanges.
    * The legal distinction between crypto assets as securities, commodities, or other financial instruments.

    ---

    Now, apply this exact process to the following:

    `[User Query]`: {user_search_query}
    """
        
        # Format the prompt with the user's query
        enhancement_prompt = prompt_for_enhance_search_query.format(user_search_query=user_query)
        
        try:
            response = self.model.generate_content(enhancement_prompt)
            response_text = response.text.strip()
            
            # Extract the Enhanced Query from the response
            enhanced_query = self._extract_enhanced_query(response_text)
            
            print(f"🔍 Query enhanced: '{user_query}' → '{enhanced_query}'")
            return enhanced_query
            
        except Exception as e:
            print(f"❌ Error enhancing query: {str(e)}")
            return user_query

    def _extract_enhanced_query(self, response_text: str) -> str:
        """
        Extract the Enhanced Query from the LLM response
        
        Args:
            response_text: Raw response from the LLM
            
        Returns:
            str: Extracted enhanced query
        """
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for the Enhanced Query line
            if line.startswith('**Enhanced Query:**'):
                # Extract everything after the marker
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
        
        # Fallback: if we can't find the specific format, 
        # look for the first substantial sentence
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
        
    def generate_initial_plan(self, enhanced_query: str, key_topics: List[str] = None) -> Dict[str, Any]:
        """
        Generate initial search plan using the specialized prompt
        
        Args:
            enhanced_query: The enhanced search query
            key_topics: Optional list of key topics (if not provided, will be extracted)
            
        Returns:
            Dict: Initial search plan components
        """
        prompt_for_generate_initial_plan = """
    **System Message:** You are an expert Research Planner AI. Your core responsibility is to translate a highly specific and enhanced research query into a foundational, actionable, and logical initial research plan. This plan will serve as the starting point for a comprehensive research project.

    ---

    **User Message:**

    Your task is to develop a comprehensive initial research plan based on the provided **Enhanced Query** and its **Key Topics**. This plan should outline the strategic steps needed to investigate and address all components of the query thoroughly.

    **Follow these steps:**

    1.  **Understand the Scope:** Analyze the `Enhanced Query` and its `Key Topics` to fully grasp the research objectives and boundaries.
    2.  **Categorize Information Needs:** For each `Key Topic`, identify the type of information required (e.g., factual data, historical context, qualitative insights, quantitative analysis, case studies, theoretical frameworks).
    3.  **Propose Initial Research Avenues:** Suggest primary methods and general categories of sources for each `Key Topic` (e.g., academic databases, industry reports, governmental data, news archives, expert interviews, surveys). Do not list specific URLs or proprietary databases.
    4.  **Outline Sequential Phases:** Structure the plan into logical, progressive phases, from broad understanding to detailed investigation. Each phase should build upon the previous one.
    5.  **Suggest Initial Keywords/Concepts:** Provide a list of broad, foundational keywords and concepts relevant to the `Enhanced Query` for initial search queries. Do not generate specific search strings with operators yet.
    6.  **Identify Potential Ambiguities (Pre-Analysis):** Based on the initial plan, briefly note any areas or `Key Topics` that might inherently contain ambiguities or require further clarification before deeper research can commence. Frame these as potential "decision points."

    **Crucial Constraints:**

    * **Actionable and Logical:** Every step must be a clear, logical action that can be taken in a research process.
    * **Comprehensive:** The plan must aim to address all aspects implied by the `Enhanced Query` and `Key Topics`.
    * **Initial Focus:** This is an *initial* plan; it should not be overly detailed or prescriptive about specific findings, but rather about the *process*.
    * **No Research Execution:** Do not actually perform research or provide answers to the query.
    * **No Specific Data Points/URLs:** Avoid mentioning specific journal articles, websites, or precise data values. Focus on categories of sources.
    * **Strict Formatting:** Your output must strictly follow the format shown in the example below.

    ---

    **Example Output Format:**

    **Initial Research Plan for: [Enhanced Query from Input]**

    ### 1. Phase 1: Foundational Understanding & Overview
        * **Objective:** To establish a broad understanding of the core subject and its historical context.
        * **Key Activities:**
            * Initial literature review using general keywords: "broad concept 1", "related field 2".
            * Explore encyclopedic sources and reputable overview articles to define key terms and concepts.
        * **Relevant Key Topics:**
            * [Key Topic 1 from input]
            * [Key Topic 2 from input]

    ### 2. Phase 2: Deep Dive into Core Components
        * **Objective:** To gather detailed information on the primary pillars identified in the Enhanced Query.
        * **Key Activities:**
            * Focused searches on academic databases for "specific aspect A" and "methodology B".
            * Investigation of industry reports or governmental publications related to "sector C".
            * Identify major organizations, theories, or models associated with these components.
        * **Relevant Key Topics:**
            * [Key Topic 3 from input]
            * [Key Topic 4 from input]

    ### 3. Phase 3: Analysis of Impacts & Challenges
        * **Objective:** To understand the implications, effects, and potential obstacles related to the research subject.
        * **Key Activities:**
            * Review of case studies illustrating "impact type X" or "challenge type Y".
            * Exploration of policy documents or regulatory frameworks.
            * Consideration of socio-economic or environmental effects.
        * **Relevant Key Topics:**
            * [Key Topic 5 from input]
            * [Key Topic 6 from input]

    ### 4. Initial Keywords for Broad Searches:
        * "global supply chain resilience"
        * "AI applications in healthcare diagnostics"
        * "marine microplastic remediation"
        * "cryptocurrency regulatory frameworks"
        * "sustainable energy policy development"

    ### 5. Potential Decision Points/Ambiguities for Clarification:
        * Clarifying the precise scope of "ethical implications" within medical AI (e.g., focus on data privacy vs. job displacement).
        * Distinguishing between short-term and long-term "impacts" of supply chain disruptions.
        * Specific geographical focus for "microplastic distribution" (e.g., coastal waters vs. deep ocean).

    ---

    Now, apply this exact process to the following:

    **Enhanced Query:** {enhanced_query}
    **Key Topics:** {key_topics}
    """
        
        # Format key topics for the prompt
        if key_topics:
            key_topics_text = "\n".join(f"* {topic}" for topic in key_topics)
        else:
            key_topics_text = "* [Key topics to be derived from the enhanced query]"
        
        # Format the prompt with the enhanced query and key topics
        planning_prompt = prompt_for_generate_initial_plan.format(
            enhanced_query=enhanced_query,
            key_topics=key_topics_text
        )
        
        try:
            response = self.model.generate_content(planning_prompt)
            response_text = response.text.strip()
            
            # Parse the structured response into plan components
            plan_data = self._parse_initial_plan_response(response_text, enhanced_query)
            
            print(f"📋 Initial plan generated with {len(plan_data.get('search_steps', []))} phases")
            return plan_data
            
        except Exception as e:
            print(f"❌ Error generating initial plan: {str(e)}")
            return {"search_steps": [], "key_areas": [], "information_sources": [], 
                "search_strategies": [], "success_metrics": []}

    def _parse_initial_plan_response(self, response_text: str, enhanced_query: str) -> Dict[str, Any]:
        """
        Parse the structured initial plan response into the expected format
        
        Args:
            response_text: Raw response from the LLM
            enhanced_query: The enhanced query for context
            
        Returns:
            Dict: Parsed plan data in expected format
        """
        plan_data = {
            "search_steps": [],
            "key_areas": [],
            "information_sources": [],
            "search_strategies": [],
            "success_metrics": []
        }
        
        lines = response_text.split('\n')
        current_section = None
        current_phase = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect phases (e.g., "### 1. Phase 1:")
            if line.startswith('###') and 'Phase' in line:
                current_section = 'phases'
                # Extract phase information as a search step
                phase_title = line.replace('###', '').strip()
                if phase_title:
                    plan_data['search_steps'].append(phase_title)
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
                # Extract objectives, activities, and key topics from phases
                if '**Objective:**' in line:
                    objective = line.replace('**Objective:**', '').strip()
                    if objective:
                        plan_data['key_areas'].append(objective)
                
                elif line.startswith('*') and any(keyword in line.lower() for keyword in 
                    ['literature', 'database', 'report', 'interview', 'survey', 'search']):
                    # Extract information sources and strategies
                    activity = line.lstrip('* ').strip()
                    if 'database' in activity.lower() or 'report' in activity.lower():
                        plan_data['information_sources'].append(activity)
                    else:
                        plan_data['search_strategies'].append(activity)
            
            elif current_section == 'keywords':
                # Extract keywords
                if line.startswith('*') or line.startswith('-'):
                    keyword = line.lstrip('*- ').strip().strip('"\'')
                    if keyword and len(keyword) > 3:
                        plan_data['search_strategies'].append(f"Search for: {keyword}")
            
            elif current_section == 'decision_points':
                # Extract decision points as success metrics
                if line.startswith('*') or line.startswith('-'):
                    decision_point = line.lstrip('*- ').strip()
                    if decision_point:
                        plan_data['success_metrics'].append(f"Clarify: {decision_point}")
        
        # Ensure we have at least some content
        if not plan_data['search_steps']:
            # Fallback: create basic phases
            plan_data['search_steps'] = [
                "Phase 1: Foundational Understanding & Overview",
                "Phase 2: Deep Dive into Core Components", 
                "Phase 3: Analysis of Impacts & Challenges"
            ]
        
        if not plan_data['key_areas']:
            plan_data['key_areas'] = [
                "Establish broad understanding of the research topic",
                "Gather detailed information on core components",
                "Analyze implications and challenges"
            ]
        
        if not plan_data['information_sources']:
            plan_data['information_sources'] = [
                "Academic databases and peer-reviewed journals",
                "Industry reports and governmental publications",
                "Expert interviews and case studies"
            ]
        
        if not plan_data['search_strategies']:
            plan_data['search_strategies'] = [
                "Systematic literature review approach",
                "Progressive refinement from broad to specific",
                "Multi-source validation and cross-referencing"
            ]
        
        if not plan_data['success_metrics']:
            plan_data['success_metrics'] = [
                "Comprehensive coverage of all key topics",
                "Quality and credibility of sources identified",
                "Clear identification of research gaps and ambiguities"
            ]
        
        return plan_data
    
    def ambiguity_finder(self, enhanced_query: str, plan_data: Dict[str, Any], max_questions: int = 3) -> Dict[str, Any]:
        """
        Analyze the plan for ambiguities and generate questions to resolve them
        
        Args:
            enhanced_query: The enhanced search query
            plan_data: The search plan data
            max_questions: Maximum number of clarifying questions to generate (default: 3)
            
        Returns:
            Dict: Evaluation results with identified ambiguities and clarifying questions
        """
        prompt_evaluate_plan_quality = """
    **System Message:** You are an expert Research Plan Evaluator AI. Your primary function is to conduct a rigorous, objective assessment of a provided research plan. Your evaluation must highlight the plan's strengths, identify any weaknesses, and provide actionable recommendations for improvement, specifically focusing on its completeness, logical flow, feasibility, and clarity. Additionally, you must generate specific clarifying questions to resolve identified ambiguities.

    ---

    **User Message:**

    Your task is to thoroughly evaluate the given `Research Plan` and generate clarifying questions to resolve any ambiguities or gaps identified. Provide a structured assessment that pinpoints areas of excellence and areas requiring refinement, along with specific questions that would help clarify these issues.

    **Input:**

    The input will be a structured `Research Plan` (which is the output from the `generate_initial_plan` function, representing an enhanced plan).

    Research Plan Data:
    {{
    "enhanced_query": "{enhanced_query}",
    "initial_plan": {{
        "search_steps": {search_steps},
        "key_areas": {key_areas},
        "information_sources": {information_sources},
        "search_strategies": {search_strategies},
        "success_metrics": {success_metrics}
    }}
    }}

    **Follow these steps for evaluation:**

    1.  **Completeness:** Assess if all aspects of the `enhanced_query` and its `key_topics` appear to be adequately covered by the plan's phases and activities. Are there any obvious missing components or gaps in scope?
    2.  **Logical Flow and Cohesion:** Evaluate the sequence of phases and activities. Is the progression logical? Do later phases appropriately build upon earlier ones? Is the plan coherent and easy to follow?
    3.  **Feasibility/Realism:** Comment on whether the proposed activities and sources seem realistic and achievable within a typical research context. Are there any overly ambitious or vague activities that might be difficult to execute?
    4.  **Clarity and Specificity:** How clear are the objectives, activities, and relevant key topics within each phase? Are there any remaining vague terms or activities that could be more specific?
    5.  **Generate Clarifying Questions:** Create exactly {max_questions} simple, straightforward questions that would help clarify the most important ambiguities. Questions must be:
    - **Simple and clear**: Can be answered with 1-2 words or a short phrase
    - **Non-specialized**: No technical jargon or expert knowledge required
    - **High-impact**: Focus only on the most critical clarifications needed
    - **Easy to answer**: Require minimal user effort and thought
    - **Specific scope**: Ask about timeframes, regions, audience, scale, or focus areas
    
    **Examples of good questions:**
    - "What time period should this research cover?"
    - "Which region or country should be the main focus?"
    - "What is the target audience for this research?"
    - "Should this focus on current trends or future predictions?"
    - "What industry sector is most important?"

    **Crucial Constraints:**

    * **Structured Output:** Your output must be a JSON object with specific keys as shown in the example.
    * **Question Limit:** Generate exactly {max_questions} questions, prioritizing the most important ones.
    * **Simplicity First:** All questions must be answerable by a general user without specialized knowledge.
    * **No Technical Questions:** Avoid asking about methodologies, specific tools, or technical approaches.
    * **No Conversational Filler:** Only the JSON output.

    **Expected Output (JSON):**

    {{
    "overall_assessment": "The research plan is generally well-structured and addresses the core aspects of the enhanced query. Some areas could benefit from further specificity to enhance feasibility and actionable steps.",
    "strengths": [
        "Clear phasing that logically progresses from foundational understanding to deeper dives.",
        "Effective integration of user-provided specificity on key concerns.",
        "Relevant initial keywords are provided for broad searches."
    ],
    "weaknesses_and_recommendations": [
        {{
        "weakness": "Specific weakness identified in the plan",
        "recommendation": "Actionable recommendation to address the weakness",
        "clarifying_questions": [
            "What time period should this cover?",
            "Which region should be the focus?"
        ]
        }}
    ],
    "areas_for_potential_further_clarification": [
        "Areas that need more clarification or definition",
        "Aspects that could be more specific or detailed"
    ],
    "generated_questions": [
        "What time period should this research cover?",
        "Which region or country should be the main focus?",
        "What is the target audience for this research?"
    ]
    }}

    Return only the JSON object, no additional text or markdown formatting.
    """
        
        # Format the prompt with the plan data and max questions
        formatted_prompt = prompt_evaluate_plan_quality.format(
            enhanced_query=enhanced_query,
            max_questions=max_questions,
            search_steps=json.dumps(plan_data.get('search_steps', []), indent=4),
            key_areas=json.dumps(plan_data.get('key_areas', []), indent=4),
            information_sources=json.dumps(plan_data.get('information_sources', []), indent=4),
            search_strategies=json.dumps(plan_data.get('search_strategies', []), indent=4),
            success_metrics=json.dumps(plan_data.get('success_metrics', []), indent=4)
        )
        
        try:
            response = self.model.generate_content(formatted_prompt)
            response_text = response.text.strip()
            
            # Clean response - remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                evaluation_result = json.loads(response_text)
                
                # Validate required keys and provide defaults
                required_keys = ['overall_assessment', 'strengths', 'weaknesses_and_recommendations', 'areas_for_potential_further_clarification', 'generated_questions']
                for key in required_keys:
                    if key not in evaluation_result:
                        if key == 'overall_assessment':
                            evaluation_result[key] = "Plan evaluation completed."
                        else:
                            evaluation_result[key] = []
                
                # Extract decision points/ambiguities for backward compatibility
                decision_points = []
                
                # Extract from weaknesses and recommendations
                for weakness_item in evaluation_result.get('weaknesses_and_recommendations', []):
                    if isinstance(weakness_item, dict):
                        weakness = weakness_item.get('weakness', '')
                        if weakness:
                            decision_points.append(weakness)
                    elif isinstance(weakness_item, str):
                        decision_points.append(weakness_item)
                
                # Extract from areas for clarification
                for clarification in evaluation_result.get('areas_for_potential_further_clarification', []):
                    if isinstance(clarification, str):
                        decision_points.append(clarification)
                
                # Add decision_points to the result for backward compatibility
                evaluation_result['decision_points'] = decision_points
                
                # Extract all clarifying questions into a single list
                all_questions = []
                
                # Get questions from generated_questions
                all_questions.extend(evaluation_result.get('generated_questions', []))
                
                # Get questions from weaknesses_and_recommendations
                for weakness_item in evaluation_result.get('weaknesses_and_recommendations', []):
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
                
                # Limit to max_questions and prioritize generated_questions
                final_questions = evaluation_result.get('generated_questions', [])[:max_questions]
                
                # If we don't have enough from generated_questions, add from other sources
                if len(final_questions) < max_questions:
                    additional_needed = max_questions - len(final_questions)
                    for question in unique_questions:
                        if question not in final_questions:
                            final_questions.append(question)
                            additional_needed -= 1
                            if additional_needed == 0:
                                break
                
                # Ensure we have exactly max_questions (or fewer if that's all we can generate)
                final_questions = final_questions[:max_questions]
                
                evaluation_result['clarifying_questions'] = final_questions
                
                print(f"🤔 Identified {len(decision_points)} decision points and ambiguities")
                print(f"❓ Generated {len(final_questions)} simple clarifying questions")
                return evaluation_result
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing failed in ambiguity finder: {str(e)}")
                print(f"Raw response: {response_text[:200]}...")
                # Fallback parsing
                return self._parse_evaluation_fallback_ambiguity(response_text, max_questions)
                
        except Exception as e:
            print(f"❌ Error in ambiguity finder: {str(e)}")
            return {
                "overall_assessment": "Error occurred during evaluation",
                "strengths": [],
                "weaknesses_and_recommendations": [],
                "areas_for_potential_further_clarification": [],
                "decision_points": [],
                "clarifying_questions": self._get_default_simple_questions(max_questions)
            }

    def _parse_evaluation_fallback_ambiguity(self, response_text: str, max_questions: int) -> Dict[str, Any]:
        """
        Fallback parser for evaluation responses that aren't valid JSON
        
        Args:
            response_text: Raw response text
            max_questions: Maximum number of questions to return
            
        Returns:
            Dict: Parsed evaluation data
        """
        evaluation_result = {
            "overall_assessment": "Plan requires further analysis and refinement",
            "strengths": [],
            "weaknesses_and_recommendations": [],
            "areas_for_potential_further_clarification": [],
            "decision_points": [],
            "generated_questions": [],
            "clarifying_questions": []
        }
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            line_lower = line.lower()
            if 'strength' in line_lower:
                current_section = 'strengths'
            elif 'weakness' in line_lower or 'recommendation' in line_lower:
                current_section = 'weaknesses'
            elif 'clarification' in line_lower or 'ambiguit' in line_lower:
                current_section = 'clarifications'
            elif 'question' in line_lower:
                current_section = 'questions'
            elif 'assessment' in line_lower:
                current_section = 'assessment'
            
            # Extract content
            if current_section and (line.startswith(('-', '•', '*')) or line[0].isdigit() or '?' in line):
                cleaned_line = line.lstrip('-•*0123456789. ').strip()
                if cleaned_line and len(cleaned_line) > 10:
                    if current_section == 'strengths':
                        evaluation_result['strengths'].append(cleaned_line)
                    elif current_section == 'weaknesses':
                        evaluation_result['weaknesses_and_recommendations'].append({
                            "weakness": cleaned_line,
                            "recommendation": "Requires further analysis and refinement",
                            "clarifying_questions": []
                        })
                    elif current_section == 'clarifications':
                        evaluation_result['areas_for_potential_further_clarification'].append(cleaned_line)
                    elif current_section == 'questions':
                        if '?' in cleaned_line and len(evaluation_result['generated_questions']) < max_questions:
                            evaluation_result['generated_questions'].append(cleaned_line)
                    
                    # Add to decision points for backward compatibility
                    if current_section in ['weaknesses', 'clarifications']:
                        evaluation_result['decision_points'].append(cleaned_line)
        
        # Ensure we have some content
        if not evaluation_result['decision_points']:
            evaluation_result['decision_points'] = [
                "Plan scope and objectives need clarification",
                "Research methodology requires more specificity",
                "Success criteria and metrics need definition"
            ]
        
        # Generate simple questions if none found
        if not evaluation_result['generated_questions']:
            evaluation_result['generated_questions'] = self._get_default_simple_questions(max_questions)
        
        # Set clarifying questions to the generated ones (limited)
        evaluation_result['clarifying_questions'] = evaluation_result['generated_questions'][:max_questions]
        
        return evaluation_result

    def _get_default_simple_questions(self, max_questions: int) -> List[str]:
        """
        Get default simple clarifying questions
        
        Args:
            max_questions: Maximum number of questions to return
            
        Returns:
            List[str]: List of default simple questions
        """
        default_questions = [
            "What time period should this research cover?",
            "Which region or country should be the main focus?",
            "What is the target audience for this research?",
            "Should this focus on current trends or future predictions?",
            "What industry sector is most important?",
            "What is the primary goal of this research?",
            "Which aspect should be prioritized?",
            "What level of detail is needed?",
            "Are there any specific constraints to consider?",
            "What type of sources are most valuable?"
        ]
        
        return default_questions[:max_questions]

    def enhance_plan_with_answers(self, plan_data: Dict[str, Any], 
                                qa_pairs: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate enhanced plan based on Q&A pairs
        
        Args:
            plan_data: Original plan data
            qa_pairs: Dictionary of questions and answers
            
        Returns:
            Dict: Enhanced plan data
        """
        # Format Q&A pairs for the prompt
        qa_text = ""
        if qa_pairs:
            qa_text = "\n".join(f"Q: {q}\nA: {a}\n" for q, a in qa_pairs.items())
        else:
            qa_text = "No specific clarifications provided."
        
        enhancement_prompt = f"""
        You are an expert research strategist. Use the provided answers to refine and enhance the original search plan.

        Original Plan:
        {json.dumps(plan_data, indent=2)}

        Clarifying Q&A:
        {qa_text}

        Based on these answers, create an enhanced search plan that:
        1. Incorporates the clarifications and preferences
        2. Resolves ambiguities identified earlier
        3. Adjusts priorities and scope accordingly
        4. Maintains the same JSON structure as the original
        5. Makes the plan more specific and actionable

        IMPORTANT: Return ONLY a valid JSON object with this exact structure:
        {{
            "search_steps": ["step1", "step2", "step3"],
            "key_areas": ["area1", "area2"],
            "information_sources": ["source1", "source2"],
            "search_strategies": ["strategy1", "strategy2"],
            "success_metrics": ["metric1", "metric2"]
        }}

        Return only the JSON, no additional text or markdown formatting.
        """
        
        try:
            response = self.model.generate_content(enhancement_prompt)
            response_text = response.text.strip()
            
            # Clean response - remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                enhanced_plan = json.loads(response_text)
                # Validate structure
                required_keys = ['search_steps', 'key_areas', 'information_sources', 'search_strategies', 'success_metrics']
                for key in required_keys:
                    if key not in enhanced_plan:
                        enhanced_plan[key] = plan_data.get(key, [])
                        
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing failed in enhancement: {str(e)}")
                print(f"Raw response: {response_text[:200]}...")
                enhanced_plan = self._parse_plan_response(response_text)
                # If parsing still fails, return original
                if not enhanced_plan.get('search_steps'):
                    enhanced_plan = plan_data
            
            print(f"🔄 Plan enhanced with {len(qa_pairs)} clarifications")
            return enhanced_plan
            
        except Exception as e:
            print(f"❌ Error enhancing plan: {str(e)}")
            return plan_data
    
    def evaluate_plan_quality(self, plan_data: Dict[str, Any], enhanced_query: str = "") -> float:
        """
        Evaluate the quality of a search plan using metric-based scoring
        
        Args:
            plan_data: Plan data to evaluate
            enhanced_query: The enhanced query for context
            
        Returns:
            float: Quality score (0-100)
        """
        prompt_evaluate_plan_quality_scored = """
    **System Message:** You are an expert Research Plan Scorer and Evaluator AI. Your primary function is to rigorously assess the quality of a given research plan against specific metrics. You will assign a numerical score (1-10) for each metric and provide an overall weighted score, alongside concise, actionable feedback for improvement. Your assessment must be objective and based solely on the provided plan's content.

    ---

    **User Message:**

    Your task is to evaluate the provided `Research Plan` based on a predefined set of quality metrics. Assign a score from **1 (Poor) to 10 (Excellent)** for each metric, calculate an overall weighted score, and provide a brief justification for your scores along with specific, actionable recommendations for improvement.

    **Input:**

    The input will be a structured `Research Plan` (representing an enhanced plan).

    Research Plan Data:
    {{
    "enhanced_query": "{enhanced_query}",
    "initial_plan": {{
        "search_steps": {search_steps},
        "key_areas": {key_areas},
        "information_sources": {information_sources},
        "search_strategies": {search_strategies},
        "success_metrics": {success_metrics}
    }}
    }}

    **Evaluation Metrics and Scoring (1-10 Scale):**

    * **1. Completeness (Weight: 0.25):** How well does the plan cover all facets of the `enhanced_query` and its `key_topics`? Are there significant omissions?
        * 1-3: Major gaps, large parts of query unaddressed.
        * 4-6: Some gaps, requires additional topics/phases.
        * 7-8: Mostly complete, minor aspects could be expanded.
        * 9-10: Highly comprehensive, all key areas addressed.
    * **2. Clarity & Specificity (Weight: 0.20):** How clear, unambiguous, and detailed are the objectives, activities, and relevant topics within each phase? Are the actions concrete?
        * 1-3: Vague, difficult to understand actions, ambiguous terms.
        * 4-6: Some clarity, but many steps remain high-level.
        * 7-8: Generally clear, but a few areas lack explicit detail.
        * 9-10: Exceptionally clear and specific, actionable steps.
    * **3. Logical Flow & Cohesion (Weight: 0.20):** Is the progression of phases and activities logical and sequential? Does the plan build coherently from one step to the next?
        * 1-3: Disorganized, illogical progression, disjointed.
        * 4-6: Some logical steps, but breaks in coherence.
        * 7-8: Mostly logical, minor reordering could improve.
        * 9-10: Seamless, highly logical, well-integrated phases.
    * **4. Feasibility & Realism (Weight: 0.15):** Are the proposed activities and source types realistic and achievable given typical research constraints? Avoid overly ambitious or impractical steps.
        * 1-3: Highly unrealistic or impractical activities.
        * 4-6: Some impractical elements, might require significant resources.
        * 7-8: Mostly feasible, minor adjustments might be needed.
        * 9-10: Highly realistic and practical, well-scoped.
    * **5. Keyword Relevance & Breadth (Weight: 0.20):** How relevant and comprehensive are the initial keywords/strategies provided for broad searches? Do they cover the necessary breadth for initial exploration?
        * 1-3: Very limited or irrelevant keywords/strategies.
        * 4-6: Some relevant terms, but missing key areas.
        * 7-8: Good selection, minor additions could enhance.
        * 9-10: Excellent, broad, and highly relevant set.

    **Follow these steps for evaluation:**

    1.  **Metric-by-Metric Assessment:** For each of the five metrics above, carefully read the plan and assign a score from 1-10 based on the provided descriptions.
    2.  **Calculate Overall Score:** Compute the weighted average of the individual metric scores.
        * `Overall Score = (Completeness * 0.25) + (Clarity & Specificity * 0.20) + (Logical Flow & Cohesion * 0.20) + (Feasibility & Realism * 0.15) + (Keyword Relevance & Breadth * 0.20)`
    3.  **Justify Scores:** Provide a concise, 1-2 sentence justification for the scores, highlighting the plan's overall strengths and main areas for improvement.
    4.  **Formulate Actionable Feedback:** Based on metrics with lower scores or any identified weaknesses, provide concrete, numbered recommendations for how to directly improve the plan's content, structure, or detail.

    **Crucial Constraints:**

    * **Strict JSON Output:** The entire response must be a valid JSON object matching the `Example Output Format`. No conversational text, explanations, or preambles outside the JSON.
    * **Numerical Scores:** All scores must be integers or floats as specified.
    * **Objectivity:** Base assessment solely on the plan's content, not external knowledge.
    * **Actionable Feedback:** Ensure recommendations are specific and tell the user *how* to improve, not just *what* is wrong.
    * **No Plan Modification:** Do not modify the plan itself.

    **Example Output Format (JSON):**

    {{
    "overall_score": 7.9,
    "metric_scores": {{
        "completeness": 8,
        "clarity_specificity": 7,
        "logical_flow_cohesion": 9,
        "feasibility_realism": 8,
        "keyword_relevance_breadth": 7
    }},
    "evaluation_summary": "The research plan demonstrates strong logical flow and good overall completeness, especially in addressing the ethical components. However, some activities lack granular detail, and the initial keywords could be more comprehensive to kickstart diverse searches.",
    "actionable_feedback": [
        "Increase specificity in Phase 1's activities by suggesting types of academic review articles or influential reports instead of just general sources.",
        "For socio-economic effects analysis, explicitly list 2-3 specific sub-areas to guide more focused research.",
        "Expand the search strategies with more long-tail and diverse terms that capture specific nuances of the research topic."
    ]
    }}

    Return only the JSON object, no additional text or markdown formatting.
    """
        
        # Format the prompt with the plan data
        formatted_prompt = prompt_evaluate_plan_quality_scored.format(
            enhanced_query=enhanced_query,
            search_steps=json.dumps(plan_data.get('search_steps', []), indent=4),
            key_areas=json.dumps(plan_data.get('key_areas', []), indent=4),
            information_sources=json.dumps(plan_data.get('information_sources', []), indent=4),
            search_strategies=json.dumps(plan_data.get('search_strategies', []), indent=4),
            success_metrics=json.dumps(plan_data.get('success_metrics', []), indent=4)
        )
        
        try:
            response = self.model.generate_content(formatted_prompt)
            response_text = response.text.strip()
            
            # Clean response - remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
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
                import re
                scores = re.findall(r'\d+\.?\d*', response_text)
                if scores:
                    overall_score = float(scores[-1])
                    # Normalize to 0-100 range
                    if overall_score <= 10:
                        overall_score *= 10
                    elif overall_score > 100:
                        overall_score = min(overall_score, 100)
                else:
                    overall_score = 50.0  # Default middle score
                
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
        return getattr(self, '_last_evaluation_details', {})

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

    def refine_plan(self, plan_data: Dict[str, Any], evaluation_details: Dict[str, Any], 
                    enhanced_query: str = "") -> Dict[str, Any]:
        """
        Refine the plan based on evaluation feedback and quality assessment
        
        Args:
            plan_data: Current plan data
            evaluation_details: Detailed evaluation results with feedback
            enhanced_query: The enhanced query for context
            
        Returns:
            Dict: Refined plan data
        """
        prompt_refine_plan = """
    **System Message:** You are a dedicated Research Plan Refinement Specialist AI. Your core mission is to meticulously enhance and optimize a given research plan by directly implementing actionable feedback from a quality evaluation. Your goal is to produce a more robust, detailed, and effective research plan without altering its fundamental scope.

    ---

    **User Message:**

    Your task is to refine the provided `Research Plan` by strictly incorporating the `Actionable Feedback` and `Areas for Potential Further Clarification` from the `Plan Evaluation`. You must modify the plan's components to reflect these improvements while maintaining the original structure and scope.

    **Input:**

    The input will consist of two JSON objects:
    1.  **`current_research_plan` (JSON Object):** The research plan that needs refinement.
    2.  **`plan_evaluation` (JSON Object):** The evaluation results containing `actionable_feedback` and other improvement areas.

    Current Research Plan:
    {{
    "enhanced_query": "{enhanced_query}",
    "plan_components": {{
        "search_steps": {search_steps},
        "key_areas": {key_areas},
        "information_sources": {information_sources},
        "search_strategies": {search_strategies},
        "success_metrics": {success_metrics}
    }}
    }}

    Plan Evaluation:
    {plan_evaluation}

    **Follow these steps for refinement:**

    1.  **Iterate through Feedback:** Go through each item in `plan_evaluation.actionable_feedback` and directly apply the suggested changes to the `current_research_plan`.
        * **Specificity:** If feedback requests more specificity, add detailed examples, types of sources, or sub-areas to relevant activities or objectives.
        * **Expansion:** If feedback requests expansion (e.g., keywords, sub-topics), add those directly to the respective lists.
        * **Structure/Flow:** If feedback suggests structural changes, integrate them logically.
    2.  **Address Clarification Areas:** Review any clarification areas and make reasonable improvements based on the existing plan's content without adding external knowledge.
    3.  **Enhance Quality:** Focus on improving the specific metrics that scored lower in the evaluation.
    4.  **Maintain Structure:** The final output must maintain the same JSON structure as the input plan.

    **Crucial Constraints:**

    * **Strict Adherence to Feedback:** Only make modifications explicitly guided by the `actionable_feedback` and evaluation results.
    * **No Scope Creep:** Do not add new overarching topics or drastically change the query's intent. Refinement means making the *existing* plan better.
    * **Strict JSON Output:** Return only a valid JSON object representing the refined plan structure.
    * **No External Knowledge:** Do not inject external knowledge not present in the input plan or evaluation.

    **Expected Output Format (JSON):**

    {{
    "search_steps": [
        "Refined and more specific search steps",
        "Enhanced activities with clearer objectives"
    ],
    "key_areas": [
        "More detailed key areas with specific focus",
        "Enhanced areas addressing evaluation feedback"
    ],
    "information_sources": [
        "More specific and diverse information sources",
        "Enhanced source types based on feedback"
    ],
    "search_strategies": [
        "Refined search strategies with specific keywords",
        "Enhanced approaches addressing clarity concerns"
    ],
    "success_metrics": [
        "More measurable and specific success criteria",
        "Enhanced metrics addressing evaluation feedback"
    ]
    }}

    Return only the JSON object, no additional text or markdown formatting.
    """
        
        # Format the prompt with the plan data and evaluation
        formatted_prompt = prompt_refine_plan.format(
            enhanced_query=enhanced_query,
            search_steps=json.dumps(plan_data.get('search_steps', []), indent=4),
            key_areas=json.dumps(plan_data.get('key_areas', []), indent=4),
            information_sources=json.dumps(plan_data.get('information_sources', []), indent=4),
            search_strategies=json.dumps(plan_data.get('search_strategies', []), indent=4),
            success_metrics=json.dumps(plan_data.get('success_metrics', []), indent=4),
            plan_evaluation=json.dumps(evaluation_details, indent=4)
        )
        
        try:
            response = self.model.generate_content(formatted_prompt)
            response_text = response.text.strip()
            
            # Clean response - remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                refined_plan = json.loads(response_text)
                
                # Validate structure and provide defaults
                required_keys = ['search_steps', 'key_areas', 'information_sources', 'search_strategies', 'success_metrics']
                for key in required_keys:
                    if key not in refined_plan:
                        refined_plan[key] = plan_data.get(key, [])
                    # Ensure we have some content
                    elif not refined_plan[key]:
                        refined_plan[key] = plan_data.get(key, [])
                
                # Log improvements made
                self._log_refinement_improvements(plan_data, refined_plan, evaluation_details)
                
                print(f"🔧 Plan refined based on evaluation feedback")
                return refined_plan
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing failed in refinement: {str(e)}")
                print(f"Raw response: {response_text[:200]}...")
                # Attempt fallback parsing
                refined_plan = self._parse_refinement_fallback(response_text, plan_data)
                if refined_plan:
                    print(f"🔧 Plan refined using fallback parsing")
                    return refined_plan
                else:
                    print(f"⚠️  Returning original plan due to parsing failure")
                    return plan_data
                
        except Exception as e:
            print(f"❌ Error refining plan: {str(e)}")
            return plan_data

    def _log_refinement_improvements(self, original_plan: Dict[str, Any], 
                                refined_plan: Dict[str, Any], 
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
        for key in ['search_steps', 'key_areas', 'information_sources', 'search_strategies', 'success_metrics']:
            original_count = len(original_plan.get(key, []))
            refined_count = len(refined_plan.get(key, []))
            if refined_count > original_count:
                improvements[key] = refined_count - original_count
            
            # Check for enhanced content (longer descriptions)
            original_content = ' '.join(original_plan.get(key, []))
            refined_content = ' '.join(refined_plan.get(key, []))
            if len(refined_content) > len(original_content) * 1.1:  # 10% more content
                improvements[f"{key}_enhanced"] = True
        
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

    def _parse_refinement_fallback(self, response_text: str, original_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback parser for refinement responses that aren't valid JSON
        
        Args:
            response_text: Raw response text
            original_plan: Original plan to fall back to
            
        Returns:
            Dict: Parsed refinement data or None if parsing fails
        """
        try:
            refined_plan = {
                "search_steps": original_plan.get('search_steps', []).copy(),
                "key_areas": original_plan.get('key_areas', []).copy(),
                "information_sources": original_plan.get('information_sources', []).copy(),
                "search_strategies": original_plan.get('search_strategies', []).copy(),
                "success_metrics": original_plan.get('success_metrics', []).copy()
            }
            
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect sections
                line_lower = line.lower()
                if 'search_steps' in line_lower or 'steps' in line_lower:
                    current_section = 'search_steps'
                    continue
                elif 'key_areas' in line_lower or 'areas' in line_lower:
                    current_section = 'key_areas'
                    continue
                elif 'information_sources' in line_lower or 'sources' in line_lower:
                    current_section = 'information_sources'
                    continue
                elif 'search_strategies' in line_lower or 'strategies' in line_lower:
                    current_section = 'search_strategies'
                    continue
                elif 'success_metrics' in line_lower or 'metrics' in line_lower:
                    current_section = 'success_metrics'
                    continue
                
                # Extract enhanced content
                if current_section and (line.startswith(('-', '•', '*')) or line[0].isdigit()):
                    cleaned_line = line.lstrip('-•*0123456789. ').strip().strip('"\'')
                    if cleaned_line and len(cleaned_line) > 10:
                        # Replace or append based on content
                        if cleaned_line not in refined_plan[current_section]:
                            # If it's an enhancement of existing content, replace
                            for i, existing in enumerate(refined_plan[current_section]):
                                if any(word in cleaned_line.lower() for word in existing.lower().split()[:3]):
                                    refined_plan[current_section][i] = cleaned_line
                                    break
                            else:
                                # If completely new, append
                                refined_plan[current_section].append(cleaned_line)
            
            # Ensure we have improvements
            has_improvements = False
            for key in refined_plan:
                if len(refined_plan[key]) > len(original_plan.get(key, [])):
                    has_improvements = True
                    break
                # Check for content enhancement
                original_content = ' '.join(original_plan.get(key, []))
                refined_content = ' '.join(refined_plan[key])
                if len(refined_content) > len(original_content) * 1.1:
                    has_improvements = True
                    break
            
            return refined_plan if has_improvements else None
            
        except Exception as e:
            print(f"⚠️  Fallback parsing failed: {str(e)}")
            return None

    def apply_manual_refinements(self, plan_data: Dict[str, Any], 
                            manual_feedback: List[str]) -> Dict[str, Any]:
        """
        Apply manual refinements to a plan based on user-provided feedback
        
        Args:
            plan_data: Current plan data
            manual_feedback: List of manual feedback items
            
        Returns:
            Dict: Refined plan data
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

def main():
    """
    Main function that executes the complete deep search planning workflow
    with user interaction for questions and answers
    """
    print("🤖 Deep Search Planner Agent - Interactive Mode")
    print("=" * 60)
    print("This agent creates sophisticated search plans through iterative refinement.")
    print("You'll be asked to provide clarifications to improve the plan quality.")
    print("=" * 60)
    
    # Initialize the agent
    try:
        planner = DeepSearchPlannerAgent()
        print(f"✅ API key loaded from environment")
    except ValueError as e:
        print(f"❌ {str(e)}")
        print("Make sure you have a .env file with GOOGLE_API_KEY=your-actual-api-key")
        return
    
    # Load the model
    if not planner.load_gemini_model():
        print("❌ Failed to load model. Please check your API key.")
        return
    
    print("\n🚀 Starting interactive deep search planning...")
    
    # Step 1: Get user query
    print("\n" + "="*60)
    print("STEP 1: SEARCH QUERY INPUT")
    print("="*60)
    user_query = input("\n📝 Please enter your search query: ").strip()
    
    if not user_query:
        print("❌ No query provided. Exiting...")
        return
    
    print(f"\n✅ Query received: '{user_query}'")
    
    # Step 2: Enhance query
    print("\n" + "="*60)
    print("STEP 2: QUERY ENHANCEMENT")
    print("="*60)
    enhanced_query = planner.enhance_search_query(user_query)
    
    # Step 3: Generate initial plan
    print("\n" + "="*60)
    print("STEP 3: INITIAL PLAN GENERATION")
    print("="*60)
    initial_plan_data = planner.generate_initial_plan(enhanced_query)
    
    # Step 4: Find ambiguities and generate questions
    print("\n" + "="*60)
    print("STEP 4: AMBIGUITY ANALYSIS & QUESTION GENERATION")
    print("="*60)
    
    # Get number of questions from user
    try:
        max_questions = int(input("   How many clarifying questions would you like? (default: 3): ") or "3")
        max_questions = max(1, min(max_questions, 10))  # Limit between 1 and 10
    except ValueError:
        max_questions = 3
        print("   ⚠️  Invalid input, using default: 3 questions")
    
    evaluation_result = planner.ambiguity_finder(enhanced_query, initial_plan_data, max_questions)
    
    # Step 5: Interactive Q&A with user
    print("\n" + "="*60)
    print("STEP 5: INTERACTIVE CLARIFICATION")
    print("="*60)
    
    questions = evaluation_result.get('clarifying_questions', [])
    qa_pairs = {}
    
    if questions:
        print(f"\n💡 I've generated {len(questions)} questions to improve your search plan.")
        print("Please provide answers to help refine the plan (press Enter to skip any question):\n")
        
        for i, question in enumerate(questions, 1):
            print(f"❓ Question {i}/{len(questions)}:")
            print(f"   {question}")
            answer = input(f"   Your answer: ").strip()
            
            if answer:
                qa_pairs[question] = answer
                print(f"   ✅ Answer recorded\n")
            else:
                print(f"   ⏭️  Skipped\n")
        
        print(f"📋 Collected {len(qa_pairs)} answers out of {len(questions)} questions.")
    else:
        print("ℹ️  No clarifying questions generated. Proceeding with initial plan.")
    
    # Step 6: Enhance plan with answers (if any provided)
    print("\n" + "="*60)
    print("STEP 6: PLAN ENHANCEMENT WITH USER INPUT")
    print("="*60)
    
    if qa_pairs:
        current_plan_data = planner.enhance_plan_with_answers(initial_plan_data, qa_pairs)
        print(f"🔄 Plan enhanced with {len(qa_pairs)} user clarifications")
    else:
        current_plan_data = initial_plan_data
        print("ℹ️  Using initial plan (no user clarifications provided)")
    
    # Step 7: Iterative refinement
    print("\n" + "="*60)
    print("STEP 7: ITERATIVE PLAN REFINEMENT")
    print("="*60)
    
    # Get refinement parameters from user
    print("\n🔧 Refinement Settings:")
    
    try:
        max_iterations = int(input("   How many refinement iterations? (default: 3): ") or "3")
        top_n = int(input("   How many top plans to return? (default: 2): ") or "2")
    except ValueError:
        max_iterations = 3
        top_n = 2
        print("   ⚠️  Invalid input, using defaults: 3 iterations, top 2 plans")
    
    print(f"\n🎯 Running {max_iterations} iterations, will return top {top_n} plans")
    
    all_plans = []
    
    for iteration in range(max_iterations):
        print(f"\n--- ITERATION {iteration + 1}/{max_iterations} ---")
        
        # Evaluate current plan
        quality_score = planner.evaluate_plan_quality(current_plan_data, enhanced_query)
        evaluation_details = planner.get_last_evaluation_details()
        
        # Create SearchPlan object
        search_plan = SearchPlan(
            query=user_query,
            enhanced_query=enhanced_query,
            plan_steps=current_plan_data.get('search_steps', []),
            decision_points=evaluation_result.get('decision_points', []),
            clarifying_questions=questions if iteration == 0 else [],
            quality_score=quality_score,
            iteration=iteration + 1,
            timestamp=time.time()
        )
        
        all_plans.append(search_plan)
        
        # Show detailed evaluation for current iteration
        if evaluation_details:
            planner.display_evaluation_details(evaluation_details)
        
        # Refine plan for next iteration (except last)
        if iteration < max_iterations - 1:
            current_plan_data = planner.refine_plan(current_plan_data, evaluation_details, enhanced_query)
    
    # Step 8: Present final results
    print("\n" + "="*60)
    print("STEP 8: FINAL RESULTS")
    print("="*60)
    
    # Sort by quality score and return top N
    all_plans.sort(key=lambda x: x.quality_score, reverse=True)
    top_plans = all_plans[:top_n]
    
    print(f"\n🎉 Planning cycle complete!")
    print(f"📊 Generated {len(all_plans)} plan iterations")
    print(f"🏆 Presenting top {len(top_plans)} plans (ranked by quality score):\n")
    
    for i, plan in enumerate(top_plans, 1):
        print(f"📈 RANK #{i}: Iteration {plan.iteration} - Score: {plan.quality_score:.1f}/100")
    

def demo_search_planner():
    """Demo function for automated testing with predefined inputs"""
    print("🤖 Deep Search Planner Agent - Demo Mode")
    print("=" * 40)
    print("Running automated demo with predefined inputs...")
    
    # Initialize the agent (API key will be loaded from .env file)
    try:
        planner = DeepSearchPlannerAgent()
        print(f"✅ API key loaded from environment")
    except ValueError as e:
        print(f"❌ {str(e)}")
        print("Make sure you have a .env file with GOOGLE_API_KEY=your-actual-api-key")
        return
    
    # Load the model
    if not planner.load_gemini_model():
        print("Failed to load model. Please check your API key.")
        return
    
    # Example search query
    user_query = "impact of artificial intelligence on future job markets"
    
    # Example Q&A pairs (normally these would come from user interaction)
    qa_pairs = {
        "What time horizon should we focus on?": "Next 10-15 years",
        "Which job sectors are most important?": "Technology, healthcare, manufacturing, and education",
        "Should we include global or regional perspective?": "Focus on developed economies first, then global trends"
    }
    
    # Execute planning cycle
    top_plans = planner.execute_planning_cycle(
        user_query=user_query,
        qa_pairs=qa_pairs,
        max_iterations=3,
        top_n=2
    )
    
    # Display results
    for i, plan in enumerate(top_plans, 1):
        print(f"\n🏆 TOP PLAN #{i}")
        planner.display_plan(plan)

if __name__ == "__main__":
    print("🤖 Deep Search Planner Agent")
    print("=" * 40)
    print("Choose execution mode:")
    print("1. Interactive Mode (full user interaction)")
    print("2. Demo Mode (automated with predefined inputs)")
    
    try:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == "1":
            main()
        elif choice == "2":
            demo_search_planner()
        else:
            print("Invalid choice. Running interactive mode by default...")
            main()
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Deep Search Planner Agent!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your setup and try again.")