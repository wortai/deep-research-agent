"""
Simple Research Runner

This file runs research using main.py and extracts the Query → Answer mappings
from the completed research state.
"""

from .main import main


def run_research(user_query: str, max_iterations: int = 3, confidence_threshold: float = 0.85):
    """
    Run research and return simple results
    
    Args:
        user_query: The research question
        max_iterations: Max iterations for research
        confidence_threshold: When to stop research
        
    Returns:
        dict: Simple results with query → answer mappings
    """
    # Run the main research workflow
    generator = main(user_query, max_iterations, confidence_threshold)
    
    if not generator:
        return {"error": "Research failed"}
    
    # Extract simple results
    results = {
        "user_query": user_query,
        "session_id": generator.session_id,
        "final_confidence": generator.current_confidence,
        "query_answer_mappings": {},
        "all_insights": [],
        "urls_accessed": []
    }
    
    # Extract Query → Answer mappings from the research
    for query_data in generator.monitor.detailed_queries:
        gap_query = query_data.gap_query
        insights = query_data.insights_extracted
        
        # Store the mapping: gap_query → insights (answers)
        results["query_answer_mappings"][gap_query] = insights
        results["all_insights"].extend(insights)
        results["urls_accessed"].extend(query_data.urls_accessed)
    
    # Remove duplicates from URLs
    results["urls_accessed"] = list(set(results["urls_accessed"]))
    
    return results


def print_results(results):
    """Print research results in a clean format"""
    if "error" in results:
        print(f"❌ {results['error']}")
        return
    
    print(f"\n🔬 Research Results for: {results['user_query']}")
    print(f"📊 Session: {results['session_id']}")
    print(f"🎯 Final Confidence: {results['final_confidence']:.2%}")
    print("\n" + "="*60)
    
    
    print("\n📋 QUERY → ANSWER MAPPINGS:")
    for gap_query, answers in results["query_answer_mappings"].items():
        print(f"\n🔍 Gap Query: {gap_query}")
        print("📝 Processed Answers:")
        for i, answer in enumerate(answers, 1):
            print(f"   {i}. {answer}")
    
    print(f"\n🔗 URLs Accessed ({len(results['urls_accessed'])}):")
    for i, url in enumerate(results['urls_accessed'], 1):
        print(f"   {i}. {url}")



if __name__ == "__main__":
    # Example usage
    query = "What are the latest advancements in large language models?"
    results = run_research(query)
    print_results(results)
