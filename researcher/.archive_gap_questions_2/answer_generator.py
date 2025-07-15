"""
Gap query answer generation module
"""

import logging
from typing import List, Dict
from datetime import datetime
from .models import QnAResult


class AnswerGenerator:
    """Generates answers for gap queries using research data"""
    
    def __init__(self, llm_client, monitor=None):
        self.llm_client = llm_client
        self.monitor = monitor
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def answer_gap_query(self, gap_query: str, research_data: List[Dict], 
                        level: int, parent_query: str, user_query: str) -> QnAResult:
        """Generate answer for a gap query using research data"""
        step_start = datetime.now()
        
        if self.monitor:
            self.monitor.log_step("answer_gap_query", "started", {
                "gap_query": gap_query,
                "research_data_count": len(research_data),
                "level": level
            })
        
        try:
            if not research_data:
                # No research data available
                result = QnAResult(
                    gap_query=gap_query,
                    answer="No relevant information found to answer this query.",
                    confidence_score=0.0,
                    sources=[],
                    level=level,
                    parent_query=parent_query
                )
                
                if self.monitor:
                    self.monitor.complete_step("answer_gap_query", step_start, {
                        "confidence": 0.0,
                        "sources_count": 0
                    })
                
                return result
            
            # Extract content and sources
            content_text = ""
            sources = []
            
            for i, item in enumerate(research_data, 1):
                content = item.get('content', '')
                source = item.get('source', 'unknown')
                
                if content and len(content.strip()) > 50:
                    content_text += f"\nSource {i} ({source}):\n{content[:1000]}...\n"
                    sources.append(source)
            
            # Generate answer using LLM
            answer, confidence = self._generate_answer_with_llm(
                gap_query, content_text, user_query
            )
            
            result = QnAResult(
                gap_query=gap_query,
                answer=answer,
                confidence_score=confidence,
                sources=sources,
                level=level,
                parent_query=parent_query
            )
            
            if self.monitor:
                self.monitor.complete_step("answer_gap_query", step_start, {
                    "confidence": confidence,
                    "sources_count": len(sources)
                })
            
            self.logger.info(f"Generated answer for gap query with confidence: {confidence}")
            return result
            
        except Exception as e:
            if self.monitor:
                self.monitor.log_step("answer_gap_query", "error", {"gap_query": gap_query}, str(e))
            
            self.logger.error(f"Answer generation failed: {e}")
            return QnAResult(
                gap_query=gap_query,
                answer="Error occurred while generating answer.",
                confidence_score=0.0,
                sources=[],
                level=level,
                parent_query=parent_query
            )
    
    def _generate_answer_with_llm(self, gap_query: str, content_text: str, 
                                 user_query: str) -> tuple[str, float]:
        """Generate answer and confidence score using LLM"""
        try:
            prompt = f"""Answer the gap query using the provided research content.

GAP QUERY: {gap_query}
USER QUESTION: {user_query}

RESEARCH CONTENT:
{content_text}

Provide a comprehensive answer to the gap query based on the research content.
After your answer, provide a confidence score (0.0 to 1.0) indicating how well 
the content answers the gap query.

Format:
ANSWER: [Your detailed answer here]
CONFIDENCE: [0.0 to 1.0]"""
            
            response = self.llm_client.generate(prompt, context="gap_query_answering")
            
            # Parse response
            lines = response.strip().split('\n')
            answer = ""
            confidence = 0.5  # default
            
            capture_answer = False
            for line in lines:
                if line.startswith('ANSWER:'):
                    answer = line.split(':', 1)[1].strip()
                    capture_answer = True
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':', 1)[1].strip())
                        confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
                    except:
                        confidence = 0.5
                    capture_answer = False
                elif capture_answer and line.strip():
                    answer += " " + line.strip()
            
            if not answer:
                answer = response.strip()  # Fallback to full response
            
            return answer, confidence
            
        except Exception as e:
            self.logger.error(f"LLM answer generation failed: {e}")
            return "Unable to generate answer due to processing error.", 0.0