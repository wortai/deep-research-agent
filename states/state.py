from typing import List, Dict, Any, Literal, TypedDict, Optional
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

# --- Sub-components of the State ---

# 1. Research Finding Structure (used by processed_research_content)
class ResearchFinding(TypedDict):
    """
    Represents a structured piece of information derived from raw research results.
    """
    title_header: str
    research: str
    source_url: Optional[str]
    # Add more fields if needed, e.g., 'raw_content_snippet', 'relevance_score'



# 2. Review Comment Structure (used by review_comments)
class ReviewComment(TypedDict):
    """
    Details of a single comment or feedback point from the reviewer.
    """
    reviewer_id: str
    reviews: str
    severity: Literal["critical", "major", "minor", "suggestion"]


class ReportSection(BaseModel):
    """
    Represents a single section of a structured report.
    """
    title: str = Field(description="Title of the section.")
    content: str = Field(description="The detailed content of the section, can be markdown.")
    # Allows for recursive sub-sections, enabling hierarchical reports
    sub_sections: Optional[List['ReportSection']] = Field(
        default_factory=list,
        description="Optional list of nested sub-sections."
    )

class AgentState(BaseModel):
    """
    Consolidated state for research and review efforts.
    
    - review_comments: Comments from reviewers.
    - report_sections: Sections of the report to be drafted.
    - processed_research_content: Structured research findings.
    """
    review_comments: List[ReviewComment] = Field(
        default_factory=list,
        description="List of feedback comments from reviewers."
    )
    report_sections: List[ReportSection] = Field(
        default_factory=list,
        description="List of report sections prepared for the final report."
    )
    processed_research_content: List[ResearchFinding] = Field(
        default_factory=list,
        description="Structured research findings to be used during the research process."
    )

# Report Structure (used by report)



    