# gap_question_generator.py
"""
Gap Question Generator System using LangGraph
This is the main system that orchestrates gap detection and query generation.
The external search system is imported and can be easily replaced.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import deque
from enum import Enum
from dataclasses import dataclass, asdict
import logging
import asyncio
from dotenv import load_dotenv

# LangChain imports for Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# LangGraph imports (only what we need)
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

# Import vector store research workflow
from gap_questions.search_store_retrieve import run_research_workflow

# Import external system (can be easily replaced)
# Removed MockVectorStore import as we're using real vector store now

# Load environment variables from .env file
load_dotenv()

class StopCondition(Enum):
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    CONFIDENCE_THRESHOLD_MET = "confidence_threshold_met"
    QUEUE_EMPTY = "queue_empty"

@dataclass
class ProcessingStep:
    """Record of a processing step for monitoring"""
    step_name: str
    timestamp: str
    status: str  # 'started', 'completed', 'error'
    details: Dict
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None

class ExecutionMonitor:
    """Monitor and log execution steps for later analysis"""
    
    def __init__(self, session_id: str, output_dir: str = "gap_generator_logs"):
        self.session_id = session_id
        self.output_dir = output_dir
        self.steps: List[ProcessingStep] = []
        self.start_time = datetime.now()
        
        # Create output directory
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
        """Mark a step as completed and calculate duration"""
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Update the last step with this name
        for step in reversed(self.steps):
            if step.step_name == step_name and step.status == 'started':
                step.status = 'completed'
                step.duration_ms = duration_ms
                if details:
                    step.details.update(details)
                break
    
    def export_logs(self, execution_results: Dict):
        """Export logs to both JSON and Markdown files"""
        self._export_json(execution_results)
        self._export_markdown(execution_results)
    
    def _export_json(self, execution_results: Dict):
        """Export detailed logs to JSON"""
        log_data = {
            "session_id": self.session_id,
            "execution_start": self.start_time.isoformat(),
            "execution_end": datetime.now().isoformat(),
            "total_duration_ms": int((datetime.now() - self.start_time).total_seconds() * 1000),
            "execution_results": execution_results,
            "processing_steps": [asdict(step) for step in self.steps],
            "summary_stats": self._generate_summary_stats()
        }
        
        json_file = os.path.join(self.output_dir, f"{self.session_id}_detailed_log.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def _export_markdown(self, execution_results: Dict):
        """Export readable summary to Markdown"""
        md_content = self._generate_markdown_report(execution_results)
        
        md_file = os.path.join(self.output_dir, f"{self.session_id}_execution_report.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _generate_summary_stats(self) -> Dict:
        """Generate summary statistics"""
        completed_steps = [s for s in self.steps if s.status == 'completed']
        error_steps = [s for s in self.steps if s.status == 'error']
        
        return {
            "total_steps": len(self.steps),
            "completed_steps": len(completed_steps),
            "error_steps": len(error_steps),
            "average_step_duration_ms": sum(s.duration_ms for s in completed_steps if s.duration_ms) / len(completed_steps) if completed_steps else 0,
            "longest_step": max(completed_steps, key=lambda x: x.duration_ms or 0).step_name if completed_steps else None,
            "total_execution_time_ms": int((datetime.now() - self.start_time).total_seconds() * 1000)
        }
    
    def _generate_markdown_report(self, execution_results: Dict) -> str:
        """Generate a readable Markdown report"""
        stats = self._generate_summary_stats()
        
        md_content = f"""# Gap Question Generator Execution Report

## Session Information
- **Session ID**: {self.session_id}
- **Start Time**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **End Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Duration**: {stats['total_execution_time_ms']/1000:.2f} seconds

## Execution Results
"""
        
        for key, value in execution_results.items():
            md_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        md_content += f"""
## Processing Summary
- **Total Steps**: {stats['total_steps']}
- **Completed Steps**: {stats['completed_steps']}
- **Error Steps**: {stats['error_steps']}
- **Average Step Duration**: {stats['average_step_duration_ms']:.0f}ms
- **Longest Step**: {stats['longest_step'] or 'N/A'}

## Detailed Step Log
"""
        
        for i, step in enumerate(self.steps, 1):
            status_icon = "✅" if step.status == "completed" else "❌" if step.status == "error" else "🟡"
            duration_text = f" ({step.duration_ms}ms)" if step.duration_ms else ""
            
            md_content += f"""
### {i}. {step.step_name} {status_icon}
- **Status**: {step.status.title()}{duration_text}
- **Timestamp**: {step.timestamp}
"""
            
            if step.details:
                md_content += "- **Details**:\n"
                for key, value in step.details.items():
                    if isinstance(value, list) and len(value) > 3:
                        md_content += f"  - {key}: {len(value)} items\n"
                    else:
                        md_content += f"  - {key}: {value}\n"
            
            if step.error_message:
                md_content += f"- **Error**: {step.error_message}\n"
        
        md_content += f"""
## Performance Analysis
- Most time was spent on: {stats['longest_step'] or 'N/A'}
- Processing efficiency: {stats['completed_steps']/stats['total_steps']*100:.1f}% success rate
- Average processing speed: {stats['average_step_duration_ms']:.0f}ms per step

