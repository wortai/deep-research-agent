"""
State definitions for Deep Research Agent and Subgraphs.

Includes:
- Pydantic models for LLM structured output
- ChatMessage for conversation history with tool calls
- MemoryContext for memory system integration
- Graph state definitions for main agent and subgraphs
"""

from typing import TypedDict, List, Dict, Annotated, Optional, Literal
import operator
from pydantic import BaseModel, Field


# --- Pydantic Models for Structured Output ---

class UnifiedReportResponse(BaseModel):
    """LLM response for complete unified report generation."""
    table_of_contents: str = Field(description="Markdown table of contents with chapter/subchapter hierarchy (1, 1.1, 1.2, 2, 2.1...)")
    abstract: str = Field(description="Professional abstract summarizing objectives, methodology, key findings, and conclusions in markdown")
    introduction: str = Field(description="Comprehensive introduction with background, context, objectives, and scope in markdown")
    report_body: str = Field(description="Main report content organized by chapters and subchapters with headings (#, ##, ###), URLs, tables, comparisons, etc. in markdown")
    conclusion: str = Field(description="Synthesis of findings, recommendations, limitations, and future directions in markdown")


# --- Chat Message Model for Memory System ---

class ChatMessage(BaseModel):
    """
    Represents a single chat message with full metadata.
    
    Captures user/assistant messages along with any tool calls
    and their execution results for complete conversation history.
    """
    message_id: str = Field(description="Unique message identifier")
    role: Literal["user", "assistant", "system", "tool"] = Field(description="Message sender role")
    content: str = Field(description="Message text content")
    timestamp: str = Field(description="ISO format timestamp of message creation")
    tool_calls: Optional[List[Dict]] = Field(default=None, description="Tool calls initiated by assistant")
    tool_results: Optional[List[Dict]] = Field(default=None, description="Results from tool execution")
    metadata: Optional[Dict] = Field(default=None, description="Additional metadata like tokens, latency")

















# --- Memory Context ---

class MemoryContext(TypedDict):
    """
    Context retrieved from memory systems for current turn.
    
    Populated by memory facade before planner/agent execution.
    """
    semantic_memories: List[Dict]
    user_profile: Optional[Dict]
    conversation_summary: Optional[str]


# --- Graph State Definitions ---

class RawResearchResult(TypedDict):
    """Single research result with query metadata."""
    query: str
    answer: str
    parent_query: str
    depth: int


class PlannerQuery(TypedDict):
    """Query from planner with position tracking."""
    query_num: int
    query: str


class ResearchReviewData(TypedDict):
    """
    Research results for one planner query.
    
    Accumulates raw results and reviewer feedback through
    the researcher-reviewer iteration loop.
    """
    query: str
    query_num: int
    raw_research_results: Annotated[List[RawResearchResult], operator.add]
    review_feedback: Annotated[List[str], operator.add]
    current_reviews: List[str]
    iteration_count: int


















class AgentGraphState(TypedDict):
    """
    Main graph state for DeepResearchAgent.
    
    Tracks conversation, memory context, planning, research,
    and report generation through the agent workflow.
    """
    # --- Session Identifiers ---
    thread_id: str
    user_id: str
    
    # --- Chat History (for short-term memory) ---
    chat_messages: Annotated[List[Dict], operator.add]
    
    # --- Memory Context (populated by memory system) ---
    memory_context: MemoryContext
    
    # --- User Input ---
    user_query: str
    
    # --- Intent & Search Mode ---
    search_mode: Literal["websearch", "deepsearch", "extremesearch"]
    intent_type: Literal[
        "websearch", "deepsearch", "extremesearch",
        "follow_up", "edit", "clarification", "off_topic"
    ]
    
    # --- Progress Tracking ---
    total_agents: int
    completed_agents: int
    total_research_steps: int
    completed_research_steps: int
    current_phase: Literal[
        "routing", "planning", "human_review", 
        "researching", "writing", "publishing", "responding"
    ]
    
    # --- Planner Output ---
    planner_query: List[PlannerQuery]
    
    # --- Human-in-the-Loop ---
    plan_feedback: str
    plan_approved: bool
    
    # --- Research Data ---
    research_review: Annotated[List[ResearchReviewData], operator.add]
    
    # --- Writer Output ---
    report_table_of_contents: str
    report_abstract: str
    report_introduction: str
    report_body: str
    report_conclusion: str
    report_methodology: str
    
    # --- Publisher Output ---
    final_report_path: str
    pdf_s3_path: Optional[str]
    
    # --- Response ---
    final_response: str
    
    # --- Edit Mode ---
    edit_instructions: Optional[str]

