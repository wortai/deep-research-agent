from typing import List, Dict, Any
from dataclasses import dataclass
import json
from langchain_core.language_models.base import BaseLanguageModel


@dataclass 
class UserResponse:
    """User's response to a clarifying question."""
    question: str
    answer: str


@dataclass
class AmbiguityResolverResult:
    """Result from resolving ambiguities with user input."""
    refined_query: str
    original_query: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "refined_query": self.refined_query,
            "original_query": self.original_query
        }


def ambiguity_resolver(
    original_query: str, 
    user_responses: List[UserResponse], 
    model: BaseLanguageModel
) -> AmbiguityResolverResult:
    """
    Resolve ambiguities by refining the query based on user responses.
    
    Args:
        original_query: The original search query
        user_responses: List of user responses to clarifying questions
        model: LLM model for refinement
        
    Returns:
        Refined query result
    """
    
    # Format user Q&A
    user_qna = ""
    for i, response in enumerate(user_responses, 1):
        user_qna += f"Q{i}: {response.question}\n"
        user_qna += f"A{i}: {response.answer}\n\n"
    user_qna = user_qna.strip()
    
    prompt = f"""You are an expert AI search strategist. Your primary function is to synthesize information and construct a single, highly-refined search query based on initial user intent and subsequent clarifications.

You will be given two pieces of information:
1. **The Original Enhanced Search Query:** This was the user's initial detailed request.
2. **The User's Answers:** These are the user's direct responses to the clarifying questions you generated previously.

**Your Task:**
Your goal is to create a **new, single, enhanced search query**. This new query should not be a list of steps or a conversation, but a standalone, comprehensive search command that has been meticulously refined and focused by the user's answers.

**Follow these instructions to construct the new query:**
1. **Integrate Specifics:** Carefully analyze each user answer. Use the information provided to replace ambiguous terms in the original query with precise ones. For example, if the original query mentioned "global economy" and the user specified "the G20 nations between 2010 and 2025," this new constraint must be embedded directly into the query.

2. **Apply Constraints and Scope:** Use the user's answers to set clear boundaries. This includes defining the exact time periods, geographic regions, specific sectors, or technologies to focus on.

3. **Resolve Ambiguities:** The user's answers were designed to resolve vagueness. Ensure the new query reflects this clarity. For example, if the user defined what "significant impact" means to them (e.g., "a GDP change of over 0.5%"), incorporate that quantifiable metric.

4. **Prioritize and Structure:** Based on the user's feedback, the new query may need to re-prioritize or re-structure the original points of analysis. If the user showed a strong preference for one aspect (e.g., "focus primarily on job creation and geopolitical implications"), the new query should reflect that emphasis.

5. **Synthesize, Do Not Enumerate:** Your final output must be **one single, coherent search query**. Do not list the original query and the answers. Your task is to perform the synthesis and produce only the final, polished result.

**[START OF INPUT]**
1. Original Enhanced Search Query:
"{original_query}"

2. User Q&A:
{user_qna}
**[END OF INPUT]**

**Response Format:**
Please respond with a JSON structure:
{{
    "refined_query": "Your single, comprehensive refined search query here"
}}

Your Generated Output (New Enhanced Search Query):"""
    
    try:
        # Get refinement from model
        response = model.invoke(prompt)
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
            
            refinement_data = json.loads(response_text)
            refined_query = refinement_data.get("refined_query", original_query)
            
        except json.JSONDecodeError:
            # Fallback: try to extract query from text
            refined_query = _extract_query_from_response(response_text, original_query)
        
        return AmbiguityResolverResult(
            refined_query=refined_query,
            original_query=original_query
        )
        
    except Exception as e:
        print(f"Error in ambiguity resolution: {e}")
        return AmbiguityResolverResult(
            refined_query=original_query,  # Fallback to original
            original_query=original_query
        )


