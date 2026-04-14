from typing import List, Optional

from pydantic import BaseModel


class ReportBodySection(BaseModel):
    section_id: str
    section_order: int
    section_content: str


class ReportData(BaseModel):
    run_id: Optional[str] = ""
    query: Optional[str] = ""
    table_of_contents: Optional[str] = ""
    body_sections: List[ReportBodySection] = []
    design_instructions: Optional[str] = ""
    timestamp: Optional[str] = ""
