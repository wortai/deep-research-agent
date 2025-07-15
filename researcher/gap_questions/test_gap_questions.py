#!/usr/bin/env python3
"""
Test script for Gap Questions implementation
"""

import asyncio
import logging
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_gap_questions():
    """Test the Gap Questions Orchestrator."""
    try:
        print("=" * 60)
        print("Testing Gap Questions Orchestrator")
        print("=" * 60)
        
        # Initialize orchestrator
        orchestrator = GapQuestionsOrchestrator(
            max_depth=2,
            max_gaps=2,
            max_gap_queries=1,
            vector_collection_name="test_gap_questions"
        )
        
        # Test query
        test_query = "Analyze the environmental impact of renewable energy adoption"
        
        print(f"Testing query: {test_query}")
        print("-" * 40)
        
        # Run orchestrator
        results = await orchestrator.orchestrator(test_query)
        
        # Display results
        print("\nResults:")
        print(f"Success: {results.get('success', False)}")
        if results.get('success'):
            print(f"Total Solutions: {results.get('total_solutions', 0)}")
            print(f"Processed Gaps: {results.get('processed_gaps', 0)}")
            print(f"Final Depth: {results.get('final_depth', 0)}")
            print(f"MD Report: {results.get('md_report', 'None')}")
            
            if results.get('errors'):
                print(f"Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"  - {error}")
        else:
            print(f"Error: {results.get('error', 'Unknown error')}")
        
        print("=" * 60)
        print("Test completed")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gap_questions())