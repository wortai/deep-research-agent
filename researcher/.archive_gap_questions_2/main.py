"""
Main Gap Question Generator - Orchestrator
"""

import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import List, Dict

from .models import GapQuery, ExecutionResults, StopCondition
from .vector_queries import VectorQueryGenerator
from .research import ResearchManager
from .answer_generator import AnswerGenerator
from .completeness_checker import CompletenessChecker
from .monitoring import ExecutionMonitor
from .llm_client import GeminiLLMClient

from researcher.web_search import WebSearch
from researcher.vector_store import QdrantService, VectorStoreManager


class GapQuestionGenerator:
    """Main orchestrator for gap question generation and resolution"""
    
    def __init__(
        self,
        llm_client,
        user_query: str,
        max_iterations: int = 3,
        max_depth: int = 3,
        max_gap_queries_per_parent: int = 3,
        confidence_threshold: float = 0.85,
        collection_name: str = "gap_research",
        file_logging: bool = True,
        terminal_logging: bool = False
    ):
        # Core parameters
        self.user_query = user_query
        self.max_iterations = max_iterations
        self.max_depth = max_depth
        self.max_gap_queries_per_parent = max_gap_queries_per_parent
        self.confidence_threshold = confidence_threshold
        
<<<<<<< HEAD
        generator = GapQuestionGenerator(
            llm_client=llm_client,
            user_query=user_query,
            max_iterations=max_iterations,
            confidence_threshold=confidence_threshold
        )
=======
        # State management
        self.gap_query_queue = deque()
        self.completed_qnas = []
        self.current_iteration = 0
        self.current_level = 1
        self.is_running = False
        self.stop_condition = None
>>>>>>> 6fab7b3 (mid-work push)
        
        # Track gap queries per parent
        self.parent_query_counts = {}  # parent_query -> count of children
        
        # Setup logging and monitoring
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session_id = f"gap_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.monitor = ExecutionMonitor(self.session_id, file_logging=file_logging, terminal_logging=terminal_logging)
        
        # Initialize LLM client
        if isinstance(llm_client, str):
            # If string provided, treat as API key
            self.llm_client = GeminiLLMClient(api_key=llm_client, monitor=self.monitor)
        else:
            # If object provided, use directly and set monitor
            self.llm_client = llm_client
            if hasattr(self.llm_client, 'monitor'):
                self.llm_client.monitor = self.monitor
        
<<<<<<< HEAD
        print(f"\n📋 Output Files:")
        print(f"  • Detailed JSON: {generator.monitor.output_dir}/{generator.session_id}_detailed_log.json")
        print(f"  • Markdown Report: {generator.monitor.output_dir}/{generator.session_id}_detailed_report.md")
        print(f"  • URLs & Content: {generator.monitor.output_dir}/{generator.session_id}_urls_content.json")
        print(f"  • Vector Results: {generator.monitor.output_dir}/{generator.session_id}_vector_results.json")
=======
        # Initialize vector store
        self.qdrant_service = QdrantService(collection_name=collection_name)
        self.vector_store_manager = VectorStoreManager(vector_store=self.qdrant_service.vector_store)
>>>>>>> 6fab7b3 (mid-work push)
        
        # Initialize modules
        self.vector_query_gen = VectorQueryGenerator(self.llm_client, self.monitor)
        self.research_manager = ResearchManager(self.vector_store_manager, WebSearch, self.monitor)
        self.answer_generator = AnswerGenerator(self.llm_client, self.monitor)
        self.completeness_checker = CompletenessChecker(self.llm_client, self.monitor)
        
<<<<<<< HEAD
        # Generate visualization
        print("\n📊 Generating visualization report...")
        viz_file = create_visualization_report(generator.session_id)
        if viz_file:
            print(f"Open {viz_file} in your browser to view interactive charts")
        
        # Analyze logs
        print("\n🔍 Analyzing execution data...")
        analyze_logs(generator.session_id)
        
        return generator
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return None
=======
        # Validate initialization
        self._validate_initialization()
        self.logger.info(f"Initialized session: {self.session_id}")
