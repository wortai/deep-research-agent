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
from llms import LlmsHouse
from graphs.states.subgraph_state import AgentGraphState
from langchain_core.messages import HumanMessage
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


from response.response_prompts import (
    WEBSEARCH_RESPONSE_PROMPT,
    REPORT_SUMMARY_PROMPT,
    FOLLOW_UP_PROMPT,
    OFF_TOPIC_RESPONSE,
)


class ResponseComposer:
    """
    Generates contextual responses for all workflow outcomes.

    Uses ChatGoogleGenerativeAI directly (no StrOutputParser chain)
    so LangGraph's ``messages`` stream mode can intercept AIMessageChunk
    callbacks and forward each token to the WebSocket in real time.
    """

    def __init__(self):
        """Initialize with bare ChatGoogleGenerativeAI for streaming."""
        self.llm = LlmsHouse.google_model("gemini-2.0-flash")

    def _create_chat_message(self, role: str, content: str) -> Dict:
        """Create a chat message dict for chat_messages state list."""
        return {
            "message_id": f"msg_{datetime.utcnow().timestamp()}",
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": "text"
        }

    async def compose(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Build the prompt for the current intent and invoke the LLM.

        The LLM is called via ``ainvoke`` directly — LangGraph's
        ``messages`` stream mode hooks into chat-model callbacks,
        so each token is emitted to the WebSocket automatically.

        Args:
            state: Current graph state with intent_type, user_query, etc.

        Returns:
            State update with final_response, chat_messages, current_phase.
        """
        intent_type = state.get("intent_type", "off_topic")
        user_query = state.get("user_query", "")

        logger.info(f"[ResponseComposer] Composing response for intent: {intent_type}")

        try:
            response = ""
            prompt = ""

            match intent_type:
                case "off_topic":
                    response = OFF_TOPIC_RESPONSE

                case "websearch":
                    websearch_results = state.get("websearch_results", [])
                    latest_websearch = (
                        websearch_results[-1].get("results", "")
                        if websearch_results
                        else "No websearch results found."
                    )
                    chat_messages = state.get("chat_messages", [])
                    chat_history = "\n".join(
                        f"{m.get('role', 'unknown')}: {m.get('content', '')}"
                        for m in chat_messages[-5:]
                    ) if chat_messages else "No prior conversation."

                    raw_images = state.get("analyzed_images", [])
                    images_block = "\n".join(
                        f"- IMAGE: ![{img.get('title', img.get('description', 'image')[:40])}]({img.get('url', '')})\n"
                        f"  CONTEXT: {img.get('description', 'No description')}"
                        for img in raw_images
                    ) if raw_images else "No images available."
                    skill = state.get("response_skill", "") or "Use clear prose with bold key facts. Lead with the direct answer."

                    prompt = WEBSEARCH_RESPONSE_PROMPT.format(
                        user_query=user_query,
                        chat_history=chat_history,
                        research_results=latest_websearch,
                        analyzed_images=images_block,
                        response_skill=skill,
                    )

                case "deepsearch" | "extremesearch":
                    reports = state.get("reports", [])
                    if not reports:
                        abstract = "Report generation failed or no report was created."
                        introduction = ""
                    else:
                        latest_report = reports[-1]
                        abstract = latest_report.get("abstract", "")[:500]
                        introduction = latest_report.get("introduction", "")[:500]

                    pdf_path = state.get("pdf_s3_path") or state.get("final_report_path", "")
                    prompt = REPORT_SUMMARY_PROMPT.format(
                        user_query=user_query,
                        abstract=abstract,
                        introduction=introduction,
                        pdf_path=pdf_path,
                    )

                case "follow_up":
                    reports = state.get("reports", [])
                    if not reports:
                        combined_body = "No reports have been generated yet to follow up on."
                    else:
                        latest_report = reports[-1]
                        body_sections = latest_report.get("body_sections", [])
                        combined_body = "\n\n".join(
                            s.get("section_content", "")
                            for s in sorted(body_sections, key=lambda s: s.get("section_order", 0))
                        )
                    prompt = FOLLOW_UP_PROMPT.format(
                        user_query=user_query,
                        report_body=combined_body[:30000],
                    )

                case "edit":
                    response = "I've updated the report based on your request. The revised version is available."

                case _:
                    response = "I apologize, but I couldn't process your request. Please try rephrasing your question."

            if prompt:
                async for chunk in self.llm.astream([HumanMessage(content=prompt)]):
                    response += chunk.content

                assistant_message = self._create_chat_message("assistant", response)

                logger.info(f"[ResponseComposer] Assistant response: {response}")
                return {
                    "chat_messages": [assistant_message],
                    "current_phase": "responding",
                }

        except Exception as e:
            logger.error(f"[ResponseComposer] Error composing response: {e}")
            return {
                "final_response": "I encountered an error generating your response. Please try again.",
                "current_phase": "responding",
            }


async def response_node(state: AgentGraphState) -> Dict[str, Any]:
    """Graph node entry point — delegates to ResponseComposer."""
    composer = ResponseComposer()
    return await composer.compose(state)
