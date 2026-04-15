"""
Standalone tests for _patch_report_section logic.
Copies the function inline to avoid heavy import chains.
Tests verify: edits work when they should, content is NEVER lost when they can't.
"""

import pytest
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def _patch_report_section(
    reports: List[Dict[str, Any]],
    run_id: str,
    section_id: str,
    new_html: str,
    section_order: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], bool]:
    if not new_html:
        return list(reports), False

    patched = []
    found = False

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
        return patched, True

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
            return patched, True

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
            return patched, True

    return list(reports), False


def _report(run_id, sections):
    return {"run_id": run_id, "body_sections": sections}


def _sec(sid, order, content):
    return {"section_id": sid, "section_order": order, "section_content": content}


# ── HAPPY PATH ──────────────────────────────────────────────────────────────


class TestHappyPath:
    def test_exact_match(self):
        reports = [
            _report(
                "r1",
                [
                    _sec("A", 1, "Abstract"),
                    _sec("B", 2, "Chapter 1"),
                    _sec("C", 3, "Chapter 2"),
                ],
            )
        ]
        patched, ok = _patch_report_section(reports, "r1", "B", "EDITED")

        assert ok is True
        assert patched[0]["body_sections"][1]["section_content"] == "EDITED"
        assert patched[0]["body_sections"][0]["section_content"] == "Abstract"
        assert patched[0]["body_sections"][2]["section_content"] == "Chapter 2"

    def test_original_not_mutated(self):
        sec = _sec("A", 1, "Original")
        reports = [_report("r1", [sec])]
        _patch_report_section(reports, "r1", "A", "Edited")
        assert sec["section_content"] == "Original"

    def test_multiple_reports_only_target_touched(self):
        reports = [
            _report("r1", [_sec("A", 1, "R1 Content")]),
            _report("r2", [_sec("B", 1, "R2 Content")]),
        ]
        patched, ok = _patch_report_section(reports, "r1", "A", "NEW R1")
        assert ok is True
        assert patched[0]["body_sections"][0]["section_content"] == "NEW R1"
        assert patched[1]["body_sections"][0]["section_content"] == "R2 Content"


# ── PASS 2: section_id wrong, fallback to run_id + section_order ────────────


class TestFallbackByOrder:
    def test_bad_section_id_good_order(self):
        reports = [
            _report(
                "r1",
                [
                    _sec("X", 1, "Sec 1"),
                    _sec("Y", 2, "Sec 2"),
                    _sec("Z", 3, "Sec 3"),
                ],
            )
        ]
        patched, ok = _patch_report_section(
            reports, "r1", "NONEXISTENT", "EDITED SEC 3", section_order=3
        )
        assert ok is True
        assert patched[0]["body_sections"][2]["section_content"] == "EDITED SEC 3"
        assert patched[0]["body_sections"][0]["section_content"] == "Sec 1"

    def test_bad_section_id_no_order_provided_fails_gracefully(self):
        reports = [_report("r1", [_sec("X", 1, "Safe")])]
        patched, ok = _patch_report_section(reports, "r1", "NONEXISTENT", "BAD")
        assert ok is False
        assert patched[0]["body_sections"][0]["section_content"] == "Safe"


# ── PASS 3: run_id wrong, fallback to section_id across single report ───────


class TestFallbackByIdOnly:
    def test_wrong_run_single_report_correct_section_id(self):
        reports = [_report("real-run", [_sec("s1", 1, "Original")])]
        patched, ok = _patch_report_section(reports, "wrong-run", "s1", "Edited")
        assert ok is True
        assert patched[0]["body_sections"][0]["section_content"] == "Edited"

    def test_wrong_run_multiple_reports_does_not_fallback(self):
        reports = [
            _report("r1", [_sec("s1", 1, "R1")]),
            _report("r2", [_sec("s1", 1, "R2")]),
        ]
        patched, ok = _patch_report_section(reports, "wrong-run", "s1", "DANGER")
        assert ok is False
        assert patched[0]["body_sections"][0]["section_content"] == "R1"
        assert patched[1]["body_sections"][0]["section_content"] == "R2"


# ── EMPTY HTML GUARD ────────────────────────────────────────────────────────


