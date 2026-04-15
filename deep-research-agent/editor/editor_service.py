import logging
from typing import Any, Dict, Optional

from llms import LlmsHouse

from editor.prompts.edit_prompts import generate_edit_chapter_prompt
from editor.types import ReportSectionUpdate
from editor.utils import extract_first_h2_text, strip_code_fences

logger = logging.getLogger(__name__)


class EditorService:
    def __init__(self) -> None:
        self._model = LlmsHouse().grok_model("grok-4-1-fast-reasoning", temperature=0.9)

    async def regenerate_section(
        self, *, state: Dict[str, Any], emitter=None, edit_meta=None
    ) -> Optional[ReportSectionUpdate]:
        section_id = str(state.get("edit_section_id") or "")
        if not section_id:
            return None

        old_html = state.get("edit_old_html") or ""
        feedback = (state.get("edit_feedback") or "").strip()
        if not old_html or not feedback:
            return None

        raw_order = state.get("edit_section_order")
        if isinstance(raw_order, int):
            section_order: Optional[int] = raw_order
        elif isinstance(raw_order, float) and raw_order == int(raw_order):
            section_order = int(raw_order)
        else:
            section_order = None
        chapter_heading = (state.get("edit_chapter_heading") or "").strip()

        if not chapter_heading:
            chapter_heading = extract_first_h2_text(old_html) or ""

        edit_mode = (state.get("edit_mode") or "visual").strip().lower()
        if edit_mode not in {"visual", "research"}:
            edit_mode = "visual"

        reports = state.get("reports") or []
        edit_run_id = (state.get("edit_run_id") or "").strip()
        if edit_run_id:
            latest_report = next(
                (
                    r
                    for r in reversed(reports)
                    if str(r.get("run_id", "")) == edit_run_id
                ),
                reports[-1] if reports else {},
            )
        else:
            latest_report = reports[-1] if reports else {}
        run_id = latest_report.get("run_id") or state.get("current_run_id") or ""
        table_of_contents = latest_report.get("table_of_contents")
        design_instructions = latest_report.get("design_instructions", "")

        logger.info(
            f"[EditorService] edit section_id={section_id} section_order={section_order} "
            f"run_id={run_id} edit_run_id={edit_run_id} heading={chapter_heading[:60]}"
        )

        # For research edits, an upstream node can attach additional snippets.
        additional_research = state.get("edit_additional_research")

        prompt = await generate_edit_chapter_prompt(
            chapter_heading=chapter_heading,
            table_of_contents=table_of_contents,
            design_instructions=design_instructions,
            old_html=old_html,
            feedback=feedback,
            edit_mode=edit_mode,
            additional_research=additional_research,
        )

        try:
            raw = ""
            if emitter and edit_meta:
                # One Redis stream entry per model chunk: `current_step` is only what this chunk
                # added (never the full draft). Consumer appends in order (metadata.stream_delta).
                meta_delta = {**edit_meta, "stream_delta": True}
                async for chunk in self._model.astream(prompt):
                    token = chunk.content if hasattr(chunk, "content") else str(chunk)
                    if not token:
                        continue
                    raw += token
                    pct = min(95, 10 + min(85, len(raw) // 80))
                    emitter.emit_writer_progress(
                        percentage=pct,
                        current_step=token,
                        metadata=meta_delta,
                    )
            else:
                response = await self._model.ainvoke(prompt)
                raw = (
                    response.content if hasattr(response, "content") else str(response)
                )
        except Exception as exc:
            logger.error(f"[EditorService] LLM edit failed: {exc}")
            return None

        new_html = strip_code_fences(raw)
        if not new_html:
            logger.warning(
                "[EditorService] LLM returned empty content after stripping fences"
            )
            return None

        logger.info(
            f"[EditorService] Generated {len(new_html)} chars replacement for section_id={section_id}"
        )

        return {
            "section_id": section_id,
            "section_order": section_order,
            "chapter_heading": chapter_heading,
            "new_section_content": new_html,
            "run_id": run_id,
        }