def _extract_query_from_response(response_text: str, fallback: str) -> str:
    """Extract refined query from response text when JSON parsing fails."""
    lines = response_text.split('\n')
    
    for line in lines:
        line = line.strip()
        # Skip empty lines and lines that look like instructions
        if not line or line.startswith('**') or line.startswith('Your') or line.startswith('Response'):
            continue
        
        # If line is substantial and doesn't look like metadata, it might be the query
        if len(line) > 100 and not line.startswith('{') and not line.startswith('['):
            return line
    
    return fallback


# Example usage for seamless integration
if __name__ == "__main__":
    from planner.v2.load_model import load_gemini_model
    # Demo: Seamless integration flow
    try:
        model = load_gemini_model()
        if not model:
            print("Model not available for demo")
            exit()
        
        # Step 1: Start with a query
        initial_query = "impact of renewable energy on global economy"
        print(f"Initial Query: {initial_query}")
        
        # Step 2: Find ambiguities (using existing ambiguity_finder)
        # This would call: ambiguity_finder(initial_query, model)
        
        # Step 3: Simulate user responses
        user_responses = [
            UserResponse("What specific time period should be covered?", "2015-2030"),
            UserResponse("Which regions should be prioritized?", "G20 nations, focus on US, EU, China"),
            UserResponse("What level of detail is needed?", "Focus on quantifiable economic impacts"),
            UserResponse("How should renewable energy be defined?", "Utility-scale solar, wind, and hydro installations")
        ]
        
        print(f"\nUser provided {len(user_responses)} responses")
        
        # Step 4: Resolve ambiguities
        result = ambiguity_resolver(initial_query, user_responses, model)
        
        print(f"\nOriginal: {result.original_query}")
        print(f"\nRefined: {result.refined_query}")
        
        # Step 5: Could call ambiguity_finder again on refined query
        from planner.v2.ambiguity_finder import analyze_query_ambiguities
        next_result = analyze_query_ambiguities(result.refined_query, model)
        
        print("\n✓ Seamless integration flow complete")
        
    except Exception as e:
        print(f"Demo error: {e}")from typing import List, Dict, Any
from dataclasses import dataclass
import json
from langchain_core.language_models.base import BaseLanguageModel


@dataclass 
class UserResponse:
    """User's response to a clarifying question."""
    question: str
    answer: str


@dataclass
class AmbiguityResolverResult:
    """Result from resolving ambiguities with user input."""
    refined_query: str
    original_query: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "refined_query": self.refined_query,
            "original_query": self.original_query
        }


