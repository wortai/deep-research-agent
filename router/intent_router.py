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

## Reports in Context
{reports_summary}

## Conversation History
{chat_history}

## Classification Rules
1. If the user asks a question that can be answered using details from ONE OF THE existing reports → "follow_up"
2. If the user wants to edit/change/update an existing report → "edit"
3. If the user is answering a question you previously asked → "clarification"
5. For ALL NEW distinct research questions (e.g., "now research Y", "what is X", "find me Z") → "use_search_mode". NEVER return "deepsearch" or "websearch" directly.

## Response Format
Return JSON:
{{
    "intent":  "edit" | "clarification" | "off_topic" | "use_search_mode",
    "edit_instructions": "what to edit" (only if intent is "edit"),
    "reasoning": "explanation of why you chose this intent"
}}
"""


class IntentRouter:
    """
    Classifies user intent and routes to appropriate workflow.
    
    Uses chat_messages history and existing reports to detect 
    follow-up questions, edit requests, and clarifications. 
    Falls back to frontend-provided search_mode for new research.
    """

    def __init__(self):
        """Initialize with LLM for context-aware classification."""
        self.llm = LlmsHouse.google_model("gemini-2.5-flash")
        self.parser = JsonOutputParser()
        self.chain = self.llm | self.parser

    def _format_chat_history(self, chat_messages: list) -> str:
        """Format chat_messages for prompt context."""
        if not chat_messages:
            print("No previous conversation.")
            return "No previous conversation."
            
        lines = []
        for msg in chat_messages[-5:]:
            role = msg.get("role", "unknown")
            # print(" messages ")
            # print("--"*20)
            # print(msg.get("content", ""))
            content = msg.get("content", "")[:200]
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
        
    def _format_reports_summary(self, reports: list) -> str:
        """Create a summary of available reports for the router."""
        if not reports:
            return "No reports generated yet."
            
        summary = f"There are {len(reports)} reports available in this thread:\n"
        for i, r in enumerate(reports, 1):
            summary += f"- Report {i}: {r.get('query', 'Unknown Topic')}\n"
        return summary

    def route(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Classify intent and determine workflow path.

        Args:
            state: Current state with user_query, chat_messages, reports, search_mode.
            
        Returns:
            State update with intent_type, router_thinking, and optionally edit_instructions.
        """
        user_query = state.get("user_query", "")
        search_mode = state.get("search_mode", "deepsearch")
        chat_messages = state.get("chat_messages", [])
        reports = state.get("reports", [])
        
        if not user_query:
            logger.warning("[IntentRouter] No user query provided")
            return {"intent_type": "off_topic", "current_phase": "routing", "router_thinking": "No query provided."}
        
        prompt = INTENT_CLASSIFICATION_PROMPT.format(
            user_query=user_query,
            reports_summary=self._format_reports_summary(reports),
            chat_history=self._format_chat_history(chat_messages)
        )
        
        try:
            result = self.chain.invoke(prompt)
            intent = result.get("intent", "use_search_mode")
            reasoning = result.get("reasoning", "Routing based on best guess.")
            
            if intent == "use_search_mode":
                # Limit deepsearches to prevent huge state blobs
                if search_mode in ("deepsearch", "extremesearch") and len(reports) >= 3:
                    logger.info("[IntentRouter] Max deepsearches (3) reached for this thread.")
                    return {
                        "intent_type": "off_topic",
                        "current_phase": "routing",
                        "router_thinking": "This thread has reached the maximum limit of 3 deep research reports. Please start a new chat for further deep research."
                    }
                intent = search_mode
                
            logger.info(f"[IntentRouter] Classified intent: {intent}")
            
            response = {
                "intent_type": intent,
                "current_phase": "routing",
                "router_thinking": reasoning
            }
            
            if intent == "edit" and result.get("edit_instructions"):
                response["edit_instructions"] = result["edit_instructions"]
                
            return response
            
        except Exception as e:
            logger.error(f"[IntentRouter] Classification failed: {e}")
            return {"intent_type": search_mode, "current_phase": "routing", "router_thinking": f"Fallback routing due to error: {e}"}


def router_node(state: AgentGraphState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for IntentRouter.
    """
    print(f"Thread ID: {state['thread_id']}")
    print("-"*50)
    # print(state["chat_messages"])
    router = IntentRouter()
    return router.route(state)
