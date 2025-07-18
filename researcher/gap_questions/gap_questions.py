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
from .utils import analyze_gaps, process_batch_web_search, generate_query_solution_list, RAMMonitor, generate_section_heading
from states import ResearchReviewData

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
        
        # Initialize class state variables (previously in workflow state)
        self.current_level_gaps = []
        self.next_level_gaps = []
        self.processed_gaps = []
        self.query_solutions = []
        self.current_depth = 0
        self.workflow_complete = False
        self.errors = []
        self.current_processing_query = None
        self.current_web_queries = []
        self.current_web_results = []
        self.should_continue = True
        
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
    
    def check_stop_conditions(self) -> bool:
        """Check if workflow should stop using level-based logic."""
        has_gaps_to_process = (len(self.current_level_gaps) > 0 or len(self.next_level_gaps) > 0)
        return (self.current_depth >= self.max_depth or not has_gaps_to_process)

    def build_workflow(self) -> CompiledStateGraph:
        """Build LangGraph workflow."""
        workflow = StateGraph(ResearchReviewData)
        
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
    
    def _get_research_data_for_gap(self, gap: str, raw_research_results: List[tuple]) -> List[Dict[str, Any]]:
        """Extract research data relevant to a specific gap from raw_research_results."""
        try:
            # Convert raw_research_results tuples to dictionary format
            research_data = []
            for content, url in raw_research_results:
                # Simple relevance check - if gap keywords appear in content
                gap_keywords = gap.lower().split()[:3]  # Use first 3 words of gap
                content_lower = content.lower()
                
                # Check if any gap keywords appear in content
                if any(keyword in content_lower for keyword in gap_keywords if len(keyword) > 2):
                    research_data.append({
                        'content': content,
                        'url': url
                    })
            
            # If no specific matches, return some general data
            if not research_data and raw_research_results:
                # Take first few results as fallback
                for content, url in raw_research_results[:3]:
                    research_data.append({
                        'content': content,
                        'url': url
                    })
            
            logger.info(f"Found {len(research_data)} relevant data sources for gap: {gap[:50]}...")
            return research_data
            
        except Exception as e:
            logger.error(f"Failed to get research data for gap: {e}")
            return []

    async def orchestrator(self, plan_query: str) -> Dict[str, Any]:
        """Main orchestrator function that coordinates the gap analysis workflow."""
        try:
            # Start monitoring
            start_time = time.time()
            self.ram_monitor.start_monitoring()
            
            # Initialize state with ResearchReviewData structure
            initial_state = ResearchReviewData(
                query=plan_query,
                raw_research_results=[],
                review_feedback=[],
                section={"section_heading": "", "section_content": "", "section_urls": []},
                report_sections=[]
            )
            
            # Reset class state variables
            self.current_level_gaps = []
            self.next_level_gaps = []
            self.processed_gaps = []
            self.query_solutions = []
            self.current_depth = 0
            self.workflow_complete = False
            self.errors = []
            self.current_processing_query = None
            self.current_web_queries = []
            self.current_web_results = []
            self.should_continue = True
            
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state, {"recursion_limit": 100})
            
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
                "total_solutions": len(self.query_solutions),
                "processed_gaps": len(self.processed_gaps),
                "final_depth": self.current_depth,
                "md_report": md_file_path,
                "errors": self.errors,
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
    def _initialize_node(self, state: ResearchReviewData) -> ResearchReviewData:
        """Initialize workflow state."""
        # Class variables are already initialized in __init__
        logger.info(f"Initializing workflow for query: {state['query'][:50]}...")
        return state
    
    async def _generate_web_queries_node(self, state: ResearchReviewData) -> ResearchReviewData:
        """Generate web search queries."""
        try:
            if self.current_depth == 0:
                # At depth 0, process the initial plan query
                queries = self.plan_query_generator.generate_search_queries(
                    state["query"], max_queries=3
                )
                self.current_processing_query = state["query"]
                logger.info(f"Generating web queries for plan query at depth 0")
            else:
                # At depth > 0, process gaps from current level
                queries = []
                if self.current_level_gaps:
                    gap = self.current_level_gaps.pop(0)  # Take first gap from current level
                    queries = self.gap_search_generator.generate_gap_search_queries(gap, max_queries=2)
                    self.current_processing_query = gap
                    logger.info(f"Generating web queries for gap at depth {self.current_depth}: {gap[:50]}...")
            
            self.current_web_queries = queries
            return state
        except Exception as e:
            self.errors.append(f"Failed to generate web queries: {e}")
            return state
    
    async def _process_web_search_node(self, state: ResearchReviewData) -> ResearchReviewData:
        """Process web search queries."""
        try:
            results = await process_batch_web_search(self.current_web_queries, self.query_processor) if self.current_web_queries else []
            self.current_web_results = results
            
            # Add results to raw_research_results in the format (gap_query_content, url)
            for result in results:
                content = result.get('content', '')
                url = result.get('source', '') or result.get('url', '')
                if content and url:
                    state['raw_research_results'].append((content, url))
            
            return state
        except Exception as e:
            self.errors.append(f"Failed to process web search: {e}")
            return state
    
    def _analyze_gaps_node(self, state: ResearchReviewData) -> ResearchReviewData:
        """Analyze gaps in current content using level-based processing."""
        try:
            # Get the query that was just processed
            analysis_query = self.current_processing_query or state["query"]
            
            logger.info(f"Analyzing gaps at depth {self.current_depth} for query: {analysis_query[:50]}...")
            
            # Analyze gaps for the current query
            gaps = analyze_gaps(
                query=analysis_query,
                llm_client=self.llm_client,
                vector_store_manager=self.vector_store_manager,
                performance_metrics=self.performance_metrics,
                max_gaps=self.max_gaps
            )
            
            # Mark the current query as processed
            if analysis_query not in self.processed_gaps:
                self.processed_gaps.append(analysis_query)
                logger.info(f"Marked query as processed: {analysis_query[:50]}...")
            
            # Add discovered gaps to next level (avoid duplicates)
            for gap in gaps:
                if (gap not in self.processed_gaps and 
                    gap not in self.current_level_gaps and 
                    gap not in self.next_level_gaps):
                    self.next_level_gaps.append(gap)
                    logger.info(f"Added gap to next level: {gap[:50]}...")
            
            # Check if current level is complete
            if not self.current_level_gaps:
                # Current level is complete, move to next level
                if self.next_level_gaps:
                    logger.info(f"Level {self.current_depth} complete. Moving to level {self.current_depth + 1} with {len(self.next_level_gaps)} gaps")
                    self.current_level_gaps = self.next_level_gaps.copy()
                    self.next_level_gaps = []
                    self.current_depth += 1
                else:
                    logger.info(f"No more gaps to process. Workflow should stop.")
            
            return state
        except Exception as e:
            self.errors.append(f"Failed to analyze gaps: {e}")
            return state
    
    def _check_stop_node(self, state: ResearchReviewData) -> ResearchReviewData:
        """Check stop conditions using level-based logic."""
        # Check if we should continue based on:
        # 1. Current depth hasn't exceeded max_depth
        # 2. There are still gaps to process (either in current level or next level)
        has_gaps_to_process = (len(self.current_level_gaps) > 0 or len(self.next_level_gaps) > 0)
        
        self.should_continue = (self.current_depth < self.max_depth and has_gaps_to_process)
        
        logger.info(f"Check stop: depth={self.current_depth}, max_depth={self.max_depth}, "
                   f"current_level_gaps={len(self.current_level_gaps)}, "
                   f"next_level_gaps={len(self.next_level_gaps)}, continue={self.should_continue}")
        
        return state
    
    def _generate_solutions_node(self, state: ResearchReviewData) -> ResearchReviewData:
        """Generate solutions for processed gaps and create report sections."""
        try:
            all_gaps = self.processed_gaps + self.current_level_gaps + self.next_level_gaps
            self.query_solutions = generate_query_solution_list(
                gaps=all_gaps,
                vector_search_generator=self.vector_search_generator,
                query_processor=self.query_processor,
                max_gap_queries=self.max_gap_queries
            )
            
            # Create sections for each processed gap
            sections = []
            for gap in self.processed_gaps:
                # Get relevant research data for this gap from raw_research_results
                gap_research_data = self._get_research_data_for_gap(gap, state['raw_research_results'])
                
                if gap_research_data:
                    # Generate section heading using LLM
                    section_heading = generate_section_heading(
                        gap_query=gap,
                        llm_client=self.llm_client,
                        performance_metrics=self.performance_metrics
                    )
                    
                    # Use the research data content directly (already summarized during vector retrieval)
                    section_content = "\n\n".join([data.get('content', '')[:400] for data in gap_research_data[:3]])
                    
                    # Extract URLs from research data
                    section_urls = [data.get('url', '') for data in gap_research_data if data.get('url')]
                    
                    # Create section
                    section = {
                        "section_heading": section_heading,
                        "section_content": section_content,
                        "section_urls": section_urls
                    }
                    
                    sections.append(section)
                    logger.info(f"Created section: {section_heading} with {len(section_urls)} sources")
            
            # Update state with sections
            state['report_sections'] = sections
            logger.info(f"Generated {len(sections)} report sections")
            
            return state
        except Exception as e:
            self.errors.append(f"Failed to generate solutions: {e}")
            return state
    
    def _finalize_node(self, state: ResearchReviewData) -> ResearchReviewData:
        """Finalize workflow."""
        self.workflow_complete = True
        return state
    
    def _should_continue(self, state: ResearchReviewData) -> str:
        """Conditional edge function."""
        return "continue" if self.should_continue else "stop"
    
    # Graph methods
    def _generate_md_report(self, state: ResearchReviewData, ram_stats: Dict[str, float], total_execution_time: float) -> str:
        """Generate markdown report."""
        try:
            plan_query = state["query"]
            sections = state.get("report_sections", [])
            
            md_content = f"""# Gap Questions Research Report

## Original Query
{plan_query}

## Research Summary
- **Total Sections**: {len(sections)}
- **Gaps Processed**: {len(self.processed_gaps)}
- **Final Depth**: {self.current_depth}
- **Execution Time**: {total_execution_time:.2f}s

## Performance Metrics
- **LLM Calls**: {self.performance_metrics.get("llm_calls", 0)}
- **Average RAM**: {ram_stats.get("average", 0):.1f} MB
- **Peak RAM**: {ram_stats.get("max", 0):.1f} MB
- **Max Web Results**: {self.max_web_results}

## Research Sections
"""
            
            for i, section in enumerate(sections, 1):
                section_heading = section.get('section_heading', f'Section {i}')
                section_content = section.get('section_content', 'No content available')
                section_urls = section.get('section_urls', [])
                
                md_content += f"""## {section_heading}

{section_content}

### Sources
"""
                
                if section_urls:
                    for j, url in enumerate(section_urls, 1):
                        md_content += f"{j}. [{url}]({url})\n"
                else:
                    md_content += "No sources available\n"
                
                md_content += "\n---\n\n"
            
            # Add errors if any
            if self.errors:
                md_content += f"\n## Errors\n"
                for error in self.errors:
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
            max_depth=2,
            max_gaps=2,
            max_gap_queries=1,
            max_concurrent_queries=5,
            max_web_results=1,
            vector_collection_name="test_gap_functionality"
        )
        print("✅ Orchestrator initialized successfully")
        
        # Step 2: Execute complete orchestration with a single call
        plan_query = "Check what have been the most optimal techniques while fine-tuning a language model for chatbots"
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
