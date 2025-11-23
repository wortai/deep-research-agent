from typing import List, Dict, Any, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field
import operator


# === Pydantic Models for Structured LLM Output ===
class ReportSectionModel(BaseModel):
    """Pydantic model for structured LLM output - matches ReportSection schema"""
    section_heading: str = Field(description="The heading/title of the report section")
    section_content: str = Field(description="The detailed content of the report section")
    section_urls: Optional[List[str]] = Field(default=None, description="URLs referenced in this section")

class ReportSectionsResponse(BaseModel):
    """Structured response for multiple report sections from LLM"""
    report_sections: List[ReportSectionModel] = Field(description="List of formatted report sections")

class ReportIntroductionResponse(BaseModel):
    """Structured response for report introduction from LLM"""
    introduction_heading: str = Field(description="Professional heading for the introduction")
    introduction_content: str = Field(description="Concise, insightful introduction content")

class ReportAbstractResponse(BaseModel):
    """Structured response for report abstract from LLM"""
    report_abstract: str = Field(description= "Professional abstract summarizing the report" )

class ReportConclusionResponse(BaseModel):
    """Structured response for report conclusion from LLM"""
    report_conclusion: str = Field(description= "Comprehensive conclusion based on report sections" )
















# === TypedDict Classes for LangGraph State (unchanged) ===
class ReportSection(TypedDict):
    section_heading: str 
    section_content: str
    section_urls: Optional[List[str]]

class ResearchReviewData(TypedDict):
    query : str
    raw_research_results: List[tuple[str, str]] # (gap_query_data, url)
    review_feedback: Annotated[List[str], operator.add]
    report_sections: List[ReportSection]

# --- Global Graph State (unchanged) ---
class AgentGraphState(TypedDict):
    # report Layout 
    report_introduction:str
    report_conclusion:str
    report_abstract:str 
    report_methodology:str 
    report_table_of_contents:str 
    report_sections: List[ReportSection]          # these sections from Researcher 
    updated_report_sections :str                  # these sections after Writer review them and wrote it better 
    research_review: ResearchReviewData
    report_outline :str 
    
    #--------------------------
    # final report path 
    final_report_path: str
