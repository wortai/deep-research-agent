import logging
from typing import Any, Dict, List, Optional

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
) -> List[Dict[str, Any]]:
    """
    Finds the ReportData matching run_id, locates the ReportBodySection
    by section_id, and replaces its section_content with new_html.

    Returns a new list with the patched report. All other reports and
    sections remain untouched.

    Args:
        reports: Full list of ReportData dicts from graph state.
        run_id: Target report's run_id.
        section_id: Target section's section_id within that report.
        new_html: Replacement HTML for the matched section.

    Returns:
        Patched copy of the reports list.
    """
    patched = []
    for report in reports:
        if str(report.get("run_id", "")) == str(run_id):
            new_sections = []
            for section in report.get("body_sections", []):
                if str(section.get("section_id", "")) == str(section_id):
                    new_sections.append({**section, "section_content": new_html})
                else:
                    new_sections.append(section)
            patched.append({**report, "body_sections": new_sections})
        else:
            patched.append(report)
    return patched


async def editor_node(state: AgentGraphState, writer: StreamWriter = None) -> Dict[str, Any]:
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
        state=dict(state),
        emitter=emitter,
        edit_meta=_edit_meta()
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

    if emitter:
        emitter.emit_writer_progress(
            percentage=100,
            current_step="Section updated.",
            metadata=_edit_meta({"status": "ok"}),
        )

    existing_reports = list(state.get("reports") or [])
    patched_reports = _patch_report_section(
        reports=existing_reports,
        run_id=update.get("run_id", ""),
        section_id=update.get("section_id", ""),
        new_html=update.get("new_section_content", ""),
    )

    return {
        "report_section_update": update,
        "reports": {"__overwrite__": patched_reports},
        "final_response": f"Updated section: {update.get('chapter_heading') or update.get('section_id')}",
    }
