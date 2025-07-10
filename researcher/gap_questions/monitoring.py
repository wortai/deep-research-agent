"""
Execution monitoring and logging module
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class DetailedQueryData:
    """Detailed tracking data for individual queries"""
    
    def __init__(self, gap_query: str):
        self.gap_query = gap_query
        self.vector_queries = []
        self.llm_prompt = ""
        self.llm_response = ""
        self.urls_accessed = []
        self.content_from_urls = []
        self.vector_search_results = []
        self.insights_extracted = []
        self.timestamp = datetime.now().isoformat()


class ExecutionMonitor:
    """Comprehensive execution monitoring and logging"""
    
<<<<<<< HEAD
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
=======
    def __init__(self, session_id: str, file_logging: bool = True, terminal_logging: bool = False):
        self.session_id = session_id
        self.file_logging = file_logging
        self.terminal_logging = terminal_logging
        
        # Create output directory
        self.output_dir = Path(f"logs/gap_generation/{session_id}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging
        self.logger = logging.getLogger(f"GapGen_{session_id}")
        self._setup_logging()
        
        # Storage for execution data
        self.execution_steps = []
        self.llm_interactions = []
        self.query_data_logs = []
        self.start_time = datetime.now()
        
        self.logger.info(f"Monitoring initialized for session: {session_id}")
    
    def _setup_logging(self):
        """Setup file and console logging"""
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File logging
        if self.file_logging:
            file_handler = logging.FileHandler(
                self.output_dir / "execution.log", 
                encoding='utf-8'
            )
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # Terminal logging
        if self.terminal_logging:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
>>>>>>> 6fab7b3 (mid-work push)
    
    def log_step(self, step_name: str, status: str, data: Dict[str, Any] = None, error: str = None):
        """Log execution step"""
        step_data = {
            "step_name": step_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
<<<<<<< HEAD
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
=======
            "data": data or {},
            "error": error
>>>>>>> 6fab7b3 (mid-work push)
        }
        
        self.execution_steps.append(step_data)
        
        if status == "started":
            self.logger.info(f"STEP STARTED: {step_name} - {data}")
        elif status == "error":
            self.logger.error(f"STEP ERROR: {step_name} - {error}")
        else:
            self.logger.info(f"STEP {status.upper()}: {step_name}")
    
<<<<<<< HEAD
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
=======
    def complete_step(self, step_name: str, start_time: datetime, data: Dict[str, Any] = None):
        """Complete and log execution step"""
        duration = (datetime.now() - start_time).total_seconds()
>>>>>>> 6fab7b3 (mid-work push)
        
        step_data = {
            "step_name": step_name,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "data": data or {}
        }
        
        self.execution_steps.append(step_data)
        self.logger.info(f"STEP COMPLETED: {step_name} - Duration: {duration:.2f}s - {data}")
    
<<<<<<< HEAD
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
=======
    def log_llm_interaction(self, prompt: str, response: str, context: str = "general"):
        """Log LLM interaction"""
        interaction_data = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            "response_preview": response[:200] + "..." if len(response) > 200 else response
        }
>>>>>>> 6fab7b3 (mid-work push)
        
        self.llm_interactions.append(interaction_data)
        self.logger.info(f"LLM INTERACTION: {context} - Prompt: {len(prompt)} chars, Response: {len(response)} chars")
    
    def log_query_data(self, query_data: DetailedQueryData):
        """Log detailed query processing data"""
        query_log = {
            "gap_query": query_data.gap_query,
            "timestamp": query_data.timestamp,
            "vector_queries": query_data.vector_queries,
            "urls_accessed": query_data.urls_accessed,
            "vector_search_results_count": len(query_data.vector_search_results),
            "insights_extracted_count": len(query_data.insights_extracted),
            "content_sources_count": len(query_data.content_from_urls)
        }
        
        self.query_data_logs.append(query_log)
        self.logger.info(f"QUERY DATA: {query_data.gap_query} - Sources: {len(query_data.content_from_urls)}, Insights: {len(query_data.insights_extracted)}")
    
    def export_logs(self, execution_results: Dict[str, Any] = None):
        """Export all logs to files"""
        try:
            execution_time = (datetime.now() - self.start_time).total_seconds()
            
            # Comprehensive execution report
            report = {
                "session_info": {
                    "session_id": self.session_id,
                    "start_time": self.start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "total_execution_time": execution_time
                },
                "execution_results": execution_results or {},
                "execution_steps": self.execution_steps,
                "llm_interactions": {
                    "total_interactions": len(self.llm_interactions),
                    "interactions": self.llm_interactions
                },
                "query_processing": {
                    "total_queries_processed": len(self.query_data_logs),
                    "query_details": self.query_data_logs
                },
                "summary": {
                    "total_steps": len(self.execution_steps),
                    "total_llm_calls": len(self.llm_interactions),
                    "total_queries": len(self.query_data_logs),
                    "execution_time_seconds": execution_time
                }
            }
            
            # Save main report
            with open(self.output_dir / "execution_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Save individual log files
            with open(self.output_dir / "execution_steps.json", 'w', encoding='utf-8') as f:
                json.dump(self.execution_steps, f, indent=2, ensure_ascii=False)
            
            with open(self.output_dir / "llm_interactions.json", 'w', encoding='utf-8') as f:
                json.dump(self.llm_interactions, f, indent=2, ensure_ascii=False)
            
            with open(self.output_dir / "query_processing.json", 'w', encoding='utf-8') as f:
                json.dump(self.query_data_logs, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Logs exported to: {self.output_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to export logs: {e}")
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get current execution summary"""
        return {
            "session_id": self.session_id,
            "execution_time": (datetime.now() - self.start_time).total_seconds(),
            "total_steps": len(self.execution_steps),
            "total_llm_calls": len(self.llm_interactions),
            "total_queries_processed": len(self.query_data_logs),
            "output_directory": str(self.output_dir)
        }