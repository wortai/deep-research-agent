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
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


WEBSEARCH_RESPONSE_PROMPT = """You are a helpful research assistant. Based on the provided research results, answer the user's question accurately and concisely.

## User Question
{user_query}

## Research Results
{research_results}

## Instructions
1. Synthesize the information from the research results into a coherent, conversational response.
2. Use Markdown formatting (e.g., bolding, bullet points) to improve readability.
3. Cite sources using inline citations (e.g., [Source Name] or [1]) where relevant.
4. If the provided results do not contain enough information to answer the question, state what is missing.
5. Focus on key facts and data points while maintaining a helpful tone.

Response:"""



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

        intent_type = state.get("intent_type", "off_topic")
        user_query = state.get("user_query", "")
        
        logger.info(f"[ResponseComposer] Composing response for intent: {intent_type}")
        
        try:
            response = ""
            prompt = ""

            match intent_type:
                case "off_topic":
                    response = OFF_TOPIC_RESPONSE
                    print("\n🤖 Assistant: ", end="", flush=True)
                    print(response)

                case "websearch":
                    research_review = state.get("research_review", [])
                    prompt = WEBSEARCH_RESPONSE_PROMPT.format(
                        user_query=user_query,
                        research_results=self._format_research_results(research_review)
                    )

                case "deepsearch" | "extremesearch":
                    pdf_path = state.get("pdf_s3_path") or state.get("final_report_path", "")
                    prompt = REPORT_SUMMARY_PROMPT.format(
                        user_query=user_query,
                        abstract=state.get("report_abstract", "")[:500],
                        introduction=state.get("report_introduction", "")[:500],
                        pdf_path=pdf_path
                    )
                
                case "follow_up":
                    body_sections = state.get("report_body_sections", [])
                    combined_body = "\n\n".join(
                        s.get("section_content", "")
                        for s in sorted(body_sections, key=lambda s: s.get("section_order", 0))
                    )
                    prompt = FOLLOW_UP_PROMPT.format(
                        user_query=user_query,
                        report_body=combined_body[:30000]
                    )

                case "edit":
                    response = "I've updated the report based on your request. The revised version is available."
                    print("\n🤖 Assistant: ", end="", flush=True)
                    print(response)

                case _:
                    response = "I apologize, but I couldn't process your request. Please try rephrasing your question."
                    print("\n🤖 Assistant: ", end="", flush=True)
                    print(response)

            if prompt:
                print("\n🤖 Assistant: ", end="", flush=True)
                full_response = ""
                for chunk in self.chain.stream(prompt):
                    if chunk:
                        full_response += chunk
                        print(chunk, end="", flush=True)
                response = full_response
            
            print() 
            
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

    composer = ResponseComposer()
    return composer.compose(state)
