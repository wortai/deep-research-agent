"""
Intent Router for classifying user queries.

Determines workflow path based on:
1. Search mode from frontend (websearch/deepsearch/extremesearch)
2. Context-based detection (follow_up/edit/clarification/off_topic)
"""

from typing import Dict, Any, Optional
from langchain_core.output_parsers import JsonOutputParser
from llms.llms import LlmsHouse
from graphs.states.subgraph_state import AgentGraphState
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


INTENT_CLASSIFICATION_PROMPT = """You are an intent classifier for a research assistant.

Given the user's query and conversation context, classify the intent.

## User Query
{user_query}

## Current Report Exists
{has_report}

## Conversation History
{chat_history}

## Classification Rules
1. If user asks about details from an existing report → "follow_up"
2. If user wants to edit/change/update the report → "edit"
3. If user is answering a question you asked → "clarification"
4. If query is unrelated to research (e.g., "I want cookies", "hi", "who are you") → "off_topic"
5. For ALL NEW research questions (e.g., "what is X", "find me Y"), return "use_search_mode". DO NOT return "deepsearch" or "websearch" directly.

## Response Format
Return JSON:
{{
    "intent": "follow_up" | "edit" | "clarification" | "off_topic" | "use_search_mode",
    "edit_instructions": "what to edit" (only if intent is "edit"),
    "reasoning": "explanation"
}}
"""


class IntentRouter:
    """
    Classifies user intent and routes to appropriate workflow.
    
    Uses chat_messages history to detect follow-up questions,
    edit requests, and clarifications. Falls back to frontend-provided
    search_mode for new research requests.
    """

    def __init__(self):
        """Initialize with LLM for context-aware classification."""
        self.llm = LlmsHouse.google_model("gemini-2.5-flash")
        self.parser = JsonOutputParser()
        self.chain = self.llm | self.parser

    def _format_chat_history(self, chat_messages: list) -> str:
        """Format chat_messages for prompt context."""
        if not chat_messages:
            return "No previous conversation."
            
        lines = []
        for msg in chat_messages[-5:]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:200]
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def route(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Classify intent and determine workflow path.
        
        Args:
            state: Current state with user_query, chat_messages, search_mode.
            
        Returns:
            State update with intent_type and optionally edit_instructions.
        """
        user_query = state.get("user_query", "")
        search_mode = state.get("search_mode", "deepsearch")
        chat_messages = state.get("chat_messages", [])
        has_report = bool(state.get("report_body"))
        
        if not user_query:
            logger.warning("[IntentRouter] No user query provided")
            return {"intent_type": "off_topic", "current_phase": "routing"}
        
        prompt = INTENT_CLASSIFICATION_PROMPT.format(
            user_query=user_query,
            has_report="Yes - report exists in context" if has_report else "No report yet",
            chat_history=self._format_chat_history(chat_messages)
        )
        
        try:
            result = self.chain.invoke(prompt)
            intent = result.get("intent", "use_search_mode")
            
            if intent == "use_search_mode":
                intent = search_mode
                
            logger.info(f"[IntentRouter] Classified intent: {intent}")
            
            response = {
                "intent_type": intent,
                "current_phase": "routing",
                "router_thinking": result.get("reasoning", "Mergin my Conciousness with universe to find the best possible answer for you")
            }
            
            if intent == "edit" and result.get("edit_instructions"):
                response["edit_instructions"] = result["edit_instructions"]
                
            return response
            
        except Exception as e:
            logger.error(f"[IntentRouter] Classification failed: {e}")
            return {"intent_type": search_mode, "current_phase": "routing"}


def router_node(state: AgentGraphState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for IntentRouter.
    
    Reads user_query, search_mode, chat_messages from state
    and returns intent_type for conditional routing.
    """
    router = IntentRouter()
    return router.route(state)
