from typing import Optional
from langchain_core.language_models.base import BaseLanguageModel

def enhance_search_query(user_query: str, model: BaseLanguageModel, custom_prompt: Optional[str] = None) -> str:
    """
    Enhance a user's search query to provide better search starting points for an LLM.
    
    This function takes a user's original query and improves it by:
    - Adding clarity and specificity
    - Structuring the query for better search results
    - Preserving all original information without destructing content
    - Optimizing for deep search capabilities
    
    Args:
        user_query (str): The original user query to enhance
        model (BaseLanguageModel): The LLM model to use for enhancement
        custom_prompt (str, optional): Custom enhancement prompt. Uses default if None.
    
    Returns:
        str: Enhanced and optimized search query
    
    Raises:
        ValueError: If user_query is empty or None
        Exception: If model invocation fails
    """
    
    if not user_query or not user_query.strip():
        raise ValueError("User query cannot be empty or None")
    
    # Default enhancement prompt (FIXED VERSION - removed placeholders that aren't provided)
    default_prompt = """You are an advanced Query Enhancement Engine for deep search agents. Your primary function is to transform a user's raw query into a precise, comprehensive, and structured query that is optimized for retrieval by Large Language Models and semantic search systems.

You will perform this by following a strict thought process and adhering to a set of core rules. Your goal is to ALWAYS produce an enhanced query and NEVER ask for clarification.

---
USER QUERY: {query}
---

Thought Process (Follow these steps internally before generating the output):
1.  **Deconstruct:** Identify the core entities, concepts, and the fundamental intent of the USER QUERY.
2.  **Handle Ambiguity by Broadening Scope:** If a query is broad or lacks specifics (e.g., 'machine learning'), assume the user is seeking a comprehensive, foundational overview. Identify the most critical and common sub-topics to build a well-rounded query.
3.  **Determine Context:** Infer the most likely context from the query. For example, a query like "machine learning" should be treated as seeking comprehensive information about the technology domain.
4.  **Strategize Expansion:** Based on the inferred context, plan the enhancement. Add terms related to definitions, applications, key components, benefits, and challenges to create a holistic query.
5.  **Synthesize:** Construct the final, enhanced query according to the rules below. Ensure it is a single, cohesive, and directly actionable search query.

---
RULES:
1.  **NO FOLLOW-UP QUESTIONS:** You must always generate a direct, enhanced query. Never ask the user for clarification. Make reasonable and broad assumptions for vague queries to create a comprehensive starting point for research.
2.  **Preserve Core Intent:** The user's original goal must remain the absolute center of the enhanced query. Do not change the topic.
3.  **Eliminate Vagueness:** Replace ambiguous terms by creating a broader query that covers the most likely interpretations.
4.  **Add Structure for Search:** Organize complex requests into logical components that a search agent can parse (e.g., by listing aspects like "applications," "ethical considerations," "performance metrics").
5.  **Optimize Terminology:** Use precise and standard terminology for the inferred domain to yield high-quality, authoritative results.
6.  **Be Concise Yet Comprehensive:** Do not add unnecessary boilerplate. Every added word must serve to increase the relevance, depth, or precision of the search results.
7.  **No Hallucination:** Do not add facts or assumptions not directly implied by the query. Expanding a broad topic into its logical sub-components is not hallucination.

---
EXAMPLES:
Original: "machine learning"
Enhanced: "Provide a comprehensive overview of machine learning (ML), including its core definition, a comparison of fundamental types (supervised, unsupervised, reinforcement learning), key algorithms, common real-world applications across industries, and the challenges and ethical considerations associated with ML."

Original: "climate change"
Enhanced: "Provide a detailed analysis of climate change, covering the core scientific evidence and causes, its multifaceted effects (environmental, economic, societal), key international policies and agreements (e.g., Paris Agreement), and an overview of mitigation and adaptation strategies."

Original: "Python vs Java"
Enhanced: "Provide a comparative analysis of Python and Java programming languages, focusing on key differences in syntax and readability, performance benchmarks for common tasks (e.g., web backends, data processing), ecosystem and library support, and primary use cases in the industry."

Original: "Interesting facts about Apple"
Enhanced: "Provide a detailed list of interesting and little-known facts about Apple Inc., the technology company, covering its history, product development milestones, key figures like Steve Jobs, and its cultural impact. Also include interesting botanical and historical facts about the apple fruit."

---

Now, enhance the following user query while following all the rules above.

USER QUERY: {query}

ENHANCED QUERY:"""
    
    # Use custom prompt if provided, otherwise use default
    enhancement_prompt = custom_prompt if custom_prompt else default_prompt
    
    try:
        # Format the prompt with the user query (ONLY the query placeholder now)
        formatted_prompt = enhancement_prompt.format(query=user_query)
        
        # Get enhanced query from the model
        response = model.invoke(formatted_prompt)
        enhanced_query = response.content.strip()
        
        # Basic validation - ensure we got a response
        if not enhanced_query:
            print("Warning: Model returned empty response, using original query")
            return user_query
            
        print(f"Original query: {user_query}")
        print(f"Enhanced query: {enhanced_query}")
        
        return enhanced_query
        
    except Exception as e:
        print(f"Error enhancing query: {str(e)}")
        print("Falling back to original query")
        return user_query


if __name__ == "__main__":
    try:
        # Load the Gemini model
        from planner.v2.load_model import load_gemini_model
        print("Loading Gemini model...")
        model = load_gemini_model()
        
        # Full-fledged example scenarios
        example_scenarios = [
            {
                "title": "Technology Research",
                "query": "How to implement blockchain technology in supply chain management",
                "description": "Complex technical implementation query"
            },
            {
                "title": "Academic Research", 
                "query": "Impact of social media on teenage mental health and academic performance",
                "description": "Multi-faceted research topic with social implications"
            },
            {
                "title": "Business Strategy",
                "query": "Market analysis for launching sustainable packaging startup in Europe",
                "description": "Business planning with geographic and industry specifics"
            },
            {
                "title": "Health & Wellness",
                "query": "Evidence-based approaches to managing chronic pain without opioids",
                "description": "Medical research with treatment alternatives"
            },
            {
                "title": "Educational Content",
                "query": "Teaching calculus concepts to high school students using real-world applications",
                "description": "Pedagogical approach with practical applications"
            },
            {
                "title": "Environmental Science",
                "query": "Comparing effectiveness of renewable energy sources for urban environments",
                "description": "Comparative analysis with environmental focus"
            },
            {
                "title": "Career Development",
                "query": "Transitioning from software engineering to data science career path",
                "description": "Professional development and career change guidance"
            },
            {
                "title": "Cultural Analysis",
                "query": "Influence of streaming platforms on traditional cinema and storytelling",
                "description": "Cultural and industry transformation analysis"
            }
        ]
        
        print("\n🚀 COMPREHENSIVE QUERY ENHANCEMENT EXAMPLES")
        print("=" * 80)
        
        for i, scenario in enumerate(example_scenarios, 1):
            print(f"\n{i}. {scenario['title']}")
            print(f"   Description: {scenario['description']}")
            print(f"   Original Query: '{scenario['query']}'")
            print("-" * 60)
            
            enhanced = enhance_search_query(scenario['query'], model)
            
            print(f"✅ Enhancement Complete!")
            print(f"📊 Stats: {len(scenario['query'])} → {len(enhanced)} chars "
                  f"({len(enhanced)/len(scenario['query']):.1f}x improvement)")
            print()
        
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()