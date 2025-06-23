"""
Main Gap Question Generator implementation.
"""

import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from .models import (
    StopCondition,
    CompletionCheckResult,
    DetailedQueryData,
    OrchestratorState
)
from .monitoring import ExecutionMonitor
from .llm_client import GeminiLLMClient

from .search_store_retrieve import run_research_workflow


class GapQuestionGenerator:
    """Main Gap Question Generator with comprehensive tracking"""
    
    def __init__(
        self,
        llm_client,
        user_query: str,
        max_iterations: int = 3,
        confidence_threshold: float = 0.85,
        file_logging: bool = True,
        terminal_logging: bool = False
    ):
        # Core components
        self.user_query = user_query
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold
        
        # State management
        self.gap_query_queue = deque()
        self.processed_queries = []
        self.unresolved_queries = []
        self.current_iteration = 0
        self.current_confidence = 0.0
        self.previous_confidence = 0.0
        self.is_running = False
        self.stop_condition = None
        
        # Current query data tracker
        self.current_query_data: Optional[DetailedQueryData] = None
        
        # Execution tracking
        self.execution_results = {
            'total_gaps_identified': 0,
            'gaps_resolved': 0,
            'gaps_remaining': 0,
            'queries_processed': 0,
            'final_confidence': 0.0,
            'iterations_completed': 0,
            'vector_store_calls': 0,
            'content_items_added': 0,
            'sources_processed': 0
        }
        
        # Setup logging and monitoring
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session_id = f"gap_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.monitor = ExecutionMonitor(self.session_id, file_logging=file_logging, terminal_logging=terminal_logging)
        
        # Initialize LLM client with monitor
        self.llm_client = GeminiLLMClient(monitor=self.monitor) if isinstance(llm_client, str) else llm_client
        if hasattr(self.llm_client, 'monitor'):
            self.llm_client.monitor = self.monitor
        
        # LangGraph setup
        self.checkpointer = MemorySaver()
        self.orchestrator = self._build_orchestrator()
        
        # Validate initialization
        self._validate_initialization()
        self.logger.info(f"Initialized session: {self.session_id}")

    def _validate_initialization(self):
        """Validate initialization parameters"""
        if not self.llm_client:
            raise ValueError("LLM client required")
        if not self.user_query.strip():
            raise ValueError("User query required")
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        if not 0 < self.confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be 0-1")

    # ===========================
    # Core Processing Methods
    # ===========================

    def generate_vector_store_queries(self, gap_query: str, max_queries: int = 3) -> List[str]:
        """Generate diverse search queries for vector store"""
        step_start = datetime.now()
        self.monitor.log_step("generate_vector_queries", "started", {"gap_query": gap_query})
        
        try:
            prompt = f"""Generate {max_queries} diverse search queries for a vector store.

GAP QUERY: {gap_query}
USER QUESTION: {self.user_query}

Create {max_queries} different ways to search for this information:
1. Different keywords and phrasings
2. Specific enough to find relevant documents
3. Cover different aspects of the topic

Return only queries, one per line:"""
            
            response = self.llm_client.generate(prompt, context="vector_query_generation")
            queries = [line.strip() for line in response.strip().split('\n') 
                      if line.strip() and len(line.strip()) > 10]
            
            final_queries = queries[:max_queries] or [gap_query]
            
            # Store in current query data
            if self.current_query_data:
                self.current_query_data.vector_queries = final_queries
                self.current_query_data.llm_prompt = prompt
                self.current_query_data.llm_response = response
            
            self.monitor.complete_step("generate_vector_queries", step_start, {
                "queries_generated": len(final_queries)
            })
            
            return final_queries
            
        except Exception as e:
            self.monitor.log_step("generate_vector_queries", "error", {}, str(e))
            return [gap_query]

    def generate_gap_queries(self, max_questions: int = 5) -> List[str]:
        """Generate web-optimized gap queries"""
        step_start = datetime.now()
        self.monitor.log_step("generate_gap_queries", "started", {"max_questions": max_questions})
        
        try:
            # Get current memory state
            memory_context = self._get_memory_summary()
            
            # Check if query can be answered
            can_answer, missing_info = self._attempt_query_resolution(memory_context)
            
            if can_answer:
                self.monitor.complete_step("generate_gap_queries", step_start, {"gaps_needed": 0})
                return []
            
            # Generate web-optimized queries
            gap_queries = self._generate_web_optimized_queries(missing_info, max_questions)
            final_queries = self._clean_queries(gap_queries, max_questions)
            
            # Add to queue
            for query in final_queries:
                self.gap_query_queue.append(query)
            
            self.execution_results['total_gaps_identified'] += len(final_queries)
            
            self.monitor.complete_step("generate_gap_queries", step_start, {
                "gaps_generated": len(final_queries),
                "missing_info_count": len(missing_info)
            })
            
            return final_queries
            
        except Exception as e:
            self.monitor.log_step("generate_gap_queries", "error", {}, str(e))
            return []

    def _get_memory_summary(self) -> str:
        """Get current vector store content"""
        try:
            search_queries = [
                self.user_query,
                f"information about {self.user_query}",
                f"facts related to {self.user_query}"
            ]
            
            # Query your vector store with no web search
            memory_data = asyncio.run(run_research_workflow(
                query=self.user_query,
                max_web_results=0,  # No web search, just vector store
                search_queries=search_queries
            ))
            
            if memory_data:
                content_pieces = [item['content'][:500] for item in memory_data 
                               if 'content' in item and item['content']]
                return "\n".join(content_pieces) or "No memory context"
            return "No memory context"
                
        except Exception as e:
            self.logger.warning(f"Memory extraction failed: {e}")
            return "Memory unavailable"

    def _attempt_query_resolution(self, memory_content: str) -> Tuple[bool, List[str]]:
        """Check if query can be answered with current memory"""
        prompt = f"""Can you answer this query with the provided content?

USER QUERY: {self.user_query}
CONTENT: {memory_content}

Format:
CAN_ANSWER: [YES/NO]
MISSING_INFO: [List missing information, one per line, or "None"]"""
        
        try:
            response = self.llm_client.generate(prompt, context="query_resolution_check")
            lines = response.strip().split('\n')
            can_answer = False
            missing_info = []
            
            for line in lines:
                if line.startswith('CAN_ANSWER:'):
                    can_answer = 'YES' in line.upper()
                elif line.startswith('MISSING_INFO:'):
                    info = line.split(':', 1)[1].strip()
                    if info.lower() != 'none':
                        missing_info.append(info)
                elif line.strip() and missing_info:
                    missing_info.append(line.strip())
            
            return can_answer, missing_info
        except Exception as e:
            return False, ["Analysis failed"]

    def _generate_web_optimized_queries(self, missing_info: List[str], max_questions: int) -> List[str]:
        """Generate web search optimized queries"""
        if not missing_info:
            return []
        
        prompt = f"""Generate {max_questions} web search queries for missing information.

USER QUERY: {self.user_query}
MISSING INFO: {chr(10).join([f"- {info}" for info in missing_info])}

Create web search queries that are:
1. Short and keyword-focused
2. Ready for search engines
3. Different from each other
4. Directly searchable

One query per line:"""
        
        try:
            response = self.llm_client.generate(prompt, context="web_query_generation")
            queries = [line.strip() for line in response.strip().split('\n') 
                      if line.strip() and len(line.strip()) > 3]
            return queries
        except Exception as e:
            return []

    def _clean_queries(self, queries: List[str], max_questions: int) -> List[str]:
        """Remove duplicates and limit count"""
        seen = set()
        unique_queries = []
        for query in queries:
            normalized = query.lower().strip()
            if normalized not in seen and len(query.strip()) > 3:
                unique_queries.append(query)
                seen.add(normalized)
        return unique_queries[:max_questions]

    def state_manager(self):
        """Process queries from queue"""
        step_start = datetime.now()
        self.monitor.log_step("state_manager", "started", {"queue_size": len(self.gap_query_queue)})
        
        try:
            if not self.gap_query_queue:
                self.monitor.complete_step("state_manager", step_start, {"processed": None})
                return None
            
            current_query = self.gap_query_queue.popleft()
            self._process_query_with_vector_store(current_query)
            self.processed_queries.append(current_query)
            self.execution_results['queries_processed'] += 1
            
            self.monitor.complete_step("state_manager", step_start, {"processed": current_query})
            return current_query
            
        except Exception as e:
            self.monitor.log_step("state_manager", "error", {}, str(e))
            return None

    def _process_query_with_vector_store(self, gap_query: str):
        """Process query through YOUR vector store system"""
        step_start = datetime.now()
        self.monitor.log_step("vector_store_processing", "started", {"gap_query": gap_query})
        
        # Create detailed query data tracker
        self.current_query_data = DetailedQueryData(gap_query=gap_query)
        
        try:
            # Generate vector store queries
            vector_queries = self.generate_vector_store_queries(gap_query, 3)
            
            # Call YOUR research workflow
            research_data = asyncio.run(run_research_workflow(
                query=gap_query,
                max_web_results=5,
                search_queries=vector_queries
            ))
            
            # Store raw data
            if research_data:
                for item in research_data:
                    source = item.get('source', 'unknown')
                    content = item.get('content', '')
                    
                    # Track URLs
                    if source and source.startswith('http'):
                        self.current_query_data.urls_accessed.append(source)
                    
                    # Track content
                    self.current_query_data.content_from_urls.append({
                        'source': source,
                        'content': content
                    })
                    
                    # Track vector search results
                    self.current_query_data.vector_search_results.append({
                        'source': source,
                        'content_preview': content[:200] + '...' if len(content) > 200 else content
                    })
            
            # Process results
            processed_content = self._process_research_data(gap_query, research_data)
            self.current_query_data.insights_extracted = processed_content
            
            # Log the detailed query data
            self.monitor.log_query_data(self.current_query_data)
            
            # Update metrics
            self.execution_results['vector_store_calls'] += 1
            self.execution_results['content_items_added'] += len(processed_content)
            self.execution_results['sources_processed'] += len(research_data) if research_data else 0
            
            self.monitor.complete_step("vector_store_processing", step_start, {
                "sources_found": len(research_data) if research_data else 0,
                "content_processed": len(processed_content),
                "urls_accessed": len(self.current_query_data.urls_accessed)
            })
            
        except Exception as e:
            self.monitor.log_step("vector_store_processing", "error", {"gap_query": gap_query}, str(e))
            if self.current_query_data:
                self.monitor.log_query_data(self.current_query_data)

    def _process_research_data(self, gap_query: str, research_data: List[Dict]) -> List[str]:
        """Process your vector store results"""
        if not research_data:
            return []
        
        try:
            # Extract content from your format
            content_items = []
            for item in research_data:
                content = item.get('content', '')
                source = item.get('source', '')
                
                if content and len(content.strip()) > 50:
                    content_items.append({
                        'content': content[:1500] + "..." if len(content) > 1500 else content,
                        'source': source,
                        'gap_query': gap_query
                    })
            
            # Use LLM to extract insights
            if content_items:
                return self._extract_insights_with_llm(gap_query, content_items)
            return []
                
        except Exception as e:
            self.logger.error(f"Research data processing failed: {e}")
            return []

    def _extract_insights_with_llm(self, gap_query: str, content_items: List[Dict]) -> List[str]:
        """Extract relevant insights using LLM"""
        try:
            content_text = ""
            for i, item in enumerate(content_items, 1):
                content_text += f"\nSource {i} ({item['source']}):\n{item['content']}\n"
            
            prompt = f"""Extract relevant insights for the gap query.

GAP QUERY: {gap_query}
USER QUESTION: {self.user_query}

CONTENT:
{content_text}

Extract key insights that directly address the gap query.
Focus on factual, specific information.
One insight per line (no bullets):"""
            
            response = self.llm_client.generate(prompt, context="insight_extraction")
            insights = [line.strip() for line in response.split('\n') 
                       if line.strip() and len(line.strip()) > 30]
            
            return insights[:8]  # Limit insights
            
        except Exception as e:
            return [item['content'][:200] + "..." for item in content_items[:5]]

    def check_query_completeness(self) -> CompletionCheckResult:
        """Check if query is complete"""
        step_start = datetime.now()
        self.monitor.log_step("check_completeness", "started", {"queue_size": len(self.gap_query_queue)})
        
        try:
            if self.gap_query_queue:
                result = CompletionCheckResult(False, self.current_confidence, 
                                             list(self.gap_query_queue), 0.0)
                self.monitor.complete_step("check_completeness", step_start, {"complete": False})
                return result
            
            memory_context = self._get_memory_summary()
            can_answer, missing_aspects = self._attempt_query_resolution(memory_context)
            
            completeness = 100.0 if can_answer else max(0.0, 100.0 - (len(missing_aspects) * 20))
            confidence = completeness / 100.0
            self.current_confidence = confidence
            
            result = CompletionCheckResult(can_answer, confidence, missing_aspects, completeness)
            self.monitor.complete_step("check_completeness", step_start, {
                "complete": can_answer,
                "confidence": confidence
            })
            
            return result
            
        except Exception as e:
            self.monitor.log_step("check_completeness", "error", {}, str(e))
            return CompletionCheckResult(False, 0.0, ["Error"], 0.0)

    def check_stop_conditions(self, iteration: int, confidence: float, prev_confidence: float) -> Tuple[bool, StopCondition]:
        """Check if should stop"""
        if iteration >= self.max_iterations:
            return True, StopCondition.MAX_ITERATIONS_REACHED
        if confidence >= self.confidence_threshold:
            return True, StopCondition.CONFIDENCE_THRESHOLD_MET
        if not self.gap_query_queue and not self.unresolved_queries:
            return True, StopCondition.QUEUE_EMPTY
        return False, None

    # ===========================
    # LangGraph Orchestration
    # ===========================

    def _build_orchestrator(self):
        """Build LangGraph workflow"""
        graph = StateGraph(OrchestratorState)
        
        graph.add_node("generate_gaps", self._orchestrator_generate_gaps)
        graph.add_node("process_queue", self._orchestrator_process_queue)
        graph.add_node("check_completion", self._orchestrator_check_completion)
        
        graph.add_edge(START, "generate_gaps")
        graph.add_edge("generate_gaps", "process_queue")
        graph.add_edge("process_queue", "check_completion")
        
        graph.add_conditional_edges(
            "check_completion",
            self._should_continue,
            {"continue": "generate_gaps", "stop": END}
        )
        
        return graph.compile(checkpointer=self.checkpointer)

    def _orchestrator_generate_gaps(self, state: OrchestratorState) -> OrchestratorState:
        """Generate gap queries"""
        if state["current_iteration"] == 0:
            self.generate_gap_queries()
        else:
            for query in self.unresolved_queries:
                self.gap_query_queue.append(query)
        return state

    def _orchestrator_process_queue(self, state: OrchestratorState) -> OrchestratorState:
        """Process all queries in queue"""
        while self.gap_query_queue:
            self.state_manager()
        return state

    def _orchestrator_check_completion(self, state: OrchestratorState) -> OrchestratorState:
        """Check completion and update state"""
        completion = self.check_query_completeness()
        state["current_iteration"] += 1
        self.current_iteration = state["current_iteration"]
        
        should_stop, stop_condition = self.check_stop_conditions(
            state["current_iteration"], completion.confidence_score, self.previous_confidence
        )
        
        state["should_continue"] = not should_stop
        state["stop_condition"] = stop_condition
        self.previous_confidence = self.current_confidence
        self.stop_condition = stop_condition
        
        return state

    def _should_continue(self, state: OrchestratorState) -> str:
        """Determine next step"""
        return "stop" if not state["should_continue"] else "continue"

    # ===========================
    # Main Execution
    # ===========================

    def run(self) -> Dict:
        """Execute the gap question generation process"""
        step_start = datetime.now()
        self.monitor.log_step("main_execution", "started", {"user_query": self.user_query})
        
        try:
            self.is_running = True
            
            initial_state = {
                "current_iteration": 0,
                "should_continue": True,
                "stop_condition": None
            }
            
            config = {"configurable": {"thread_id": self.session_id}}
            final_state = self.orchestrator.invoke(initial_state, config)
            
            self.execution_results['iterations_completed'] = final_state["current_iteration"]
            self.execution_results['final_confidence'] = self.current_confidence
            self.execution_results['gaps_remaining'] = len(self.gap_query_queue) + len(self.unresolved_queries)
            
            self.is_running = False
            
            self.monitor.complete_step("main_execution", step_start, {
                "stop_condition": self.stop_condition.value if self.stop_condition else None
            })
            
            # Export logs
            self.monitor.export_logs(self.execution_results)
            self.logger.info(f"Completed. Logs: {self.monitor.output_dir}")
            
            return self.execution_results
            
        except Exception as e:
            self.monitor.log_step("main_execution", "error", {}, str(e))
            self.is_running = False
            self.monitor.export_logs(self.execution_results)
            return self.execution_results