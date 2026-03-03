"""
Two-phase research report writer.

Phase 1 (_generate_outline_report): Uses full sections to produce
    table_of_contents, report_outline, abstract, introduction, conclusion.
Phase 2 (_generate_report_body_sections): Generates each chapter in parallel
    as a ReportBodySection with unique section_id for ordered preview.

Replaces the previous single-call approach that failed on large contexts.
"""

import sys
import os
import json
import re
import asyncio
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.types import StreamWriter
from graphs.states.subgraph_state import AgentGraphState as AgentState
from graphs.events.stream_emitter import get_emitter, StreamEmitter
from writer.prompts_utils.writer_prompts import (
    generate_outline_prompt, 
    generate_chapter_prompt, 
    choose_design_skill_prompt,
    generate_scoped_css_prompt,
    get_available_design_skills,
    DesignSkillSelection,
    CssGenerationResult
)
from llms import LlmsHouse
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Writer:
    """
    Generates research reports in two phases to avoid large-context failures.
    
    Phase 1: _generate_outline_report produces table_of_contents,
    report_outline (heading → [section_ids]), abstract, introduction,
    and conclusion from full research sections.
    Phase 2: _generate_report_body_sections generates each chapter in parallel.
    Returns a list of ReportBodySection dicts with UUID section_id,
    section_order, and section_content.
    """

    def __init__(self, emitter: StreamEmitter = None):
        self.gemini_model = LlmsHouse().google_model('gemini-2.5-flash')
        self.css_model = LlmsHouse().google_model('gemini-3.1-pro-preview') # As requested by user
        self._emitter = emitter

    def _emit_progress(self, percentage: int, current_step: str, metadata: dict = None) -> None:
        """
        Emit writer progress if emitter is available.

        Args:
            percentage: Progress percentage (0-100).
            current_step: Human-readable description of current activity.
            metadata: Optional extra data.
        """
        if self._emitter:
            self._emitter.emit_writer_progress(
                percentage=percentage,
                current_step=current_step,
                metadata=metadata
            )

    def _extract_json_from_response(self, text: str) -> dict:
        """
        Extracts a JSON object from raw LLM text output.

        Handles responses wrapped in markdown code blocks (```json ... ```).
        Falls back to finding the first { ... } block in the text.

        Args:
            text: Raw LLM response string.

        Returns:
            Parsed dict from the JSON content, or empty dict on failure.
        """
        code_block = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if code_block:
            try:
                return json.loads(code_block.group(1).strip())
            except json.JSONDecodeError:
                pass

        brace_match = re.search(r'\{.*\}', text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.error("[Writer] Could not extract JSON from LLM response")
        return {}

    def _aggregate_sections_from_research_review(self, state: AgentState) -> list:
        """
        Extracts raw_research_results from each ResearchReviewData.
        
        Filters by current_run_id to ensure only research from the current
        search cycle is used in the report.
        Sorts by query_num first, then by parent_query within each review.
        Converts research results into section format with section_id.
        """
        aggregated_sections = []
        current_run = state.get('current_run_id', '')
        
        # Only process research from the current run
        research_reviews = [
            r for r in state.get('research_review', [])
            if r.get('run_id') == current_run
        ]
        
        sorted_reviews = sorted(research_reviews, key=lambda r: r.get('query_num', 0))
        
        for review_data in sorted_reviews:
            raw_results = review_data.get('raw_research_results', [])
            sorted_results = sorted(raw_results, key=lambda r: r.get('parent_query', ''))
            
            for result in sorted_results:
                section = {
                    'section_content': f"# {result['query']}\n\n{result['answer']}",
                    'section_id': result.get('section_id', 'unknown')
                }
                aggregated_sections.append(section)
        
        return aggregated_sections

    def _build_section_index(self, sections: list) -> dict:
        """
        Builds a lookup dict mapping section_id to full section data.
        
        Args:
            sections: List of section dicts with section_id and section_content.
            
        Returns:
            Dict mapping section_id → section dict for O(1) lookups.
        """
        return {section.get('section_id', 'unknown'): section for section in sections}

    async def _generate_outline_report(
        self,
        user_query: str,
        planner_queries: list,
        sections: list
    ) -> dict:
        """
        Phase 1: Generates report outline with ToC, section mapping, abstract,
        introduction, and conclusion using full research sections.
        
        Calls generate_outline_prompt with full section content (no previews),
        then invokes gemini-3-pro-preview with ReportOutlineResponse structured
        output for table_of_contents, report_outline, abstract, introduction,
        and conclusion. 
        
        Args:
            user_query: Original user research question.
            planner_queries: List of planner query dicts.
            sections: List of section dicts with full content and section_id.
            
        Returns:
            Dict with table_of_contents, report_outline, abstract,
            introduction, and conclusion fields.
        """
        optimized_prompt = await generate_outline_prompt(
            user_query=user_query,
            planner_queries=planner_queries,
            sections=sections
        )

        sections_block = "RESEARCH SECTIONS (full content with section_id):\n"
        sections_block += "=" * 80 + "\n\n"
        for idx, section in enumerate(sections):
            content = section.get('section_content', '')
            section_id = section.get('section_id', 'unknown')
            sections_block += f"--- Section {idx + 1} [section_id: {section_id}] ---\n{content}\n\n"
        sections_block += "=" * 80 + "\n"

        final_prompt = f"""{optimized_prompt}

=============================================================================
Use the following sections IDs to refer to the section content.
{sections_block}
=============================================================================

NOW GENERATE THE REPORT OUTLINE following ALL instructions above.

You MUST respond with a SINGLE JSON object (no extra text before or after) with these five keys:

{{
  "table_of_contents": {{
    "1. Chapter Title": ["1.1 Subchapter", "1.2 Subchapter"],
    "2. Chapter Title": ["2.1 Subchapter"]
  }},
  "report_outline": {{
    "1. Chapter Title": ["section-id-1", "section-id-2"],
    "1.1 Subchapter": ["section-id-1", "section-id-2"],
    "1.2 Subchapter": ["section-id-3", "section-id-4"],
    "2. Chapter Title": ["section-id-5", "section-id-6"],
    "2.1 Subchapter": ["section-id-6"]
  }},
  "abstract": "Professional abstract in markdown...",
  "introduction": "Introduction in markdown...",
  "conclusion": "Conclusion in markdown..."
}}

AVAILABLE SECTION IDS: {[s.get('section_id', 'unknown') for s in sections]}

RULES:
- table_of_contents keys = main chapters, values = subchapter arrays
- report_outline keys = ALL headings (chapters + subchapters), values = section_id arrays
- Every section_id MUST appear in at least one heading
- Respond with ONLY the JSON object, no markdown fencing, no explanation
"""

        response = await self.gemini_model.ainvoke(final_prompt)
        raw_text = response.content if hasattr(response, 'content') else str(response)

        parsed = self._extract_json_from_response(raw_text)

        if not parsed or 'table_of_contents' not in parsed:
            logger.error("[Writer] Outline generation failed to produce valid JSON")
            all_ids = [s.get('section_id', '') for s in sections]
            return {
                "table_of_contents": {"1. Report": ["1.1 Content"]},
                "report_outline": {
                    "1. Report": all_ids,
                    "1.1 Content": all_ids
                },
                "abstract": "",
                "introduction": "",
                "conclusion": ""
            }

        return {
            "table_of_contents": parsed.get("table_of_contents", {}),
            "report_outline": parsed.get("report_outline", {}),
            "abstract": parsed.get("abstract", ""),
            "introduction": parsed.get("introduction", ""),
            "conclusion": parsed.get("conclusion", "")
        }

    async def _generate_design_css(
        self,
        user_query: str,
        table_of_contents: dict,
        abstract: str,
        introduction: str
    ) -> str:
        """
        Calls the LLM in a two-step process to generate custom scoped CSS:
        1. Selects the appropriate design skill from available libraries.
        2. Generates the CSS applying that specific skill's rules.
        """
        available_skills = get_available_design_skills()
        
        if not available_skills:
            logger.warning("[Writer] No design skills found. Falling back to empty CSS.")
            return ""

        # Step 1: Decide which design skill to use
        routing_prompt = await choose_design_skill_prompt(
            user_query=user_query,
            table_of_contents=table_of_contents,
            abstract=abstract,
            introduction=introduction,
            available_skills=available_skills
        )
        
        try:
            # Enforce structured output for selection
            routing_model = self.gemini_model.with_structured_output(DesignSkillSelection)
            route_response = await routing_model.ainvoke(routing_prompt)
            
            # The response is now directly a DesignSkillSelection object
            selected_filename = route_response.selected_skill_filename.strip()
            
            # Fallback if the LLM hallucinated a filename
            if selected_filename not in available_skills:
                logger.warning(f"[Writer] LLM selected unknown design skill: {selected_filename}. Defaulting to general_fallback.md")
                selected_filename = 'general_fallback.md'
                
            selected_rules = available_skills.get(selected_filename, "")
            logger.info(f"[Writer] Selected CSS Design Skill: {selected_filename}")
            
            # Emit progress showing which style was selected
            style_name = selected_filename.replace('.md', '').replace('_', ' ').title()
            self._emit_progress(88, f"Applying '{style_name}' aesthetic to the report...")

        except Exception as e:
            logger.error(f"[Writer] Error selecting design skill: {e}")
            selected_filename = 'general_fallback.md'
            selected_rules = available_skills.get(selected_filename, "")

        # Step 2: Generate the CSS using the elite model and the selected rules
        css_prompt = await generate_scoped_css_prompt(
            user_query=user_query,
            table_of_contents=table_of_contents,
            selected_skill_name=selected_filename,
            selected_skill_rules=selected_rules
        )
        
        try:
            # Enforce structured output for generation
            styled_css_model = self.css_model.with_structured_output(CssGenerationResult)
            response = await styled_css_model.ainvoke(css_prompt)
            
            # Extract pure string from Pydantic object
            raw_text = response.css_code.strip()
            
            # Clean up potential markdown code block artifacts just in case
            if '```css' in raw_text:
                raw_text = raw_text.split('```css')[1].split('```')[0].strip()
            elif '```' in raw_text:
                raw_text = raw_text.split('```')[1].split('```')[0].strip()
                
            return raw_text.strip()
        except Exception as e:
            logger.error(f"[Writer] CSS generation failed: {e}")
            return ""


    async def _generate_single_chapter(
        self,
        chapter_heading: str,
        section_ids: list,
        section_index: dict,
        table_of_contents: dict
    ) -> str:
        """
        Generates complete markdown content for one chapter/subchapter.
        
        Filters full sections by section_id from section_index, calls
        generate_chapter_prompt, and invokes LLM. Returns raw markdown
        including heading — ready to become a ReportBodySection.
        
        Args:
            chapter_heading: The heading to generate (e.g. "1.1 Architecture").
            section_ids: List of section_ids assigned to this chapter.
            section_index: Dict mapping section_id → full section data.
            table_of_contents: Full ToC dict for context.
            
        Returns:
            Complete chapter content as markdown string (heading included).
        """
        sections_for_chapter = []
        for sid in section_ids:
            if sid in section_index:
                sections_for_chapter.append(section_index[sid])
            else:
                logger.warning(f"[Writer] section_id '{sid}' not found in index, skipping")

        if not sections_for_chapter:
            logger.warning(f"[Writer] No sections found for chapter: {chapter_heading}")
            return f"## {chapter_heading}\n\nNo content available for this section.\n"

        prompt = await generate_chapter_prompt(
            chapter_heading=chapter_heading,
            table_of_contents=table_of_contents,
            sections_for_chapter=sections_for_chapter
        )

        response = await self.gemini_model.ainvoke(prompt)
        raw_text = response.content if hasattr(response, 'content') else str(response)

        if not raw_text or not raw_text.strip():
            logger.error(f"[Writer] Chapter generation returned empty for: {chapter_heading}")
            fallback = "\n\n".join([s.get('section_content', '') for s in sections_for_chapter])
            return f"## {chapter_heading}\n\n{fallback}\n"

        return raw_text.strip()


    async def _generate_report_body_sections(
        self,
        report_outline: dict,
        section_index: dict,
        table_of_contents: dict
    ) -> list:
        """
        Phase 2: Generates all chapters in parallel and returns ordered sections.
        
        For each heading in report_outline, creates a parallel task via
        _generate_single_chapter. Each task returns a complete chapter string.
        Results are wrapped in ReportBodySection dicts with UUID section_id,
        sequential section_order, and the raw markdown as section_content.
        
        Args:
            report_outline: Dict mapping heading → [section_ids].
            section_index: Dict mapping section_id → full section data.
            table_of_contents: ToC dict defining chapter order.
            
        Returns:
            List of ReportBodySection dicts ordered by section_order.
        """
        ordered_headings = []
        for main_chapter, subchapters in table_of_contents.items():
            ordered_headings.append(main_chapter)
            for sub in subchapters:
                ordered_headings.append(sub)

        tasks = []
        heading_order = []

        for heading in ordered_headings:
            section_ids = report_outline.get(heading, [])
            if not section_ids:
                continue
            
            heading_order.append(heading)
            tasks.append(
                self._generate_single_chapter(
                    chapter_heading=heading,
                    section_ids=section_ids,
                    section_index=section_index,
                    table_of_contents=table_of_contents
                )
            )

        total_chapters = len(tasks)
        chapters_done = 0
        chapter_progress_lock = asyncio.Lock()

        async def _tracked_chapter(coro, heading: str):
            """Wraps a chapter coroutine to emit progress on completion."""
            nonlocal chapters_done
            result = await coro
            async with chapter_progress_lock:
                chapters_done += 1
                pct = 30 + int((chapters_done / total_chapters) * 60)
                self._emit_progress(
                    percentage=min(pct, 90),
                    current_step=f"Chapter done: {heading[:60]}… ({chapters_done}/{total_chapters})",
                    metadata={"chapters_done": chapters_done, "chapters_total": total_chapters}
                )
            return result

        tracked_tasks = [
            _tracked_chapter(task, heading)
            for task, heading in zip(tasks, heading_order)
        ]
        chapter_contents = await asyncio.gather(*tracked_tasks)

        report_body_sections = []
        for order_idx, content in enumerate(chapter_contents, start=1):
            report_body_sections.append({
                "section_id": str(uuid.uuid4()),
                "section_order": order_idx,
                "section_content": content
            })

        return report_body_sections

    def _format_table_of_contents_markdown(self, table_of_contents: dict) -> str:
        """
        Converts table_of_contents dict into formatted markdown string.
        
        Args:
            table_of_contents: Dict where keys are main chapters, values are subchapter arrays.
            
        Returns:
            Markdown-formatted table of contents string.
        """
        lines = ["# Table of Contents\n"]
        for main_chapter, subchapters in table_of_contents.items():
            lines.append(f"- **{main_chapter}**")
            for sub in subchapters:
                lines.append(f"  - {sub}")
        return "\n".join(lines)

    async def run(self, state: AgentState) -> dict:
        """
        Orchestrates two-phase report generation with progress streaming.
        
        Phase 1: Aggregates sections → generates outline (ToC, section mapping,
        abstract, introduction, conclusion).
        Phase 2: Generates each chapter in parallel → returns report_body_sections.
        Emits writer progress events via StreamEmitter at each milestone.
        
        Returns:
            Dict with table_of_contents, abstract, introduction,
            report_body_sections (list of section dicts), and conclusion.
        """
        self._emit_progress(5, "Reading through all agent research and understanding the data…")

        aggregated_sections = self._aggregate_sections_from_research_review(state)
        
        if not aggregated_sections:
            logger.warning("[Writer] No sections found in research_review")
            return {
                "table_of_contents": "# Table of Contents\n\nNo content available",
                "abstract": "",
                "introduction": "",
                "report_body_sections": [],
                "conclusion": ""
            }

        user_query = state.get('user_query', 'Research Report')
        planner_queries = state.get('planner_query', [])

        self._emit_progress(15, "Figuring out what our chapters should look like…")

        outline = await self._generate_outline_report(
            user_query=user_query,
            planner_queries=planner_queries,
            sections=aggregated_sections
        )

        table_of_contents = outline["table_of_contents"]
        report_outline = outline["report_outline"]
        total_chapters = len(report_outline)

        section_index = self._build_section_index(aggregated_sections)

        self._emit_progress(
            30,
            f"Outline locked in. Writing {total_chapters} chapters in parallel…",
            metadata={"chapters_total": total_chapters}
        )

        report_body_sections = await self._generate_report_body_sections(
            report_outline=report_outline,
            section_index=section_index,
            table_of_contents=table_of_contents
        )

        self._emit_progress(85, "Designing and generating custom aesthetic CSS for the report…")
        
        css_content = await self._generate_design_css(
            user_query=user_query,
            table_of_contents=table_of_contents,
            abstract=outline.get("abstract", ""),
            introduction=outline.get("introduction", "")
        )

        self._emit_progress(95, "Stitching everything together into the final report…")

        toc_markdown = self._format_table_of_contents_markdown(table_of_contents)

        self._emit_progress(100, "Hell yeah, report complete! 🎉")

        return {
            "table_of_contents": toc_markdown,
            "abstract": outline["abstract"],
            "introduction": outline["introduction"],
            "report_body_sections": report_body_sections,
            "conclusion": outline["conclusion"],
            "css": css_content
        }


async def writer_node(state: AgentState, writer: StreamWriter) -> dict:
    """
    LangGraph node wrapper for Writer.
    
    Accepts StreamWriter from LangGraph to emit real-time progress events.
    Reads research_review from state, generates outline + parallel body sections,
    and returns structured output appended to the `reports` list.
    """
    emitter = get_emitter(writer)
    writer_instance = Writer(emitter=emitter)
    result = await writer_instance.run(state)
    
    report_data = {
        "run_id": state.get("current_run_id", ""),
        "query": state.get("user_query", ""),
        "table_of_contents": result["table_of_contents"],
        "abstract": result["abstract"],
        "introduction": result["introduction"],
        "body_sections": result["report_body_sections"],
        "conclusion": result["conclusion"],
        "css": result.get("css", ""),
        "timestamp": datetime.utcnow().isoformat()
    }

    return {"reports": [report_data]}


if __name__ == "__main__":
    pass
