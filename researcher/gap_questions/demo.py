#!/usr/bin/env python3
"""
Demo script for Gap Questions system
Shows how to use the GapQuestionsOrchestrator for research
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_basic_usage():
    """Demonstrate basic usage of the Gap Questions system."""
    print("🔬 Gap Questions System Demo")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    if not os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY') == 'your_google_api_key_here':
        print("⚠️ Warning: No valid GOOGLE_API_KEY found in environment")
        print("   Set your API key in .env file for full functionality")
        print("   This demo will show the structure but may not complete successfully")
        print()
    
    try:
        # Initialize the orchestrator
        print("🚀 Initializing Gap Questions Orchestrator...")
        orchestrator = GapQuestionsOrchestrator(
            max_depth=2,           # Maximum research depth
            max_gaps=2,            # Maximum gaps to identify per iteration
            max_gap_queries=1,     # Maximum queries per gap
            vector_collection_name="demo_gap_questions"
        )
        print("✅ Orchestrator initialized successfully")
        print()
        
        # Define research queries to test
        research_queries = [
            "Analyze the environmental impact of electric vehicles",
            "Evaluate the effectiveness of remote work on productivity",
            "Research trends in renewable energy adoption worldwide"
        ]
        
        # Run research for each query
        for i, query in enumerate(research_queries, 1):
            print(f"📋 Research Query {i}/{len(research_queries)}")
            print(f"Query: {query}")
            print("-" * 50)
            
            try:
                # Execute the research
                results = await orchestrator.orchestrator(query)
                
                # Display results
                if results.get("success"):
                    print("✅ Research completed successfully!")
                    print(f"   📊 Total Solutions: {results.get('total_solutions', 0)}")
                    print(f"   🔍 Processed Gaps: {results.get('processed_gaps', 0)}")
                    print(f"   📏 Final Depth: {results.get('final_depth', 0)}")
                    
                    if results.get('md_report'):
                        print(f"   📄 Report Generated: {results.get('md_report')}")
                        
                        # Show a preview of the report
                        try:
                            with open(results.get('md_report'), 'r', encoding='utf-8') as f:
                                lines = f.readlines()[:15]  # First 15 lines
                                print("   📖 Report Preview:")
                                for line in lines:
                                    print(f"      {line.rstrip()}")
                                if len(f.readlines()) > 15:
                                    print("      ...")
                        except Exception as e:
                            print(f"   ⚠️ Could not read report: {e}")
                    
                    if results.get('errors'):
                        print(f"   ⚠️ Errors encountered: {len(results['errors'])}")
                        for error in results['errors'][:3]:  # Show first 3 errors
                            print(f"      - {error}")
                else:
                    print("❌ Research failed")
                    print(f"   Error: {results.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"❌ Query failed: {e}")
                logger.error(f"Query '{query}' failed", exc_info=True)
            
            print()
            
            # Add delay between queries to be respectful to APIs
            if i < len(research_queries):
                print("⏱️ Waiting 2 seconds before next query...")
                await asyncio.sleep(2)
                print()
        
        print("🎉 Demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error("Demo failed", exc_info=True)

async def demo_component_testing():
    """Demonstrate individual component usage."""
    print("\n" + "="*60)
    print("🧩 Component Testing Demo")
    print("="*60)
    
    try:
        # Test individual components
        from researcher.gap_questions.query_generators.plan_search_query_generator import PlanSearchQueryGenerator
        from researcher.gap_questions.query_generators.gap_search_query_generator import GapSearchQueryGenerator
        from researcher.gap_questions.query_generators.vector_search_query_generator import VectorSearchQueryGenerator
        
        print("🔧 Testing Individual Components")
        print()
        
        # Test Plan Search Query Generator
        print("1️⃣ Plan Search Query Generator")
        plan_gen = PlanSearchQueryGenerator()
        
        try:
            if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'your_google_api_key_here':
                queries = plan_gen.generate_search_queries(
                    "Analyze climate change impact on agriculture", 
                    max_queries=3
                )
                print(f"   ✅ Generated {len(queries)} search queries:")
                for i, q in enumerate(queries, 1):
                    print(f"      {i}. {q}")
            else:
                print("   ⚠️ Skipped (no API key)")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print()
        
        # Test Gap Search Query Generator
        print("2️⃣ Gap Search Query Generator")
        gap_gen = GapSearchQueryGenerator()
        
        try:
            if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'your_google_api_key_here':
                gap_queries = gap_gen.generate_gap_search_queries(
                    "Missing data on crop yield changes in developing countries",
                    max_queries=2
                )
                print(f"   ✅ Generated {len(gap_queries)} gap queries:")
                for i, q in enumerate(gap_queries, 1):
                    print(f"      {i}. {q}")
            else:
                print("   ⚠️ Skipped (no API key)")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print()
        
        # Test Vector Search Query Generator
        print("3️⃣ Vector Search Query Generator")
        vector_gen = VectorSearchQueryGenerator()
        
        try:
            if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'your_google_api_key_here':
                vector_queries = vector_gen.generate_vector_search_queries(
                    "Need more information about sustainable farming practices",
                    max_queries=2
                )
                print(f"   ✅ Generated {len(vector_queries)} vector queries:")
                for i, q in enumerate(vector_queries, 1):
                    print(f"      {i}. {q}")
            else:
                print("   ⚠️ Skipped (no API key)")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print()
        print("✅ Component testing completed")
        
    except Exception as e:
        print(f"❌ Component testing failed: {e}")
        logger.error("Component testing failed", exc_info=True)

def show_usage_examples():
    """Show code examples for using the system."""
    print("\n" + "="*60)
    print("📚 Usage Examples")
    print("="*60)
    
    examples = """
# Basic Usage
from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator

async def run_research():
    # Initialize orchestrator
    orchestrator = GapQuestionsOrchestrator(
        max_depth=2,
        max_gaps=2,
        max_gap_queries=1,
        vector_collection_name="my_research"
    )
    
    # Run research
    results = await orchestrator.orchestrator(
        "Analyze the impact of AI on healthcare"
    )
    
    # Check results
    if results.get("success"):
        print(f"Solutions found: {results['total_solutions']}")
        print(f"Report file: {results['md_report']}")
    else:
        print(f"Error: {results['error']}")

# Advanced Configuration
orchestrator = GapQuestionsOrchestrator(
    max_depth=3,              # Deeper research
    max_gaps=3,               # More gaps per iteration
    max_gap_queries=2,        # More queries per gap
    vector_collection_name="advanced_research"
)

# Individual Component Usage
from researcher.gap_questions.query_generators.plan_search_query_generator import PlanSearchQueryGenerator

generator = PlanSearchQueryGenerator()
queries = generator.generate_search_queries(
    "Research renewable energy trends",
    max_queries=5
)
"""
    
    print(examples)

async def main():
    """Main demo function."""
    print("🌟 Welcome to the Gap Questions System Demo!")
    print("This demo will show you how to use the Gap Questions Orchestrator")
    print("for comprehensive research with iterative gap analysis.")
    print()
    
    # Check if user wants to run full demo
    try:
        # Run basic usage demo
        await demo_basic_usage()
        
        # Run component testing demo
        await demo_component_testing()
        
        # Show usage examples
        show_usage_examples()
        
        print("\n" + "="*60)
        print("✨ Demo completed successfully!")
        print("Check the generated MD files for detailed research reports.")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        logger.error("Demo failed", exc_info=True)

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())