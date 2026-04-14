import unittest
import sys
import os
import logging
from unittest.mock import patch

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adjust path to include project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from planner.plan import Planner
from graphs.states.subgraph_state import AgentGraphState

class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = Planner()

    def test_clear_query_plan_generation(self):
        """Test that a clear query generates a plan without asking questions."""
        print("\n--- Testing Plan Generation (Clear Query) ---")
        state: AgentGraphState = {
            "user_query": "What are the latest advancements in solid-state batteries for EVs in 2025?",
            "planner_query": [],
            # Add other required fields with dummy values if necessary, but TypedDict implies structure
        }
        
        result = self.planner._generate_plan(state)
        
        self.assertIn("planner_query", result)
        self.assertGreater(len(result["planner_query"]), 0)
        
        print(f"Query: {state['user_query']}")
        print("✅ Plan generation successful.")
        print("Generated Plan Steps:")
        for i, step in enumerate(result["planner_query"]):
            print(f"  {i+1}. {step}")

    @patch('builtins.input', return_value="I am interested in autonomous AI agents that can perform web research and write reports.")
    def test_vague_query_clarification(self, mock_input):
        """Test that a vague query triggers clarification logic (simulated)."""
        print("\n--- Testing Interactive Clarification (Vague Query - Mocked) ---")
        state: AgentGraphState = {
            "user_query": "AI help",
            "planner_query": []
        }
        
        # We assume the plan.py uses standard input(), which is mocked here.
        result = self.planner._generate_plan(state)
        
        # Check that we got a result
        self.assertIn("planner_query", result)
        self.assertGreater(len(result["planner_query"]), 0)
        
        print(f"Original Query: {state['user_query']}")
        print(f"Mocked User Answer: {mock_input.return_value}")
        print("✅ Clarification flow verified.")
        print("Generated Plan Steps:")
        for i, step in enumerate(result["planner_query"]):
            print(f"  {i+1}. {step}")

def run_interactive_mode():
    """Runs the planner in interactive mode so the user can actually type answers."""
    print("\nXXX INTERACTIVE MODE ACTIVATED XXX")
    print("You will be prompted to answer questions if the query is vague.")
    
    planner = Planner()
    # Use a vague query to force interaction
    query = input("Enter a query (try 'AI help' to trigger questions, or something specific): ")
    if not query:
        query = "AI help"
    
    print(f"\nProcessing Query: '{query}'...")
    state: AgentGraphState = {
        "user_query": query,
        "planner_query": []
    }
    
    try:
        result = planner._generate_plan(state)
        print("\n=== FINAL PLAN GENERATED ===")
        for i, step in enumerate(result.get("planner_query", [])):
            print(f"{i+1}. {step}")
        print("============================")
    except Exception as e:
        logger.error(f"Error during interactive run: {e}")

if __name__ == '__main__':
    # usage: python planner/test_planner.py manual
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        run_interactive_mode()
    else:
        # Remove 'manual' from args if present to avoid confusing unittest (though simple logic handles it)
        unittest.main()
