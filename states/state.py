from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field
import operator
from typing import List, Dict, Any, TypedDict, Annotated


class ReportSection(TypedDict):
    section_heading: str 
    section_content: str
    section_urls: Optional[List[str]]



class ResearchReviewData(TypedDict):
    query : str
    raw_research_results: List[tuple[str, str]] # (gap_query_data, url)
    review_feedback: Annotated[List[str], operator.add]
    section : ReportSection
    report_sections: List[ReportSection]


# --- Global Graph State ---
class AgentGraphState(TypedDict):

    # report Layout 
    report_introduction:str
    report_conclusion:str
    report_abstract:str 
    report_methodology:str 
    report_sections: List[ReportSection]
    final_report_sections :str 
    research_review: ResearchReviewData
    
    #--------------------------
    # final report path 
    final_report_text: Optional[str]
