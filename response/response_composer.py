"""
Response Composer for generating final user responses.

Handles all response types:
- websearch: Summarize quick search results
- deepsearch/extremesearch: Report summary + PDF link
- follow_up: Answer using report context
- edit: Confirm changes + updated PDF
- off_topic: Polite decline with capability explanation
"""

from typing import Dict, Any
from langchain_core.output_parsers import StrOutputParser
from llms import LlmsHouse
from graphs.states.subgraph_state import AgentGraphState
from graphs.events.stream_emitter import get_emitter
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


WEBSEARCH_RESPONSE_PROMPT = """Based on the research results below, provide a concise, informative answer to the user's question.

## User Question
{user_query}

## Research Results
{research_results}

Provide a helpful, conversational response. Include key facts and cite sources where relevant.
"""

REPORT_SUMMARY_PROMPT = """Summarize the research report for the user in a conversational way.

## User's Original Question
{user_query}

## Report Abstract
{abstract}

## Key Findings (from Introduction)
{introduction}

## PDF Location
{pdf_path}

Provide a brief summary highlighting the main findings and let them know the full report is available.
"""

FOLLOW_UP_PROMPT = """Answer the user's follow-up question using the report context.

## User's Follow-up Question
{user_query}

## Report Body (for context)
{report_body}

Provide a helpful answer based on the report content.
"""

OFF_TOPIC_RESPONSE = """I'm a research assistant designed to help with in-depth research on topics. 

I can help you with:
- **Web Search**: Quick factual lookups
- **Deep Search**: Comprehensive research with detailed reports
- **Extreme Search**: Exhaustive research covering all angles

Feel free to ask me a research question and I'll help you explore it!"""


class ResponseComposer:
    """
    Generates contextual responses for all workflow outcomes.
    
    Uses LLM to synthesize appropriate responses based on
    intent_type and available state data (research results, reports).
    """

    def __init__(self):
        """Initialize with LLM for response generation."""
        self.llm = LlmsHouse.google_model("gemini-2.0-flash")
        self.chain = self.llm | StrOutputParser()

    def _format_research_results(self, research_review: list) -> str:
        """Format research review data for response prompt."""
        if not research_review:
            return "No research results available."
            
        lines = []
        for review in research_review:
            for result in review.get("raw_research_results", [])[:5]:
                lines.append(f"- {result.get('query')}: {result.get('answer', '')[:300]}")
        return "\n".join(lines[:10])

    def _create_chat_message(self, role: str, content: str) -> Dict:
        """Create a chat message for history."""
        return {
            "message_id": f"msg_{datetime.utcnow().timestamp()}",
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": "text"
        }

    def compose(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Generate appropriate response based on workflow path.
        
        Args:
            state: Final state with research/report data.
            
        Returns:
            State update with final_response and chat_messages.
        """
        intent_type = state.get("intent_type", "off_topic")
        user_query = state.get("user_query", "")
        
        logger.info(f"[ResponseComposer] Composing response for intent: {intent_type}")
        
        # Get StreamEmitter with terminal output enabled for dev
        try:
            from langgraph.config import get_stream_writer
            writer = get_stream_writer()
        except Exception:
            writer = None
        
        emitter = get_emitter(writer)
        
        try:
            if intent_type == "off_topic":
                response = OFF_TOPIC_RESPONSE
                print("\n🤖 Assistant: ", end="", flush=True)
                for token in response.split():
                    emitter.emit_token(token + " ")
                emitter.emit_token("")
                
            else:
                response = ""
                prompt = ""
                if intent_type == "websearch":
                    research_review = state.get("research_review", [])
                    prompt = WEBSEARCH_RESPONSE_PROMPT.format(
                        user_query=user_query,
                        research_results=self._format_research_results(research_review)
                    )
                    
                elif intent_type in ("deepsearch", "extremesearch"):
                    pdf_path = state.get("pdf_s3_path") or state.get("final_report_path", "")
                    prompt = REPORT_SUMMARY_PROMPT.format(
                        user_query=user_query,
                        abstract=state.get("report_abstract", "")[:500],
                        introduction=state.get("report_introduction", "")[:500],
                        pdf_path=pdf_path
                    )
                    
                elif intent_type == "follow_up":
                    prompt = FOLLOW_UP_PROMPT.format(
                        user_query=user_query,
                        report_body=state.get("report_body", "")[:3000]
                    )
                    
                elif intent_type == "edit":
                    pdf_path = state.get("pdf_s3_path") or state.get("final_report_path", "")
                    response = f"I've updated the report based on your request. The revised version is available at: {pdf_path}"
                    print("\n🤖 Assistant: ", end="", flush=True)
                    for token in response.split():
                        emitter.emit_token(token + " ")
                    emitter.emit_token("")
                response = "I apologize, but I couldn't process your request. Please try rephrasing your question."
                print("\n🤖 Assistant: ", end="", flush=True)
                for token in response.split():
                    emitter.emit_token(token + " ")

            if prompt:
                print("\n🤖 Assistant: ", end="", flush=True)
                full_response = ""
                for chunk in self.chain.stream(prompt):
                    content = chunk # Assuming chunk is already the string content
                    if content:
                        full_response += content
                        # Stream token to user
                        emitter.emit_token(content)
                        print(content, end="", flush=True)
                response = full_response # Update response with streamed content
            
            emitter.emit_token("") # Optional: signal end
            print() # Newline after assistant response
            
            assistant_message = self._create_chat_message("assistant", response)
            
            return {
                "final_response": response,
                "chat_messages": [assistant_message],
                "current_phase": "responding"
            }
            
        except Exception as e:
            logger.error(f"[ResponseComposer] Error composing response: {e}")
            return {
                "final_response": "I encountered an error generating your response. Please try again.",
                "current_phase": "responding"
            }


def response_node(state: AgentGraphState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for ResponseComposer.
    
    Generates final response based on intent_type and workflow results.
    """
    composer = ResponseComposer()
    return composer.compose(state)
