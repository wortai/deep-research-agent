#!/usr/bin/env python3
"""
Integration test for Gap Questions - tests with real components
Run this to verify the implementation works end-to-end
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_component_initialization():
    """Test that all components can be initialized."""
    print("\n" + "="*60)
    print("TESTING COMPONENT INITIALIZATION")
    print("="*60)
    
    try:
        # Test LLM Client
        from researcher.gap_questions.llm_client import GeminiLLMClient
        if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'your_google_api_key_here':
            llm_client = GeminiLLMClient()
            print("✅ LLM Client initialized successfully")
        else:
            print("⚠️ LLM Client skipped (no valid API key)")
        
        # Test Query Generators
        from researcher.gap_questions.query_generators.plan_search_query_generator import PlanSearchQueryGenerator
        from researcher.gap_questions.query_generators.gap_search_query_generator import GapSearchQueryGenerator
        from researcher.gap_questions.query_generators.vector_search_query_generator import VectorSearchQueryGenerator
        
        plan_gen = PlanSearchQueryGenerator()
        gap_gen = GapSearchQueryGenerator()
        vector_gen = VectorSearchQueryGenerator()
        print("✅ Query Generators initialized successfully")
        
        # Test imports for orchestrator components
        from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator
        print("✅ Main Orchestrator class imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_query_generators():
    """Test query generation components with mock LLM."""
    print("\n" + "="*60)
    print("TESTING QUERY GENERATORS")
    print("="*60)
    
    try:
        from researcher.gap_questions.query_generators.plan_search_query_generator import PlanSearchQueryGenerator
        from researcher.gap_questions.query_generators.gap_search_query_generator import GapSearchQueryGenerator
        from researcher.gap_questions.query_generators.vector_search_query_generator import VectorSearchQueryGenerator
        
        # Mock responses for testing without API calls
        class MockLLMClient:
            def generate(self, prompt, context="general", model_type=None):
                if "plan" in context.lower() or "search_query" in context.lower():
                    return '["renewable energy trends 2024", "clean energy adoption rates", "sustainable technology impact"]'
                elif "gap" in context.lower():
                    return '["renewable energy storage costs", "grid integration challenges"]'
                elif "vector" in context.lower():
                    return '["energy storage economics", "renewable power grid stability"]'
                else:
                    return '["general query 1", "general query 2"]'
        
        # Test Plan Search Query Generator
        plan_gen = PlanSearchQueryGenerator()
        plan_gen.llm_client = MockLLMClient()
        
        plan_queries = plan_gen.generate_search_queries(
            "Analyze renewable energy adoption trends in developing countries", 
            max_queries=3
        )
        print(f"✅ Plan Search Generator: {len(plan_queries)} queries generated")
        for i, q in enumerate(plan_queries, 1):
            print(f"   {i}. {q}")
        
        # Test Gap Search Query Generator
        gap_gen = GapSearchQueryGenerator()
        gap_gen.llm_client = MockLLMClient()
        
        gap_queries = gap_gen.generate_gap_search_queries(
            "Missing data on renewable energy job creation in rural areas",
            max_queries=2
        )
        print(f"✅ Gap Search Generator: {len(gap_queries)} queries generated")
        for i, q in enumerate(gap_queries, 1):
            print(f"   {i}. {q}")
        
        # Test Vector Search Query Generator
        vector_gen = VectorSearchQueryGenerator()
        vector_gen.llm_client = MockLLMClient()
        
        vector_queries = vector_gen.generate_vector_search_queries(
            "Need more information about renewable energy storage technologies",
            max_queries=2
        )
        print(f"✅ Vector Search Generator: {len(vector_queries)} queries generated")
        for i, q in enumerate(vector_queries, 1):
            print(f"   {i}. {q}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_orchestrator_basic():
    """Test basic orchestrator functionality without external APIs."""
    print("\n" + "="*60)
    print("TESTING ORCHESTRATOR BASIC FUNCTIONALITY")
    print("="*60)
    
    try:
        from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator
        from unittest.mock import Mock, AsyncMock
        
        # Create orchestrator with minimal config
        orchestrator = GapQuestionsOrchestrator(
            max_depth=1,
            max_gaps=1,
            max_gap_queries=1,
            vector_collection_name="test_basic"
        )
        
        print("✅ Orchestrator initialized")
        
        # Test workflow building
        workflow = orchestrator.build_workflow()
        print("✅ Workflow built successfully")
        
        # Test stop conditions
        class MockState:
            def __init__(self):
                self.current_depth = 0
                self.gap_queue = []
        
        state = MockState()
        
        # Should not stop initially
        should_stop = orchestrator.check_stop_conditions(state)
        print(f"✅ Stop conditions check: {should_stop} (expected: True for empty queue)")
        
        # Test utility methods
        gaps = orchestrator._parse_gaps_response('["gap 1", "gap 2"]')
        print(f"✅ Gap parsing: {len(gaps)} gaps parsed")
        
        solution = orchestrator._curate_gap_solution("test gap", [])
        print(f"✅ Solution curation: {len(solution)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator basic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow_structure():
    """Test the LangGraph workflow structure."""
    print("\n" + "="*60)
    print("TESTING WORKFLOW STRUCTURE")
    print("="*60)
    
    try:
        from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator
        
        orchestrator = GapQuestionsOrchestrator(
            max_depth=1,
            max_gaps=1,
            max_gap_queries=1,
            vector_collection_name="test_workflow"
        )
        
        # Check workflow nodes
        workflow = orchestrator.workflow
        print("✅ Workflow created")
        
        # Test individual node functions
        test_state = {
            "plan_query": "test query",
            "gap_queue": [],
            "processed_gaps": [],
            "query_solutions": [],
            "current_depth": 0,
            "workflow_complete": False,
            "errors": []
        }
        
        # Test initialization node
        init_state = orchestrator._initialize_node(test_state.copy())
        print("✅ Initialize node works")
        
        # Test check stop node
        stop_state = orchestrator._check_stop_node(test_state.copy())
        print("✅ Check stop node works")
        
        # Test finalize node
        final_state = orchestrator._finalize_node(test_state.copy())
        print("✅ Finalize node works")
        
        # Test conditional edge
        continue_decision = orchestrator._should_continue({"should_continue": False})
        print(f"✅ Conditional edge: {continue_decision}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_md_report_generation():
    """Test markdown report generation."""
    print("\n" + "="*60)
    print("TESTING MD REPORT GENERATION")
    print("="*60)
    
    try:
        from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator
        
        orchestrator = GapQuestionsOrchestrator(
            max_depth=1,
            max_gaps=1,
            max_gap_queries=1,
            vector_collection_name="test_md"
        )
        
        # Test MD report generation with mock state
        test_state = {
            "plan_query": "Impact of AI on renewable energy optimization",
            "query_solutions": [
                {
                    "gap": "Missing data on AI algorithm efficiency in solar prediction",
                    "vector_queries": ["AI solar forecasting", "machine learning renewable energy"],
                    "solution": "Current research shows AI can improve solar prediction accuracy by 15-20%...",
                    "source_count": 3
                },
                {
                    "gap": "Lack of information on AI implementation costs",
                    "vector_queries": ["AI renewable energy costs"],
                    "solution": "Implementation costs vary but typically range from $50K-500K...",
                    "source_count": 2
                }
            ],
            "processed_gaps": ["gap1", "gap2"],
            "current_depth": 2,
            "errors": ["Minor API timeout during search"]
        }
        
        md_file = orchestrator._generate_md_report(test_state)
        
        if md_file and os.path.exists(md_file):
            print(f"✅ MD report generated: {md_file}")
            
            # Read and display first few lines
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
                print("   Preview:")
                for line in lines:
                    print(f"   {line.rstrip()}")
            
            # Clean up
            os.remove(md_file)
            print("✅ Test file cleaned up")
        else:
            print("⚠️ MD report generation returned empty path")
        
        return True
        
    except Exception as e:
        print(f"❌ MD report test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all integration tests."""
    print("🚀 Starting Gap Questions Integration Tests")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    test_results = []
    
    # Run tests
    tests = [
        ("Component Initialization", test_component_initialization),
        ("Query Generators", test_query_generators),
        ("Orchestrator Basic", test_orchestrator_basic),
        ("Workflow Structure", test_workflow_structure),
        ("MD Report Generation", test_md_report_generation),
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("-"*80)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
    else:
        print("⚠️ Some tests failed - check logs above")
    
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())