---
*Generated by Gap Question Generator v1.0*
"""
        
        return md_content

@dataclass
class CompletionCheckResult:
    is_complete: bool
    confidence_score: float
    missing_aspects: List[str]
    completeness_percentage: float

# Simple state for LangGraph orchestrator
class OrchestratorState(dict):
    current_iteration: int
    should_continue: bool
    stop_condition: Optional[StopCondition]

class GeminiLLMClient:
    """LangChain-based Gemini client with model selection for different tasks"""
    
    def __init__(self, api_key: str = None):
        # Load from .env file first, then fallback to parameter or environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key or self.api_key == "your_google_api_key_here":
            raise ValueError(
                "Google API key is required. Please set GOOGLE_API_KEY in your .env file.\n"
                "You can get your API key from: https://makersuite.google.com/app/apikey"
            )
        
        # Different models for different tasks
        self.thinking_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-thinking-exp",  # Best for complex reasoning
            google_api_key=self.api_key,
            temperature=0.1
        )
        
        self.analysis_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",  # Good for analysis tasks
            google_api_key=self.api_key,
            temperature=0.2
        )
        
        self.generation_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Fast for generation tasks
            google_api_key=self.api_key,
            temperature=0.3
        )
    
    def _select_model(self, prompt: str):
        """Select the best Gemini model based on the prompt type"""
        prompt_lower = prompt.lower()
        
        # Use thinking model for complex analysis and reasoning
        if any(keyword in prompt_lower for keyword in [
            "analyze", "determine", "reasoning", "complex", "evaluate", "assess"
        ]):
            return self.thinking_model
        
        # Use analysis model for detailed content analysis
        elif any(keyword in prompt_lower for keyword in [
            "can_answer", "missing_info", "content analysis", "query resolution"
        ]):
            return self.analysis_model
        
        # Use generation model for creating queries and simple tasks
        else:
            return self.generation_model
    
    def generate(self, prompt: str) -> str:
        """Generate response using appropriate Gemini model"""
        try:
            model = self._select_model(prompt)
            messages = [HumanMessage(content=prompt)]
            response = model.invoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
    
    def complete(self, prompt: str) -> str:
        """Alias for generate to support different interfaces"""
        return self.generate(prompt)

class StopCondition(Enum):
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    CONFIDENCE_THRESHOLD_MET = "confidence_threshold_met"
    QUEUE_EMPTY = "queue_empty"

@dataclass
class ProcessingStep:
    """Record of a processing step for monitoring"""
    step_name: str
    timestamp: str
    status: str  # 'started', 'completed', 'error'
    details: Dict
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None

class ExecutionMonitor:
    """Monitor and log execution steps for later analysis"""
    
    def __init__(self, session_id: str, output_dir: str = "gap_generator_logs"):
        self.session_id = session_id
        self.output_dir = output_dir
        self.steps: List[ProcessingStep] = []
        self.start_time = datetime.now()
        
        # Create output directory
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
        """Mark a step as completed and calculate duration"""
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Update the last step with this name
        for step in reversed(self.steps):
            if step.step_name == step_name and step.status == 'started':
                step.status = 'completed'
                step.duration_ms = duration_ms
                if details:
                    step.details.update(details)
                break
    
    def export_logs(self, execution_results: Dict):
        """Export logs to both JSON and Markdown files"""
        self._export_json(execution_results)
        self._export_markdown(execution_results)
    
    def _export_json(self, execution_results: Dict):
        """Export detailed logs to JSON"""
        log_data = {
            "session_id": self.session_id,
            "execution_start": self.start_time.isoformat(),
            "execution_end": datetime.now().isoformat(),
            "total_duration_ms": int((datetime.now() - self.start_time).total_seconds() * 1000),
            "execution_results": execution_results,
            "processing_steps": [asdict(step) for step in self.steps],
            "summary_stats": self._generate_summary_stats()
        }
        
        json_file = os.path.join(self.output_dir, f"{self.session_id}_detailed_log.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def _export_markdown(self, execution_results: Dict):
        """Export readable summary to Markdown"""
        md_content = self._generate_markdown_report(execution_results)
        
        md_file = os.path.join(self.output_dir, f"{self.session_id}_execution_report.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _generate_summary_stats(self) -> Dict:
        """Generate summary statistics"""
        completed_steps = [s for s in self.steps if s.status == 'completed']
        error_steps = [s for s in self.steps if s.status == 'error']
        
        return {
            "total_steps": len(self.steps),
            "completed_steps": len(completed_steps),
            "error_steps": len(error_steps),
            "average_step_duration_ms": sum(s.duration_ms for s in completed_steps if s.duration_ms) / len(completed_steps) if completed_steps else 0,
            "longest_step": max(completed_steps, key=lambda x: x.duration_ms or 0).step_name if completed_steps else None,
            "total_execution_time_ms": int((datetime.now() - self.start_time).total_seconds() * 1000)
        }
    
    def _generate_markdown_report(self, execution_results: Dict) -> str:
        """Generate a readable Markdown report"""
        stats = self._generate_summary_stats()
        
        md_content = f"""# Gap Question Generator Execution Report

## Session Information
- **Session ID**: {self.session_id}
- **Start Time**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **End Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Duration**: {stats['total_execution_time_ms']/1000:.2f} seconds

## Execution Results
"""
        
        for key, value in execution_results.items():
            md_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        md_content += f"""
## Processing Summary
- **Total Steps**: {stats['total_steps']}
- **Completed Steps**: {stats['completed_steps']}
- **Error Steps**: {stats['error_steps']}
- **Average Step Duration**: {stats['average_step_duration_ms']:.0f}ms
- **Longest Step**: {stats['longest_step'] or 'N/A'}

## Detailed Step Log
"""
        
        for i, step in enumerate(self.steps, 1):
            status_icon = "✅" if step.status == "completed" else "❌" if step.status == "error" else "🟡"
            duration_text = f" ({step.duration_ms}ms)" if step.duration_ms else ""
            
            md_content += f"""
### {i}. {step.step_name} {status_icon}
- **Status**: {step.status.title()}{duration_text}
- **Timestamp**: {step.timestamp}
"""
            
            if step.details:
                md_content += "- **Details**:\n"
                for key, value in step.details.items():
                    if isinstance(value, list) and len(value) > 3:
                        md_content += f"  - {key}: {len(value)} items\n"
                    else:
                        md_content += f"  - {key}: {value}\n"
            
            if step.error_message:
                md_content += f"- **Error**: {step.error_message}\n"
        
        md_content += f"""
