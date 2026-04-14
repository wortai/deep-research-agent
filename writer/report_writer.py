"""
Two-phase research report writer producing HTML output.

Phase 1 (_generate_outline_report): Uses full sections to produce
    table_of_contents, report_outline, abstract, introduction, conclusion.
Phase 1.5 (_generate_design_instructions): Selects a design skill and
    produces a comprehensive visual style brief (colors, fonts, spacing).
Phase 2 (_generate_report_body_sections): Generates each chapter in parallel
    as self-contained HTML sections guided by the design instructions.
"""

import sys
import os
import json
import re
import asyncio
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.types import StreamWriter
from graphs.states.subgraph_state import AgentGraphState as AgentState
from graphs.events.stream_emitter import get_emitter, StreamEmitter
from writer.prompts_utils.writer_prompts import (
    generate_chapter_prompt,
    choose_design_skill_prompt,
    generate_design_instructions_prompt,
    generate_single_chapter_outline_prompt,
    generate_framing_guidance_prompt,
    get_available_design_skills,
    DesignSkillSelection,
    DesignInstructionsResult,
)
from llms import LlmsHouse
import uuid
from datetime import datetime
from typing import Optional
from utils.cost_tracker import CostTracker
from utils.errors import LLMCatchError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default report writer LLM when the user does not supply manual API keys + model picks
# (see FrontEnd ChatInput: without provider keys, model_selections are not sent).
DEFAULT_REPORT_WRITER_GROK_MODEL = "grok-4-1-fast-reasoning"