def ambiguity_resolver(
    original_query: str, 
    user_responses: List[UserResponse], 
    model: BaseLanguageModel
) -> AmbiguityResolverResult:
    """
    Resolve ambiguities by refining the query based on user responses.
    
    Args:
        original_query: The original search query
        user_responses: List of user responses to clarifying questions
        model: LLM model for refinement
        
    Returns:
        Refined query result
    """
    
    # Format user Q&A
    user_qna = ""
    for i, response in enumerate(user_responses, 1):
        user_qna += f"Q{i}: {response.question}\n"
        user_qna += f"A{i}: {response.answer}\n\n"
    user_qna = user_qna.strip()
    
    prompt = f"""You are an expert AI search strategist. Your primary function is to synthesize information and construct a single, highly-refined search query based on initial user intent and subsequent clarifications.

You will be given two pieces of information:
1. **The Original Enhanced Search Query:** This was the user's initial detailed request.
2. **The User's Answers:** These are the user's direct responses to the clarifying questions you generated previously.

**Your Task:**
Your goal is to create a **new, single, enhanced search query**. This new query should not be a list of steps or a conversation, but a standalone, comprehensive search command that has been meticulously refined and focused by the user's answers.

**Follow these instructions to construct the new query:**
1. **Integrate Specifics:** Carefully analyze each user answer. Use the information provided to replace ambiguous terms in the original query with precise ones. For example, if the original query mentioned "global economy" and the user specified "the G20 nations between 2010 and 2025," this new constraint must be embedded directly into the query.

2. **Apply Constraints and Scope:** Use the user's answers to set clear boundaries. This includes defining the exact time periods, geographic regions, specific sectors, or technologies to focus on.

3. **Resolve Ambiguities:** The user's answers were designed to resolve vagueness. Ensure the new query reflects this clarity. For example, if the user defined what "significant impact" means to them (e.g., "a GDP change of over 0.5%"), incorporate that quantifiable metric.

4. **Prioritize and Structure:** Based on the user's feedback, the new query may need to re-prioritize or re-structure the original points of analysis. If the user showed a strong preference for one aspect (e.g., "focus primarily on job creation and geopolitical implications"), the new query should reflect that emphasis.

5. **Synthesize, Do Not Enumerate:** Your final output must be **one single, coherent search query**. Do not list the original query and the answers. Your task is to perform the synthesis and produce only the final, polished result.

**[START OF INPUT]**
1. Original Enhanced Search Query:
"{original_query}"

2. User Q&A:
{user_qna}
**[END OF INPUT]**

**Response Format:**
Please respond with a JSON structure:
{{
    "refined_query": "Your single, comprehensive refined search query here"
}}

Your Generated Output (New Enhanced Search Query):"""
    
    try:
        # Get refinement from model
        response = model.invoke(prompt)
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
            
            refinement_data = json.loads(response_text)
            refined_query = refinement_data.get("refined_query", original_query)
            
        except json.JSONDecodeError:
            # Fallback: try to extract query from text
            refined_query = _extract_query_from_response(response_text, original_query)
        
        return AmbiguityResolverResult(
            refined_query=refined_query,
            original_query=original_query
        )
        
    except Exception as e:
        print(f"Error in ambiguity resolution: {e}")
        return AmbiguityResolverResult(
            refined_query=original_query,  # Fallback to original
            original_query=original_query
        )


def _extract_query_from_response(response_text: str, fallback: str) -> str:
    """Extract refined query from response text when JSON parsing fails."""
    lines = response_text.split('\n')
    
    for line in lines:
        line = line.strip()
        # Skip empty lines and lines that look like instructions
        if not line or line.startswith('**') or line.startswith('Your') or line.startswith('Response'):
            continue
        
        # If line is substantial and doesn't look like metadata, it might be the query
        if len(line) > 100 and not line.startswith('{') and not line.startswith('['):
            return line
    
    return fallback


# Example usage for seamless integration
if __name__ == "__main__":
    from planner.v2.load_model import load_gemini_model
    
    # Demo: Seamless integration flow
    try:
        model = load_gemini_model()
        if not model:
            print("Model not available for demo")
            exit()
        
        # Step 1: Start with a query
        initial_query = "impact of renewable energy on global economy"
        print(f"Initial Query: {initial_query}")
        
        # Step 2: Find ambiguities (using existing ambiguity_finder)
        # This would call: ambiguity_finder(initial_query, model)
        
        # Step 3: Simulate user responses
        user_responses = [
            UserResponse("What specific time period should be covered?", "2015-2030"),
            UserResponse("Which regions should be prioritized?", "G20 nations, focus on US, EU, China"),
            UserResponse("What level of detail is needed?", "Focus on quantifiable economic impacts"),
            UserResponse("How should renewable energy be defined?", "Utility-scale solar, wind, and hydro installations")
        ]
        
        print(f"\nUser provided {len(user_responses)} responses")
        
        # Step 4: Resolve ambiguities
        result = ambiguity_resolver(initial_query, user_responses, model)
        
        print(f"\nOriginal: {result.original_query}")
        print(f"\nRefined: {result.refined_query}")
        
        # Step 5: Could call ambiguity_finder again on refined query
        from planner.v2.ambiguity_finder import analyze_query_ambiguities
        next_result = analyze_query_ambiguities(result.refined_query, model)
        
        print("\n✓ Seamless integration flow complete")
        
    except Exception as e:
        print(f"Demo error: {e}")