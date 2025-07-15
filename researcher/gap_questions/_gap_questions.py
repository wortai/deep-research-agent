# Main Orchestrator for GapQuestionGenerator

# 1. Use <step> of plan to generate search queries for web (constraint: maximum queries) ✅ + UPDATE plan_query
# 2. Run query processor for each search query ✅ + UPDATE raw_research_results
# 3. Use data from vector store to answer the gap query
#       - create vector search queries      
#       - curate an answer
#  (create a curated answer) + UPDATE processed_findings
# 4. Check Stop Condition (Conditions: Tree Depth, Confidence Score)
# 5. Analyze + generate Gaps (orchestrator function keeps a queue of gaps)
# 6. Create Search Queries based on Gaps
# 6. Branch to (2) to again run query processor.
# 7. Create Final Proposed Report + UPDATE PROPOSED_CONTENT

import asyncio
import logging
from typing import List, Dict, Any, TypedDict

from langgraph.graph import StateGraph, START, END

from .search_queries_per_plan import PlanSearchQueryGenerator
from .query_processor.query_processor import QueryProcessor
from ..vectore_store import QdrantService, VectorStoreManager

logger = logging.getLogger(__name__)

# Workflow State
class GapQuestionsState(TypedDict):
    plan_step: str
    research_results: List[Dict[str, Any]]
    vector_store_manager: Any
    errors: List[str]
    workflow_complete: bool