## Performance Analysis
- Most time was spent on: {stats['longest_step'] or 'N/A'}
- Processing efficiency: {stats['completed_steps']/stats['total_steps']*100:.1f}% success rate
- Average processing speed: {stats['average_step_duration_ms']:.0f}ms per step

---
*Generated by Gap Question Generator v1.0*
"""
        
        return md_content

@dataclass
class CompletionCheckResult:
    is_complete: bool
    confidence_score: float
    missing_aspects: List[str]
    completeness_percentage: float
class OrchestratorState(dict):
    current_iteration: int
    should_continue: bool
    stop_condition: Optional[StopCondition]

# Simple state for LangGraph orchestrator
    """LangChain-based Gemini client with model selection for different tasks"""
    
    def __init__(self, api_key: str = None):
        # Load from .env file first, then fallback to parameter or environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key or self.api_key == "your_google_api_key_here":
            raise ValueError(
                "Google API key is required. Please set GOOGLE_API_KEY in your .env file.\n"
                "You can get your API key from: https://makersuite.google.com/app/apikey"
            )
        
        # Different models for different tasks
        self.thinking_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-thinking-exp",  # Best for complex reasoning
            google_api_key=self.api_key,
            temperature=0.1
        )
        
        self.analysis_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",  # Good for analysis tasks
            google_api_key=self.api_key,
            temperature=0.2
        )
        
        self.generation_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Fast for generation tasks
            google_api_key=self.api_key,
            temperature=0.3
        )
    
    def _select_model(self, prompt: str):
        """Select the best Gemini model based on the prompt type"""
        prompt_lower = prompt.lower()
        
        # Use thinking model for complex analysis and reasoning
        if any(keyword in prompt_lower for keyword in [
            "analyze", "determine", "reasoning", "complex", "evaluate", "assess"
        ]):
            return self.thinking_model
        
        # Use analysis model for detailed content analysis
        elif any(keyword in prompt_lower for keyword in [
            "can_answer", "missing_info", "content analysis", "query resolution"
        ]):
            return self.analysis_model
        
        # Use generation model for creating queries and simple tasks
        else:
            return self.generation_model
    
    def generate(self, prompt: str) -> str:
        """Generate response using appropriate Gemini model"""
        try:
            model = self._select_model(prompt)
            messages = [HumanMessage(content=prompt)]
            response = model.invoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
    
    def complete(self, prompt: str) -> str:
        """Alias for generate to support different interfaces"""
        return self.generate(prompt)

class GapQuestionGenerator:
    def __init__(
        self,
        llm_client,
        user_query: str,
        memory,
        max_iterations: int = 5,
        confidence_threshold: float = 0.85
    ):
        # Core components
        self.llm_client = llm_client
        self.user_query = user_query
        self.memory = memory
        
        # Configuration
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold
        
        # State management
        self.gap_query_queue = deque()
        self.processed_queries = []
        self.unresolved_queries = []
        
        # Tracking
        self.current_iteration = 0
        self.current_confidence = 0.0
        self.previous_confidence = 0.0
        
        # Execution state
        self.is_running = False
        self.stop_condition = None
        self.execution_results = {
            'total_gaps_identified': 0,
            'gaps_resolved': 0,
            'gaps_remaining': 0,
            'queries_processed': 0,
            'final_confidence': 0.0,
            'iterations_completed': 0,
            'external_system_calls': 0,
            'content_items_added': 0,
            'sources_processed': 0
        }
        
        # Error handling
        self.error_count = 0
        self.max_errors = 10
        self.last_error = None
        
        # Setup
        self.logger = logging.getLogger(f"{__class__.__name__}")
        self.session_id = f"gap_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.checkpointer = MemorySaver()
        self.orchestrator = self._build_orchestrator()
        
        # Execution Monitor
        self.monitor = ExecutionMonitor(self.session_id)
        
        # Validation
        self._validate_initialization()
        self.logger.info(f"GapQuestionGenerator initialized with session_id: {self.session_id}")

    def _validate_initialization(self):
        """Validate initialization parameters"""
        if not self.llm_client:
            raise ValueError("LLM client cannot be None")
        if not self.user_query or not self.user_query.strip():
            raise ValueError("User query cannot be empty")
        # Removed memory validation since we're using your vector store directly
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        if not 0 < self.confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be between 0 and 1")
        self.logger.info("Initialization validation passed")

    def generate_vector_store_queries(self, gap_query: str, max_queries: int = 3) -> List[str]:
        """Generate vector store search queries for a given gap query"""
        step_start = datetime.now()
        self.monitor.log_step("generate_vector_store_queries", "started", {
            "gap_query": gap_query,
            "max_queries": max_queries
        })
        
        try:
            self.logger.info(f"Generating vector store queries for gap: '{gap_query}'")
            
            prompt = f"""
You are a search query expert. Generate {max_queries} different search queries to find relevant information in a vector store/knowledge base.

ORIGINAL GAP QUERY: {gap_query}
USER'S MAIN QUESTION: {self.user_query}

Your task is to create {max_queries} diverse search queries that would help find information related to the gap query. 
Each query should:
1. Be a different way to ask about the same topic
2. Use different keywords and phrasings
3. Be specific enough to find relevant documents
4. Cover different aspects of the topic

Format: Return only the queries, one per line, without numbering or bullets.

