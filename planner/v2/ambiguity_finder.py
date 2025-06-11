from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import json
from langchain_core.language_models.base import BaseLanguageModel


@dataclass
class AmbiguityCategory:
    """Represents a category of potential ambiguity in the research query."""
    category_name: str
    description: str
    identified_issues: List[str] = field(default_factory=list)
    clarifying_questions: List[str] = field(default_factory=list)


@dataclass
class QueryAmbiguityAnalysis:
    """Complete analysis of ambiguities in a research query."""
    original_query: str
    analysis_timestamp: str
    total_ambiguities_found: int
    ambiguity_categories: List[AmbiguityCategory] = field(default_factory=list)
    clarifying_questions: List[str] = field(default_factory=list)
    priority_questions: List[str] = field(default_factory=list)
    execution_recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary format."""
        return {
            "original_query": self.original_query,
            "analysis_timestamp": self.analysis_timestamp,
            "total_ambiguities_found": self.total_ambiguities_found,
            "ambiguity_categories": [
                {
                    "category_name": cat.category_name,
                    "description": cat.description,
                    "identified_issues": cat.identified_issues,
                    "clarifying_questions": cat.clarifying_questions
                }
                for cat in self.ambiguity_categories
            ],
            "all_clarifying_questions": self.clarifying_questions,
            "priority_questions": self.priority_questions,
            "execution_recommendations": self.execution_recommendations
        }


def generate_ambiguity_resolution_prompt(user_search_query: str) -> str:
    """
    Generate the complete prompt for ambiguity analysis.
    
    Args:
        user_search_query: The enhanced search query to analyze
        
    Returns:
        Complete formatted prompt for the LLM
    """
    
    prompt = f"""You are a sophisticated AI assistant tasked with refining user search queries to ensure comprehensive and precise results. Your goal is to anticipate and resolve ambiguities in a user's detailed search plan before execution.

Analyze the following user search query:
"{user_search_query}"

**Your Task:**

1. **Identify Potential Ambiguities and Execution Challenges:**
   * **Scope and Delimiters:** Are there any terms that are too broad or lack clear boundaries? (e.g., "global economy" - does this include developing nations, emerging markets, or specific economic blocs? What is the time period of interest?).
   * **Implicit Assumptions:** What underlying assumptions might the user be making that could affect the search? (e.g., assuming a universally accepted definition of "energy security").
   * **Comparative Analysis Nuances:** What factors could make a "comparative analysis" difficult or misleading without further clarification? (e.g., varying lifecycles of power plants, unpriced externalities like pollution).
   * **Data Availability and Bias:** Consider the potential for data to be unavailable, outdated, or biased for certain regions or energy sources. How might this impact the quality of the analysis? (e.g., lack of reliable data on biomass in certain countries).
   * **Vague Terminology:** Pinpoint any words or phrases that could be interpreted in multiple ways (e.g., "significant impact," "long-term effects").

2. **Generate Clarifying Questions:**
Based on your analysis, create a list of simple, concise, and impactful questions to ask the user. These questions should be designed to resolve the identified ambiguities and refine the search query. The questions should be:
   * **Short and to the point.**
   * **Easy for a non-expert to understand and answer.**
   * **Focused on eliciting specific choices or parameters.**

**Response Format:**
Please respond with a JSON structure containing your analysis:

{{
    "ambiguity_analysis": {{
        "scope_and_delimiters": {{
            "identified_issues": ["issue 1", "issue 2"],
            "clarifying_questions": ["question 1", "question 2"]
        }},
        "implicit_assumptions": {{
            "identified_issues": ["assumption 1", "assumption 2"],
            "clarifying_questions": ["question 1", "question 2"]
        }},
        "comparative_analysis_nuances": {{
            "identified_issues": ["nuance 1", "nuance 2"],
            "clarifying_questions": ["question 1", "question 2"]
        }},
        "data_availability_and_bias": {{
            "identified_issues": ["data issue 1", "data issue 2"],
            "clarifying_questions": ["question 1", "question 2"]
        }},
        "vague_terminology": {{
            "identified_issues": ["vague term 1", "vague term 2"],
            "clarifying_questions": ["question 1", "question 2"]
        }}
    }},
    "priority_clarifying_questions": [
        "Most important question 1",
        "Most important question 2",
        "Most important question 3"
    ],
    "execution_recommendations": [
        "Recommendation 1 for better research execution",
        "Recommendation 2 for better research execution"
    ]
}}