class GapQuestionsOrchestrator:
    """Simple orchestrator that processes plan steps in parallel using LangGraph."""
    
    def __init__(self, 
                 max_search_queries: int = 3,
                 max_web_results: int = 5,
                 vector_collection_name: str = "gap_questions"):
        self.max_search_queries = max_search_queries
        self.max_web_results = max_web_results
        self.vector_collection_name = vector_collection_name
        
        # Initialize vector store once at class level
        logger.info(f"Initializing Qdrant vector store: {vector_collection_name}")
        self.qdrant_service = QdrantService(collection_name=vector_collection_name)
        self.vector_store_manager = VectorStoreManager(vector_store=self.qdrant_service.vector_store)
        
        self.query_generator = PlanSearchQueryGenerator()
        self.query_processor = QueryProcessor(vector_store_manager=self.vector_store_manager)
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build simple LangGraph workflow."""
        workflow = StateGraph(GapQuestionsState)
        
        workflow.add_node("process_plan", self.process_plan_node)
        workflow.add_node("research", self.research_node)
        workflow.add_node("finalize", self.finalize_node)
        
        workflow.add_edge(START, "process_plan")
        workflow.add_edge("process_plan", "research")
        workflow.add_edge("research", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    # LangGraph Node Functions
    
    def process_plan_node(self, state: GapQuestionsState) -> GapQuestionsState:
        """Process and validate single plan step."""
        try:
            plan_step = state["plan_step"]
            logger.info(f"Processing plan step: {plan_step[:50]}...")
            
            state["research_results"] = []
            state["errors"] = []
            state["workflow_complete"] = False
            state["vector_store_manager"] = self.vector_store_manager
            
            return state
        except Exception as e:
            state["errors"].append(f"Plan processing failed: {e}")
            return state
    
    async def research_node(self, state: GapQuestionsState) -> GapQuestionsState:
        """Execute research for the single plan step."""
        try:
            plan_step = state["plan_step"]
            
            logger.info(f"Starting research execution for plan step")
            
            # Process the single plan step
            result = await self._process_single_plan_step(plan_step)
            
            if isinstance(result, Exception):
                logger.error(f"Plan step failed: {result}")
                state["errors"].append(f"Step failed: {str(result)}")
                state["research_results"] = []
            else:
                state["research_results"] = result.get("research_results", [])
                logger.info(f"Research execution completed: {len(state['research_results'])} results")
            
            return state
        except Exception as e:
            state["errors"].append(f"Research failed: {e}")
            return state
    
    def finalize_node(self, state: GapQuestionsState) -> GapQuestionsState:
        """Finalize workflow and prepare results."""
        try:
            state["workflow_complete"] = True
            
            total_results = len(state["research_results"])
            logger.info(f"Workflow finalized: {total_results} total results")
            
            return state
        except Exception as e:
            state["errors"].append(f"Finalization failed: {e}")
            return state
    
    # Helper Methods
    
    async def _process_single_plan_step(self, plan_step: str) -> Dict[str, Any]:
        """Process a single plan step: generate queries -> research -> store in vector DB."""
        try:
            logger.info(f"Processing step: {plan_step[:50]}...")
            
            # Step 1: Generate search queries
            queries = self.query_generator.generate_search_queries(
                plan_step,
                max_queries=self.max_search_queries
            )
            
            if not queries:
                return {
                    "plan_step": plan_step,
                    "generated_queries": [],
                    "research_results": [],
                    "success": False,
                    "error": "No queries generated"
                }
            
            logger.info(f"Generated {len(queries)} queries")
            
            # Step 2: Execute research for each query
            all_research_results = []
            
            for query in queries:
                try:
                    # Collect data from web
                    scraped_data = await self.query_processor.collect_only(
                        query=query,
                        max_web_results=self.max_web_results
                    )
                    
                    if scraped_data:
                        # Store in vector database
                        self.vector_store_manager.load(scraped_data)
                        logger.info(f"Loaded {len(scraped_data)} documents for query '{query}'")
                        
                        # Convert to consistent format
                        for item in scraped_data:
                            all_research_results.append({
                                "source": item.get('url', 'N/A'),
                                "content": item.get('content', '')[:500],  # Truncate for summary
                                "query": query
                            })
                
                except Exception as e:
                    logger.warning(f"Query '{query}' failed: {e}")
            
            # Step 3: Return results
            return {
                "plan_step": plan_step,
                "generated_queries": queries,
                "research_results": all_research_results,
                "success": len(all_research_results) > 0,
                "query_count": len(queries),
                "result_count": len(all_research_results)
            }
            
        except Exception as e:
            logger.error(f"Step completely failed: {e}")
            return {
                "plan_step": plan_step,
                "generated_queries": [],
                "research_results": [],
                "success": False,
                "error": str(e)
            }
    
    # Main execution method
    async def execute_plan_step(self, plan_step: str) -> Dict[str, Any]:
        """Main method to execute a single research plan step."""
        try:
            logger.info(f"Starting Gap Questions research for plan step: {plan_step[:50]}...")
            
            initial_state = GapQuestionsState(
                plan_step=plan_step,
                research_results=[],
                vector_store_manager=self.vector_store_manager,
                errors=[],
                workflow_complete=False
            )
            
            # Execute LangGraph workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Return summary
            total_results = len(final_state["research_results"])
            
            return {
                "success": len(final_state["errors"]) == 0,
                "plan_step": plan_step,
                "total_results": total_results,
                "vector_collection": self.vector_collection_name,
                "research_results": final_state["research_results"],
                "errors": final_state["errors"]
            }
            
        except Exception as e:
            logger.error(f"Plan step execution failed: {e}")
            return {
                "success": False,
                "plan_step": plan_step,
                "error": str(e),
                "vector_collection": self.vector_collection_name
            }
    
    def display_results(self, results: Dict[str, Any]) -> None:
        """Display execution results."""
        print("=" * 60)
        print("GAP QUESTIONS RESEARCH RESULTS")
        print("=" * 60)
        
        if results.get("success"):
            print(f"✅ Execution completed successfully")
            print(f"📝 Plan Step: {results['plan_step'][:60]}...")
            print(f"📄 Total Results: {results['total_results']}")
            print(f"🗄️  Vector Collection: {results['vector_collection']}")
            
            if results.get("research_results"):
                print(f"\n📄 Research Results:")
                for i, result in enumerate(results["research_results"][:3], 1):  # Show first 3
                    print(f"   {i}. Source: {result.get('source', 'N/A')}")
                    print(f"      Content: {result.get('content', '')[:100]}...")
            
            if results.get("errors"):
                print(f"\n⚠️  Errors ({len(results['errors'])}):")
                for error in results["errors"]:
                    print(f"   - {error}")
        else:
            print(f"❌ Execution failed: {results.get('error', 'Unknown error')}")
        
        print("=" * 60)
    
    def get_vector_store_content(self) -> List[Dict[str, Any]]:
        """Get content from vector store for MD file generation."""
        try:
            # Search for all content in vector store
            results = self.vector_store_manager.similarity_search(
                query="renewable energy development research",
                k=50  # Get more results for comprehensive view
            )
            
            content = []
            for doc in results:
                content.append({
                    "source": doc.metadata.get('source', 'Unknown'),
                    "content": doc.page_content[:300],  # First 300 chars
                    "full_content": doc.page_content
                })
            
            return content
        except Exception as e:
            logger.error(f"Failed to get vector store content: {e}")
            return []
    
    def generate_vector_store_md(self, output_path: str = "vector_store_content.md") -> str:
        """Generate MD file showing vector store content."""
        try:
            content = self.get_vector_store_content()
            
            if not content:
                md_content = "# Vector Store Content\n\n**Status:** No content found in vector store.\n"
            else:
                md_content = f"# Vector Store Content\n\n"
                md_content += f"**Collection:** {self.vector_collection_name}\n"
                md_content += f"**Total Documents:** {len(content)}\n"
                md_content += f"**Generated:** {asyncio.get_event_loop().time()}\n\n"
                
                md_content += "## Documents\n\n"
                
                for i, doc in enumerate(content, 1):
                    md_content += f"### Document {i}\n\n"
                    md_content += f"**Source:** {doc['source']}\n\n"
                    md_content += f"**Content Preview:**\n```\n{doc['content']}\n```\n\n"
                    md_content += "---\n\n"
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"Vector store content saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate MD file: {e}")
            return ""

# Example usage
if __name__ == "__main__":
    async def test_orchestrator():
        plan_step = "Foundational Understanding of Renewable Energy and Development"
        
        orchestrator = GapQuestionsOrchestrator(
            max_search_queries=2,
            max_web_results=3,
            vector_collection_name="gap_questions_research"
        )
        
        # Execute single research plan step
        results = await orchestrator.execute_plan_step(plan_step)
        
        # Display results
        orchestrator.display_results(results)
        
        # Generate vector store content MD file
        vector_content = orchestrator.get_vector_store_content()
        if vector_content:
            print(f"\n📄 Vector store contains {len(vector_content)} documents")
            
            # Generate MD file
            md_path = orchestrator.generate_vector_store_md("gap_questions_vector_content.md")
            if md_path:
                print(f"📝 Vector store content saved to: {md_path}")
        else:
            print("\n📄 Vector store is empty or unavailable")
    
    asyncio.run(test_orchestrator())
    