GENERATED QUERIES:
"""
            
            response = self._call_llm(prompt)
            
            # Parse the response into individual queries
            queries = []
            for line in response.strip().split('\n'):
                line = line.strip()
                line = line.lstrip('0123456789.-•* ').strip()
                
                if line and len(line) > 10:
                    queries.append(line)
            
            final_queries = queries[:max_queries] if queries else [gap_query]
            
            self.monitor.complete_step("generate_vector_store_queries", step_start, {
                "generated_queries": final_queries,
                "queries_count": len(final_queries)
            })
            
            self.logger.info(f"Generated {len(final_queries)} vector store queries")
            return final_queries
            
        except Exception as e:
            self.monitor.log_step("generate_vector_store_queries", "error", {
                "gap_query": gap_query
            }, str(e))
            self.logger.warning(f"Error generating vector store queries: {str(e)}")
            return [gap_query]

    def generate_gap_queries(self, max_questions: int = 5) -> List[str]:
        """Generate gap queries that are web-optimized and ready for search"""
        step_start = datetime.now()
        self.monitor.log_step("generate_gap_queries", "started", {
            "max_questions": max_questions,
            "user_query": self.user_query
        })
        
        try:
            self.logger.info(f"Generating gap queries, max_questions: {max_questions}")
            
            # Get current memory context
            memory_context = self._get_memory_summary()
            
            # Check if we can answer with current memory
            can_answer, missing_info = self._attempt_query_resolution(memory_context)
            
            if can_answer:
                self.monitor.complete_step("generate_gap_queries", step_start, {
                    "can_answer_with_memory": True,
                    "gap_queries_generated": 0
                })
                self.logger.info("Query can be fully answered with existing memory content")
                return []
            
            # Generate gap queries for missing information
            gap_queries = self._generate_queries_for_missing_info(missing_info, max_questions)
            
            # Clean and limit queries
            final_queries = self._clean_and_limit_queries(gap_queries, max_questions)
            
            # Add to queue for processing
            for query in final_queries:
                self.gap_query_queue.append(query)
            
            # Update tracking
            self.execution_results['total_gaps_identified'] += len(final_queries)
            
            self.monitor.complete_step("generate_gap_queries", step_start, {
                "can_answer_with_memory": False,
                "missing_info_count": len(missing_info),
                "gap_queries_generated": len(final_queries),
                "final_queries": final_queries
            })
            
            self.logger.info(f"Generated {len(final_queries)} gap queries")
            return final_queries
            
        except Exception as e:
            self.monitor.log_step("generate_gap_queries", "error", {
                "max_questions": max_questions
            }, str(e))
            self._handle_error(f"Error generating gap queries: {str(e)}")
            return []

    def check_gap_elimination(self, max_retry=3):
        """
        This function sees if after the gap query execution, and memory updation the gap queries are resolved or not
        by cross verifying the new updations and summarized earlier memory.

        Consider:
        1. Memory
        2. List of earlier Gap Queries
        
        Output: List of Gap Queries Unresolved -> to call execution of gap_query again with {max_tries}
        """
        try:
            self.logger.info("Checking gap elimination...")
            
            if not self.processed_queries:
                return []
            
            # Get updated memory context
            updated_memory = self._get_memory_summary()
            
            # Check each processed query against updated memory
            unresolved = []
            for query in self.processed_queries:
                if not self._is_query_resolved(query, updated_memory):
                    unresolved.append(query)
            
            self.unresolved_queries = unresolved
            self.execution_results['gaps_resolved'] = len(self.processed_queries) - len(unresolved)
            self.execution_results['gaps_remaining'] = len(unresolved)
            
            self.logger.info(f"Gap elimination check: {len(unresolved)} queries remain unresolved")
            return unresolved
            
        except Exception as e:
            self._handle_error(f"Error in gap elimination check: {str(e)}")
            return self.processed_queries  # Assume all unresolved on error

    def check_query_completeness(self) -> CompletionCheckResult:
        """Check if the gap_query queue is empty and if query can be answered"""
        step_start = datetime.now()
        self.monitor.log_step("check_query_completeness", "started", {
            "queue_size": len(self.gap_query_queue),
            "current_confidence": self.current_confidence
        })
        
        try:
            self.logger.info("Checking query completeness...")
            
            # Check if queue is empty
            if self.gap_query_queue:
                result = CompletionCheckResult(
                    is_complete=False,
                    confidence_score=self.current_confidence,
                    missing_aspects=list(self.gap_query_queue),
                    completeness_percentage=0.0
                )
                
                self.monitor.complete_step("check_query_completeness", step_start, {
                    "is_complete": False,
                    "reason": "queue_not_empty",
                    "remaining_queries": len(self.gap_query_queue)
                })
                
                return result
            
            # Get current memory and check resolution
            memory_context = self._get_memory_summary()
            can_answer, missing_aspects = self._attempt_query_resolution(memory_context)
            
            completeness = 100.0 if can_answer else max(0.0, 100.0 - (len(missing_aspects) * 20))
            confidence = completeness / 100.0
            
            self.current_confidence = confidence
            
            result = CompletionCheckResult(
                is_complete=can_answer,
                confidence_score=confidence,
                missing_aspects=missing_aspects,
                completeness_percentage=completeness
            )
            
            self.monitor.complete_step("check_query_completeness", step_start, {
                "is_complete": can_answer,
                "confidence_score": confidence,
                "completeness_percentage": completeness,
                "missing_aspects_count": len(missing_aspects)
            })
            
            self.logger.info(f"Completeness: {completeness}%, confidence: {confidence}")
            return result
            
        except Exception as e:
            self.monitor.log_step("check_query_completeness", "error", {
                "queue_size": len(self.gap_query_queue)
            }, str(e))
            self._handle_error(f"Error in completeness check: {str(e)}")
            return CompletionCheckResult(
                is_complete=False,
                confidence_score=0.0,
                missing_aspects=["Error in completeness check"],
                completeness_percentage=0.0
            )

    def check_stop_conditions(self, current_iteration: int, current_confidence: float, previous_confidence: float) -> Tuple[bool, StopCondition]:
        """Check if GapQuestionGenerator should stop execution"""
        if current_iteration >= self.max_iterations:
            return True, StopCondition.MAX_ITERATIONS_REACHED
        if current_confidence >= self.confidence_threshold:
            return True, StopCondition.CONFIDENCE_THRESHOLD_MET
        if not self.gap_query_queue and not self.unresolved_queries:
            return True, StopCondition.QUEUE_EMPTY
        return False, None

    def state_manager(self):
        """Manage gap query queue and process queries"""
        step_start = datetime.now()
        self.monitor.log_step("state_manager", "started", {
            "queue_size": len(self.gap_query_queue)
        })
        
        try:
            if not self.gap_query_queue:
                self.monitor.complete_step("state_manager", step_start, {
                    "queue_empty": True,
                    "query_processed": None
                })
                return None
            
            current_query = self.gap_query_queue.popleft()
            self.logger.info(f"Processing gap query: {current_query}")
            
            # Process through vector store system
            self._pass_query_to_vector_store_system(current_query)
            
            self.processed_queries.append(current_query)
            self.execution_results['queries_processed'] += 1
            
            self.monitor.complete_step("state_manager", step_start, {
                "query_processed": current_query,
                "remaining_queue_size": len(self.gap_query_queue),
                "total_processed": len(self.processed_queries)
            })
            
            return current_query
            
        except Exception as e:
            self.monitor.log_step("state_manager", "error", {
                "queue_size": len(self.gap_query_queue)
            }, str(e))
            self._handle_error(f"Error in state management: {str(e)}")
            return None

    def _pass_query_to_vector_store_system(self, gap_query: str):
        """Process gap query through vector store system"""
        step_start = datetime.now()
        self.monitor.log_step("vector_store_processing", "started", {
            "gap_query": gap_query
        })
        
        try:
            self.logger.info(f"🔗 Processing gap query through vector store system: '{gap_query}'")
            
            # Step 1: Generate vector store search queries
            vector_search_queries = self.generate_vector_store_queries(gap_query, max_queries=3)
            
            # Step 2: Run the research workflow
            self.logger.info("Running research workflow with web search and vector store...")
            
            research_data = asyncio.run(run_research_workflow(
                research_query=gap_query,
                max_web_results=5,
                search_queries=vector_search_queries
            ))
            
            # Step 3: Process the returned data
            processed_content = self._process_research_data(gap_query, research_data)
            
            # Step 4: Update execution results
            self.execution_results['external_system_calls'] += 1
            self.execution_results['content_items_added'] += len(processed_content)
            self.execution_results['sources_processed'] += len(research_data) if research_data else 0
            
            self.monitor.complete_step("vector_store_processing", step_start, {
                "vector_search_queries": vector_search_queries,
                "sources_found": len(research_data) if research_data else 0,
                "content_items_processed": len(processed_content),
                "success": True
            })
            
            self.logger.info(f"✅ Vector store system processing complete: Added {len(processed_content)} items")
            
            return {
                "success": True,
                "query": gap_query,
                "sources_found": len(research_data) if research_data else 0,
                "content_added": len(processed_content),
                "summary": f"Processed {len(research_data) if research_data else 0} sources, added {len(processed_content)} content items"
            }
            
        except Exception as e:
            self.monitor.log_step("vector_store_processing", "error", {
                "gap_query": gap_query
            }, str(e))
            self.logger.error(f"Error in vector store system: {str(e)}")
            return {
                "success": False,
                "query": gap_query,
                "error": str(e),
                "summary": f"Failed to process gap query '{gap_query}': {str(e)}"
            }
    
    def _process_research_data(self, gap_query: str, research_data: List[Dict]) -> List[str]:
        """
        Process the research data returned from run_research_workflow
        
        Args:
            gap_query: The original gap query
            research_data: List of dicts with 'source' and 'content' keys
            
        Returns:
            List of processed content strings
        """
        try:
            if not research_data:
                self.logger.warning("No research data to process")
                return []
            
            self.logger.info(f"Processing {len(research_data)} research documents")
            
            # Extract content from research data
            extracted_content = []
            for item in research_data:
                try:
                    # Your vector store returns: {"source": "url", "content": "text"}
                    content = item.get('content', '')
                    source = item.get('source', '')
                    
                    if content and len(content.strip()) > 50:  # Only substantial content
                        extracted_content.append({
                            'content': content[:1500] + "..." if len(content) > 1500 else content,
                            'source': source,
                            'gap_query': gap_query
                        })
                except Exception as e:
                    self.logger.warning(f"Error processing research item: {e}")
                    continue
            
            # Use LLM to process and filter the content for relevance
            if extracted_content:
                processed_insights = self._llm_process_research_content(gap_query, extracted_content)
                return processed_insights
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error processing research data: {str(e)}")
            return []
    
    def _llm_process_research_content(self, gap_query: str, content_list: List[Dict]) -> List[str]:
        """
        Use LLM to process and extract relevant insights from research content
        """
        try:
            # Prepare content for LLM analysis
            content_text = ""
            for i, item in enumerate(content_list, 1):
                content_text += f"\nSource {i} ({item['source']}):\n{item['content']}\n"
            
            prompt = f"""
