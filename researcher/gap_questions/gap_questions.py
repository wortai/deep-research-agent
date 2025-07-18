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
from .utils import analyze_gaps, process_batch_web_search
from .prompts import create_sections_from_research_prompt
from states import ResearchReviewData

logger = logging.getLogger(__name__)

class GapQuestions:
    """Orchestration of GapQuestionGenerator: The heart of WORT Research!"""

    def __init__(self, 
                 max_depth: int = 2,
                 max_gaps: int = 2, 
                 max_gap_queries: int = 1,
                 vector_collection_name: str = "gap_questions",
                 max_web_results: int = 2):
        
        # Store configuration
        self.max_depth = max_depth
        self.max_gaps = max_gaps
        self.max_gap_queries = max_gap_queries
        self.max_web_results = max_web_results
        
        # Initialize performance metrics
        self.performance_metrics = {"llm_calls": 0, "total_time": 0}
        
        # Initialize class state variables
        self.current_level_gaps = []
        self.next_level_gaps = []
        self.processed_gaps = []
        self.query_sections = []
        self.current_depth = 0
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

    def build_workflow(self) -> CompiledStateGraph:
        """Build LangGraph workflow."""
        workflow = StateGraph(ResearchReviewData)
        
        # Add nodes
        workflow.add_node("process_web_search", self._process_web_search_node)
        workflow.add_node("analyze_gaps", self._analyze_gaps_node)
        workflow.add_node("check_stop", self._check_stop_node)
        workflow.add_node("generate_sections", self._generate_sections_node)
        
        # Add edges
        workflow.add_edge(START, "process_web_search")
        workflow.add_edge("process_web_search", "analyze_gaps")
        workflow.add_edge("analyze_gaps", "check_stop")
        workflow.add_conditional_edges(
            "check_stop",
            self._should_continue,
            {"continue": "process_web_search", "stop": "generate_sections"}
        )
        workflow.add_edge("generate_sections", END)
        
        return workflow.compile()
    
    @classmethod
    async def run(cls, 
                  query: str,
                  max_depth: int = 2,
                  max_gaps: int = 2,
                  max_gap_queries: int = 1,
                  vector_collection_name: str = "gap_questions",
                  max_web_results: int = 5) -> Dict[str, Any]:
        """Simple run method that initializes the orchestrator and executes the complete gap analysis workflow."""
        # Initialize the orchestrator with provided parameters
        orchestrator = cls(
            max_depth=max_depth,
            max_gaps=max_gaps,
            max_gap_queries=max_gap_queries,
            vector_collection_name=vector_collection_name,
            max_web_results=max_web_results
        )
        
        # Run the orchestrator
        return await orchestrator.orchestrator(query)
    
    async def orchestrator(self, plan_query: str) -> Dict[str, Any]:
        """Main orchestrator function that coordinates the gap analysis workflow."""
        try:
            # Start timing
            start_time = time.time()
            
            # Initialize state with ResearchReviewData structure
            initial_state = ResearchReviewData(
                query=plan_query,
                raw_research_results=[],
                review_feedback=[],
                section={"section_heading": "", "section_content": "", "section_urls": []},
                report_sections=[]
            )
            
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state, {"recursion_limit": 100})
            
            # Calculate metrics
            total_execution_time = time.time() - start_time
            self.performance_metrics["total_time"] = total_execution_time
            
            # Generate report
            md_file_path = self._generate_md_report(final_state, total_execution_time)
            
            return {
                "success": True,
                "plan_query": plan_query,
                "total_sections": len(self.query_sections),
                "processed_gaps": len(self.processed_gaps),
                "final_depth": self.current_depth,
                "md_report": md_file_path,
                "errors": self.errors,
                "performance_metrics": self.performance_metrics.copy(),
                "total_execution_time": total_execution_time
            }
            
        except Exception as e:
            logger.error(f"Orchestrator failed: {e}")
            return {
                "success": False,
                "plan_query": plan_query,
                "error": str(e),
                "performance_metrics": self.performance_metrics.copy(),
                "total_execution_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    # Helper methods for workflow nodes
    
    async def _process_web_search_node(self, state: ResearchReviewData) -> ResearchReviewData:
        """Generate web search queries and process them."""
        try:
            # Generate web search queries
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
            
            # Process web search queries
            results = await process_batch_web_search(self.current_web_queries, self.query_processor) if self.current_web_queries else []
            self.current_web_results = results
            
            # Results processed but not stored in raw_research_results
            
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
            gaps, research_results = analyze_gaps(
                query=analysis_query,
                llm_client=self.llm_client,
                vector_store_manager=self.vector_store_manager,
                performance_metrics=self.performance_metrics,
                max_gaps=self.max_gaps
            )
            
            # Add research results to raw_research_results state
            for vector_query, document, urls in research_results:
                state['raw_research_results'].append((vector_query, document, urls))
            
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
    
    def _should_continue(self, state: ResearchReviewData) -> str:
        """Conditional edge function."""
        return "continue" if self.should_continue else "stop"
    
    def _generate_sections_node(self, state: ResearchReviewData) -> ResearchReviewData:
        """Generate sections from raw_research_results using LLM."""
        try:
            raw_research_results = state.get('raw_research_results', [])
            
            if not raw_research_results:
                logger.info("No raw research results available for section generation")
                state['report_sections'] = []
                return state
            
            # Use LLM to create sections from raw research results
            prompt = create_sections_from_research_prompt(raw_research_results)
            response = self.llm_client.generate(prompt, context="section_generation", model_type="analysis")
            self.performance_metrics["llm_calls"] += 1
            
            # Parse the JSON response
            sections = self._parse_sections_response(response)
            
            # Update state with generated sections
            state['report_sections'] = sections
            logger.info(f"Generated {len(sections)} sections from {len(raw_research_results)} research results")
            
            return state
        except Exception as e:
            self.errors.append(f"Failed to generate sections: {e}")
            state['report_sections'] = []
            return state
    
    def _parse_sections_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response to extract sections."""
        try:
            import json
            
            # Find JSON array in response
            response_clean = response.strip()
            start_idx = response_clean.find('[')
            end_idx = response_clean.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON array found in sections response")
                return []
            
            json_str = response_clean[start_idx:end_idx]
            sections = json.loads(json_str)
            
            if isinstance(sections, list):
                # Validate and clean sections
                cleaned_sections = []
                for section in sections:
                    if isinstance(section, dict) and all(key in section for key in ['section_heading', 'section_content', 'section_urls']):
                        cleaned_section = {
                            'section_heading': section['section_heading'].strip(),
                            'section_content': section['section_content'].strip(),
                            'section_urls': section.get('section_urls', [])
                        }
                        cleaned_sections.append(cleaned_section)
                
                return cleaned_sections
            else:
                logger.warning("Response not in expected list format")
                return []
                
        except json.JSONDecodeError:
            logger.error("Failed to parse sections response as JSON")
            return []
        except Exception as e:
            logger.error(f"Error parsing sections response: {e}")
            return []
    
    # Graph methods
    def _generate_md_report(self, state: ResearchReviewData, total_execution_time: float) -> str:
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
        

async def test_gap_questions_functionality():
    """Test the complete gap questions orchestration with real-world usage."""
    print("🧪 Testing Gap Questions Full Orchestration")
    print("="*50)
    
    try:
        # Step 1: Execute complete orchestration with a single call
        plan_query = "Check what have been the most optimal techniques while fine-tuning a language model for chatbots"
        print(f"\n📋 Step 1: Executing Full Orchestration")
        print(f"Query: {plan_query}")
        print("\n🚀 Running complete gap analysis workflow...")
        
        # This single line initializes and executes the entire workflow
        result = await GapQuestions.run(
            query=plan_query,
            max_depth=2,
            max_gaps=2,
            max_gap_queries=1,
            max_web_results=1,
            vector_collection_name="test_gap_functionality"
        )
        
        # Step 2: Display results
        print(f"\n📊 Results Summary:")
        print(f"   Status: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"   Total Solutions: {result.get('total_section', 0)}")
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
        print(f"   result = await GapQuestions.run('{plan_query}')")
        
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
