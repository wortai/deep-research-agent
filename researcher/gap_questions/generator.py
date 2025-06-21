#!/usr/bin/env python3
"""
Gap Question Generator with Comprehensive Data Tracking
A complete, production-ready implementation in a single file.
"""

import json
import os
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from collections import deque
from enum import Enum
from dataclasses import dataclass, asdict, field
from urllib.parse import urlparse
from dotenv import load_dotenv

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# LangGraph imports
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

# Your vector store system
from gap_questions import run_research_workflow

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ===========================
# Data Models
# ===========================

class StopCondition(Enum):
    """Reasons for stopping the generation process"""
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    CONFIDENCE_THRESHOLD_MET = "confidence_threshold_met"
    QUEUE_EMPTY = "queue_empty"

@dataclass
class ProcessingStep:
    """Tracks individual processing steps"""
    step_name: str
    timestamp: str
    status: str
    details: Dict
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class CompletionCheckResult:
    """Results from checking query completeness"""
    is_complete: bool
    confidence_score: float
    missing_aspects: List[str]
    completeness_percentage: float

@dataclass
class DetailedQueryData:
    """Comprehensive data for each query processed"""
    gap_query: str
    vector_queries: List[str] = field(default_factory=list)
    llm_prompt: str = ""
    llm_response: str = ""
    urls_accessed: List[str] = field(default_factory=list)
    content_from_urls: List[Dict[str, str]] = field(default_factory=list)
    vector_search_results: List[Dict[str, str]] = field(default_factory=list)
    insights_extracted: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class OrchestratorState(dict):
    """State for LangGraph orchestration"""
    current_iteration: int
    should_continue: bool
    stop_condition: Optional[StopCondition]

# ===========================
# Monitoring and Logging
# ===========================