You are a research analyst processing web search and vector store results. Extract the most relevant insights that address the gap query.

GAP QUERY: {gap_query}
ORIGINAL USER QUESTION: {self.user_query}

RESEARCH CONTENT:
{content_text}

Instructions:
1. Extract only information that directly addresses the gap query
2. Focus on factual, specific, and recent information
3. Remove redundant or duplicate information
4. Format as clear, actionable insights
5. Each insight should be substantial and valuable

Provide key insights as bullet points, one insight per line (without bullet symbols):
"""
            
            response = self._call_llm(prompt)
            
            # Parse insights from response
            insights = []
            for line in response.split('\n'):
                line = line.strip()
                if line and len(line) > 30:  # Filter substantial insights
                    # Remove any bullet points or numbering
                    clean_line = line.lstrip('-•*0123456789. ').strip()
                    if clean_line:
                        insights.append(clean_line)
            
            self.logger.info(f"LLM extracted {len(insights)} relevant insights")
            return insights[:8]  # Limit to top 8 insights
            
        except Exception as e:
            self.logger.warning(f"LLM processing of research content failed: {e}")
            # Fallback: return cleaned content excerpts
            return [item['content'][:200] + "..." for item in content_list[:5]]

    # LangGraph orchestrator (simple workflow)
    def _build_orchestrator(self):
        """Build simple LangGraph orchestrator for main workflow"""
        graph = StateGraph(OrchestratorState)
        
        graph.add_node("generate_gaps", self._orchestrator_generate_gaps)
        graph.add_node("process_queue", self._orchestrator_process_queue)
        graph.add_node("check_completion", self._orchestrator_check_completion)
        graph.add_node("check_elimination", self._orchestrator_check_elimination)
        
        # Simple linear flow with conditional continuation
        graph.add_edge(START, "generate_gaps")
        graph.add_edge("generate_gaps", "process_queue")
        graph.add_edge("process_queue", "check_elimination")
        graph.add_edge("check_elimination", "check_completion")
        
        # Conditional edge for continuation
        graph.add_conditional_edges(
            "check_completion",
            self._should_continue,
            {
                "continue": "generate_gaps",
                "stop": END
            }
        )
        
        return graph.compile(checkpointer=self.checkpointer)

    def _orchestrator_generate_gaps(self, state: OrchestratorState) -> OrchestratorState:
        """Generate gap queries step in orchestrator"""
        if state["current_iteration"] == 0:
            # First iteration - generate initial gaps
            self.generate_gap_queries()
        else:
            # Subsequent iterations - generate gaps for unresolved queries
            if self.unresolved_queries:
                for query in self.unresolved_queries:
                    self.gap_query_queue.append(query)
        
        return state

    def _orchestrator_process_queue(self, state: OrchestratorState) -> OrchestratorState:
        """Process all queries in queue"""
        while self.gap_query_queue:
            self.state_manager()
        return state

    def _orchestrator_check_elimination(self, state: OrchestratorState) -> OrchestratorState:
        """Check gap elimination"""
        self.check_gap_elimination()
        return state

    def _orchestrator_check_completion(self, state: OrchestratorState) -> OrchestratorState:
        """Check completion and update state"""
        completion_result = self.check_query_completeness()
        
        state["current_iteration"] += 1
        self.current_iteration = state["current_iteration"]
        
        # Check stop conditions
        should_stop, stop_condition = self.check_stop_conditions(
            state["current_iteration"],
            completion_result.confidence_score,
            self.previous_confidence
        )
        
        state["should_continue"] = not should_stop
        state["stop_condition"] = stop_condition
        
        self.previous_confidence = self.current_confidence
        self.stop_condition = stop_condition
        
        return state

    def _should_continue(self, state: OrchestratorState) -> str:
        """Determine if orchestrator should continue"""
        return "stop" if not state["should_continue"] else "continue"

    def run(self) -> Dict:
        """Main orchestrator function"""
        step_start = datetime.now()
        self.monitor.log_step("main_execution", "started", {
            "user_query": self.user_query,
            "max_iterations": self.max_iterations,
            "confidence_threshold": self.confidence_threshold
        })
        
        try:
            self.logger.info("Starting Gap Question Generator execution...")
            self.is_running = True
            
            # Initialize orchestrator state
            initial_state = {
                "current_iteration": 0,
                "should_continue": True,
                "stop_condition": None
            }
            
            # Run the LangGraph orchestrator
            config = {"configurable": {"thread_id": self.session_id}}
            final_state = self.orchestrator.invoke(initial_state, config)
            
            # Update final execution results
            self.execution_results['iterations_completed'] = final_state["current_iteration"]
            self.execution_results['final_confidence'] = self.current_confidence
            
            self.is_running = False
            
            self.monitor.complete_step("main_execution", step_start, {
                "stop_condition": self.stop_condition.value if self.stop_condition else None,
                "final_confidence": self.current_confidence,
                "iterations_completed": final_state["current_iteration"]
            })
            
            # Export monitoring logs
            self.monitor.export_logs(self.execution_results)
            
            self.logger.info(f"Gap Question Generator completed. Stop condition: {self.stop_condition}")
            self.logger.info(f"Execution logs exported to: {self.monitor.output_dir}")
            
            return self.execution_results
            
        except Exception as e:
            self.monitor.log_step("main_execution", "error", {
                "user_query": self.user_query
            }, str(e))
            self._handle_error(f"Error in main execution: {str(e)}")
            self.is_running = False
            
            # Export logs even on error
            self.monitor.export_logs(self.execution_results)
            
            return self.execution_results

    # Helper methods for LLM interactions and processing
    def _get_memory_summary(self) -> str:
        """Extract relevant context from YOUR REAL VECTOR STORE when needed"""
        try:
            # Use YOUR real vector store system directly
            temp_search_queries = [
                self.user_query,
                f"information about {self.user_query}",
                f"facts related to {self.user_query}"
            ]
            
            # Call YOUR run_research_workflow with no web search, just vector store
            memory_data = asyncio.run(run_research_workflow(
                query=self.user_query,
                max_web_results=0,  # No web search, just YOUR vector store
                search_queries=temp_search_queries
            ))
            
            if memory_data:
                # Extract content from YOUR data format
                content_pieces = []
                for item in memory_data:
                    if 'content' in item and item['content']:
                        content_pieces.append(item['content'][:500])
                
                return "\n".join(content_pieces) if content_pieces else "No memory context available"
            else:
                return "No memory context available"
                
        except Exception as e:
            self.logger.warning(f"Could not extract memory context: {str(e)}")
            return "Memory context unavailable"

    def _attempt_query_resolution(self, memory_content: str) -> Tuple[bool, List[str]]:
        """Attempt to resolve user query with existing memory content"""
        prompt = f"""
