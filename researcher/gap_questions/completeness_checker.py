"""
Query completeness checking module
"""

import logging
from typing import List, Dict
from datetime import datetime
from .models import QnAResult, CompletionCheckResult


class CompletenessChecker:
    """Checks if queries are complete and generates new gap queries if needed"""
    
    def __init__(self, llm_client, monitor=None):
        self.llm_client = llm_client
        self.monitor = monitor
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def check_query_completeness(self, qna_result: QnAResult, user_query: str, 
                               current_level: int, max_depth: int, 
                               parent_query_counts: Dict[str, int],
                               max_gap_queries_per_parent: int) -> CompletionCheckResult:
        """
        Check if query is complete or needs more gap queries.
        Takes in QnA and determines if more gap queries are needed.
        """
        step_start = datetime.now()
        
        if self.monitor:
            self.monitor.log_step("check_completeness", "started", {
                "gap_query": qna_result.gap_query,
                "current_level": current_level,
                "confidence": qna_result.confidence_score,
                "current_children": parent_query_counts.get(qna_result.gap_query, 0),
                "max_children_allowed": max_gap_queries_per_parent
            })
        
        try:
            # Check if we've reached max depth
            if current_level >= max_depth:
                result = CompletionCheckResult(
                    is_complete=True,
                    confidence_score=qna_result.confidence_score,
                    new_gap_queries=[],
                    reasoning="Maximum depth reached",
                    parent_limit_reached=False
                )
                
                if self.monitor:
                    self.monitor.complete_step("check_completeness", step_start, {
                        "complete": True,
                        "reason": "max_depth"
                    })
                
                return result
            
            # Check if parent already has maximum gap queries
            current_children = parent_query_counts.get(qna_result.gap_query, 0)
            if current_children >= max_gap_queries_per_parent:
                result = CompletionCheckResult(
                    is_complete=True,
                    confidence_score=qna_result.confidence_score,
                    new_gap_queries=[],
                    reasoning=f"Maximum gap queries per parent reached ({current_children}/{max_gap_queries_per_parent})",
                    parent_limit_reached=True
                )
                
                if self.monitor:
                    self.monitor.complete_step("check_completeness", step_start, {
                        "complete": True,
                        "reason": "parent_limit_reached",
                        "current_children": current_children,
                        "max_allowed": max_gap_queries_per_parent
                    })
                
                return result
            
            # Check if confidence is high enough
            if qna_result.confidence_score >= 0.8:
                result = CompletionCheckResult(
                    is_complete=True,
                    confidence_score=qna_result.confidence_score,
                    new_gap_queries=[],
                    reasoning="High confidence answer achieved",
                    parent_limit_reached=False
                )
                
                if self.monitor:
                    self.monitor.complete_step("check_completeness", step_start, {
                        "complete": True,
                        "reason": "high_confidence"
                    })
                
                return result
            
            # Use LLM to determine if more gap queries are needed
            new_gap_queries, reasoning, confidence = self._analyze_completeness_with_llm(
                qna_result, user_query
            )
            
            # Respect the parent limit - only take what we can fit
            remaining_slots = max_gap_queries_per_parent - current_children
            if len(new_gap_queries) > remaining_slots:
                new_gap_queries = new_gap_queries[:remaining_slots]
                reasoning += f" (Limited to {remaining_slots} queries due to parent limit)"
            
            is_complete = len(new_gap_queries) == 0
            
            result = CompletionCheckResult(
                is_complete=is_complete,
                confidence_score=confidence,
                new_gap_queries=new_gap_queries,
                reasoning=reasoning,
                parent_limit_reached=(current_children + len(new_gap_queries)) >= max_gap_queries_per_parent
            )
            
            if self.monitor:
                self.monitor.complete_step("check_completeness", step_start, {
                    "complete": is_complete,
                    "new_queries_count": len(new_gap_queries),
                    "confidence": confidence,
                    "current_children": current_children,
                    "new_children_added": len(new_gap_queries),
                    "parent_limit_reached": result.parent_limit_reached
                })
            
            self.logger.info(f"Completeness check: {'Complete' if is_complete else f'{len(new_gap_queries)} new queries'} (Parent: {current_children + len(new_gap_queries)}/{max_gap_queries_per_parent})")
            return result
            
        except Exception as e:
            if self.monitor:
                self.monitor.log_step("check_completeness", "error", 
                                    {"gap_query": qna_result.gap_query}, str(e))
            
            self.logger.error(f"Completeness check failed: {e}")
            return CompletionCheckResult(
                is_complete=True,
                confidence_score=0.0,
                new_gap_queries=[],
                reasoning="Error during completeness check",
                parent_limit_reached=False
            )
    
    def _analyze_completeness_with_llm(self, qna_result: QnAResult, 
                                     user_query: str) -> tuple[List[str], str, float]:
        """Use LLM to analyze completeness and generate new gap queries"""
        try:
            prompt = f"""Analyze if this gap query and answer is complete or needs more investigation.

USER QUESTION: {user_query}
GAP QUERY: {qna_result.gap_query}
ANSWER: {qna_result.answer}
CURRENT CONFIDENCE: {qna_result.confidence_score}

Determine:
1. Is this gap query sufficiently answered?
2. Are there follow-up questions needed to better address the original user question?
3. What specific gap queries would help improve understanding?

If the answer is sufficient (confidence > 0.7), respond with "COMPLETE".
If more investigation is needed, generate 1-3 specific gap queries that would help.

Format:
STATUS: [COMPLETE or NEEDS_MORE]
REASONING: [Brief explanation]
CONFIDENCE: [0.0 to 1.0 overall confidence]
GAP_QUERIES: [List new gap queries, one per line, or "None"]"""
            
            response = self.llm_client.generate(prompt, context="completeness_analysis")
            
            # Parse response
            lines = response.strip().split('\n')
            status = "COMPLETE"
            reasoning = "No reasoning provided"
            confidence = qna_result.confidence_score
            gap_queries = []
            
            capture_queries = False
            for line in lines:
                if line.startswith('STATUS:'):
                    status = line.split(':', 1)[1].strip()
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':', 1)[1].strip())
                        confidence = max(0.0, min(1.0, confidence))
                    except:
                        confidence = qna_result.confidence_score
                elif line.startswith('GAP_QUERIES:'):
                    query_text = line.split(':', 1)[1].strip()
                    if query_text.lower() != 'none':
                        gap_queries.append(query_text)
                    capture_queries = True
                elif capture_queries and line.strip() and not line.startswith(('STATUS:', 'REASONING:', 'CONFIDENCE:')):
                    gap_queries.append(line.strip())
            
            # Clean up gap queries
            gap_queries = [q for q in gap_queries if len(q.strip()) > 10][:3]  # Max 3 queries
            
            if status == "COMPLETE":
                gap_queries = []
            
            return gap_queries, reasoning, confidence
            
        except Exception as e:
            self.logger.error(f"LLM completeness analysis failed: {e}")
            return [], "Analysis failed", qna_result.confidence_score