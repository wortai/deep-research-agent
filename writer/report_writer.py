import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.states.subgraph_state import AgentGraphState as AgentState
from graphs.states.subgraph_state import UnifiedReportResponse
from writer.prompts_utils.writer_prompts import generate_unified_report_prompt
from llms import LlmsHouse


class Writer:
    """
    Generates unified research reports using 2 LLM calls.
    
    First call generates an optimized prompt analyzing user query, planner plan,
    and sections. Second call produces the complete report with ToC, abstract,
    introduction, chapter-based body, and conclusion.
    """

    def __init__(self):
        self.gemini_model = LlmsHouse().google_model('gemini-3-pro-preview')


    def _aggregate_sections_from_research_review(self, state: AgentState) -> list:
        """
        Extracts raw_research_results from each ResearchReviewData.
        
        Sorts by query_num first, then by parent_query within each review.
        Converts research results into section format for report generation.
        """
        aggregated_sections = []
        research_reviews = state.get('research_review', [])
        
        sorted_reviews = sorted(research_reviews, key=lambda r: r.get('query_num', 0))
        
        for review_data in sorted_reviews:
            raw_results = review_data.get('raw_research_results', [])
            
            sorted_results = sorted(raw_results, key=lambda r: r.get('parent_query', ''))
            
            for result in sorted_results:
                section = {
                    'section_content': f"# {result['query']}\n\n{result['answer']}"
                }
                aggregated_sections.append(section)
        
        return aggregated_sections


    async def _generate_unified_report(
        self,
        user_query: str,
        planner_queries: list,
        sections: list
    ) -> dict:
        """
        Second LLM call: generates complete unified report.
        
        Takes the optimized prompt from first call and produces the final report
        with all components (ToC, abstract, introduction, body, conclusion).
        
        Args:
            user_query: Original user research question
            planner_queries: List of planner query dicts
            sections: List of research section dicts
            
        Returns:
            Dict with table_of_contents, abstract, introduction, report_body, conclusion
        """
        # First LLM call: generate optimized prompt
        optimized_prompt = await generate_unified_report_prompt(
            user_query=user_query,
            planner_queries=planner_queries,
            sections=sections
        )
        
        # Format sections for second LLM call
        sections_formatted = "\n\n".join([
            f"=== SECTION {idx + 1} ===\n{section.get('section_content', '')}"
            for idx, section in enumerate(sections)
        ])
        
        # Second LLM call prompt
        final_prompt = f"""
{optimized_prompt}

=============================================================================
RESEARCH SECTIONS TO UNIFY (already in markdown with URLs embedded):
=============================================================================

{sections_formatted}

=============================================================================

NOW GENERATE THE COMPLETE UNIFIED REPORT following ALL instructions above.

OUTPUT STRUCTURE:
- table_of_contents: Markdown ToC with chapter/subchapter numbering
- abstract: Professional abstract (150-250 words)
- introduction: Comprehensive introduction with context and objectives
- report_body: Full report organized by chapters (1, 1.1, 2, 2.1...) in markdown
- conclusion: Synthesis with recommendations and future directions

CRITICAL REMINDERS:
✓ ALL content must be in valid markdown format
✓ Preserve URLs from sections and place next to relevant content
✓ Unify sections without major rewrites - organize and enhance presentation
✓ Use chapter hierarchy: # for chapters, ## for subchapters, ### for sub-subchapters
✓ Ensure smooth transitions and eliminate redundancy
✓ Directly address the user's query: "{user_query}"
"""
        
        # Configure model with max tokens and structured output
        model_with_structure = self.gemini_model.with_structured_output(
            UnifiedReportResponse
        ).with_config(
            {"max_output_tokens": 20000}
        )
        
        # Generate report
        structured_response = await model_with_structure.ainvoke(final_prompt)
        
        return {
            "table_of_contents": structured_response.table_of_contents,
            "abstract": structured_response.abstract,
            "introduction": structured_response.introduction,
            "report_body": structured_response.report_body,
            "conclusion": structured_response.conclusion
        }


    async def run(self, state: AgentState) -> dict:
        """
        Main entry point - generates complete unified report using 2 LLM calls.
        
        Aggregates sections from research_review, then generates unified report
        with table of contents, abstract, introduction, body, and conclusion.
        """
        aggregated_sections = self._aggregate_sections_from_research_review(state)
        
        if not aggregated_sections:
            print("Warning: No sections found in research_review")
            return {
                "table_of_contents": "# Table of Contents\n\nNo content available",
                "abstract": "No abstract - No sections available",
                "introduction": "No introduction - No sections available",
                "report_body": "No report body - No sections available",
                "conclusion": "No conclusion - No sections available"
            }

        user_query = state.get('user_query', 'Research Report')
        planner_queries = state.get('planner_query', [])
        
        report = await self._generate_unified_report(
            user_query=user_query,
            planner_queries=planner_queries,
            sections=aggregated_sections
        )
        
        return report


async def writer_node(state: AgentState) -> dict:
    """
    LangGraph node wrapper for Writer.
    
    Reads research_review from state, generates unified report,
    and returns structured output matching AgentGraphState fields.
    """
    writer = Writer()
    result = await writer.run(state)
    
    return {
        "report_table_of_contents": result["table_of_contents"],
        "report_abstract": result["abstract"],
        "report_introduction": result["introduction"],
        "report_body": result["report_body"],
        "report_conclusion": result["conclusion"]
    }


if __name__ == "__main__":
    pass