Analyze if the provided content can answer the user's query.

USER QUERY: {self.user_query}
CONTENT: {memory_content}

Respond: CAN_ANSWER: [YES/NO]
MISSING_INFO: [List missing info, one per line, or "None"]
"""
        
        try:
            response = self._call_llm(prompt)
            lines = response.strip().split('\n')
            can_answer = False
            missing_info = []
            
            for line in lines:
                if line.startswith('CAN_ANSWER:'):
                    can_answer = line.split(':', 1)[1].strip().upper() == 'YES'
                elif line.startswith('MISSING_INFO:'):
                    info = line.split(':', 1)[1].strip()
                    if info.lower() != 'none':
                        missing_info.append(info)
                elif line.strip() and missing_info:
                    missing_info.append(line.strip())
            
            return can_answer, missing_info
        except Exception as e:
            self.logger.warning(f"Error in query resolution: {str(e)}")
            return False, ["Unable to determine missing information"]

    def _generate_queries_for_missing_info(self, missing_info: List[str], max_questions: int) -> List[str]:
        """Generate web-optimized search queries for missing information"""
        if not missing_info:
            return []
        
        prompt = f"""
Generate web-optimized search queries for missing information.

USER QUERY: {self.user_query}
MISSING INFO: {chr(10).join([f"- {info}" for info in missing_info])}

