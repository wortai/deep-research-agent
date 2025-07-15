#!/usr/bin/env python3
"""
Unit tests for Gap Questions module components
Focused on testing individual functions with minimal dependencies
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, AsyncMock
from collections import deque

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

class TestGapQuestionsUtilities(unittest.TestCase):
    """Test utility functions and parsing methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Import here to avoid initialization issues
        from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator
        
        # Create orchestrator with mocked dependencies
        with patch.multiple(
            'researcher.gap_questions.gap_questions',
            QdrantService=Mock(),
            VectorStoreManager=Mock(),
            GeminiLLMClient=Mock(),
            QueryProcessor=Mock(),
            PlanSearchQueryGenerator=Mock(),
            GapSearchQueryGenerator=Mock(),
            VectorSearchQueryGenerator=Mock()
        ):
            self.orchestrator = GapQuestionsOrchestrator()
    
    def test_parse_gaps_response_valid_json(self):
        """Test parsing valid JSON gaps response."""
        response = '["Missing renewable energy data", "Need cost analysis information"]'
        gaps = self.orchestrator._parse_gaps_response(response)
        
        self.assertEqual(len(gaps), 2)
        self.assertIn("Missing renewable energy data", gaps)
        self.assertIn("Need cost analysis information", gaps)
    
    def test_parse_gaps_response_invalid_json(self):
        """Test parsing invalid JSON gracefully."""
        response = 'Not a JSON response'
        gaps = self.orchestrator._parse_gaps_response(response)
        
        self.assertEqual(gaps, [])
    
    def test_parse_gaps_response_empty(self):
        """Test parsing empty response."""
        response = ''
        gaps = self.orchestrator._parse_gaps_response(response)
        
        self.assertEqual(gaps, [])
    
    def test_parse_gaps_response_with_extra_text(self):
        """Test parsing JSON embedded in text."""
        response = '''Here are the gaps I found:
        ["Gap about solar energy", "Gap about wind power"]
        These are the main issues.'''
        gaps = self.orchestrator._parse_gaps_response(response)
        
        self.assertEqual(len(gaps), 2)
        self.assertIn("Gap about solar energy", gaps)
    
    def test_curate_gap_solution_empty(self):
        """Test gap solution curation with no solutions."""
        gap = "Missing data about renewable energy"
        solutions = []
        
        result = self.orchestrator._curate_gap_solution(gap, solutions)
        
        self.assertIn("No information found", result)
        self.assertIn(gap, result)
    
    def test_curate_gap_solution_with_data(self):
        """Test gap solution curation with solutions."""
        gap = "Missing renewable energy data"
        solutions = [
            {"content": "Solar energy has grown by 20% annually..."},
            {"content": "Wind power installations increased..."},
            {"content": "Renewable energy costs have decreased..."}
        ]
        
        result = self.orchestrator._curate_gap_solution(gap, solutions)
        
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        # Should contain parts from multiple solutions
        self.assertTrue(any(sol["content"][:50] in result for sol in solutions))
    
    def test_should_continue_logic(self):
        """Test conditional edge logic."""
        # Should continue
        state = {"should_continue": True}
        result = self.orchestrator._should_continue(state)
        self.assertEqual(result, "continue")
        
        # Should stop
        state = {"should_continue": False}
        result = self.orchestrator._should_continue(state)
        self.assertEqual(result, "stop")
        
        # Missing key (default to stop)
        state = {}
        result = self.orchestrator._should_continue(state)
        self.assertEqual(result, "stop")

class TestQueryGeneratorParsing(unittest.TestCase):
    """Test query generator parsing functions."""
    
    def test_plan_search_query_parsing(self):
        """Test plan search query parsing."""
        from researcher.gap_questions.query_generators.plan_search_query_generator import PlanSearchQueryGenerator
        
        with patch('researcher.gap_questions.query_generators.plan_search_query_generator.GeminiLLMClient'):
            generator = PlanSearchQueryGenerator()
            
            # Test valid JSON response
            response = '["renewable energy trends", "solar power statistics", "wind energy growth"]'
            queries = generator._parse_search_queries(response, max_queries=5)
            
            self.assertEqual(len(queries), 3)
            self.assertIn("renewable energy trends", queries)
    
    def test_plan_search_query_manual_parsing(self):
        """Test manual parsing fallback."""
        from researcher.gap_questions.query_generators.plan_search_query_generator import PlanSearchQueryGenerator
        
        with patch('researcher.gap_questions.query_generators.plan_search_query_generator.GeminiLLMClient'):
            generator = PlanSearchQueryGenerator()
            
            # Test manual parsing
            response = '''1. renewable energy adoption
            2. solar panel efficiency
            3. wind turbine technology'''
            
            queries = generator._manual_parse_queries(response, max_queries=5)
            
            self.assertGreater(len(queries), 0)
            # Should extract clean queries without numbers/bullets
            for query in queries:
                self.assertNotRegex(query, r'^\d+\.')

