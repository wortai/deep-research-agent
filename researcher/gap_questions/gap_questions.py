import asyncio
import logging
import json
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

class GapQuestionsState:
    """State for LangGraph workflow."""
    def __init__(self):
        self.plan_query: str = ""
        self.gap_queue: deque = deque()
        self.processed_gaps: List[str] = []
        self.query_solutions: List[Dict[str, Any]] = []
        self.current_depth: int = 0
        self.workflow_complete: bool = False
        self.errors: List[str] = []

class GapQuestionsOrchestrator:
    "Orchestration of GapQuestionGenerator: The heart of WORT Research!"

    def __init__(self, 
                 max_depth: int = 2,
                 max_gaps: int = 2, 
                 max_gap_queries: int = 1,
                 vector_collection_name: str = "gap_questions"):
        """
        - Initialize Vector Store
        - Build Langgraph workflow
        - Tracks a queue of gaps that needs to be resolved
        """
        self.max_depth = max_depth
        self.max_gaps = max_gaps
        self.max_gap_queries = max_gap_queries
        self.vector_collection_name = vector_collection_name
        
        # Initialize components
        self.llm_client = GeminiLLMClient()
        
        # Initialize vector store
        logger.info(f"Initializing vector store: {vector_collection_name}")
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
        """
        This function uses the content and the query to analyze gaps that needs to be filled to complete the query answer. 
        Uses llm_client to find gaps and generate a queue of gaps to return

        Use the vector_search_query_generator.py file function to get vector search optimized queries based on the gap needs to be addressed
        """
        try:
            logger.info(f"Analyzing gaps for query: {query[:50]}...")
            
            # Get content from vector store
            vector_content = self._get_vector_store_content(query)
            
            if not vector_content:
                logger.warning("No content found in vector store for gap analysis")
                return []
            
            # Create gap analysis prompt
            prompt = create_gap_analysis_prompt(query, vector_content)
            
            # Generate gaps using LLM
            response = self.llm_client.generate(prompt, context="gap_analysis", model_type="analysis")
            
            # Parse gaps from response
            gaps = self._parse_gaps_response(response)
            
            logger.info(f"Identified {len(gaps)} gaps")
            return gaps[:self.max_gaps]  # Limit to max_gaps
            
        except Exception as e:
            logger.error(f"Failed to analyze gaps: {e}")
            return []
    
    async def process_batch_web_search(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        This function uses query_processor.py file to process each web search query

        Use analyze_gaps function to get the gaps, and use the function in gap_search_query_generator.py to get the search queries list
        this list will be processed here.
        """
        try:
            logger.info(f"Processing batch web search for {len(queries)} queries")
            
            all_results = []
            
            for query in queries:
                try:
                    # Process query using QueryProcessor
                    results = await self.query_processor.process_query(query, max_web_results=5)
                    
                    if results:
                        all_results.extend(results)
                        logger.info(f"Processed query '{query}': {len(results)} results")
                    else:
                        logger.warning(f"No results for query: {query}")
                        
                except Exception as e:
                    logger.error(f"Failed to process query '{query}': {e}")
            
            logger.info(f"Batch processing completed: {len(all_results)} total results")
            return all_results
            
        except Exception as e:
            logger.error(f"Batch web search processing failed: {e}")
            return []
    
    def check_stop_conditions(self, state: GapQuestionsState) -> bool:
        """
        Checks if the query_queue is empty or max depth of tree is reached. Whatever comes first exit out the GapQuestionsOrchestrator
        """
        if state.current_depth >= self.max_depth:
            logger.info(f"Max depth reached: {state.current_depth}")
            return True
        
        if len(state.gap_queue) == 0:
            logger.info("Gap queue is empty")
            return True
        
        return False
    
    def generate_query_solution_list(self, gaps: List[str]) -> List[Dict[str, Any]]:
        """
        Keeps on generating a list of query and its solution using the content in Vector Store, Using the vector search queries.
        """
        try:
            query_solutions = []
            
            for gap in gaps:
                try:
                    # Generate vector search queries for the gap
                    vector_queries = self.vector_search_generator.generate_vector_search_queries(
                        gap, max_queries=self.max_gap_queries
                    )
                    
                    if not vector_queries:
                        continue
                    
                    # Search vector store for each query
                    gap_solutions = []
                    for vq in vector_queries:
                        results = self.query_processor.search_only([vq], k=3)
                        gap_solutions.extend(results)
                    
                    # Curate solution for this gap
                    solution = self._curate_gap_solution(gap, gap_solutions)
                    
                    query_solutions.append({
                        "gap": gap,
                        "vector_queries": vector_queries,
                        "solution": solution,
                        "source_count": len(gap_solutions)
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to generate solution for gap '{gap}': {e}")
            
            logger.info(f"Generated solutions for {len(query_solutions)} gaps")
            return query_solutions
            
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
        """
        This function orchestrates the process like this: 
        1. Plan Query is used with plan_search_query_generator to get web search queries
        2. Web search queries are used with query_processor
        3. gaps are analyzed and gap queries are generated and stored in queue (using vector_search_queries)
        4. stop conditions are checked: if stop conditions are not met, we loop back to get more gaps, and processing the whole workflow.
        5. In the end I want an md file to see each query with its answer curated.
        6. Keep depth to 2 and maximum gaps generated = 2 and maximum gap queries generated per gap to 1.
        """
        try:
            logger.info(f"Starting orchestrator for plan query: {plan_query[:50]}...")
            
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
            
            # Generate MD file
            md_file_path = self._generate_md_report(final_state)
            
            return {
                "success": True,
                "plan_query": plan_query,
                "total_solutions": len(final_state.get("query_solutions", [])),
                "processed_gaps": len(final_state.get("processed_gaps", [])),
                "final_depth": final_state.get("current_depth", 0),
                "md_report": md_file_path,
                "errors": final_state.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Orchestrator failed: {e}")
            return {
                "success": False,
                "plan_query": plan_query,
                "error": str(e)
            }
    
    # Helper methods for workflow nodes
    
    def _initialize_node(self, state: dict) -> dict:
        """Initialize workflow state."""
        logger.info("Initializing workflow state")
        state["gap_queue"] = deque()
        state["processed_gaps"] = []
        state["query_solutions"] = []
        state["current_depth"] = 0
        state["workflow_complete"] = False
        state["errors"] = []
        return state
    
    async def _generate_web_queries_node(self, state: dict) -> dict:
        """Generate web search queries from plan query or gaps."""
        try:
            if state["current_depth"] == 0:
                # Initial plan query
                queries = self.plan_query_generator.generate_search_queries(
                    state["plan_query"], max_queries=3
                )
                logger.info(f"Generated {len(queries)} initial web queries")
            else:
                # Generate queries from gaps
                queries = []
                if state["gap_queue"]:
                    current_gap = state["gap_queue"].popleft()
                    gap_queries = self.gap_search_generator.generate_gap_search_queries(
                        current_gap, max_queries=2
                    )
                    queries.extend(gap_queries)
                    state["processed_gaps"].append(current_gap)
                    logger.info(f"Generated {len(queries)} gap-based queries")
            
            state["current_web_queries"] = queries
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to generate web queries: {e}")
            return state
    
    async def _process_web_search_node(self, state: dict) -> dict:
        """Process web search queries."""
        try:
            queries = state.get("current_web_queries", [])
            if queries:
                results = await self.process_batch_web_search(queries)
                state["current_web_results"] = results
                logger.info(f"Processed web search: {len(results)} results")
            else:
                state["current_web_results"] = []
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to process web search: {e}")
            return state
    
    def _analyze_gaps_node(self, state: dict) -> dict:
        """Analyze gaps in current content."""
        try:
            gaps = self.analyze_gaps(state["plan_query"])
            
            # Add new gaps to queue (avoid duplicates)
            for gap in gaps:
                if gap not in state["processed_gaps"] and gap not in state["gap_queue"]:
                    state["gap_queue"].append(gap)
            
            logger.info(f"Analyzed gaps: {len(gaps)} new gaps added to queue")
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to analyze gaps: {e}")
            return state
    
    def _check_stop_node(self, state: dict) -> dict:
        """Check stop conditions."""
        state["current_depth"] += 1
        
        should_stop = (
            state["current_depth"] >= self.max_depth or
            len(state["gap_queue"]) == 0
        )
        
        state["should_continue"] = not should_stop
        logger.info(f"Depth: {state['current_depth']}, Queue: {len(state['gap_queue'])}, Continue: {state['should_continue']}")
        return state
    
    def _generate_solutions_node(self, state: dict) -> dict:
        """Generate final solutions for all processed gaps."""
        try:
            all_gaps = state["processed_gaps"] + list(state["gap_queue"])
            solutions = self.generate_query_solution_list(all_gaps)
            state["query_solutions"] = solutions
            logger.info(f"Generated {len(solutions)} final solutions")
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to generate solutions: {e}")
            return state
    
    def _finalize_node(self, state: dict) -> dict:
        """Finalize workflow."""
        state["workflow_complete"] = True
        logger.info("Workflow finalized")
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
    
    def _generate_md_report(self, state: dict) -> str:
        """Generate markdown report of the research."""
        try:
            plan_query = state.get("plan_query", "Unknown Query")
            solutions = state.get("query_solutions", [])
            
            md_content = f"""# Gap Questions Research Report

## Original Query
{plan_query}

## Research Summary
- **Total Solutions Generated**: {len(solutions)}
- **Gaps Processed**: {len(state.get("processed_gaps", []))}
- **Final Depth**: {state.get("current_depth", 0)}

## Gap Analysis & Solutions

"""
            
            for i, solution in enumerate(solutions, 1):
                md_content += f"""### Gap {i}: {solution.get('gap', 'Unknown Gap')}

**Vector Search Queries Used:**
{', '.join(solution.get('vector_queries', []))}

**Solution:**
{solution.get('solution', 'No solution available')}

**Sources**: {solution.get('source_count', 0)} documents

---

"""
            
            # Add errors if any
            errors = state.get("errors", [])
            if errors:
                md_content += f"""## Errors Encountered

"""
                for error in errors:
                    md_content += f"- {error}\n"
            
            # Write to file
            filename = f"gap_questions_report_{hash(plan_query) % 10000}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"Generated MD report: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to generate MD report: {e}")
            return ""