Generate up to {max_questions} web search queries that are:
1. Already optimized for web search engines (short, keyword-focused)
2. Specific and directly searchable
3. Different from each other
4. Ready to use in web search without modification

Format: One query per line, no numbering or bullets.

QUERIES:
"""
        
        try:
            response = self._call_llm(prompt)
            queries = []
            for line in response.strip().split('\n'):
                line = line.strip().lstrip('- •*0123456789.)').strip()
                if line and len(line) > 3:
                    queries.append(line)
            
            # Remove duplicates and limit quantity
            return self._clean_and_limit_queries(queries, max_questions)
        except Exception as e:
            self.logger.warning(f"Error generating queries: {str(e)}")
            return []

    def _clean_and_limit_queries(self, queries: List[str], max_questions: int) -> List[str]:
        """Remove duplicates and limit query count"""
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for query in queries:
            normalized = query.lower().strip()
            if normalized not in seen and len(query.strip()) > 3:
                unique_queries.append(query)
                seen.add(normalized)
        
        return unique_queries[:max_questions]

    def _is_query_resolved(self, query: str, updated_memory: str) -> bool:
        """Check if a specific query is resolved with updated memory"""
        prompt = f"""
Can this query be answered with the provided information?

QUERY: {query}
INFORMATION: {updated_memory}

