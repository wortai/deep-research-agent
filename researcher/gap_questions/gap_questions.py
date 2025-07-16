import asyncio
import logging
import json
import time
import psutil
import threading
from typing import List, Dict, Any, Optional
from collections import deque

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from .llm_client import GeminiLLMClient
from .prompts import create_gap_analysis_prompt
from .query_generators.plan_search_query_generator import PlanSearchQueryGenerator
from .query_generators.gap_search_query_generator import GapSearchQueryGenerator
from .query_generators.vector_search_query_generator import VectorSearchQueryGenerator
from .search_query_processor.query_processor import QueryProcessor
from ..vectore_store import VectorStoreManager, QdrantService

logger = logging.getLogger(__name__)

class RAMMonitor:
    """Simplified RAM monitoring."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.ram_samples = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start RAM monitoring."""
        self.monitoring = True
        self.ram_samples = []
        self.monitor_thread = threading.Thread(target=self._monitor_ram)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop RAM monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_ram(self):
        """Monitor RAM usage."""
        while self.monitoring:
            try:
                memory_info = self.process.memory_info()
                ram_mb = memory_info.rss / (1024 * 1024)
                self.ram_samples.append(ram_mb)
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"RAM monitoring error: {e}")
                break
    
    def get_ram_stats(self) -> Dict[str, float]:
        """Get RAM statistics."""
        if not self.ram_samples:
            return {"average": 0, "max": 0, "current": 0}
        
        current_memory = self.process.memory_info().rss / (1024 * 1024)
        return {
            "average": sum(self.ram_samples) / len(self.ram_samples),
            "max": max(self.ram_samples),
            "current": current_memory
        }

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
    
    def analyze_gaps(self, query: str) -> List[str]:
        """Analyze gaps in content to identify missing information."""
        try:
            # Get content from vector store
            vector_content = self._get_vector_store_content(query)
            if not vector_content:
                return []
            
            # Generate gaps using LLM
            prompt = create_gap_analysis_prompt(query, vector_content)
            response = self.llm_client.generate(prompt, context="gap_analysis", model_type="analysis")
            self.performance_metrics["llm_calls"] += 1
            
            # Parse result
            gaps = self._parse_gaps_response(response)[:self.max_gaps]
            
            return gaps
            
        except Exception as e:
            logger.error(f"Failed to analyze gaps: {e}")
            return []
    
    async def process_batch_web_search(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Process web search queries using the new simplified logic."""
        try:
            logger.info(f"Processing {len(queries)} web search queries in batch")
            
            # Use the new process_multiple_queries method
            # This will collect 1 result per query by default and store all in vector DB in one shot
            all_results = await self.query_processor.process_multiple_queries(queries)
            
            logger.info(f"Batch processing completed. Collected {len(all_results)} total results")
            return all_results
            
        except Exception as e:
            logger.error(f"Batch web search processing failed: {e}")
            return []
    
    def check_stop_conditions(self, state: dict) -> bool:
        """Check if workflow should stop."""
        return (state.get("current_depth", 0) >= self.max_depth or 
                len(state.get("gap_queue", [])) == 0)
    
    def generate_query_solution_list(self, gaps: List[str]) -> List[Dict[str, Any]]:
        """Generate solutions for identified gaps using simplified search."""
        try:
            final_solutions = []
            
            logger.info(f"Processing {len(gaps)} gaps")
            
            # Collect all vector queries
            all_vector_queries = []
            gap_to_queries = {}
            
            for gap in gaps:
                vector_queries = self.vector_search_generator.generate_vector_search_queries(
                    gap, max_queries=self.max_gap_queries
                )
                gap_to_queries[gap] = vector_queries
                all_vector_queries.extend(vector_queries)
            
            # Search all queries using simplified search_only method
            if all_vector_queries:
                logger.info(f"Searching {len(all_vector_queries)} vector queries")
                all_search_results = self.query_processor.search_only(all_vector_queries, k=3)
                
                # Group results by gap (simplified approach)
                for gap in gaps:
                    gap_queries = gap_to_queries.get(gap, [])
                    
                    # For simplicity, take a portion of results for each gap
                    # This is a simple distribution - could be made more sophisticated
                    results_per_gap = len(all_search_results) // len(gaps) if gaps else 0
                    gap_start_idx = gaps.index(gap) * results_per_gap
                    gap_end_idx = gap_start_idx + results_per_gap
                    
                    gap_solutions = all_search_results[gap_start_idx:gap_end_idx] if all_search_results else []
                    
                    # Create solution
                    solution_data = {
                        "gap": gap,
                        "vector_queries": gap_queries,
                        "solution": self._curate_gap_solution(gap, gap_solutions),
                        "source_count": len(gap_solutions)
                    }
                    
                    final_solutions.append(solution_data)
            
            logger.info(f"Processing completed for {len(gaps)} gaps")
            
            return final_solutions
            
        except Exception as e:
            logger.error(f"Failed to generate query solution list: {e}")
            return []

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
            results = await self.process_batch_web_search(queries) if queries else []
            state["current_web_results"] = results
            return state
        except Exception as e:
            state["errors"].append(f"Failed to process web search: {e}")
            return state
    
    def _analyze_gaps_node(self, state: dict) -> dict:
        """Analyze gaps in current content."""
        try:
            gaps = self.analyze_gaps(state["plan_query"])
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
            state["query_solutions"] = self.generate_query_solution_list(all_gaps)
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
    
    # Utility methods
    
    def _get_vector_store_content(self, query: str, k: int = 10) -> str:
        """Get content from vector store for gap analysis."""
        try:
            results = self.vector_store_manager.similarity_search(query, k=k)
            content = "\n\n".join([doc.page_content[:500] for doc in results])
            return content
        except Exception as e:
            logger.error(f"Failed to get vector store content: {e}")
            return ""
    
    def _parse_gaps_response(self, response: str) -> List[str]:
        """Parse gaps from LLM response."""
        try:
            response_clean = response.strip()
            start_idx = response_clean.find('[')
            end_idx = response_clean.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                return []
            
            json_str = response_clean[start_idx:end_idx]
            gaps = json.loads(json_str)
            
            if isinstance(gaps, list):
                return [gap.strip() for gap in gaps if isinstance(gap, str) and gap.strip()]
            return []
            
        except Exception as e:
            logger.error(f"Failed to parse gaps response: {e}")
            return []
    
    def _curate_gap_solution(self, gap: str, solutions: List[Dict[str, Any]]) -> str:
        """Curate a solution for a specific gap."""
        if not solutions:
            return f"No information found to address: {gap}"
        
        # Combine solutions into a coherent response
        content_parts = []
        for sol in solutions[:3]:  # Use top 3 solutions
            if sol.get("content"):
                content_parts.append(sol["content"][:200])
        
        return " ".join(content_parts) if content_parts else f"Limited information available for: {gap}"
    
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
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        return {
            "performance_metrics": self.performance_metrics.copy(),
            "ram_stats": self.ram_monitor.get_ram_stats(),
            "configuration": {
                "max_concurrent_queries": self.max_concurrent_queries,
                "max_depth": self.max_depth,
                "max_gaps": self.max_gaps,
                "max_gap_queries": self.max_gap_queries,
                "max_web_results": self.max_web_results
            }
        }
    
    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        self.performance_metrics = {"llm_calls": 0, "total_time": 0}
    
    def log_performance_summary(self) -> None:
        """Log performance summary."""
        summary = self.get_performance_summary()
        logger.info("=== PERFORMANCE SUMMARY ===")
        logger.info(f"Total time: {summary['performance_metrics']['total_time']:.2f}s")
        logger.info(f"LLM calls: {summary['performance_metrics']['llm_calls']}")
        logger.info(f"Average RAM: {summary['ram_stats']['average']:.1f} MB")
        logger.info("=== END SUMMARY ===")
    
    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, 'ram_monitor'):
                self.ram_monitor.stop_monitoring()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

async def test_gap_questions_functionality():
    """Test the core gap questions functionality step by step."""
    print("🧪 Testing Gap Questions Core Functionality")
    print("="*50)
    
    try:
        # Step 1: Initialize orchestrator
        print("\n📋 Step 1: Initializing Gap Questions Orchestrator")
        orchestrator = GapQuestionsOrchestrator(
            max_depth=1,
            max_gaps=2,
            max_gap_queries=1,
            max_concurrent_queries=3,
            max_web_results=5,
            vector_collection_name="test_gap_functionality"
        )
        print("✅ Orchestrator initialized successfully")
        
        # Step 2: Test plan query
        plan_query = "Future trends in renewable energy technology"
        print(f"\n📋 Step 2: Plan Query")
        print(f"Query: {plan_query}")
        
        # Step 3: Generate web search queries
        print(f"\n📋 Step 3: Generating Web Search Queries")
        web_search_queries = orchestrator.plan_query_generator.generate_search_queries(
            plan_query, max_queries=3
        )
        print(f"Generated {len(web_search_queries)} web search queries:")
        for i, query in enumerate(web_search_queries, 1):
            print(f"   {i}. {query}")
        
        # Step 4: Use search_query_processor to get data
        print(f"\n📋 Step 4: Processing Web Search Queries")
        all_results = await orchestrator.process_batch_web_search(web_search_queries)
        print(f"✅ Collected {len(all_results)} results from web search")
        
        # Show some sample results
        if all_results:
            print("Sample results:")
            for i, result in enumerate(all_results[:3], 1):
                source = result.get('source', 'N/A')
                content_preview = result.get('content', '')[:100] + "..."
                print(f"   {i}. Source: {source}")
                print(f"      Content: {content_preview}")
        
        # Step 5: Analyze gaps
        print(f"\n📋 Step 5: Analyzing Gaps")
        gaps = orchestrator.analyze_gaps(plan_query)
        print(f"✅ Identified {len(gaps)} gaps:")
        
        if gaps:
            for i, gap in enumerate(gaps, 1):
                print(f"   {i}. {gap}")
        else:
            print("   No gaps identified")
        
        # Summary
        print(f"\n✅ Test completed successfully!")
        print(f"   Web Search Queries: {len(web_search_queries)}")
        print(f"   Web Results: {len(all_results)}")
        print(f"   Identified Gaps: {len(gaps)}")
        
        return True
        
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
