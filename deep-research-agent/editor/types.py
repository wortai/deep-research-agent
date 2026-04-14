from typing import Literal, Optional, TypedDict


EditMode = Literal["visual", "research"]


class EditSectionRequest(TypedDict):
    section_id: str
    section_order: Optional[int]
    chapter_heading: str
    old_html: str
    feedback: str
    edit_mode: EditMode


class ReportSectionUpdate(TypedDict):
    section_id: str
    section_order: Optional[int]
    chapter_heading: str
    new_section_content: str
    run_id: Optional[str]  # Target report when multiple exist