Answer: YES or NO
"""
        
        try:
            response = self._call_llm(prompt)
            return response.strip().upper().startswith('YES')
        except:
            return False

    def _call_llm(self, prompt: str) -> str:
        """Call LLM with error handling"""
        try:
            if hasattr(self.llm_client, 'generate'):
                response = self.llm_client.generate(prompt)
            elif hasattr(self.llm_client, 'complete'):
                response = self.llm_client.complete(prompt)
            elif callable(self.llm_client):
                response = self.llm_client(prompt)
            else:
                raise ValueError("Unknown LLM client interface")
            
            if hasattr(response, 'text'):
                return response.text
            elif isinstance(response, str):
                return response
            else:
                return str(response)
        except Exception as e:
            raise Exception(f"LLM call failed: {str(e)}")

    def _handle_error(self, error_message: str):
        """Handle errors with logging and tracking"""
        self.error_count += 1
        self.last_error = error_message
        self.logger.error(error_message)
        
        if self.error_count >= self.max_errors:
            self.logger.critical(f"Maximum error count ({self.max_errors}) reached")
            raise Exception(f"Too many errors encountered: {error_message}")


# Example Usage and Testing
def main():
    """
    Main example showing Gap Question Generator with Vector Store System
    """
    print("🚀 Starting Gap Question Generator with Vector Store Integration")
    print("=" * 70)
    
    try:
        # Initialize Gemini LLM client
        print("📡 Initializing Gemini LLM client...")
        gemini_client = GeminiLLMClient()
        print("✅ Gemini client initialized successfully")
        
        # Initialize mock vector store (you'll replace this with your real vector store)
        print("💾 Setting up vector store...")
        memory_store = MockVectorStore()
        print("✅ Vector store initialized")
        
        # Test queries
        user_queries = [
            "What is the current state of the AI market and its future prospects?",
            "How are recent advances in large language models affecting enterprise adoption?"
        ]
        
        for i, user_query in enumerate(user_queries, 1):
            print(f"\n📋 Example {i}: {user_query}")
            print("=" * 50)
            
            # Initialize Gap Question Generator
            generator = GapQuestionGenerator(
                llm_client=gemini_client,
                user_query=user_query,
                memory=memory_store,
                max_iterations=2,  # Reduced for demo
                confidence_threshold=0.85
            )
            
            print(f"🔧 Generator initialized with session_id: {generator.session_id}")
            
            # Test vector store query generation
            print("\n🔍 Testing vector store query generation:")
            test_gap_query = "latest AI market trends"
            vector_queries = generator.generate_vector_store_queries(test_gap_query, max_queries=3)
            print(f"Gap query: '{test_gap_query}'")
            print("Generated vector store queries:")
            for j, vq in enumerate(vector_queries, 1):
                print(f"  {j}. {vq}")
            
            # Run complete workflow with vector store integration
            print(f"\n🚀 Running complete workflow with vector store integration...")
            print("   This will:")
            print("   • Generate gap queries using Gemini")
            print("   • Create vector store search queries for each gap")
            print("   • Run research workflow (web search + vector store)")
            print("   • Process results with Gemini LLM")
            print("   • Check for gap resolution and completeness")
            print("   ⚠️  This may take a few minutes due to web requests...")
            
            results = generator.run()
            
            print("📊 Final Results:")
            print(f"  • Total gaps identified: {results['total_gaps_identified']}")
            print(f"  • Queries processed: {results['queries_processed']}")
            print(f"  • Vector store system calls: {results['external_system_calls']}")
            print(f"  • Content items added: {results['content_items_added']}")
            print(f"  • Sources processed: {results['sources_processed']}")
            print(f"  • Final confidence: {results['final_confidence']:.2f}")
            print(f"  • Iterations completed: {results['iterations_completed']}")
            print(f"  • Stop condition: {generator.stop_condition}")
            
            print("=" * 50)
            
            if i == 1:  # Only run first query for demo
                break
        
    except Exception as e:
        print(f"❌ Error in example execution: {str(e)}")
        print("💡 Make sure to:")
        print("   1. Set GOOGLE_API_KEY in .env file")
        print("   2. Install required dependencies")
        print("   3. Have the gap_questions.search_store_retrieve module available")

def main_with_mock():
    """Fallback demo with mock client"""
    print("🚀 Running Gap Question Generator Demo (Mock LLM Mode)")
    print("=" * 60)
    
    class MockGeminiClient:
        def generate(self, prompt):
            if "CAN_ANSWER" in prompt:
                return "CAN_ANSWER: NO\nMISSING_INFO: Current market data\nCompetitive landscape\nTechnology trends"
            elif "Generate web search" in prompt or "web search queries" in prompt.lower():
                return "AI market size 2024\nartificial intelligence trends\nmachine learning adoption enterprise"
            elif "vector store search queries" in prompt.lower() or "Generate" in prompt and "diverse search queries" in prompt:
                return "artificial intelligence market trends\nAI industry developments\nlarge language model innovations"
            elif "Can this query be answered" in prompt:
                return "NO"
            elif "research analyst processing" in prompt.lower():
                return "Global AI market experienced significant growth in 2024\nLarge language models showed major improvements in reasoning capabilities\nEnterprise adoption of AI increased substantially across industries"
            else:
                return "Analysis complete"
        
        def complete(self, prompt):
            return self.generate(prompt)
    
    # Mock run_research_workflow function
    async def mock_run_research_workflow(query, max_web_results=5, search_queries=None):
        """Mock version of run_research_workflow for testing"""
        import time
        await asyncio.sleep(1)  # Simulate processing time
        
        # Create mock data in your format: [{"source": "url", "content": "text"}]
        mock_data = []
        for i, search_query in enumerate(search_queries or [query], 1):
            mock_data.append({
                "source": f"https://example.com/source{i}",
                "content": f"Mock content for query '{search_query}': This contains relevant information about {query} with detailed analysis and recent developments."
            })
        
        return mock_data
    
    # Monkey patch the import for testing
    import sys
    import types
    mock_module = types.ModuleType('search_store_retrieve')
    mock_module.run_research_workflow = mock_run_research_workflow
    sys.modules['search_store_retrieve'] = mock_module
    
    mock_client = MockGeminiClient()
    user_query = "What is the current state of the AI market and its future prospects?"
    
    # Test with mock system
    generator = GapQuestionGenerator(
        llm_client=mock_client,
        user_query=user_query,
        memory=None,  # Using your vector store system
        max_iterations=2,
        confidence_threshold=0.85
    )
    
    print(f"📋 Processing Query: {user_query}")
    print("-" * 50)
    
    # Test vector store query generation
    print("\n🔍 Testing vector store query generation:")
    test_gap = "AI market trends 2024"
    vector_queries = generator.generate_vector_store_queries(test_gap)
    print(f"Gap query: '{test_gap}'")
    print("Generated vector store queries:")
    for i, vq in enumerate(vector_queries, 1):
        print(f"  {i}. {vq}")
    
    # Run complete workflow
    print("\n🚀 Running complete workflow with mock vector store system...")
    results = generator.run()
    
    # Show monitoring files
    print(f"\n📋 Execution Monitoring:")
    print(f"  • JSON log: {generator.monitor.output_dir}/{generator.session_id}_detailed_log.json")
    print(f"  • MD report: {generator.monitor.output_dir}/{generator.session_id}_execution_report.md")
    print(f"  • Processing steps: {len(generator.monitor.steps)}")
    
    print("\n✅ Demo completed successfully!")
    print("💡 To use real systems:")
    print("   1. Set GOOGLE_API_KEY in .env file")
    print("   2. Install search_store_retrieve module with Qdrant")
    print("   3. Run with real vector store")
    print(f"   4. Check execution logs in '{generator.monitor.output_dir}/' folder")

if __name__ == "__main__":
    # Check if .env file exists and provide helpful guidance
    env_file_path = ".env"
    
    if not os.path.exists(env_file_path):
        print("📄 Creating sample .env file...")
        sample_env_content = """# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Set other configurations
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your_langsmith_api_key_here
"""
        try:
            with open(env_file_path, 'w') as f:
                f.write(sample_env_content)
            print(f"✅ Created {env_file_path} file")
            print("📝 Please update the GOOGLE_API_KEY in the .env file")
            print("   You can get your API key from: https://makersuite.google.com/app/apikey")
        except Exception as e:
            print(f"❌ Could not create .env file: {e}")
    
    # Check if API key is available after loading .env
    if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_google_api_key_here":
        print("⚠️  WARNING: GOOGLE_API_KEY not properly set in .env file!")
        print(f"   Please edit {env_file_path} and add your actual Google API key")
        print("\n🔄 Running with mock responses for demonstration...")
        
        # Run with mock client for demonstration
        main_with_mock()
    else:
        print("✅ GOOGLE_API_KEY loaded successfully from .env file")
        main()