class TestEmptyHtmlGuard:
    def test_empty_string_never_destroys_content(self):
        reports = [_report("r1", [_sec("A", 1, "PRECIOUS")])]
        patched, ok = _patch_report_section(reports, "r1", "A", "")
        assert ok is False
        assert patched[0]["body_sections"][0]["section_content"] == "PRECIOUS"

    def test_none_never_destroys_content(self):
        reports = [_report("r1", [_sec("A", 1, "PRECIOUS")])]
        patched, ok = _patch_report_section(reports, "r1", "A", None)
        assert ok is False
        assert patched[0]["body_sections"][0]["section_content"] == "PRECIOUS"


# ── NOTHING MATCHES AT ALL ──────────────────────────────────────────────────


class TestTotalFailure:
    def test_everything_wrong_preserves_all_content(self):
        reports = [
            _report("r1", [_sec("A", 1, "R1-A"), _sec("B", 2, "R1-B")]),
            _report("r2", [_sec("C", 1, "R2-C")]),
        ]
        patched, ok = _patch_report_section(
            reports, "wrong-run", "wrong-sec", "SHOULD NOT APPEAR", section_order=99
        )
        assert ok is False
        assert patched[0]["body_sections"][0]["section_content"] == "R1-A"
        assert patched[0]["body_sections"][1]["section_content"] == "R1-B"
        assert patched[1]["body_sections"][0]["section_content"] == "R2-C"

    def test_empty_reports_list(self):
        patched, ok = _patch_report_section([], "r1", "A", "New")
        assert ok is False
        assert patched == []


# ── REAL-WORLD: EXACT USER SCENARIO ─────────────────────────────────────────


class TestRealWorldChapter2:
    def test_edit_chapter_2_uuid_flow(self):
        run = "84ab4f0f-0ebb-47c1-b9e0-60b0f4d381f4"
        ch2_id = "ddd-444"
        reports = [
            _report(
                run,
                [
                    _sec("aaa-111", 1, "Abstract"),
                    _sec("bbb-222", 2, "Introduction"),
                    _sec("ccc-333", 3, "Chapter 1"),
                    _sec(ch2_id, 4, "Chapter 2 Calculus"),
                    _sec("eee-555", 5, "Conclusion"),
                ],
            )
        ]

        edited = "<div class='report-chapter'><div class='report-page'>EDITED CALCULUS</div></div>"
        patched, ok = _patch_report_section(reports, run, ch2_id, edited)

        assert ok is True
        assert patched[0]["body_sections"][3]["section_content"] == edited
        assert patched[0]["body_sections"][0]["section_content"] == "Abstract"
        assert patched[0]["body_sections"][4]["section_content"] == "Conclusion"

    def test_edit_chapter_2_with_wrong_run_but_good_id(self):
        """run_id changed between edit initiation and completion."""
        reports = [_report("old-run", [_sec("ddd-444", 4, "Chapter 2")])]
        patched, ok = _patch_report_section(
            reports, "new-run", "ddd-444", "Edited Chapter 2"
        )
        assert ok is True
        assert patched[0]["body_sections"][0]["section_content"] == "Edited Chapter 2"

    def test_edit_chapter_2_with_wrong_id_but_good_order(self):
        """section_id corrupted but section_order is correct."""
        run = "run-1"
        reports = [
            _report(
                run,
                [
                    _sec("aaa", 1, "Abstract"),
                    _sec("bbb", 2, "Intro"),
                    _sec("ccc", 3, "Ch1"),
                    _sec("ddd", 4, "Ch2 Calculus"),
                    _sec("eee", 5, "Conclusion"),
                ],
            )
        ]
        patched, ok = _patch_report_section(
            reports, run, "WRONG-ID", "Edited Ch2", section_order=4
        )
        assert ok is True
        assert patched[0]["body_sections"][3]["section_content"] == "Edited Ch2"
        assert patched[0]["body_sections"][0]["section_content"] == "Abstract"

    def test_edit_chapter_2_total_disaster_content_survives(self):
        """Everything is wrong — the edit is lost but original survives."""
        reports = [
            _report(
                "run-1",
                [
                    _sec("ddd-444", 4, "Chapter 2 Calculus — precious"),
                ],
            )
        ]
        patched, ok = _patch_report_section(
            reports, "wrong-run", "wrong-id", "SHOULD NOT APPEAR", section_order=99
        )
        assert ok is False
        assert (
            patched[0]["body_sections"][0]["section_content"]
            == "Chapter 2 Calculus — precious"
        )
