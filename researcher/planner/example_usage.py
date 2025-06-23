"""
Example usage of the Deep Search Planner Agent

This file demonstrates various ways to use the planner programmatically.
"""

from researcher.planner.planner import DeepSearchPlannerAgent
from researcher.planner.models import PlanData
import json


def basic_usage_example():
    """Basic usage example - simple plan generation"""
    print("🔬 BASIC USAGE EXAMPLE")
    print("=" * 50)
    
    # Initialize planner
    planner = DeepSearchPlannerAgent()
    
    if not planner.load_gemini_model():
        print("❌ Failed to load model. Check your API key.")
        return
    
    # Simple query enhancement and plan generation
    user_query = "renewable energy adoption in developing countries"
    
    # Step 1: Enhance the query
    enhanced_query = planner.enhance_search_query(user_query)
    print(f"Enhanced Query: {enhanced_query}")
    
    # Step 2: Generate initial plan
    plan_data = planner.generate_initial_plan(enhanced_query)
    
    # Step 3: Display plan components
    print(f"\n📋 Generated Plan:")
    print(f"🔍 Search Steps ({len(plan_data.search_steps)}):")
    for i, step in enumerate(plan_data.search_steps, 1):
        print(f"   {i}. {step}")
    
    print(f"\n🎯 Key Areas ({len(plan_data.key_areas)}):")
    for i, area in enumerate(plan_data.key_areas, 1):
        print(f"   {i}. {area}")
    
    print(f"\n📚 Information Sources ({len(plan_data.information_sources)}):")
    for i, source in enumerate(plan_data.information_sources, 1):
        print(f"   {i}. {source}")
    
    print(f"\n🎯 Search Strategies ({len(plan_data.search_strategies)}):")
    for i, strategy in enumerate(plan_data.search_strategies, 1):
        print(f"   {i}. {strategy}")
    
    print(f"\n📊 Success Metrics ({len(plan_data.success_metrics)}):")
    for i, metric in enumerate(plan_data.success_metrics, 1):
        print(f"   {i}. {metric}")


if __name__ == "__main__":
    basic_usage_example()