class ExecutionMonitor:
    """Comprehensive monitoring and logging system"""
    
    def __init__(self, session_id: str, output_dir: str = "gap_generator_logs"):
        self.session_id = session_id
        self.output_dir = output_dir
        self.steps: List[ProcessingStep] = []
        self.start_time = datetime.now()
        self.detailed_queries: List[DetailedQueryData] = []
        self.all_urls_accessed: set = set()
        self.all_vector_queries: List[str] = []
        self.llm_interactions: List[Dict[str, Any]] = []
        
        os.makedirs(output_dir, exist_ok=True)
        
    def log_step(self, step_name: str, status: str, details: Dict, error_message: str = None):
        """Log a processing step"""
        step = ProcessingStep(
            step_name=step_name,
            timestamp=datetime.now().isoformat(),
            status=status,
            details=details,
            error_message=error_message
        )
        self.steps.append(step)
        
    def complete_step(self, step_name: str, start_time: datetime, details: Dict = None):
        """Mark a step as completed with duration"""
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        for step in reversed(self.steps):
            if step.step_name == step_name and step.status == 'started':
                step.status = 'completed'
                step.duration_ms = duration_ms
                if details:
                    step.details.update(details)
                break
    
    def log_query_data(self, query_data: DetailedQueryData):
        """Log detailed data for a query"""
        self.detailed_queries.append(query_data)
        self.all_urls_accessed.update(query_data.urls_accessed)
        self.all_vector_queries.extend(query_data.vector_queries)
    
    def log_llm_interaction(self, prompt: str, response: str, context: str):
        """Log LLM interactions"""
        self.llm_interactions.append({
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "prompt": prompt[:500] + "..." if len(prompt) > 500 else prompt,
            "response": response,
            "prompt_length": len(prompt),
            "response_length": len(response)
        })
    
    def export_logs(self, execution_results: Dict):
        """Export all logs to files"""
        self._export_json(execution_results)
        self._export_markdown(execution_results)
        self._export_detailed_data()
    
    def _export_json(self, execution_results: Dict):
        """Export comprehensive JSON log"""
        log_data = {
            "session_id": self.session_id,
            "execution_start": self.start_time.isoformat(),
            "execution_end": datetime.now().isoformat(),
            "total_duration_ms": int((datetime.now() - self.start_time).total_seconds() * 1000),
            "execution_results": execution_results,
            "processing_steps": [asdict(step) for step in self.steps],
            "detailed_queries": [asdict(q) for q in self.detailed_queries],
            "all_urls_accessed": list(self.all_urls_accessed),
            "all_vector_queries": self.all_vector_queries,
            "llm_interactions": self.llm_interactions
        }
        
        json_file = os.path.join(self.output_dir, f"{self.session_id}_detailed_log.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def _export_markdown(self, execution_results: Dict):
        """Export human-readable markdown report"""
        md_content = f"""# Gap Question Generator Detailed Report

## Session: {self.session_id}
**Start:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}  
**Duration:** {(datetime.now() - self.start_time).total_seconds():.1f}s

## Summary Results
"""
        for key, value in execution_results.items():
            md_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        # URLs Section
        md_content += f"\n## URLs Accessed ({len(self.all_urls_accessed)})\n"
        for i, url in enumerate(self.all_urls_accessed, 1):
            md_content += f"{i}. {url}\n"
        
        # Vector Queries Section
        md_content += f"\n## Vector Queries Generated ({len(self.all_vector_queries)})\n"
        for i, query in enumerate(self.all_vector_queries, 1):
            md_content += f"{i}. {query}\n"
        
        # Detailed Query Processing
        md_content += "\n## Detailed Query Processing\n"
        for i, query_data in enumerate(self.detailed_queries, 1):
            md_content += f"\n### Gap Query {i}: {query_data.gap_query}\n"
            md_content += f"**Timestamp:** {query_data.timestamp}\n\n"
            
            md_content += "**Vector Queries:**\n"
            for vq in query_data.vector_queries:
                md_content += f"- {vq}\n"
            
            md_content += f"\n**URLs Accessed ({len(query_data.urls_accessed)}):**\n"
            for url in query_data.urls_accessed:
                md_content += f"- {url}\n"
            
            md_content += f"\n**Content Retrieved ({len(query_data.content_from_urls)} items):**\n"
            for j, content in enumerate(query_data.content_from_urls[:3], 1):
                md_content += f"{j}. Source: {content.get('source', 'N/A')}\n"
                md_content += f"   Content: {content.get('content', '')[:200]}...\n\n"
            
            md_content += f"\n**Insights Extracted ({len(query_data.insights_extracted)}):**\n"
            for insight in query_data.insights_extracted:
                md_content += f"- {insight}\n"
        
        # LLM Interactions
        md_content += "\n## LLM Interactions\n"
        for i, interaction in enumerate(self.llm_interactions, 1):
            md_content += f"\n### Interaction {i} - {interaction['context']}\n"
            md_content += f"**Timestamp:** {interaction['timestamp']}\n"
            md_content += f"**Prompt Length:** {interaction['prompt_length']} chars\n"
            md_content += f"**Response Length:** {interaction['response_length']} chars\n"
            md_content += f"**Response Preview:**\n```\n{interaction['response'][:500]}...\n```\n"
        
        # Processing Steps
        md_content += "\n## Processing Steps\n"
        for i, step in enumerate(self.steps, 1):
            icon = "✅" if step.status == "completed" else "❌" if step.status == "error" else "🟡"
            duration = f" ({step.duration_ms}ms)" if step.duration_ms else ""
            md_content += f"{i}. {step.step_name} {icon}{duration}\n"
        
        md_file = os.path.join(self.output_dir, f"{self.session_id}_detailed_report.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _export_detailed_data(self):
        """Export detailed data to separate files"""
        # Export URLs with their content
        urls_file = os.path.join(self.output_dir, f"{self.session_id}_urls_content.json")
        urls_data = {}
        for query_data in self.detailed_queries:
            for content in query_data.content_from_urls:
                url = content.get('source', 'unknown')
                if url not in urls_data:
                    urls_data[url] = []
                urls_data[url].append({
                    'gap_query': query_data.gap_query,
                    'content': content.get('content', '')
                })
        
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(urls_data, f, indent=2, ensure_ascii=False)
        
        # Export vector search results
        vector_file = os.path.join(self.output_dir, f"{self.session_id}_vector_results.json")
        vector_data = []
        for query_data in self.detailed_queries:
            vector_data.append({
                'gap_query': query_data.gap_query,
                'vector_queries': query_data.vector_queries,
                'results': query_data.vector_search_results
            })
        
        with open(vector_file, 'w', encoding='utf-8') as f:
            json.dump(vector_data, f, indent=2, ensure_ascii=False)

# ===========================
# LLM Client
# ===========================

class GeminiLLMClient:
    """Gemini LLM client with smart model selection and logging"""
    
    def __init__(self, api_key: str = None, monitor: ExecutionMonitor = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.monitor = monitor
        
        if not self.api_key or self.api_key == "your_google_api_key_here":
            raise ValueError("Set GOOGLE_API_KEY in .env file")
        
        self.thinking_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-thinking-exp",
            google_api_key=self.api_key,
            temperature=0.1
        )
        
        self.analysis_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=self.api_key,
            temperature=0.2
        )
        
        self.generation_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.3
        )
    
    def _select_model(self, prompt: str):
        """Select appropriate model based on prompt content"""
        prompt_lower = prompt.lower()
        if any(k in prompt_lower for k in ["analyze", "evaluate", "assess"]):
            return self.thinking_model
        elif any(k in prompt_lower for k in ["can_answer", "missing_info"]):
            return self.analysis_model
        else:
            return self.generation_model
    
    def generate(self, prompt: str, context: str = "general") -> str:
        """Generate response with logging"""
        try:
            model = self._select_model(prompt)
            response = model.invoke([HumanMessage(content=prompt)])
            result = response.content
            
            # Log interaction if monitor available
            if self.monitor:
                self.monitor.log_llm_interaction(prompt, result, context)
            
            return result
        except Exception as e:
            raise Exception(f"Gemini API failed: {str(e)}")