**Generate your analysis now:**"""
    
    return prompt


def analyze_query_ambiguities(
    enhanced_query: str,
    model: BaseLanguageModel,
    custom_prompt: Optional[str] = None
) -> QueryAmbiguityAnalysis:
    """
    Analyze potential ambiguities in the enhanced search query.
    
    Args:
        enhanced_query: The enhanced research query to analyze
        model: LLM model for analysis
        custom_prompt: Optional custom prompt (uses default if not provided)
        
    Returns:
        Complete ambiguity analysis with clarifying questions
    """
    
    
    if not enhanced_query or not enhanced_query.strip():
        raise ValueError("Enhanced query cannot be empty")
    
    # Generate analysis prompt
    analysis_prompt = custom_prompt if custom_prompt else generate_ambiguity_resolution_prompt(enhanced_query)
    
    try:
        print("Analyzing query for potential ambiguities...")
        
        # Get analysis from model
        response = model.invoke(analysis_prompt)
        response_text = response.content.strip()
        
        # Parse JSON response
        try:
            # Extract JSON from response if it's wrapped in markdown
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.rfind("```")
                response_text = response_text[start:end].strip()
            
            analysis_data = json.loads(response_text)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            # Create fallback analysis
            analysis_data = _create_fallback_analysis(enhanced_query)
        
        # Process the analysis data
        ambiguity_categories = []
        all_clarifying_questions = []
        
        # Process each ambiguity category
        ambiguity_analysis = analysis_data.get("ambiguity_analysis", {})
        
        category_mapping = {
            "scope_and_delimiters": "Scope and Boundary Definitions",
            "implicit_assumptions": "Implicit Assumptions",
            "comparative_analysis_nuances": "Comparative Analysis Challenges", 
            "data_availability_and_bias": "Data Quality and Availability",
            "vague_terminology": "Terminology Clarity"
        }
        
        for category_key, category_name in category_mapping.items():
            if category_key in ambiguity_analysis:
                category_data = ambiguity_analysis[category_key]
                
                category = AmbiguityCategory(
                    category_name=category_name,
                    description=f"Analysis of {category_name.lower()} issues",
                    identified_issues=category_data.get("identified_issues", []),
                    clarifying_questions=category_data.get("clarifying_questions", [])
                )
                
                ambiguity_categories.append(category)
                all_clarifying_questions.extend(category.clarifying_questions)
        
        # Get priority questions and recommendations
        priority_questions = analysis_data.get("priority_clarifying_questions", [])
        execution_recommendations = analysis_data.get("execution_recommendations", [])
        
        # Create analysis object
        from datetime import datetime
        analysis = QueryAmbiguityAnalysis(
            original_query=enhanced_query,
            analysis_timestamp=datetime.now().isoformat(),
            total_ambiguities_found=len(all_clarifying_questions),
            ambiguity_categories=ambiguity_categories,
            clarifying_questions=all_clarifying_questions,
            priority_questions=priority_questions,
            execution_recommendations=execution_recommendations
        )
        
        print(f"✓ Analysis complete: {analysis.total_ambiguities_found} potential ambiguities identified")
        return analysis
        
    except Exception as e:
        print(f"Error in ambiguity analysis: {str(e)}")
        # Return minimal fallback analysis
        from datetime import datetime
        return QueryAmbiguityAnalysis(
            original_query=enhanced_query,
            analysis_timestamp=datetime.now().isoformat(),
            total_ambiguities_found=0,
            clarifying_questions=["What specific time period should be covered?", "Which geographic regions are of primary interest?"],
            priority_questions=["What specific time period should be covered?", "Which geographic regions are of primary interest?"],
            execution_recommendations=["Consider narrowing the scope", "Define key terms clearly"]
        )


def _create_fallback_analysis(query: str) -> Dict[str, Any]:
    """Create a basic fallback analysis when parsing fails."""
    return {
        "ambiguity_analysis": {
            "scope_and_delimiters": {
                "identified_issues": ["Unclear time period", "Broad geographical scope"],
                "clarifying_questions": ["What specific time period should be covered?", "Which geographic regions are of primary interest?"]
            },
            "vague_terminology": {
                "identified_issues": ["General terms without specific definitions"],
                "clarifying_questions": ["How should key terms be specifically defined?", "What level of detail is needed in the analysis?"]
            }
        },
        "priority_clarifying_questions": [
            "What specific time period should be covered?",
            "Which geographic regions are of primary interest?",
            "What level of detail is needed in the analysis?"
        ],
        "execution_recommendations": [
            "Consider narrowing the scope to specific regions or time periods",
            "Define key terminology clearly before beginning research"
        ]
    }


def print_ambiguity_analysis(analysis: QueryAmbiguityAnalysis) -> None:
    """
    Print a formatted summary of the ambiguity analysis.
    
    Args:
        analysis: The completed ambiguity analysis
    """
    
    print("=" * 80)
    print("QUERY AMBIGUITY ANALYSIS REPORT")
    print("=" * 80)
    print(f"Query: {analysis.original_query[:100]}{'...' if len(analysis.original_query) > 100 else ''}")
    print(f"Analysis Time: {analysis.analysis_timestamp}")
    print(f"Total Ambiguities Found: {analysis.total_ambiguities_found}")
    print()
    
    # Print by category
    for category in analysis.ambiguity_categories:
        print(f"📋 {category.category_name.upper()}")
        print("-" * 60)
        
        if category.identified_issues:
            print("Issues Identified:")
            for i, issue in enumerate(category.identified_issues, 1):
                print(f"  {i}. {issue}")
            print()
        
        if category.clarifying_questions:
            print("Clarifying Questions:")
            for i, question in enumerate(category.clarifying_questions, 1):
                print(f"  {i}. {question}")
            print()
    
    # Priority questions
    if analysis.priority_questions:
        print("🎯 PRIORITY CLARIFYING QUESTIONS")
        print("-" * 60)
        for i, question in enumerate(analysis.priority_questions, 1):
            print(f"{i}. {question}")
        print()
    
    # Recommendations
    if analysis.execution_recommendations:
        print("💡 EXECUTION RECOMMENDATIONS")
        print("-" * 60)
        for i, rec in enumerate(analysis.execution_recommendations, 1):
            print(f"{i}. {rec}")
        print()


def save_analysis_to_json(analysis: QueryAmbiguityAnalysis, filename: str) -> None:
    """
    Save the ambiguity analysis to a JSON file.
    
    Args:
        analysis: The completed ambiguity analysis
        filename: Name of the output JSON file
    """
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"✓ Analysis saved to {filename}")
    except Exception as e:
        print(f"Error saving analysis: {e}")


# Example usage and testing
if __name__ == "__main__":
    from planner.v2.load_model import load_gemini_model
    
    try:
        # Example enhanced query
        enhanced_query = """Provide a comprehensive analysis of the impact of renewable energy sources (solar, wind, hydro, geothermal, biomass) on the global economy, considering: (1) macroeconomic effects on GDP growth, job creation, and investment; (2) sector-specific impacts on energy production, manufacturing, and transportation; (3) geopolitical implications related to energy security and international trade; (4) the role of government policies (subsidies, carbon pricing, regulations) in shaping renewable energy adoption and economic outcomes; (5) challenges and opportunities related to grid integration, energy storage, and technological advancements; and (6) a comparative analysis of the economic performance of renewable energy versus fossil fuels."""
        
        print("=" * 80)
        print("AMBIGUITY RESOLVER MODULE DEMO")
        print("=" * 80)
        print(f"Analyzing Query: {enhanced_query[:100]}...")
        print()
        
        # Load model
        model = load_gemini_model()
        if model is None:
            print("Failed to load model. Using fallback analysis.")
            # Create mock analysis for demonstration
            from datetime import datetime
            analysis = QueryAmbiguityAnalysis(
                original_query=enhanced_query,
                analysis_timestamp=datetime.now().isoformat(),
                total_ambiguities_found=8,
                clarifying_questions=[
                    "What specific time period should the analysis cover?",
                    "Which countries or regions should be prioritized?",
                    "Should the analysis focus on current or projected impacts?",
                    "What baseline should be used for comparison with fossil fuels?"
                ],
                priority_questions=[
                    "What specific time period should the analysis cover?",
                    "Which countries or regions should be prioritized?",
                    "Should the analysis focus on current or projected impacts?"
                ],
                execution_recommendations=[
                    "Define specific time boundaries (e.g., 2020-2030)",
                    "Prioritize major economies for focused analysis",
                    "Establish clear baselines for comparative analysis"
                ]
            )
        else:
            # Run actual analysis
            analysis = analyze_query_ambiguities(enhanced_query, model)
        
        # Display results
        print_ambiguity_analysis(analysis)
        
        # Save to file
        save_analysis_to_json(analysis, "query_ambiguity_analysis.json")
        
        print("\n" + "=" * 80)
        print("ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"📊 Total Clarifying Questions Generated: {len(analysis.clarifying_questions)}")
        print(f"🎯 Priority Questions for User: {len(analysis.priority_questions)}")
        print(f"💡 Execution Recommendations: {len(analysis.execution_recommendations)}")
        print(f"📁 Analysis saved to: query_ambiguity_analysis.json")
        
    except Exception as e:
        print(f"Error in ambiguity analysis demo: {e}")
        import traceback
        traceback.print_exc()