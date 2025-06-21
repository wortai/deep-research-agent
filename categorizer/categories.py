from enum import Enum
from pydantic import BaseModel, Field, field_validator
class ResearchCategory(Enum):
    """Enum representing the available research categories"""
    CODING = "coding"
    FINANCE = "finance"
    NEWS = "news"
    HISTORY = "history"
    GENERAL = "general"
    WRITING = "writing"
   


class CategorizationResponse(BaseModel):
    """
    Structured response model for categorizing user intent or content into a single, most appropriate 
    research category, based on the semantic and contextual signals found in the input (e.g., messages, 
    planner prompt, or goal statements). This model is optimized for LLM-driven evaluation and scoring.

    ---------------------
    🧠 CATEGORY SELECTION
    ---------------------
    Select ONE category from the predefined set of research domains below. Choose the one that most 
    strongly reflects the core *intent* and *nature* of the input content. The categories are:

    - CODING: Any task related to programming, debugging, code generation, algorithm development, 
      or technical implementation of software systems.
      
    - FINANCE: Involves financial planning, investment advice, budgeting, markets, or economic reasoning.
    
    - NEWS: Involves staying informed, summarizing events, or reasoning about real-world developments, 
      including current events or fact-gathering.

    - HISTORY: Focused on past events, historical analysis, context building from previous eras, 
      or understanding the evolution of topics over time.

    - WRITING: Focused on generating, improving, or planning written content — including storytelling, 
      copywriting, essay writing, scripting, or other expressive formats.

    - GENERAL: Use only when the content is too broad, lacks a clear topical anchor, or does not fit 
      cleanly into any of the above categories. Should be a fallback, not a default.

    -----------------------------------------------
    🔍 HOW TO THINK THROUGH THE CATEGORY ASSIGNMENT
    -----------------------------------------------
    To assign a category, follow this reasoning process step-by-step:

    1. **Extract Core Objective**: Identify the core goal or problem being solved. Ignore surface keywords — 
       aim to understand *what the user is trying to achieve*.

    2. **Evaluate Dominant Theme**: Is the content primarily technical (code), financial, analytical, creative, 
       etc.? Identify the dominant research mode.

    3. **Eliminate Non-Fits**: For each category, ask: "Does the intent clearly match this domain?" 
       Eliminate any category that only partially applies.

    4. **Consider Overlap Cases Carefully**:
        - If writing code *and* asking for explanation, it’s likely **CODING**.
        - If narrating a story or composing text, it leans **WRITING**.
        - If mixing history and writing (e.g., writing historical fiction), prefer **WRITING** but explain the nuance.
        - If information is purely factual, lean toward **NEWS** or **HISTORY** depending on recency.

    5. **Default to GENERAL only when truly necessary**. Avoid choosing GENERAL unless none of the other domains 
       dominate or if the content is vague or too meta.

    ----------------------------------------
    📈 CONFIDENCE SCORE: HOW TO JUDGE ACCURACY
    ----------------------------------------
    The confidence score should reflect how *unambiguously* and *strongly* the content supports the 
    selected category. Think of it as a probability estimate that another expert would agree with the 
    same choice.

    - Use **1.0** only when there is **no ambiguity or overlap** (e.g., “generate a Python script” → clearly CODING).
    - Use **0.7–0.9** when the match is strong but there could be mild overlap or complexity.
    - Use **0.4–0.6** if multiple categories are plausible and your choice is the best available but not ideal.
    - Use **<0.4** if the input is vague, unclear, or nearly equally maps to multiple domains.

    ------------------
    📝 REASONING FIELD
    ------------------
    The `reasoning` field should contain a detailed explanation of:

    - Why the chosen category was selected.
    - What aspects of the input support this.
    - Why other categories were ruled out.
    - Any signals of ambiguity that affect the confidence score.

    This helps developers and evaluators audit the categorization logic.
    """

    category: ResearchCategory = Field(
        description=(
            "The single most appropriate category from the predefined set (CODING, FINANCE, NEWS, HISTORY, "
            "WRITING, GENERAL) that best aligns with the user's goal or intent. Choose only one."
        )
    )

    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description=(
            "A value between 0.0 and 1.0 indicating how confident you are in the selected category. "
            "Higher scores mean stronger evidence and lower ambiguity."
        )
    )

    reasoning: str = Field(
        min_length=20,
        description=(
            "A thoughtful justification for the chosen category. Explain what parts of the content point to this "
            "category, and why other categories were ruled out. Mention any overlap or ambiguity if present."
        )
    )

    @field_validator('confidence_score')
    def validate_confidence(cls, v):
        """Ensure confidence score is between 0.0 and 1.0"""
        return max(0.0, min(1.0, v))