class Writer:
    """
    Generates research reports as HTML in two phases to avoid large-context failures.

    Phase 1: _generate_outline_report produces table_of_contents,
    report_outline (heading → [section_ids]), abstract, introduction,
    and conclusion from full research sections.
    Phase 1.5: _generate_design_instructions selects a design skill and
    creates a detailed visual style brief (colors, fonts, spacing, charts).
    Phase 2: _generate_report_body_sections generates each chapter in parallel
    as self-contained HTML guided by the design instructions.
    """

    def __init__(
        self,
        emitter: StreamEmitter = None,
        api_keys: dict = None,
        model_selections: dict = None,
    ):
        self._api_keys = api_keys or {}
        self._model_selections = model_selections or {}
        openai_key = self._api_keys.get("openai")
        google_key = self._api_keys.get("gemini")
        anthropic_key = self._api_keys.get("anthropic")

        def _grok(temperature: float, max_tokens: Optional[int] = None):
            """LlmsHouse Grok; uses GROK_API_KEY from env, or optional `grok` in api_keys."""
            extra: dict = {}
            if max_tokens is not None:
                extra["max_tokens"] = max_tokens
            if self._api_keys.get("grok"):
                extra["xai_api_key"] = self._api_keys["grok"]
            return LlmsHouse().grok_model(
                DEFAULT_REPORT_WRITER_GROK_MODEL,
                temperature=temperature,
                **extra,
            )

        # Chapter HTML: user's OpenAI + openai_model if both set; else default Grok.
        openai_model_name = self._model_selections.get("openai_model")
        if openai_model_name and openai_key:
            self.chapter_model = LlmsHouse().openai_model(
                openai_model_name,
                temperature=0.9,
                max_tokens=6000,
                api_key=openai_key,
            )
        else:
            self.chapter_model = _grok(temperature=0.9, max_tokens=6000)

        # Outline / framing JSON: user's Gemini + gemini_model if both set; else Grok.
        gemini_model_name = self._model_selections.get("gemini_model")
        if gemini_model_name and google_key:
            self.outline_model = LlmsHouse().google_model(
                gemini_model_name, api_key=google_key
            )
        else:
            self.outline_model = _grok(temperature=0.95)

        # Design instructions (structured): same rule as outline.
        if gemini_model_name and google_key:
            self.design_model = LlmsHouse().google_model(
                gemini_model_name, temperature=1.25, api_key=google_key
            )
        else:
            self.design_model = _grok(temperature=1.25)

        # Design skill routing (structured): same rule as outline.
        if gemini_model_name and google_key:
            self.lower_gemini_model = LlmsHouse().google_model(
                gemini_model_name, api_key=google_key
            )
        else:
            self.lower_gemini_model = _grok(temperature=0.95)

        anthropic_model_name = self._model_selections.get("anthropic_model")
        if anthropic_model_name and anthropic_key:
            self.anthropic_model = LlmsHouse().anthropic_model(
                anthropic_model_name, api_key=anthropic_key
            )
        else:
            self.anthropic_model = None

        self._emitter = emitter

    def _emit_progress(
        self, percentage: int, current_step: str, metadata: dict = None
    ) -> None:
        """
        Emit writer progress if emitter is available.

        Args:
            percentage: Progress percentage (0-100).
            current_step: Human-readable description of current activity.
            metadata: Optional extra data.
        """
        if self._emitter:
            self._emitter.emit_writer_progress(
                percentage=percentage, current_step=current_step, metadata=metadata
            )

    @staticmethod
    def _response_text(response) -> str:
        """
        Extracts plain text from an LLM response object.

        Handles both legacy models (response.content is a str) and newer
        models (response.content is a list of content blocks, e.g. Gemini 3.x).

        Args:
            response: LangChain LLM response object.

        Returns:
            String text content from the response.
        """
        content = response.content if hasattr(response, "content") else str(response)
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    parts.append(block["text"])
                elif isinstance(block, str):
                    parts.append(block)
            return "".join(parts) if parts else str(content)
        return str(content)

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
        code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if code_block:
            try:
                return json.loads(code_block.group(1).strip())
            except json.JSONDecodeError:
                pass

        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
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
        current_run = state.get("current_run_id", "")

        research_reviews = [
            r
            for r in state.get("research_review", [])
            if r.get("run_id") == current_run
        ]

        sorted_reviews = sorted(research_reviews, key=lambda r: r.get("query_num", 0))

        for review_data in sorted_reviews:
            raw_results = review_data.get("raw_research_results", [])
            sorted_results = sorted(
                raw_results, key=lambda r: r.get("parent_query", "")
            )

            for result in sorted_results:
                section = {
                    "section_content": f"# {result['query']}\n\n{result['answer']}",
                    "section_id": result.get("section_id", "unknown"),
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
        return {section.get("section_id", "unknown"): section for section in sections}

    async def _generate_chapter_outline(
        self,
        chapter_num: int,
        total_chapters: int,
        review_data: dict,
        all_queries: list,
    ) -> dict:
        """
        Generates the outline for exactly ONE chapter from a single ResearchReviewData.

        Calls outline_model with generate_single_chapter_outline_prompt which contains
        only this query's sections (~5-10k tokens). Returns a dict with chapter_title,
        subchapters list, and the outline mapping (heading -> [section_ids]).

        Args:
            chapter_num: 1-based position of this chapter in the report.
            total_chapters: Total number of chapters (for positional awareness prompt).
            review_data: ResearchReviewData dict with `query` and `raw_research_results`.
            all_queries: Full ordered planner_query list for positional context in prompt.

        Returns:
            Dict with keys: chapter_title (str), subchapters ([str]), outline ({str: [str]}).
            Falls back to a safe default on parse failure.
        """
        query = review_data.get("query", f"Chapter {chapter_num}")
        raw_results = review_data.get("raw_research_results", [])

        sections = [
            {
                "section_content": f"# {r.get('query', '')}\n\n{r.get('answer', '')}",
                "section_id": r.get("section_id", "unknown"),
            }
            for r in sorted(raw_results, key=lambda r: r.get("parent_query", ""))
        ]

        if not sections:
            fallback_title = f"{chapter_num}. {query}"
            return {
                "chapter_title": fallback_title,
                "subchapters": [f"{chapter_num}.1 Overview"],
                "outline": {fallback_title: [], f"{chapter_num}.1 Overview": []},
            }

        prompt = generate_single_chapter_outline_prompt(
            chapter_num=chapter_num,
            total_chapters=total_chapters,
            query=query,
            sections=sections,
            all_queries=all_queries,
        )

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = await self.outline_model.ainvoke(prompt)
                raw_text = self._response_text(response)
                parsed = self._extract_json_from_response(raw_text)

                if parsed and "chapter_title" in parsed and "outline" in parsed:
                    return parsed

                logger.warning(
                    f"[Writer] Chapter {chapter_num} outline parse failed (attempt {attempt + 1})"
                )
            except Exception as exc:
                logger.warning(
                    f"[Writer] Chapter {chapter_num} outline error (attempt {attempt + 1}): {exc}"
                )
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)

        # Retries exhausted. Raise a catchable error so the graph pauses safely
        error_msg = f"[Writer] Exhausted retries attempting to generate outline for: {query}"
        logger.error(error_msg)
        raise LLMCatchError(
            message=error_msg,
            raw_output="",
            error_details="Max retries reached without a valid JSON parse."
        )

    async def _generate_framing_guidance(
        self,
        user_query: str,
        ordered_chapter_titles: list,
    ) -> dict:
        """
        Generates TEXT guidance for abstract, introduction, and conclusion.

        Returns descriptive text (not HTML) that will be fed into
        generate_chapter_prompt so these sections are rendered with the
        same design, theme, and page structure as body chapters.

        Args:
            user_query: Original research question from the user.
            ordered_chapter_titles: List of top-level chapter title strings in order.

        Returns:
            Dict with keys abstract, introduction, conclusion (all text guidance strings).
        """
        prompt = generate_framing_guidance_prompt(
            user_query=user_query,
            ordered_chapter_titles=ordered_chapter_titles,
        )

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = await self.outline_model.ainvoke(prompt)
                raw_text = self._response_text(response)
                parsed = self._extract_json_from_response(raw_text)

                if parsed and "abstract" in parsed:
                    return {
                        "abstract": parsed.get("abstract", ""),
                        "introduction": parsed.get("introduction", ""),
                        "conclusion": parsed.get("conclusion", ""),
                    }

                logger.warning(
                    f"[Writer] Framing guidance parse failed (attempt {attempt + 1})"
                )
            except Exception as exc:
                logger.warning(
                    f"[Writer] Framing guidance error (attempt {attempt + 1}): {exc}"
                )
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)

        error_msg = f"[Writer] Framing guidance failed after {max_retries} retries."
        logger.error(error_msg)
        raise LLMCatchError(
            message=error_msg,
            raw_output="",
            error_details="Max retries reached without parsing framing guidance."
        )

    async def _generate_outline_report(
        self,
        user_query: str,
        planner_queries: list,
        sections: list,
        state: dict = None,
    ) -> dict:
        """
        Phase 1: Generates report outline via N parallel per-query LLM calls.

        Each ResearchReviewData maps to exactly one numbered chapter with any
        number of subchapters and a section_id mapping. The merge produces the
        same table_of_contents and report_outline format that Phase 2 consumes,
        so the chapter body generation is unchanged.

        After merging, a lightweight framing call generates abstract, introduction,
        and conclusion from only the ordered chapter titles (no raw section text).

        Args:
            user_query: Original user research question.
            planner_queries: Ordered list of planner query dicts.
            sections: Aggregated flat sections list (for fallback reference only).
            state: AgentState dict — used to access research_review directly.

        Returns:
            Dict with table_of_contents, report_outline, abstract, introduction, conclusion.
        """
        if state is None:
            state = {}

        current_run = state.get("current_run_id", "")
        research_reviews = [
            r
            for r in state.get("research_review", [])
            if r.get("run_id") == current_run
        ]
        sorted_reviews = sorted(research_reviews, key=lambda r: r.get("query_num", 0))

        if not sorted_reviews:
            all_ids = [s.get("section_id", "") for s in sections]
            return {
                "table_of_contents": {"1. Report": ["1.1 Content"]},
                "report_outline": {"1. Report": all_ids, "1.1 Content": all_ids},
                "abstract": "",
                "introduction": "",
                "conclusion": "",
            }

        total = len(sorted_reviews)

        outlines_done = 0
        outline_progress_lock = asyncio.Lock()

        async def _tracked_outline(coro, query_name: str):
            nonlocal outlines_done
            result = await coro
            async with outline_progress_lock:
                outlines_done += 1
                pct = 10 + int((outlines_done / total) * 10)
                self._emit_progress(
                    percentage=min(pct, 20),
                    current_step=f"Outlined chapter: {query_name[:60]}… ({outlines_done}/{total})",
                    metadata={"outlines_done": outlines_done, "outlines_total": total},
                )
            return result

        tasks = [
            self._generate_chapter_outline(
                chapter_num=idx + 1,
                total_chapters=total,
                review_data=review,
                all_queries=planner_queries,
            )
            for idx, review in enumerate(sorted_reviews)
        ]

        tracked_tasks = [
            _tracked_outline(task, review.get("query", f"Chapter {idx + 1}"))
            for idx, (task, review) in enumerate(zip(tasks, sorted_reviews))
        ]

        # Fire one chapter outline call per query in parallel (per-query fallback path)
        chapter_results = await asyncio.gather(*tracked_tasks)

        # Merge ordered per-query results into table_of_contents and report_outline (fallback structures)
        fallback_table_of_contents: dict = {}
        fallback_report_outline: dict = {}

        for result in chapter_results:
            chapter_title = result.get("chapter_title", "")
            subchapters = result.get("subchapters", [])
            outline_entries = result.get("outline", {})

            fallback_table_of_contents[chapter_title] = subchapters
            fallback_report_outline.update(outline_entries)

        # --- Global outline attempt using all sections together -----------------
        # Build a lightweight snapshot of section contents (first N lines) for the global prompt
        from writer.prompts_utils.writer_prompts import (
            generate_global_outline_prompt,
        )  # local import to avoid cycles

        # Group sections by chapter using the per-query results as a guide
        # (in case the global attempt fails, we fall back to these structures)
        global_outline_prompt = generate_global_outline_prompt(
            user_query=user_query,
            planner_queries=planner_queries,
            sections=sections,
        )

        try:
            response = await self.outline_model.ainvoke(global_outline_prompt)
            raw_text = self._response_text(response)
            parsed = self._extract_json_from_response(raw_text)
            if parsed and "table_of_contents" in parsed and "report_outline" in parsed:
                table_of_contents = parsed["table_of_contents"]
                report_outline = parsed["report_outline"]
            else:
                logger.warning(
                    "[Writer] Global outline parse failed, falling back to per-query outlines."
                )
                table_of_contents = fallback_table_of_contents
                report_outline = fallback_report_outline
        except Exception as exc:
            logger.warning(
                f"[Writer] Global outline generation error: {exc}. Falling back to per-query outlines."
            )
            table_of_contents = fallback_table_of_contents
            report_outline = fallback_report_outline

        ordered_chapter_titles = list(table_of_contents.keys())

        print(
            f"\n[Writer] Table of Contents:\n{json.dumps(table_of_contents, indent=2)}\n"
        )
        print(
            f"[Writer] Report Outline Sections:\n{json.dumps(report_outline, indent=2)}\n"
        )

        # Generate text guidance for abstract / intro / conclusion (fed to chapter pipeline later)
        framing_guidance = await self._generate_framing_guidance(
            user_query=user_query,
            ordered_chapter_titles=ordered_chapter_titles,
        )

        return {
            "table_of_contents": table_of_contents,
            "report_outline": report_outline,
            "framing_guidance": framing_guidance,
        }

    async def _generate_design_instructions(
        self,
        user_query: str,
        planner_queries: list,
        table_of_contents: dict,
        abstract: str,
        introduction: str,
    ) -> str:
        """
                Selects the best design skill and generates a comprehensive visual
                style brief (colors, fonts, spacing, chart conventions).

                Two-step process:
                1. Routes to the best design skill file from available libraries.
                2. Uses that skill to generate an exhaustive text-based design brief
                   covering every visual property chapters will need.

                The returned string is injected into every chapter prompt so all
                chapters share consistent inline CSS values.

        .
        """
        available_skills = get_available_design_skills()

        if not available_skills:
            logger.warning(
                "[Writer] No design skills found. Using default design instructions."
            )
            return ""

        routing_prompt = await choose_design_skill_prompt(
            user_query=user_query,
            planner_queries=planner_queries,
            table_of_contents=table_of_contents,
            abstract=abstract,
            introduction=introduction,
            available_skills=available_skills,
        )

        try:
            routing_model = self.lower_gemini_model.with_structured_output(
                DesignSkillSelection
            )
            route_response = await routing_model.ainvoke(routing_prompt)

            selected_filename = route_response.selected_skill_filename.strip()

            if selected_filename not in available_skills:
                logger.warning(
                    f"[Writer] LLM selected unknown design skill: {selected_filename}. Defaulting to general_fallback.md"
                )
                selected_filename = "general_fallback.md"

            selected_rules = available_skills.get(selected_filename, "")
            logger.info(f"[Writer] Selected Design Skill: {selected_filename}")

            style_name = selected_filename.replace(".md", "").replace("_", " ").title()
            self._emit_progress(
                25, f"Creating '{style_name}' visual design brief for the report..."
            )

        except Exception as e:
            logger.error(f"[Writer] Error selecting design skill: {e}")
            selected_filename = "general_fallback.md"
            selected_rules = available_skills.get(selected_filename, "")

        instructions_prompt = await generate_design_instructions_prompt(
            user_query=user_query,
            planner_queries=planner_queries,
            table_of_contents=table_of_contents,
            selected_skill_name=selected_filename,
            selected_skill_rules=selected_rules,
        )

        try:
            styled_model = self.design_model.with_structured_output(
                DesignInstructionsResult
            )
            response = await styled_model.ainvoke(instructions_prompt)

            return response.design_instructions.strip()
        except Exception as e:
            logger.error(f"[Writer] Design instructions generation failed: {e}")
            return ""

    async def _generate_single_chapter(
        self,
        chapter_heading: str,
        section_ids: list = None,
        section_index: dict = None,
        table_of_contents: dict = None,
        design_instructions: str = "",
        user_query: str = "",
        planner_queries: list = None,
        sections_override: list = None,
    ) -> str:
        """
        Generates complete HTML content for one chapter.

        For body chapters: filters full sections by section_id from section_index.
        For framing sections (abstract/intro/conclusion): uses sections_override
        which contains the guidance text directly.

        Both paths call generate_chapter_prompt so they share the same design,
        theme, and page structure.

        Args:
            chapter_heading: The heading to generate (e.g. "1. Architecture" or "Abstract").
            section_ids: List of section_ids assigned to this chapter (body chapters).
            section_index: Dict mapping section_id → full section data (body chapters).
            table_of_contents: Full ToC dict for context.
            design_instructions: Visual style brief for consistent HTML styling.
            user_query: Original user research query for section-focus context.
            planner_queries: Planner query list for section-focus context.
            sections_override: Direct list of section dicts — bypasses section_id lookup.

        Returns:
            Complete chapter content as an HTML string.
        """
        if sections_override is not None:
            sections_for_chapter = sections_override
        else:
            sections_for_chapter = []
            for sid in section_ids or []:
                if sid in (section_index or {}):
                    sections_for_chapter.append(section_index[sid])
                else:
                    logger.warning(
                        f"[Writer] section_id '{sid}' not found in index, skipping"
                    )

        if not sections_for_chapter:
            logger.warning(f"[Writer] No sections found for chapter: {chapter_heading}")
            return f'<section class="report-chapter"><h2>{chapter_heading}</h2><p>No content available for this section.</p></section>'

        prompt = await generate_chapter_prompt(
            chapter_heading=chapter_heading,
            table_of_contents=table_of_contents,
            sections_for_chapter=sections_for_chapter,
            design_instructions=design_instructions,
            user_query=user_query,
            planner_queries=planner_queries or [],
        )

        max_retries = 2
        raw_text = ""
        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    self.chapter_model.ainvoke(prompt), timeout=300
                )
                raw_text = self._response_text(response)
                break
            except asyncio.TimeoutError:
                logger.warning(
                    f"[Writer] Chapter '{chapter_heading}' attempt {attempt + 1} timed out (300s)"
                )
                if attempt == max_retries - 1:
                    logger.error(
                        f"[Writer] Max retries reached for chapter '{chapter_heading}'."
                    )
                else:
                    await asyncio.sleep(2**attempt)
            except Exception as e:
                logger.warning(
                    f"[Writer] Chapter '{chapter_heading}' attempt {attempt + 1} failed: {e}"
                )
                if attempt == max_retries - 1:
                    logger.error(
                        f"[Writer] Max retries reached for chapter '{chapter_heading}'."
                    )
                else:
                    await asyncio.sleep(2**attempt)

        if not raw_text or not raw_text.strip():
            error_msg = f"[Writer] Chapter generation returned empty for: {chapter_heading}"
            logger.error(error_msg)
            raise LLMCatchError(
                message=error_msg,
                error_details="LLM output was entirely empty or timed out.",
            )

        cleaned = raw_text.strip()

        # Strip markdown code fences if LLM wrapped the HTML in them
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:html)?\s*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)

        return cleaned

    async def _generate_report_body_sections(
        self,
        report_outline: dict,
        section_index: dict,
        table_of_contents: dict,
        design_instructions: str = "",
        user_query: str = "",
        planner_queries: list = None,
        framing_guidance: dict = None,
    ) -> list:
        """
        Phase 2: Generates abstract, introduction, body chapters, and conclusion
        ALL through the same generate_chapter_prompt pipeline.

        Builds an extended TOC (Abstract → Introduction → body chapters → Conclusion)
        so the model always knows where the current section sits in the full report.
        Framing sections use the guidance text from Phase 1 as their source material.
        Body chapters use section_ids from the report_outline as before.

        Returns:
            List of ReportBodySection dicts ordered by section_order.
            Order: abstract(1), introduction(2), body chapters(3..N+2), conclusion(N+3).
        """
        planner_queries = planner_queries or []
        framing_guidance = framing_guidance or {}

        # Build extended TOC so the model sees where Abstract/Intro/Conclusion sit
        from collections import OrderedDict

        extended_toc = OrderedDict()
        extended_toc["Abstract"] = []
        extended_toc["Introduction"] = []
        for chapter, subs in table_of_contents.items():
            extended_toc[chapter] = subs
        extended_toc["Conclusion"] = []

        tasks = []
        heading_order = []

        # --- Abstract ---
        abstract_guidance = framing_guidance.get("abstract", "")
        if abstract_guidance:
            heading_order.append("Abstract")
            tasks.append(
                self._generate_single_chapter(
                    chapter_heading="Abstract",
                    table_of_contents=extended_toc,
                    design_instructions=design_instructions,
                    user_query=user_query,
                    planner_queries=planner_queries,
                    sections_override=[
                        {
                            "section_content": abstract_guidance,
                            "section_id": "framing-abstract",
                        }
                    ],
                )
            )

        # --- Introduction ---
        intro_guidance = framing_guidance.get("introduction", "")
        if intro_guidance:
            heading_order.append("Introduction")
            tasks.append(
                self._generate_single_chapter(
                    chapter_heading="Introduction",
                    table_of_contents=extended_toc,
                    design_instructions=design_instructions,
                    user_query=user_query,
                    planner_queries=planner_queries,
                    sections_override=[
                        {
                            "section_content": intro_guidance,
                            "section_id": "framing-introduction",
                        }
                    ],
                )
            )

        # --- Body chapters ---
        for main_chapter, _subchapters in table_of_contents.items():
            section_ids = report_outline.get(main_chapter, [])
            if not section_ids:
                continue
            heading_order.append(main_chapter)
            tasks.append(
                self._generate_single_chapter(
                    chapter_heading=main_chapter,
                    section_ids=section_ids,
                    section_index=section_index,
                    table_of_contents=extended_toc,
                    design_instructions=design_instructions,
                    user_query=user_query,
                    planner_queries=planner_queries,
                )
            )

        # --- Conclusion ---
        conclusion_guidance = framing_guidance.get("conclusion", "")
        if conclusion_guidance:
            heading_order.append("Conclusion")
            tasks.append(
                self._generate_single_chapter(
                    chapter_heading="Conclusion",
                    table_of_contents=extended_toc,
                    design_instructions=design_instructions,
                    user_query=user_query,
                    planner_queries=planner_queries,
                    sections_override=[
                        {
                            "section_content": conclusion_guidance,
                            "section_id": "framing-conclusion",
                        }
                    ],
                )
            )

        total_chapters = len(tasks)
        chapters_done = 0
        chapter_progress_lock = asyncio.Lock()

        async def _tracked_chapter(coro, heading: str):
            nonlocal chapters_done
            result = await coro
            async with chapter_progress_lock:
                chapters_done += 1
                pct = 40 + int((chapters_done / total_chapters) * 50)
                self._emit_progress(
                    percentage=min(pct, 90),
                    current_step=f"Done: {heading[:60]}… ({chapters_done}/{total_chapters})",
                    metadata={
                        "chapters_done": chapters_done,
                        "chapters_total": total_chapters,
                    },
                )
            return result

        tracked_tasks = [
            _tracked_chapter(task, heading)
            for task, heading in zip(tasks, heading_order)
        ]
        chapter_contents = await asyncio.gather(*tracked_tasks)

        report_body_sections = []
        for order_idx, content in enumerate(chapter_contents, start=1):
            report_body_sections.append(
                {
                    "section_id": str(uuid.uuid4()),
                    "section_order": order_idx,
                    "section_content": content,
                }
            )

        return report_body_sections

    def _format_table_of_contents_html(self, table_of_contents: dict) -> str:
        """
        Converts table_of_contents dict into a styled HTML nav element.

        Args:
            table_of_contents: Dict where keys are main chapters, values are subchapter arrays.

        Returns:
            HTML-formatted table of contents string.
        """
        lines = ['<nav class="report-toc">']
        lines.append(
            "<h2 style=\"font-family: 'Space Grotesk', sans-serif; font-size: 1.8em; font-weight: 700; color: #1a365d; margin-bottom: 1em; padding-bottom: 0.5em; border-bottom: 2px solid #2c5282;\">Table of Contents</h2>"
        )
        lines.append('<ol style="list-style: none; padding: 0; margin: 0;">')
        for main_chapter, subchapters in table_of_contents.items():
            lines.append(f'<li style="margin-bottom: 0.8em;">')
            lines.append(
                f"<span style=\"font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.05em; color: #1a365d;\">{main_chapter}</span>"
            )
            if subchapters:
                lines.append(
                    '<ol style="list-style: none; padding-left: 1.5em; margin-top: 0.4em;">'
                )
                for sub in subchapters:
                    lines.append(
                        f'<li style="margin-bottom: 0.3em; color: #2c5282; font-size: 0.95em; padding-left: 0.5em; border-left: 2px solid #e2e8f0;">{sub}</li>'
                    )
                lines.append("</ol>")
            lines.append("</li>")
        lines.append("</ol>")
        lines.append("</nav>")
        return "\n".join(lines)

    async def run(self, state: AgentState) -> dict:
        """
        Orchestrates report generation with progress streaming.

        Phase 1: Aggregates sections → generates outline (ToC, section mapping,
        framing guidance for abstract/intro/conclusion).
        Phase 1.5: Generates design instructions (visual style brief).
        Phase 2: Generates abstract, introduction, body chapters, and conclusion
        ALL through the same chapter pipeline with identical design/theme/pages.

        Returns:
            Dict with table_of_contents (HTML), report_body_sections (list of
            section dicts — abstract, intro, chapters, conclusion all included
            in order), and design_instructions (text).
        """
        self._emit_progress(
            5, "Reading through all agent research and understanding the data…"
        )

        aggregated_sections = self._aggregate_sections_from_research_review(state)

        if not aggregated_sections:
            logger.warning("[Writer] No sections found in research_review")
            return {
                "table_of_contents": "<p>No content available</p>",
                "report_body_sections": [],
                "design_instructions": "",
            }

        user_query = state.get("user_query", "Research Report")
        planner_queries = state.get("planner_query", [])

        self._emit_progress(10, "Figuring out what our chapters should look like…")

        outline = await self._generate_outline_report(
            user_query=user_query,
            planner_queries=planner_queries,
            sections=aggregated_sections,
            state=state,
        )

        table_of_contents = outline["table_of_contents"]
        report_outline = outline["report_outline"]
        framing_guidance = outline.get("framing_guidance", {})
        total_chapters = (
            len(table_of_contents) + 3
        )  # body chapters + abstract + intro + conclusion

        self._emit_progress(20, "Designing the visual aesthetic for the report…")

        design_instructions = await self._generate_design_instructions(
            user_query=user_query,
            planner_queries=planner_queries,
            table_of_contents=table_of_contents,
            abstract=framing_guidance.get("abstract", ""),
            introduction=framing_guidance.get("introduction", ""),
        )

        section_index = self._build_section_index(aggregated_sections)

        self._emit_progress(
            35,
            f"Outline and design locked in. Writing {total_chapters} sections in parallel…",
            metadata={"chapters_total": total_chapters},
        )

        report_body_sections = await self._generate_report_body_sections(
            report_outline=report_outline,
            section_index=section_index,
            table_of_contents=table_of_contents,
            design_instructions=design_instructions,
            user_query=user_query,
            planner_queries=planner_queries,
            framing_guidance=framing_guidance,
        )

        self._emit_progress(95, "Stitching everything together into the final report…")

        toc_html = self._format_table_of_contents_html(table_of_contents)

        self._emit_progress(100, "Hell yeah, report complete! 🎉")

        return {
            "table_of_contents": toc_html,
            "report_body_sections": report_body_sections,
            "design_instructions": design_instructions,
        }


async def writer_node(state: AgentState, writer: StreamWriter) -> dict:
    """
    LangGraph node wrapper for Writer.

    Accepts StreamWriter from LangGraph to emit real-time progress events.
    Reads research_review from state, generates outline + parallel body sections,
    and returns structured output appended to the `reports` list.
    """
    emitter = get_emitter(writer)
    api_keys = state.get("api_keys", {})
    model_selections = state.get("model_selections", {})
    writer_instance = Writer(
        emitter=emitter, api_keys=api_keys, model_selections=model_selections
    )
    result = await writer_instance.run(state)

    report_data = {
        "run_id": state.get("current_run_id", ""),
        "query": state.get("user_query", ""),
        "table_of_contents": result["table_of_contents"],
        "body_sections": result["report_body_sections"],
        "design_instructions": result.get("design_instructions", ""),
        "timestamp": datetime.utcnow().isoformat(),
    }

    return {"reports": [report_data]}


if __name__ == "__main__":
    pass
