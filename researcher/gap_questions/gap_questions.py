import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from collections import deque

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from .llm_client import GeminiLLMClient
from .query_generators.plan_search_query_generator import PlanSearchQueryGenerator
from .query_generators.gap_search_query_generator import GapSearchQueryGenerator
from .query_generators.vector_search_query_generator import VectorSearchQueryGenerator
from .search_query_processor.query_processor import QueryProcessor
from ..vectore_store import VectorStoreManager, QdrantService
from .utils import analyze_gaps, process_batch_web_search, generate_query_solution_list, RAMMonitor

logger = logging.getLogger(__name__)

class GapQuestionsOrchestrator:
    """Orchestration of GapQuestionGenerator: The heart of WORT Research!"""

    def __init__(self, 
                 max_depth: int = 2,
                 max_gaps: int = 2, 
                 max_gap_queries: int = 1,
                 vector_collection_name: str = "gap_questions",
                 max_concurrent_queries: int = 5,
                 max_web_results: int = 5):
        
        # Store configuration
        self.max_depth = max_depth
        self.max_gaps = max_gaps
        self.max_gap_queries = max_gap_queries
        self.max_concurrent_queries = max_concurrent_queries
        self.max_web_results = max_web_results
        
        # Initialize monitoring and metrics
        self.ram_monitor = RAMMonitor()
        self.performance_metrics = {"llm_calls": 0, "total_time": 0}
        
        # Initialize components
        self.llm_client = GeminiLLMClient()
        self.qdrant_service = QdrantService(collection_name=vector_collection_name)
        self.vector_store_manager = VectorStoreManager(vector_store=self.qdrant_service.vector_store)
        
        # Initialize query generators and processor
        self.plan_query_generator = PlanSearchQueryGenerator()
        self.gap_search_generator = GapSearchQueryGenerator()
        self.vector_search_generator = VectorSearchQueryGenerator()
        self.query_processor = QueryProcessor(vector_store_manager=self.vector_store_manager)
        
        # Build workflow
        self.workflow = self.build_workflow()
    
    def check_stop_conditions(self, state: dict) -> bool:
        """Check if workflow should stop."""
        return (state.get("current_depth", 0) >= self.max_depth or 
                len(state.get("gap_queue", [])) == 0)

    def build_workflow(self) -> CompiledStateGraph:
        """Build LangGraph workflow."""
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("generate_web_queries", self._generate_web_queries_node)
        workflow.add_node("process_web_search", self._process_web_search_node)
        workflow.add_node("analyze_gaps", self._analyze_gaps_node)
        workflow.add_node("check_stop", self._check_stop_node)
        workflow.add_node("generate_solutions", self._generate_solutions_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Add edges
        workflow.add_edge(START, "initialize")
        workflow.add_edge("initialize", "generate_web_queries")
        workflow.add_edge("generate_web_queries", "process_web_search")
        workflow.add_edge("process_web_search", "analyze_gaps")
        workflow.add_edge("analyze_gaps", "check_stop")
        workflow.add_conditional_edges(
            "check_stop",
            self._should_continue,
            {"continue": "generate_web_queries", "stop": "generate_solutions"}
        )
        workflow.add_edge("generate_solutions", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()

    async def orchestrator(self, plan_query: str) -> Dict[str, Any]:
        """Main orchestrator function that coordinates the gap analysis workflow."""
        try:
            # Start monitoring
            start_time = time.time()
            self.ram_monitor.start_monitoring()
            
            # Initialize state
            initial_state = {
                "plan_query": plan_query,
                "gap_queue": deque(),
                "processed_gaps": [],
                "query_solutions": [],
                "current_depth": 0,
                "workflow_complete": False,
                "errors": []
            }
            
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Stop monitoring and calculate metrics
            self.ram_monitor.stop_monitoring()
            total_execution_time = time.time() - start_time
            self.performance_metrics["total_time"] = total_execution_time
            ram_stats = self.ram_monitor.get_ram_stats()
            
            # Generate report
            md_file_path = self._generate_md_report(final_state, ram_stats, total_execution_time)
            
            return {
                "success": True,
                "plan_query": plan_query,
                "total_solutions": len(final_state.get("query_solutions", [])),
                "processed_gaps": len(final_state.get("processed_gaps", [])),
                "final_depth": final_state.get("current_depth", 0),
                "md_report": md_file_path,
                "errors": final_state.get("errors", []),
                "performance_metrics": self.performance_metrics.copy(),
                "ram_stats": ram_stats,
                "total_execution_time": total_execution_time
            }
            
        except Exception as e:
            self.ram_monitor.stop_monitoring()
            logger.error(f"Orchestrator failed: {e}")
            return {
                "success": False,
                "plan_query": plan_query,
                "error": str(e),
                "performance_metrics": self.performance_metrics.copy(),
                "ram_stats": self.ram_monitor.get_ram_stats(),
                "total_execution_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    # Helper methods for workflow nodes
    def _initialize_node(self, state: dict) -> dict:
        """Initialize workflow state."""
        state.update({
            "gap_queue": deque(),
            "processed_gaps": [],
            "query_solutions": [],
            "current_depth": 0,
            "workflow_complete": False,
            "errors": []
        })
        return state
    
    async def _generate_web_queries_node(self, state: dict) -> dict:
        """Generate web search queries."""
        try:
            if state["current_depth"] == 0:
                queries = self.plan_query_generator.generate_search_queries(
                    state["plan_query"], max_queries=3
                )
            else:
                queries = []
                if state["gap_queue"]:
                    gap = state["gap_queue"].popleft()
                    queries = self.gap_search_generator.generate_gap_search_queries(gap, max_queries=2)
                    state["processed_gaps"].append(gap)
            
            state["current_web_queries"] = queries
            return state
        except Exception as e:
            state["errors"].append(f"Failed to generate web queries: {e}")
            return state
    
    async def _process_web_search_node(self, state: dict) -> dict:
        """Process web search queries."""
        try:
            queries = state.get("current_web_queries", [])
            results = await process_batch_web_search(queries, self.query_processor) if queries else []
            state["current_web_results"] = results
            return state
        except Exception as e:
            state["errors"].append(f"Failed to process web search: {e}")
            return state
    
    def _analyze_gaps_node(self, state: dict) -> dict:
        """Analyze gaps in current content."""
        try:
            gaps = analyze_gaps(
                query=state["plan_query"],
                llm_client=self.llm_client,
                vector_store_manager=self.vector_store_manager,
                performance_metrics=self.performance_metrics,
                max_gaps=self.max_gaps
            )
            for gap in gaps:
                if gap not in state["processed_gaps"] and gap not in state["gap_queue"]:
                    state["gap_queue"].append(gap)
            return state
        except Exception as e:
            state["errors"].append(f"Failed to analyze gaps: {e}")
            return state
    
    def _check_stop_node(self, state: dict) -> dict:
        """Check stop conditions."""
        state["current_depth"] += 1
        state["should_continue"] = not self.check_stop_conditions(state)
        return state
    
    def _generate_solutions_node(self, state: dict) -> dict:
        """Generate solutions for processed gaps."""
        try:
            all_gaps = state["processed_gaps"] + list(state["gap_queue"])
            state["query_solutions"] = generate_query_solution_list(
                gaps=all_gaps,
                vector_search_generator=self.vector_search_generator,
                query_processor=self.query_processor,
                max_gap_queries=self.max_gap_queries
            )
            return state
        except Exception as e:
            state["errors"].append(f"Failed to generate solutions: {e}")
            return state
    
    def _finalize_node(self, state: dict) -> dict:
        """Finalize workflow."""
        state["workflow_complete"] = True
        return state
    
    def _should_continue(self, state: dict) -> str:
        """Conditional edge function."""
        return "continue" if state.get("should_continue", False) else "stop"
    
    # Graph methods
    def _generate_md_report(self, state: dict, ram_stats: Dict[str, float], total_execution_time: float) -> str:
        """Generate markdown report."""
        try:
            plan_query = state.get("plan_query", "Unknown Query")
            solutions = state.get("query_solutions", [])
            
            md_content = f"""# Gap Questions Research Report

## Original Query
{plan_query}

## Research Summary
- **Total Solutions**: {len(solutions)}
- **Gaps Processed**: {len(state.get("processed_gaps", []))}
- **Final Depth**: {state.get("current_depth", 0)}
- **Execution Time**: {total_execution_time:.2f}s

## Performance Metrics
- **LLM Calls**: {self.performance_metrics.get("llm_calls", 0)}
- **Average RAM**: {ram_stats.get("average", 0):.1f} MB
- **Peak RAM**: {ram_stats.get("max", 0):.1f} MB
- **Max Web Results**: {self.max_web_results}

## Gap Analysis & Solutions
"""
            
            for i, solution in enumerate(solutions, 1):
                md_content += f"""### Gap {i}: {solution.get('gap', 'Unknown Gap')}
**Solution:** {solution.get('solution', 'No solution available')}
**Sources**: {solution.get('source_count', 0)} documents

---
"""
            
            # Add errors if any
            errors = state.get("errors", [])
            if errors:
                md_content += f"\n## Errors\n"
                for error in errors:
                    md_content += f"- {error}\n"
            
            # Write to file
            filename = f"gap_questions_report_{hash(plan_query) % 10000}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            return filename
            
        except Exception as e:
            logger.error(f"Failed to generate MD report: {e}")
            return ""
    
    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, 'ram_monitor'):
                self.ram_monitor.stop_monitoring()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

async def test_gap_questions_functionality():
    """Test the complete gap questions orchestration with real-world usage."""
    print("🧪 Testing Gap Questions Full Orchestration")
    print("="*50)
    
    try:
        # Step 1: Initialize orchestrator
        print("\n📋 Step 1: Initializing Gap Questions Orchestrator")
        orchestrator = GapQuestionsOrchestrator(
            max_depth=4,
            max_gaps=2,
            max_gap_queries=1,
            max_concurrent_queries=5,
            max_web_results=1,
            vector_collection_name="test_gap_functionality"
        )
        print("✅ Orchestrator initialized successfully")
        
        # Step 2: Execute complete orchestration with a single call
        plan_query = "Future trends in renewable energy technology and their impact on global energy markets"
        print(f"\n📋 Step 2: Executing Full Orchestration")
        print(f"Query: {plan_query}")
        print("\n🚀 Running complete gap analysis workflow...")
        
        # This single line executes the entire workflow
        result = await orchestrator.orchestrator(plan_query)
        
        # Step 3: Display results
        print(f"\n📊 Results Summary:")
        print(f"   Status: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"   Total Solutions: {result.get('total_solutions', 0)}")
        print(f"   Processed Gaps: {result.get('processed_gaps', 0)}")
        print(f"   Final Depth: {result.get('final_depth', 0)}")
        print(f"   Execution Time: {result.get('total_execution_time', 0):.2f}s")
        
        # Performance metrics
        if 'performance_metrics' in result:
            metrics = result['performance_metrics']
            print(f"\n📈 Performance Metrics:")
            print(f"   LLM Calls: {metrics.get('llm_calls', 0)}")
            print(f"   Vector Searches: {metrics.get('vector_searches', 0)}")
            print(f"   Web Searches: {metrics.get('web_searches', 0)}")
        
        # RAM statistics
        if 'ram_stats' in result:
            ram = result['ram_stats']
            print(f"\n💾 RAM Usage:")
            print(f"   Average: {ram.get('average', 0):.2f} MB")
            print(f"   Peak: {ram.get('max', 0):.2f} MB")
            print(f"   Current: {ram.get('current', 0):.2f} MB")
        
        # Report file
        if result.get('md_report'):
            print(f"\n📄 Detailed Report: {result['md_report']}")
        
        # Errors (if any)
        if result.get('errors'):
            print(f"\n⚠️  Errors encountered:")
            for error in result['errors']:
                print(f"   - {error}")
        
        print(f"\n✅ Real-world orchestration test completed!")
        print(f"   This demonstrates how to use the system with just one line:")
        print(f"   result = await orchestrator.orchestrator('{plan_query}')")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Gap questions functionality test failed", exc_info=True)
        return False

if __name__ == "__main__":
    import asyncio
    import os
    
    # Set up test environment
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️ Warning: No GOOGLE_API_KEY found - setting test key")
        os.environ['GOOGLE_API_KEY'] = 'test_key_for_functionality_test'
    
    print("🚀 Gap Questions Functionality Test")
    print("Testing core functionality step by step")
    print()
    
    # Run the functionality test
    success = asyncio.run(test_gap_questions_functionality())
    
    if success:
        print("\n🎉 All functionality tests passed!")
    else:
        print("\n❌ Some functionality tests failed!")
    
    # Exit with appropriate code
    exit(0 if success else 1)
