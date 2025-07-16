"""
Monitoring and logging system for Gap Question Generator.
"""

import json
import os
from dataclasses import asdict
from datetime import datetime
from typing import List, Dict, Any

from ..models import ProcessingStep, DetailedQueryData


class ExecutionMonitor:
    """Comprehensive monitoring and logging system"""
    
    def __init__(self, session_id: str, output_dir: str = "gap_generator_logs", file_logging: bool = True, terminal_logging: bool = False):
        self.session_id = session_id
        self.output_dir = output_dir
        self.file_logging = file_logging
        self.terminal_logging = terminal_logging
        self.steps: List[ProcessingStep] = []
        self.start_time = datetime.now()
        self.detailed_queries: List[DetailedQueryData] = []
        self.all_urls_accessed: set = set()
        self.all_vector_queries: List[str] = []
        self.llm_interactions: List[Dict[str, Any]] = []
        if self.file_logging:
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
        if self.terminal_logging:
            print(f"[MONITOR] Step: {step_name} | Status: {status} | Details: {details}" + (f" | Error: {error_message}" if error_message else ""))
        
    def complete_step(self, step_name: str, start_time: datetime, details: Dict = None):
        """Mark a step as completed with duration"""
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        for step in reversed(self.steps):
            if step.step_name == step_name and step.status == 'started':
                step.status = 'completed'
                step.duration_ms = duration_ms
                if details:
                    step.details.update(details)
                if self.terminal_logging:
                    print(f"[MONITOR] Step: {step_name} | Status: completed | Duration: {duration_ms}ms | Details: {step.details}")
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
        if not self.file_logging:
            if self.terminal_logging:
                print("[MONITOR] File logging is disabled. No logs will be written to disk.")
            return
        self._export_json(execution_results)
        self._export_markdown(execution_results)
        self._export_detailed_data()
    
    def _export_json(self, execution_results: Dict):
        """Export comprehensive JSON log"""
        if not self.file_logging:
            return
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
        if not self.file_logging:
            return
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
        if not self.file_logging:
            return
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