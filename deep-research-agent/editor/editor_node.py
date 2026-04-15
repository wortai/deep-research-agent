import logging
import copy
from typing import Any, Dict, List, Optional, Tuple

from langgraph.types import StreamWriter

from editor.editor_service import EditorService
from graphs.events.stream_emitter import get_emitter
from graphs.states.subgraph_state import AgentGraphState


logger = logging.getLogger(__name__)


def _patch_report_section(
    reports: List[Dict[str, Any]],
    run_id: str,
    section_id: str,
    new_html: str,
    section_order: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Finds the target ReportData and ReportBodySection, then replaces
    section_content with new_html.

    Matching priority:
      1) run_id + section_id  (primary — always correct)
      2) run_id + section_order (fallback — for edge-case ID mismatches)
      3) any report + section_id (last resort — single-report case)

    Returns (patched_reports_list, was_section_found).
    If was_section_found is False the reports are returned unchanged.
    """
    if not new_html:
        logger.error(
            "[editor_node._patch] new_html is empty — refusing to patch, keeping current content"
        )
        return list(reports), False

    patched = []
    found = False

    # --- Pass 1: exact match on run_id + section_id ---
    for report in reports:
        if str(report.get("run_id", "")) != str(run_id):
            patched.append(report)
            continue
        new_sections = []
        for section in report.get("body_sections", []):
            if not found and str(section.get("section_id", "")) == str(section_id):
                new_sections.append({**section, "section_content": new_html})
                found = True
            else:
                new_sections.append(section)
        patched.append({**report, "body_sections": new_sections})

    if found:
        logger.info(
            f"[editor_node._patch] Matched by run_id+section_id: run={run_id} sec={section_id}"
        )
        return patched, True

    # --- Pass 2: run_id + section_order fallback ---
    if section_order is not None:
        patched = []
        for report in reports:
            if str(report.get("run_id", "")) != str(run_id):
                patched.append(report)
                continue
            new_sections = []
            for section in report.get("body_sections", []):
                if (
                    not found
                    and isinstance(section.get("section_order"), int)
                    and section["section_order"] == section_order
                ):
                    new_sections.append({**section, "section_content": new_html})
                    found = True
                else:
                    new_sections.append(section)
            patched.append({**report, "body_sections": new_sections})
        if found:
            logger.warning(
                f"[editor_node._patch] section_id mismatch — fell back to run_id+section_order: "
                f"run={run_id} order={section_order} (original section_id={section_id})"
            )
            return patched, True

    # --- Pass 3: any report + section_id (single-report safety net) ---
    if len(reports) <= 1:
        patched = []
        for report in reports:
            new_sections = []
            for section in report.get("body_sections", []):
                if not found and str(section.get("section_id", "")) == str(section_id):
                    new_sections.append({**section, "section_content": new_html})
                    found = True
                else:
                    new_sections.append(section)
            patched.append({**report, "body_sections": new_sections})
        if found:
            logger.warning(
                f"[editor_node._patch] run_id mismatch — fell back to section_id across all reports: "
                f"sec={section_id} (original run_id={run_id})"
            )
            return patched, True

    logger.error(
        f"[editor_node._patch] Could not find section in any report: "
        f"run_id={run_id} section_id={section_id} section_order={section_order} "
        f"reports_count={len(reports)}"
    )
    return list(reports), False


async def editor_node(
    state: AgentGraphState, writer: StreamWriter = None
) -> Dict[str, Any]:
    """
    Targeted report section editing node.

    Reads edit payload from state, calls EditorService to regenerate the
    section HTML via LLM, then patches the matching ReportBodySection
    in the existing reports list. Uses __overwrite__ to replace the full
    reports list in the checkpoint (bypassing operator.add).
    """
    emitter = get_emitter(writer)
    edit_section_id = str(state.get("edit_section_id") or "")
    edit_run_id = (state.get("edit_run_id") or "").strip()
    edit_chapter_heading = (state.get("edit_chapter_heading") or "").strip()

    def _edit_meta(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        meta: Dict[str, Any] = {
            "mode": "edit",
            "section_id": edit_section_id,
            "run_id": edit_run_id or None,
            "chapter_heading": edit_chapter_heading or None,
        }
        if extra:
            meta.update(extra)
        return meta

    if emitter:
        emitter.emit_writer_progress(
            percentage=10,
            current_step="Applying your edit to the selected report section…",
            metadata=_edit_meta(),
        )

    service = EditorService()
    update = await service.regenerate_section(
        state=dict(state), emitter=emitter, edit_meta=_edit_meta()
    )

    if not update:
        logger.warning(
            "[editor_node] No update returned (missing edit payload or empty LLM output)"
        )
        if emitter:
            emitter.emit_writer_progress(
                percentage=100,
                current_step="Edit failed: missing edit payload or empty output.",
                metadata=_edit_meta({"status": "error"}),
            )
        return {
            "final_response": "I couldn't apply that edit (missing section content or feedback). Please try again with more detail.",
        }

    existing_reports = list(state.get("reports") or [])

    logger.info(
        f"[editor_node] Patching reports={len(existing_reports)} "
        f"run_id={update.get('run_id')} section_id={update.get('section_id')} "
        f"section_order={update.get('section_order')} new_html_len={len(update.get('new_section_content', ''))}"
    )

    patched_reports, patched_ok = _patch_report_section(
        reports=existing_reports,
        run_id=update.get("run_id", ""),
        section_id=update.get("section_id", ""),
        new_html=update.get("new_section_content", ""),
        section_order=update.get("section_order"),
    )

    if not patched_ok:
        logger.error(
            f"[editor_node] Section patch FAILED — returning update without checkpoint patch. "
            f"Frontend report_section_update handler will attempt in-memory patch. "
            f"section_id={update.get('section_id')} run_id={update.get('run_id')}"
        )
        if emitter:
            emitter.emit_writer_progress(
                percentage=100,
                current_step="Edit completed but checkpoint update may be delayed — refreshing report.",
                metadata=_edit_meta({"status": "partial"}),
            )

    if emitter:
        emitter.emit_writer_progress(
            percentage=100,
            current_step="Section updated.",
            metadata=_edit_meta({"status": "ok" if patched_ok else "partial"}),
        )

    return {
        "report_section_update": update,
        "reports": {"__overwrite__": patched_reports},
        "final_response": f"Updated section: {update.get('chapter_heading') or update.get('section_id')}",
    }
