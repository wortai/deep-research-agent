from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field
import operator
from typing import List, Dict, Any, TypedDict, Annotated


class ReportSection(BaseModel):
    """Represents a single section of a structured report."""
    section_heading: str = Field(description="Heading of the section.")
    section_content: str = Field(description="The detailed content of the section, can be markdown.")
    section_urls: Optional[List[str]] = Field(description="URLs of sources used in the section.")


# We will use this for our subgraph   (Researcher-->Reveiwer --> Researcher)
class ResearchReviewData(TypedDict):
    """
    `GapQueryGenerator generates data for this state: Each Plan Query has its own instance of this state`
    Intermediate state data for the research and review process
    `review_feedback` is annotated to aggregate feedback from multiple review steps.
    """
    query : str
    task_description: str
    raw_research_results: List[tuple[str, str]]
    # processed_findings: List[ReportSection]
    review_feedback: Annotated[List[str], operator.add]


# --- Global Graph State ---
class AgentGraphState(BaseModel):
    """
    Global state for the research and report generation graph.
    Contains data related to the research/review process and the final report structure.
    This serves as the single state object passed between nodes in the LangGraph.
    """
    research_review: ResearchReviewData
    report_sections: List[ReportSection]
    proposed_research: str
    final_report_text: Optional[str]