# ===========================
# Main Generator Class
# ===========================

class GapQuestionGenerator:
    """Main Gap Question Generator with comprehensive tracking"""
    
    def __init__(
        self,
        llm_client,
        user_query: str,
        max_iterations: int = 3,
        confidence_threshold: float = 0.85
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
        self.monitor = ExecutionMonitor(self.session_id)
        
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

# ===========================
# Utility Functions
# ===========================

def analyze_logs(session_id: str, log_dir: str = "gap_generator_logs"):
    """Analyze and display insights from logged data"""
    print(f"\n📈 Analyzing logs for session: {session_id}")
    
    try:
        # Load detailed log
        json_file = os.path.join(log_dir, f"{session_id}_detailed_log.json")
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        print("\n🔍 Analysis Results:")
        print(f"Total URLs accessed: {len(data['all_urls_accessed'])}")
        print(f"Total vector queries: {len(data['all_vector_queries'])}")
        print(f"LLM interactions: {len(data['llm_interactions'])}")
        
        # URL domain analysis
        domains = {}
        for url in data['all_urls_accessed']:
            domain = urlparse(url).netloc
            domains[domain] = domains.get(domain, 0) + 1
        
        print("\n📊 Top domains accessed:")
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {domain}: {count} times")
        
        # Query complexity
        print("\n📝 Query processing complexity:")
        for i, query in enumerate(data['detailed_queries'], 1):
            print(f"\nQuery {i}: {query['gap_query']}")
            print(f"  - Vector queries: {len(query['vector_queries'])}")
            print(f"  - URLs accessed: {len(query['urls_accessed'])}")
            print(f"  - Content items: {len(query['content_from_urls'])}")
            print(f"  - Insights extracted: {len(query['insights_extracted'])}")
        
        # LLM usage patterns
        print("\n🤖 LLM Usage Patterns:")
        total_prompt_chars = sum(i['prompt_length'] for i in data['llm_interactions'])
        total_response_chars = sum(i['response_length'] for i in data['llm_interactions'])
        print(f"  - Total prompt characters: {total_prompt_chars:,}")
        print(f"  - Total response characters: {total_response_chars:,}")
        print(f"  - Average response length: {total_response_chars // len(data['llm_interactions']):,} chars")
        
        # Context distribution
        context_counts = {}
        for interaction in data['llm_interactions']:
            ctx = interaction['context']
            context_counts[ctx] = context_counts.get(ctx, 0) + 1
        
        print("\n🎯 LLM Context Distribution:")
        for context, count in context_counts.items():
            print(f"  - {context}: {count} calls")
        
        return data
        
    except Exception as e:
        print(f"❌ Error analyzing logs: {e}")
        return None

def create_visualization_report(session_id: str, log_dir: str = "gap_generator_logs") -> str:
    """Create an HTML visualization report"""
    try:
        json_file = os.path.join(log_dir, f"{session_id}_detailed_log.json")
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Calculate metrics
        domains = {}
        for url in data['all_urls_accessed']:
            domain = urlparse(url).netloc
            domains[domain] = domains.get(domain, 0) + 1
        
        # Generate HTML report
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Gap Generator Report - {session_id}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #333; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #e3f2fd; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #1976d2; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        .query-box {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #2196f3; }}
        .url-list {{ max-height: 300px; overflow-y: auto; background: #fafafa; padding: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #e3f2fd; font-weight: bold; }}
        .insight {{ background: #e8f5e9; padding: 8px; margin: 5px 0; border-radius: 3px; }}
        .chart {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Gap Question Generator Analysis Report</h1>
        <p>Session: {session_id}</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Performance Metrics</h2>
        <div>
            <div class="metric">
                <div class="metric-value">{data['execution_results']['queries_processed']}</div>
                <div class="metric-label">Queries Processed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['execution_results']['sources_processed']}</div>
                <div class="metric-label">Sources Processed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(data['all_urls_accessed'])}</div>
                <div class="metric-label">Unique URLs</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['execution_results']['content_items_added']}</div>
                <div class="metric-label">Content Items</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['execution_results']['final_confidence']:.2%}</div>
                <div class="metric-label">Final Confidence</div>
            </div>
        </div>
        
        <h2>Processing Timeline</h2>
        <div id="timeline-chart" class="chart"></div>
        
        <h2>URL Domain Distribution</h2>
        <div id="domain-chart" class="chart"></div>
        
        <h2>Processing Steps Status</h2>
        <div id="steps-chart" class="chart"></div>
        
        <h2>Query Details</h2>
        <div id="query-details">
            <!-- Query details will be added by JavaScript -->
        </div>
    </div>
    
    <script>
        // Data preparation
        const data = {json.dumps(data)};
        
        // Timeline chart
        const timelineData = [];
        const timelineLayout = {{
            title: 'Processing Step Durations',
            xaxis: {{ title: 'Duration (ms)' }},
            yaxis: {{ title: 'Step Name' }},
            margin: {{ l: 150 }}
        }};
        
        data.processing_steps.forEach(step => {{
            if (step.status === 'completed' && step.duration_ms) {{
                timelineData.push({{
                    x: [step.duration_ms],
                    y: [step.step_name],
                    type: 'bar',
                    orientation: 'h',
                    name: step.step_name
                }});
            }}
        }});
        
        Plotly.newPlot('timeline-chart', timelineData, timelineLayout);
        
        // Domain distribution
        const domains = {json.dumps(domains)};
        const domainData = [{{
            labels: Object.keys(domains),
            values: Object.values(domains),
            type: 'pie'
        }}];
        
        Plotly.newPlot('domain-chart', domainData, {{
            title: 'URL Domain Distribution'
        }});
        
        // Step status distribution
        const statusCounts = {{ completed: 0, started: 0, error: 0 }};
        data.processing_steps.forEach(step => {{
            if (statusCounts.hasOwnProperty(step.status)) {{
                statusCounts[step.status]++;
            }}
        }});
        
        const stepsData = [{{
            x: Object.keys(statusCounts),
            y: Object.values(statusCounts),
            type: 'bar',
            marker: {{ color: ['#4caf50', '#ff9800', '#f44336'] }}
        }}];
        
        Plotly.newPlot('steps-chart', stepsData, {{
            title: 'Processing Step Status Distribution'
        }});
        
        // Query details
        const queryDetailsDiv = document.getElementById('query-details');
        data.detailed_queries.forEach((query, index) => {{
            const queryBox = document.createElement('div');
            queryBox.className = 'query-box';
            queryBox.innerHTML = `
                <h3>Gap Query ${{index + 1}}: ${{query.gap_query}}</h3>
                <p><strong>Vector Queries:</strong> ${{query.vector_queries.length}}</p>
                <p><strong>URLs Accessed:</strong> ${{query.urls_accessed.length}}</p>
                <p><strong>Insights Extracted:</strong> ${{query.insights_extracted.length}}</p>
            `;
            queryDetailsDiv.appendChild(queryBox);
        }});
    </script>
</body>
</html>
"""
        
        # Save HTML file
        html_file = os.path.join(log_dir, f"{session_id}_visualization.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Visualization report created: {html_file}")
        return html_file
        
    except Exception as e:
        print(f"❌ Error creating visualization: {e}")
        return None

# ===========================
# Main Entry Point
# ===========================

def main():
    """Main execution function"""
    print("🚀 Gap Question Generator with Comprehensive Data Tracking")
    print("=" * 60)
    
    try:
        # Initialize
        llm_client = GeminiLLMClient()
        user_query = "What are the best Ai companies that have good funding in 2025 and what they doing ?"
        
        generator = GapQuestionGenerator(
            llm_client=llm_client,
            user_query=user_query,
            max_iterations=3,
            confidence_threshold=0.85
        )
        
        print(f"Session: {generator.session_id}")
        print(f"Query: {user_query}")
        print("-" * 40)
        
        # Run complete workflow
        results = generator.run()
        
        print("\n📊 Results Summary:")
        for key, value in results.items():
            print(f"  • {key}: {value}")
        
        print(f"\n📋 Output Files:")
        print(f"  • Detailed JSON: {generator.monitor.output_dir}/{generator.session_id}_detailed_log.json")
        print(f"  • Markdown Report: {generator.monitor.output_dir}/{generator.session_id}_detailed_report.md")
        print(f"  • URLs & Content: {generator.monitor.output_dir}/{generator.session_id}_urls_content.json")
        print(f"  • Vector Results: {generator.monitor.output_dir}/{generator.session_id}_vector_results.json")
        
        # Display sample data
        print("\n📌 Sample Data from Processing:")
        if generator.monitor.detailed_queries:
            query_data = generator.monitor.detailed_queries[0]
            print(f"\nFirst Gap Query: {query_data.gap_query}")
            print(f"Vector Queries Generated: {len(query_data.vector_queries)}")
            for vq in query_data.vector_queries[:2]:
                print(f"  - {vq}")
            print(f"URLs Accessed: {len(query_data.urls_accessed)}")
            for url in query_data.urls_accessed[:2]:
                print(f"  - {url}")
            print(f"Insights Extracted: {len(query_data.insights_extracted)}")
            for insight in query_data.insights_extracted[:2]:
                print(f"  - {insight[:100]}...")
        
        # Generate visualization
        print("\n📊 Generating visualization report...")
        viz_file = create_visualization_report(generator.session_id)
        if viz_file:
            print(f"Open {viz_file} in your browser to view interactive charts")
        
        # Analyze logs
        print("\n🔍 Analyzing execution data...")
        analyze_logs(generator.session_id)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Environment setup
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
        print("⚠️  Created .env file. Please add your Google API key.")
        print("   Get your key from: https://makersuite.google.com/app/apikey")
        exit(1)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        print("⚠️  Please set GOOGLE_API_KEY in the .env file")
        print("   Get your key from: https://makersuite.google.com/app/apikey")
        exit(1)
    
    # Run main
    main()