class TestStateManagement(unittest.TestCase):
    """Test state management and workflow nodes."""
    
    def setUp(self):
        """Set up test fixtures."""
        from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator
        
        with patch.multiple(
            'researcher.gap_questions.gap_questions',
            QdrantService=Mock(),
            VectorStoreManager=Mock(),
            GeminiLLMClient=Mock(),
            QueryProcessor=Mock(),
            PlanSearchQueryGenerator=Mock(),
            GapSearchQueryGenerator=Mock(),
            VectorSearchQueryGenerator=Mock()
        ):
            self.orchestrator = GapQuestionsOrchestrator()
    
    def test_initialize_node(self):
        """Test workflow initialization node."""
        initial_state = {"plan_query": "test query"}
        
        result_state = self.orchestrator._initialize_node(initial_state)
        
        self.assertIn("gap_queue", result_state)
        self.assertIn("processed_gaps", result_state)
        self.assertIn("query_solutions", result_state)
        self.assertEqual(result_state["current_depth"], 0)
        self.assertEqual(result_state["workflow_complete"], False)
        self.assertEqual(result_state["errors"], [])
    
    def test_check_stop_node(self):
        """Test stop condition checking node."""
        state = {
            "current_depth": 0,
            "gap_queue": deque(["gap1", "gap2"])
        }
        
        result_state = self.orchestrator._check_stop_node(state)
        
        # Depth should be incremented
        self.assertEqual(result_state["current_depth"], 1)
        # Should have continue decision
        self.assertIn("should_continue", result_state)
    
    def test_finalize_node(self):
        """Test workflow finalization node."""
        state = {"workflow_complete": False}
        
        result_state = self.orchestrator._finalize_node(state)
        
        self.assertTrue(result_state["workflow_complete"])
    
    def test_generate_solutions_node(self):
        """Test solution generation node."""
        state = {
            "processed_gaps": ["gap1"],
            "gap_queue": deque(["gap2"])
        }
        
        # Mock the generate_query_solution_list method
        with patch.object(self.orchestrator, 'generate_query_solution_list', return_value=[{"gap": "gap1", "solution": "sol1"}]):
            result_state = self.orchestrator._generate_solutions_node(state)
        
        self.assertIn("query_solutions", result_state)
        self.assertEqual(len(result_state["query_solutions"]), 1)

class TestErrorHandling(unittest.TestCase):
    """Test error handling throughout the system."""
    
    def setUp(self):
        """Set up test fixtures."""
        from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator
        
        with patch.multiple(
            'researcher.gap_questions.gap_questions',
            QdrantService=Mock(),
            VectorStoreManager=Mock(),
            GeminiLLMClient=Mock(),
            QueryProcessor=Mock(),
            PlanSearchQueryGenerator=Mock(),
            GapSearchQueryGenerator=Mock(),
            VectorSearchQueryGenerator=Mock()
        ):
            self.orchestrator = GapQuestionsOrchestrator()
    
    def test_analyze_gaps_no_content(self):
        """Test gap analysis with no vector store content."""
        with patch.object(self.orchestrator, '_get_vector_store_content', return_value=""):
            gaps = self.orchestrator.analyze_gaps("test query")
            self.assertEqual(gaps, [])
    
    def test_analyze_gaps_llm_error(self):
        """Test gap analysis with LLM error."""
        with patch.object(self.orchestrator, '_get_vector_store_content', return_value="some content"):
            with patch.object(self.orchestrator.llm_client, 'generate', side_effect=Exception("LLM error")):
                gaps = self.orchestrator.analyze_gaps("test query")
                self.assertEqual(gaps, [])
    
    async def test_process_batch_web_search_error(self):
        """Test batch web search with errors."""
        # Mock query processor to raise exception
        self.orchestrator.query_processor.process_query = AsyncMock(side_effect=Exception("Search error"))
        
        results = await self.orchestrator.process_batch_web_search(["query1", "query2"])
        
        # Should return empty list on error
        self.assertEqual(results, [])
    
    def test_generate_query_solution_list_error(self):
        """Test solution list generation with errors."""
        # Mock vector search generator to raise exception
        self.orchestrator.vector_search_generator.generate_vector_search_queries = Mock(side_effect=Exception("Generator error"))
        
        solutions = self.orchestrator.generate_query_solution_list(["gap1", "gap2"])
        
        # Should return empty list on error
        self.assertEqual(solutions, [])

def run_tests():
    """Run all unit tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestGapQuestionsUtilities))
    suite.addTest(unittest.makeSuite(TestQueryGeneratorParsing))
    suite.addTest(unittest.makeSuite(TestStateManagement))
    suite.addTest(unittest.makeSuite(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == "__main__":
    print("🧪 Running Gap Questions Unit Tests")
    print("="*50)
    
    result = run_tests()
    
    print("\n" + "="*50)
    if result.wasSuccessful():
        print("✅ All unit tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'Unknown error'}")
    
    print("="*50)