from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field
import operator
from typing import List, Dict, Any, TypedDict, Annotated




# We will use this for our subgraph   (Researcher-->Reveiwer --> Reviewer)
class ResearchReviewData(TypedDict):
    """
    Intermediate state data for the research and review process.
    `review_feedback` is annotated to aggregate feedback from multiple review steps.
    """
    topic: str
    task_description: str
    raw_research_results: List[str]
    processed_findings: List[Dict[str, Any]]
    review_feedback: Annotated[List[str], operator.add]
    Proposed_Research: str

class ReportSection(BaseModel):
    """Represents a single section of a structured report."""
    title: str = Field(description="Title of the section.")
    content: str = Field(description="The detailed content of the section, can be markdown.")
    conclusion :str = Field(description="The conclusion of the section.")
    sources: Optional[List[str]] = Field(description="Sources used in the section.")
    sub_sections: Optional[List['ReportSection']] = Field(
        default_factory=list,
        description="Optional list of nested sub-sections."
    )





# --- Global Graph State ---
class AgentGraphState(BaseModel):
    """
    Global state for the research and report generation graph.

    Contains data related to the research/review process and the final report structure.
    This serves as the single state object passed between nodes in the LangGraph.
    """
    research_review: ResearchReviewData
    report_sections: List[ReportSection]
    final_report_text: Optional[str]