>>>>>>> 6fab7b3 (mid-work push)

    def _validate_initialization(self):
        """Validate initialization parameters"""
        if not self.llm_client:
            raise ValueError("LLM client required")
        if not self.user_query.strip():
            raise ValueError("User query required")
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        if self.max_depth <= 0:
            raise ValueError("max_depth must be positive")
        if self.max_gap_queries_per_parent <= 0:
            raise ValueError("max_gap_queries_per_parent must be positive")
        if not 0 < self.confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be 0-1")

    def _generate_initial_gap_queries(self) -> List[str]:
        """Generate initial gap queries from user query"""
        try:
            prompt = f"""Analyze this user question and identify 2-3 key gap queries that need to be answered 
to provide a comprehensive response.

USER QUESTION: {self.user_query}

Generate specific, focused questions that when answered will help address the user's question.
Each gap query should target a specific aspect or component needed for the complete answer.

Return only the gap queries, one per line:"""
            
            response = self.llm_client.generate(prompt, context="initial_gap_generation")
            queries = [line.strip() for line in response.strip().split('\n') 
                      if line.strip() and len(line.strip()) > 10]
            
            return queries[:3]  # Limit to 3 initial queries
            
        except Exception as e:
            self.logger.error(f"Initial gap query generation failed: {e}")
            return [self.user_query]  # Fallback to user query

    async def _process_gap_query(self, gap_query: GapQuery) -> bool:
        """Process a single gap query through the complete workflow"""
        try:
            self.logger.info(f"Processing gap query (Level {gap_query.level}): {gap_query.query}")
            
            # Step 1: Generate vector store queries
            vector_queries = self.vector_query_gen.generate_queries(
                gap_query.query, self.user_query, max_queries=3
            )
            
            # Step 2: Research and store
            research_data = await self.research_manager.research_and_store(
                query=gap_query.query,
                vector_queries=vector_queries,
                max_web_results=5
            )
            
            # Step 3: Answer gap query
            qna_result = self.answer_generator.answer_gap_query(
                gap_query=gap_query.query,
                research_data=research_data,
                level=gap_query.level,
                parent_query=gap_query.parent_query,
                user_query=self.user_query
            )
            
            # Store completed Q&A
            self.completed_qnas.append({
                "gap_query": qna_result.gap_query,
                "answer": qna_result.answer,
                "confidence_score": qna_result.confidence_score,
                "sources": qna_result.sources,
                "level": qna_result.level,
                "parent_query": qna_result.parent_query
            })
            
            # Step 4: Check completeness
            completeness_result = self.completeness_checker.check_query_completeness(
                qna_result=qna_result,
                user_query=self.user_query,
                current_level=gap_query.level,
                max_depth=self.max_depth,
                parent_query_counts=self.parent_query_counts,
                max_gap_queries_per_parent=self.max_gap_queries_per_parent
            )
            
            # Step 5: Add new gap queries if needed
            if not completeness_result.is_complete and completeness_result.new_gap_queries:
                for new_query in completeness_result.new_gap_queries:
                    new_gap_query = GapQuery(
                        query=new_query,
                        level=gap_query.level + 1,
                        parent_query=gap_query.query,
                        created_at=datetime.now().isoformat()
                    )
                    self.gap_query_queue.append(new_gap_query)
                
                # Update parent query count tracking
                parent_key = gap_query.query
                self.parent_query_counts[parent_key] = self.parent_query_counts.get(parent_key, 0) + len(completeness_result.new_gap_queries)
                
                # Update max level reached
                self.current_level = max(self.current_level, gap_query.level + 1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process gap query '{gap_query.query}': {e}")
            return False

    def _check_stop_conditions(self) -> tuple[bool, StopCondition]:
        """Check if execution should stop"""
        # Check max iterations
        if self.current_iteration >= self.max_iterations:
            return True, StopCondition.MAX_ITERATIONS_REACHED
        
        # Check max depth
        if self.current_level > self.max_depth:
            return True, StopCondition.MAX_DEPTH_REACHED
        
        # Check if queue is empty
        if not self.gap_query_queue:
            return True, StopCondition.QUEUE_EMPTY
        
        # Check overall confidence
        if self.completed_qnas:
            avg_confidence = sum(qna['confidence_score'] for qna in self.completed_qnas) / len(self.completed_qnas)
            if avg_confidence >= self.confidence_threshold:
                return True, StopCondition.CONFIDENCE_THRESHOLD_MET
        
        return False, None

    async def run(self) -> ExecutionResults:
        """Execute the gap question generation process"""
        execution_start = datetime.now()
        self.monitor.log_step("main_execution", "started", {"user_query": self.user_query})
        
        try:
            self.is_running = True
            
            # Generate initial gap queries
            initial_queries = self._generate_initial_gap_queries()
            for query in initial_queries:
                gap_query = GapQuery(
                    query=query,
                    level=1,
                    parent_query=self.user_query,
                    created_at=datetime.now().isoformat()
                )
                self.gap_query_queue.append(gap_query)
            
            self.logger.info(f"Starting with {len(initial_queries)} initial gap queries")
            
            # Main processing loop
            while self.current_iteration < self.max_iterations:
                iteration_start = datetime.now()
                self.monitor.log_step(f"iteration_{self.current_iteration}", "started", {
                    "queue_size": len(self.gap_query_queue)
                })
                
                # Process all queries in current queue
                queries_to_process = list(self.gap_query_queue)
                self.gap_query_queue.clear()
                
                for gap_query in queries_to_process:
                    success = await self._process_gap_query(gap_query)
                    if not success:
                        self.logger.warning(f"Failed to process: {gap_query.query}")
                
                # Check stop conditions
                should_stop, stop_condition = self._check_stop_conditions()
                
                self.current_iteration += 1
                self.stop_condition = stop_condition
                
                self.monitor.complete_step(f"iteration_{self.current_iteration-1}", iteration_start, {
                    "queries_processed": len(queries_to_process),
                    "completed_qnas": len(self.completed_qnas)
                })
                
                if should_stop:
                    self.logger.info(f"Stopping: {stop_condition.value}")
                    break
            
            # Calculate final results
            execution_time = (datetime.now() - execution_start).total_seconds()
            final_confidence = 0.0
            if self.completed_qnas:
                final_confidence = sum(qna['confidence_score'] for qna in self.completed_qnas) / len(self.completed_qnas)
            
            results = ExecutionResults(
                gap_queries_with_answers=self.completed_qnas,
                total_queries_processed=len(self.completed_qnas),
                max_level_reached=self.current_level,
                final_confidence=final_confidence,
                stop_condition=self.stop_condition,
                execution_time=execution_time
            )
            
            self.is_running = False
            
            self.monitor.complete_step("main_execution", execution_start, {
                "stop_condition": self.stop_condition.value if self.stop_condition else None,
                "final_confidence": final_confidence,
                "total_qnas": len(self.completed_qnas)
            })
            
            # Export logs
            self.monitor.export_logs({
                'total_queries_processed': len(self.completed_qnas),
                'max_level_reached': self.current_level,
                'final_confidence': final_confidence,
                'execution_time': execution_time
            })
            
            self.logger.info(f"Completed. Generated {len(self.completed_qnas)} Q&As. Logs: {self.monitor.output_dir}")
            
            return results
            
        except Exception as e:
            self.monitor.log_step("main_execution", "error", {}, str(e))
            self.is_running = False
            self.logger.error(f"Execution failed: {e}")
            
            return ExecutionResults(
                gap_queries_with_answers=self.completed_qnas,
                total_queries_processed=len(self.completed_qnas),
                max_level_reached=self.current_level,
                final_confidence=0.0,
                stop_condition=StopCondition.QUEUE_EMPTY,
                execution_time=(datetime.now() - execution_start).total_seconds()
            )