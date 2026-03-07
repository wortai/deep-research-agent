"""
State definitions for Deep Research Agent and Subgraphs.

Includes:
- Pydantic models for LLM structured output
- ChatMessage for conversation history with tool calls
- MemoryContext for memory system integration
- Custom reducers for state channel management
- Graph state definitions for main agent and subgraphs
"""

from typing import TypedDict, List, Dict, Annotated, Optional, Literal, Any
import operator
from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Custom Reducers
# ---------------------------------------------------------------------------

def chat_messages_reducer(existing: List[Dict], new: List[Dict]) -> List[Dict]:
    """
    Reducer for chat_messages that supports both append and full replacement.

    Normal behavior: appends new messages (like operator.add).
    When the first item in `new` carries ``_context_reset: True``,
    the entire existing list is discarded and replaced with the
    remaining items. This allows the memory compactor to swap old
    messages for a compact summary without unbounded growth.
    """
    if not new:
        return existing
    if new[0].get("_context_reset"):
        return [m for m in new if not m.get("_context_reset")]
    return (existing or []) + new


# --- Pydantic Models for Structured Output ---

class ReportOutlineResponse(BaseModel):
    """
    LLM response for report outline generation (Phase 1).
    
    Produces a table of contents with chapter/subchapter hierarchy,
    a report_outline mapping headings to section_ids, plus abstract,
    introduction, and conclusion content.
    """
    table_of_contents: Dict[str, List[str]] = Field(
        description="Table of contents where keys are main chapter headings (e.g. '1. Neural Network Fundamentals') and values are arrays of subchapter headings (e.g. ['1.1 Architecture', '1.2 Activation Functions'])"
    )
    report_outline: Dict[str, List[str]] = Field(
        description="Mapping of each chapter/subchapter heading to array of section_ids required to generate that part. Keys must match exactly the headings from table_of_contents (both main chapters and subchapters)"
    )
    abstract: str = Field(
        description="Professional abstract (150-300 words) summarizing the report objectives, methodology, key findings, and conclusions in markdown"
    )
    introduction: str = Field(
        description="Comprehensive introduction with background context, research objectives, scope, and report roadmap in markdown"
    )
    conclusion: str = Field(
        description="Synthesis of all findings, key takeaways, practical recommendations, limitations, and future directions in markdown"
    )

    @model_validator(mode='before')
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        import json
        if isinstance(data, dict):
            for field in ['table_of_contents', 'report_outline']:
                if field in data and isinstance(data[field], str):
                    try:
                        # Clean markdown code blocks if present
                        value = data[field].strip()
                        if value.startswith('```json'):
                            value = value.split('```json')[1]
                        if value.endswith('```'):
                            value = value.rsplit('```', 1)[0]
                        data[field] = json.loads(value)
                    except json.JSONDecodeError:
                        pass
        return data






class ReportChapterResponse(BaseModel):
    """
    LLM response for a single chapter/subchapter body (Phase 2).
    
    Contains the generated markdown content for one chapter or subchapter,
    produced in parallel for each entry in the report_outline.
    """
    chapter_content: str = Field(
        description="Complete markdown content for this chapter/subchapter with proper headings, URLs, tables, comparisons, and formatting"
    )

    @model_validator(mode='before')
    @classmethod
    def parse_chapter_content(cls, data: Any) -> Any:
        # If the model returns a plain string (raw markdown), treat it as the content
        if isinstance(data, str):
            return {"chapter_content": data}
        return data


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
    message_type: Literal["chat", "log", "plan", "report"] = Field(
        default="chat", 
        description="Type of message: 'chat' for conversation, 'log' for system events, 'plan' for research plans, 'report' for final output"
    )
    metadata: Optional[Dict] = Field(default=None, description="Additional metadata like tokens, latency, step_duration")






















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
    section_id: str


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
    run_id: str
    query: str
    query_num: int
    raw_research_results: Annotated[List[RawResearchResult], operator.add]
    review_feedback: Annotated[List[str], operator.add]
    current_reviews: List[str]
    iteration_count: int
    logs: Annotated[List[Dict], operator.add]
    report_style_skill: str
    clarification_context: List[Dict]




class ReportBodySection(TypedDict):
    """Single report body section with unique ID for tracking."""
    section_id: str
    section_order: int
    section_content: str


class ReportData(TypedDict):
    """A complete generated report for a specific research run."""
    run_id: str
    query: str
    table_of_contents: str
    abstract: str
    introduction: str
    body_sections: List[ReportBodySection]
    conclusion: str
    css: str
    timestamp: str

class WebSearchItem(TypedDict):
    """A single web search result with title, url, and content."""
    title: str
    url: str
    content: str

class WebSearchData(TypedDict):
    """Results from a quick websearch run with top-level images."""
    run_id: str
    query: str
    results: List[WebSearchItem]
    images: List[Dict[str, str]]
    timestamp: str

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
    # Uses custom reducer: append by default, full replace on _context_reset
    chat_messages: Annotated[List[Dict], chat_messages_reducer ]
    
    # --- Memory Context (populated by memory system) ---
    memory_context: MemoryContext
    
    # --- User Input ---
    user_query: str
    
    # --- Run Tracking ---
    current_run_id: str
    
    # --- Intent & Search Mode ---
    search_mode: Literal["websearch", "deepsearch", "extremesearch"]
    intent_type: Literal[
        "websearch", "deepsearch", "extremesearch",
        "follow_up", "edit", "clarification", "off_topic"
    ]
    router_thinking:str
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
    
    # --- Clarification HITL (pre-plan) ---
    clarification_questions: List[str]
    clarification_answers: Annotated[List[Dict], operator.add]
    clarification_loop_count: int
    
    # --- Skill Selection ---
    selected_skills: List[str]
    
    # --- Human-in-the-Loop (plan approval) ---
    plan_feedback: str
    plan_approved: bool
    
    # --- Research Data ---
    research_review: Annotated[List[ResearchReviewData], operator.add]
    
    # --- Results & Reports ---
    reports: Annotated[List[ReportData], operator.add]
    websearch_results: Annotated[List[WebSearchData], operator.add]
    
    # --- Image Analysis (from websearch agent) ---
    analyzed_images: Annotated[List[Dict], operator.add]
    
    # --- Report Style Skill (LLM-generated formatting/presentation directive) ---
    report_style_skill: str
    
    # --- Response Skill (LLM-generated presentation instructions) ---
    response_skill: str
    
    # --- Response ---
    final_response: str
    
    # --- Edit Mode ---
    edit_instructions: Optional[str]

