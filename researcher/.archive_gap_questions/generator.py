"""
Main Gap Question Generator implementation - Simplified.
"""

import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from researcher.gap_questions.models import (
    StopCondition,
    CompletionCheckResult,
    DetailedQueryData
)
<<<<<<< HEAD:researcher/gap_questions/generator.py
from .monitoring import ExecutionMonitor
from .llm_client import GeminiLLMClient

# IMPORTANT: Import your search_store_retrieve module here
# Make sure search_store_retrieve.py is in the same directory as this file
from .search_store_retrieve import run_research_workflow
=======
from researcher.gap_questions.monitoring import ExecutionMonitor
from researcher.gap_questions.llm_client import GeminiLLMClient
from researcher.web_search import WebSearch
from researcher.vector_store import QdrantService, VectorStoreManager
>>>>>>> 6fab7b3 (mid-work push):researcher/.archive_gap_questions/generator.py


class GapQuestionGenerator:
    """Main Gap Question Generator with comprehensive tracking"""
    
    def __init__(
        self,
        llm_client,
        user_query: str,
        max_iterations: int = 3,
<<<<<<< HEAD:researcher/gap_questions/generator.py
        confidence_threshold: float = 0.85
=======
        confidence_threshold: float = 0.85,
        collection_name: str = "gap_research",
        file_logging: bool = True,
        terminal_logging: bool = False
>>>>>>> 6fab7b3 (mid-work push):researcher/.archive_gap_questions/generator.py
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
        
        # Vector store components
        self.qdrant_service = QdrantService(collection_name=collection_name)
        self.vector_store_manager = VectorStoreManager(vector_store=self.qdrant_service.vector_store)
        
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
        self.monitor = ExecutionMonitor(self.session_id)
        
        # Initialize LLM client with monitor
        self.llm_client = GeminiLLMClient(monitor=self.monitor) if isinstance(llm_client, str) else llm_client
        if hasattr(self.llm_client, 'monitor'):
            self.llm_client.monitor = self.monitor
        
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
    # Research and Vector Store Methods
    # ===========================

    async def research_and_store(self, query: str, max_web_results: int = 5, search_queries: List[str] = None) -> List[Dict]:
        """
        Integrated research workflow: web search, vector store, and similarity search.
        
        Args:
            query: The research query
            max_web_results: Maximum web search results to process
            search_queries: Specific queries for vector store search
            
        Returns:
            List of extracted data with source and content
        """
        step_start = datetime.now()
        self.monitor.log_step("research_and_store", "started", {
            "query": query, 
            "max_web_results": max_web_results
        })
        
        extracted_data = []
        
        try:
            # Step 1: Web Search and Data Extraction (only if web results requested)
            if max_web_results > 0:
                self.logger.info(f"Performing web search for: {query}")
                web_search = WebSearch(query=query, max_results=max_web_results)
                scraped_data = await web_search.initiate_research()
                
                if scraped_data:
                    self.logger.info(f"Successfully scraped data from {len(scraped_data)} URLs")
                    # Load new data into vector store
                    self.vector_store_manager.load(scraped_data)
                    self.logger.info("New data loaded into vector store")
                else:
                    self.logger.warning("No data scraped from web search")
            
            # Step 2: Vector Store Similarity Search
            self.logger.info("Performing vector store similarity search")
            
            # Use provided search queries or generate defaults
            if search_queries:
                queries_to_search = search_queries
            else:
                queries_to_search = [
                    query,
                    f"What are the key findings about {query}?",
                    f"facts related to {query}"
                ]
            
            # Search vector store for each query
            for search_query in queries_to_search:
                self.logger.info(f"Searching vector store for: '{search_query}'")
                
                search_results = self.vector_store_manager.similarity_search(
                    query=search_query, 
                    k=4  # Top 4 results per query
                )
                
                if search_results:
                    self.logger.info(f"Found {len(search_results)} relevant documents")
                    for doc in search_results:
                        extracted_data.append({
                            "source": doc.metadata.get('source', 'vector_store'),
                            "content": doc.page_content
                        })
                else:
                    self.logger.info("No relevant documents found for this query")
            
            # Remove duplicates based on content similarity
            extracted_data = self._deduplicate_results(extracted_data)
            
            self.monitor.complete_step("research_and_store", step_start, {
                "results_found": len(extracted_data),
                "web_results": max_web_results if max_web_results > 0 else 0
            })
            
            return extracted_data
            
        except Exception as e:
            self.monitor.log_step("research_and_store", "error", {"query": query}, str(e))
            self.logger.error(f"Research workflow failed: {e}")
            return []

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on content similarity"""
        if not results:
            return []
        
        unique_results = []
        seen_content = set()
        
        for result in results:
            content = result.get('content', '')
            # Use first 200 chars as deduplication key
            content_key = content[:200].strip().lower()
            
            if content_key and content_key not in seen_content:
                unique_results.append(result)
                seen_content.add(content_key)
        
        return unique_results

    # ===========================
    # Core Processing Methods
    # ===========================

    def generate_vector_store_queries(self, gap_query: str, max_queries: int = 3) -> List[str]:
        """Generate diverse search queries for vector store"""
        step_start = datetime.now()
        self.monitor.log_step("generate_vector_queries", "started", {"gap_query": gap_query})
        
        try:
            prompt = f"""You are an expert information retrieval specialist. Your task is to generate a set of diverse, high-quality search queries for a semantic vector database. The goal is to retrieve comprehensive and precise information to address the `GAP QUERY`.

**Context:**
- **GAP QUERY (The specific information we need):** "{gap_query}"
- **Original User Question (The broader context):** "{self.user_query}"

**Instructions for Generating Semantic Queries:**

Your queries must be optimized for a semantic search engine that understands natural language, intent, and conceptual relationships.

1.  **Conceptual Diversification:**
    - Go beyond simple keywords. Generate queries that explore different facets, underlying concepts, and related sub-topics.
    - Think about the "who, what, where, when, why, and how" of the gap query.

2.  **Varied Formulations:**
    - **As Questions:** Phrase queries as direct questions (e.g., "What are the economic impacts of...").
    - **As Descriptions:** Use descriptive phrases that state the desired information (e.g., "A detailed analysis of the technical challenges of...").
    - **As Relational Searches:** Explore relationships and causality (e.g., "The relationship between X and Y," "How does A cause B?").

3.  **Perspective Shifting:**
    - Formulate queries from different viewpoints (e.g., for a topic on technology, create queries from an economic, ethical, and social perspective).

**Task:**
Generate {max_queries} distinct and effective search queries based on the instructions above.

**Output Format:**
- Provide ONLY the raw queries.
- Each query must be on a new line.
- Do not include numbers, bullets, or any other explanatory text.
"""
            
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
            
            # Query vector store with no web search (just existing content)
            memory_data = asyncio.run(self.research_and_store(
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
        
        prompt = f"""You are an expert search strategist. Your goal is to create a set of concise, powerful web search queries to find specific missing information for a research task.

    **Main Research Goal:**
    {self.user_query}

    **Specific Information Gaps to Fill:**
    {chr(10).join([f"- {info}" for info in missing_info])}

    **Instructions for Generating Search Queries:**

    1.  **Think Like a Power User:** Formulate queries you would type directly into Google. Be direct and keyword-focused.
    2.  **Extract Core Concepts:** Distill the "Information Gaps" into essential keywords. Combine them with terms from the "Main Research Goal" for context.
    3.  **Use Actionable Modifiers:** Employ terms like "statistics", "impact of", "vs", "challenges", "benefits", "case study", "tutorial" to narrow the search intent.
    4.  **Keep it Lean:** Aim for queries between 8 and 16 words. Avoid full sentences or conversational questions.
    5.  **Diversify:** Create a mix of query types. Some can be phrased as questions (e.g., "how does X affect Y"), others as keyword statements (e.g., "X effect on Y statistics").

    **Task:**
    Generate {max_questions} distinct and effective search queries based on the instructions.

    **Output Format:**
    - Provide ONLY the raw queries.
    - Each query must be on a new line.
    - Do not include numbers, bullets, or any other explanatory text.
    """
        
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

    def process_next_query(self) -> Optional[str]:
        """Process next query from queue"""
        step_start = datetime.now()
        self.monitor.log_step("process_next_query", "started", {"queue_size": len(self.gap_query_queue)})
        
        try:
            if not self.gap_query_queue:
                self.monitor.complete_step("process_next_query", step_start, {"processed": None})
                return None
            
            current_query = self.gap_query_queue.popleft()
            self._process_query_with_vector_store(current_query)
            self.processed_queries.append(current_query)
            self.execution_results['queries_processed'] += 1
            
            self.monitor.complete_step("process_next_query", step_start, {"processed": current_query})
            return current_query
            
        except Exception as e:
            self.monitor.log_step("process_next_query", "error", {}, str(e))
            return None

    def _process_query_with_vector_store(self, gap_query: str):
        """Process query through integrated research workflow"""
        step_start = datetime.now()
        self.monitor.log_step("query_processing", "started", {"gap_query": gap_query})
        
        # Create detailed query data tracker
        self.current_query_data = DetailedQueryData(gap_query=gap_query)
        
        try:
            # Generate vector store queries
            vector_queries = self.generate_vector_store_queries(gap_query, 3)
            
            # Use integrated research workflow
            research_data = asyncio.run(self.research_and_store(
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
            
            self.monitor.complete_step("query_processing", step_start, {
                "sources_found": len(research_data) if research_data else 0,
                "content_processed": len(processed_content),
                "urls_accessed": len(self.current_query_data.urls_accessed)
            })
            
        except Exception as e:
            self.monitor.log_step("query_processing", "error", {"gap_query": gap_query}, str(e))
            if self.current_query_data:
                self.monitor.log_query_data(self.current_query_data)

    def _process_research_data(self, gap_query: str, research_data: List[Dict]) -> List[str]:
        """Process vector store results"""
        if not research_data:
            return []
        
        try:
            # Extract content from format
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
            
            prompt = f"""**Role:** You are a meticulous research analyst. Your task is to synthesize complex information into clear, factual insights.

**Primary Goal:**
Answer the `GAP QUERY` by extracting and synthesizing relevant information exclusively from the provided `CONTENT`. The final output should be a series of clear, explanatory statements that collectively answer the query.

**Context:**
- **Main User Question (Broader Context):** "{self.user_query}"
- **Specific Gap Query (Your Focus):** "{gap_query}"
- **Source Content (Your Only Source of Truth):**
---
{content_text}
---

**Instructions & Constraints:**

1.  **Synthesize, Don't Just Extract:** Do not simply copy-paste sentences. Analyze the `CONTENT` and formulate your own clear, well-written sentences that directly address the `GAP QUERY`.
2.  **Factual Accuracy:** Every statement you make must be directly supported by the provided `CONTENT`. Do not add external information or make assumptions.
3.  **Break Down the Answer:** Structure your response as a series of distinct insights. Each insight should tackle a different facet of the `GAP QUERY`, building a comprehensive answer piece by piece.
4.  **Concise and Clear:** Each insight should be a complete thought, ideally under 100 words. The language should be professional and easy to understand.

**Output Format:**
- Provide ONLY the synthesized insights.
- Each insight must be on a new line.
- DO NOT use bullet points, numbers, or any other list formatting.

**Synthesized Insights:**
"""
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

    def check_stop_conditions(self, completion: CompletionCheckResult) -> Tuple[bool, StopCondition]:
        """Check if should stop"""
        if self.current_iteration >= self.max_iterations:
            return True, StopCondition.MAX_ITERATIONS_REACHED
        
        if completion.confidence_score >= self.confidence_threshold:
            return True, StopCondition.CONFIDENCE_THRESHOLD_MET
        
        if not self.gap_query_queue and not self.unresolved_queries:
            return True, StopCondition.QUEUE_EMPTY
        
        # Check for confidence plateau
        if (self.current_iteration > 1 and 
            abs(self.current_confidence - self.previous_confidence) < 0.05):
            return True, StopCondition.CONFIDENCE_THRESHOLD_MET
        
        return False, None

    def process_all_queries(self):
        """Process all queries in the current queue"""
        step_start = datetime.now()
        self.monitor.log_step("process_all_queries", "started", {"queue_size": len(self.gap_query_queue)})
        
        processed_count = 0
        while self.gap_query_queue:
            query = self.process_next_query()
            if query:
                processed_count += 1
        
        self.monitor.complete_step("process_all_queries", step_start, {
            "queries_processed": processed_count
        })

    # ===========================
    # Main Execution
    # ===========================

    def run(self) -> Dict:
        """Execute the gap question generation process"""
        step_start = datetime.now()
        self.monitor.log_step("main_execution", "started", {"user_query": self.user_query})
        
        try:
            self.is_running = True
            
            # Main execution loop
            while self.current_iteration < self.max_iterations:
                iteration_start = datetime.now()
                self.monitor.log_step(f"iteration_{self.current_iteration}", "started", {})
                
                # Generate gap queries (only on first iteration or if we have unresolved queries)
                if self.current_iteration == 0:
                    gap_queries = self.generate_gap_queries()
                    if not gap_queries:
                        # Query can already be answered
                        completion = self.check_query_completeness()
                        self.execution_results['final_confidence'] = completion.confidence_score
                        break
                else:
                    # Add unresolved queries back to queue
                    for query in self.unresolved_queries:
                        self.gap_query_queue.append(query)
                    self.unresolved_queries.clear()
                
                # Process all queries in queue
                self.process_all_queries()
                
                # Check completion
                completion = self.check_query_completeness()
                
                # Check stop conditions
                should_stop, stop_condition = self.check_stop_conditions(completion)
                
                # Update iteration tracking
                self.current_iteration += 1
                self.previous_confidence = self.current_confidence
                self.stop_condition = stop_condition
                
                self.monitor.complete_step(f"iteration_{self.current_iteration-1}", iteration_start, {
                    "confidence": completion.confidence_score,
                    "queries_processed": len(self.processed_queries)
                })
                
                # Check if we should stop
                if should_stop:
                    break
                
                # Store unresolved queries for next iteration
                if completion.missing_aspects:
                    self.unresolved_queries = completion.missing_aspects[:3]  # Limit for next iteration
            
            # Final results
            self.execution_results['iterations_completed'] = self.current_iteration
            self.execution_results['final_confidence'] = self.current_confidence
            self.execution_results['gaps_remaining'] = len(self.gap_query_queue) + len(self.unresolved_queries)
            
            self.is_running = False
            
            self.monitor.complete_step("main_execution", step_start, {
                "stop_condition": self.stop_condition.value if self.stop_condition else None,
                "final_confidence": self.current_confidence
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