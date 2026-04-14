"""
Response Composer for generating final user responses.

Handles all response types:
- websearch: Summarize quick search results
- deepsearch/extremesearch: Report summary + PDF link
"""

from typing import Dict, Any, List
from urllib.parse import urlparse
from llms import LlmsHouse
from graphs.states.subgraph_state import AgentGraphState
from langchain_core.messages import HumanMessage, SystemMessage
from response.utils import _extract_citation_label, _build_citation_map
from prompt_datetime import now_utc_for_prompt
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


from response.response_prompts import (
    WEBSEARCH_SYSTEM_PROMPT,
    WEBSEARCH_HUMAN_TEMPLATE,
    REPORT_SUMMARY_PROMPT,
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
        self.llm = LlmsHouse.grok_model(
            model_name="grok-4-1-fast-reasoning",
            temperature=1.1,
            max_output_tokens=12000,
            top_p=0.9,
            top_k=40,
        )

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
            state: Current graph state with search_mode, user_query, etc.

        Returns:
            State update with final_response, chat_messages, current_phase.
        """
        search_mode = state.get("search_mode", "deepsearch")
        user_query = state.get("user_query", "")

        logger.info(f"[ResponseComposer] Composing response for mode: {search_mode}")

        try:
            response = ""
            prompt = ""

            match search_mode:
                case "websearch":
                    websearch_results = state.get("websearch_results", [])
                    latest_data = websearch_results[-1] if websearch_results else {}
                    latest_results = latest_data.get("results", [])
                    latest_images = latest_data.get("images", [])

                    formatted_results = ""
                    citation_entries: List[Dict[str, str]] = []

                    if isinstance(latest_results, list):
                        for i, res in enumerate(latest_results, 1):
                            title = res.get("title", "No Title")
                            url = res.get("url", "No URL")
                            content = res.get("content", "No Content")

                            formatted_results += f"--- SEARCH RESULT {i} ---\n"
                            formatted_results += f"SOURCE TITLE: {title}\n"
                            formatted_results += f"SOURCE URL: {url}\n"
                            label = _extract_citation_label(title, url)
                            formatted_results += f"CITATION_LABEL: {label}\n"
                            formatted_results += f"EXTRACTED CONTENT:\n{content}\n"
                            formatted_results += "--------------------------------------------------------\n\n"

                            citation_entries.append({"label": label, "url": url})
                    else:
                        formatted_results = str(latest_results)

                    if latest_images:
                        formatted_results += "\n=== IMAGES FOR REFERENCE ===\n"
                        for idx, img in enumerate(latest_images, 1):
                            img_title = img.get("title") or img.get("description") or "Image"
                            img_url = img.get("url", "")
                            img_desc = img.get("description", "")
                            formatted_results += (
                                f"IMAGE {idx}: ![{img_title}]({img_url})\n"
                                f"  CONTEXT: {img_desc}\n"
                            )
                        formatted_results += "============================\n"

                    citation_map = _build_citation_map(citation_entries)

                    chat_messages = state.get("chat_messages", [])
                    chat_history = "\n".join(
                        f"{m.get('role', 'unknown')}: {m.get('content', '')}"
                        for m in chat_messages[-5:]
                    ) if chat_messages else "No prior conversation."

                    skill = state.get("response_skill", "") or "Use clear prose with bold key facts. Lead with the direct answer."

                    system_prompt = WEBSEARCH_SYSTEM_PROMPT
                    human_prompt = WEBSEARCH_HUMAN_TEMPLATE.format(
                        current_datetime=now_utc_for_prompt(),
                        user_query=user_query,
                        chat_history=chat_history,
                        citation_map=citation_map,
                        research_results=formatted_results or "No websearch results found.",
                        response_skill=skill,
                    )

                    prompt = None
                    async for chunk in self.llm.astream([
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=human_prompt),
                    ]):
                        response += chunk.content

                    print(f"\n{'='*80}")
                    print(f"[DEBUG] RAW WEBSEARCH LLM OUTPUT:")
                    print(f"{'='*80}")
                    print(response)
                    print(f"{'='*80}\n")

                    final_text = response.strip() or "I could not generate a response. Please try again."
                    assistant_message = self._create_chat_message("assistant", final_text)
                    return {
                        "chat_messages": [assistant_message],
                        "final_response": final_text,
                        "current_phase": "responding",
                    }

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
                    )

                case "edit":
                    response = "I have applied your edit request to the report flow placeholder. Detailed edit behavior will be expanded next."

                case _:
                    logger.warning(
                        f"[ResponseComposer] Unknown search_mode '{search_mode}', using deepsearch summary path."
                    )
                    reports = state.get("reports", [])
                    latest_report = reports[-1] if reports else {}
                    prompt = REPORT_SUMMARY_PROMPT.format(
                        user_query=user_query,
                        abstract=latest_report.get("abstract", "")[:500],
                        introduction=latest_report.get("introduction", "")[:500],
                    )

            if prompt:
                async for chunk in self.llm.astream([HumanMessage(content=prompt)]):
                    response += chunk.content

                final_text = response.strip() or "I could not generate a response. Please try again."
                assistant_message = self._create_chat_message("assistant", final_text)
                return {
                    "chat_messages": [assistant_message],
                    "final_response": final_text,
                    "current_phase": "responding",
                }

            if response:
                assistant_message = self._create_chat_message("assistant", response)
                return {
                    "chat_messages": [assistant_message],
                    "final_response": response,
                    "current_phase": "responding",
                }

            fallback_text = "I could not generate a response. Please try again."
            fallback = self._create_chat_message("assistant", fallback_text)
            return {
                "chat_messages": [fallback],
                "final_response": fallback_text,
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
