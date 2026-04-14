"""
Checkpoint reader for extracting report and state data from LangGraph checkpoints.

Instead of duplicating report content in a separate table, this utility reads
directly from the LangGraph checkpoint tables using the existing checkpointer.
A session_id (== thread_id) is the lookup key.
"""

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class CheckpointReader:
    """
    Reads report, response, and planner data from LangGraph checkpoints.

    Uses the AsyncPostgresSaver checkpointer to fetch the latest state
    snapshot for a given thread_id, then extracts specific channel values.
    """

    def __init__(self, checkpointer):
        """
        Args:
            checkpointer: LangGraph AsyncPostgresSaver or MemorySaver instance
                          (the same one used for graph compilation).
        """
        self._checkpointer = checkpointer

    async def get_report(self, thread_id: str) -> Dict[str, Any]:
        """
        Reads the full report from the latest checkpoint of a thread.

        Extracts the latest report from the 'reports' list.
        Returns empty dict if no report data exists.

        Args:
            thread_id: Session/thread UUID string (same as session_id).

        Returns:
            Report dictionary with all sections, or empty dict.
        """
        values = await self._get_channel_values(thread_id)
        if not values:
            return {}

        reports = values.get("reports", [])
        if not reports:
            return {}

        latest_report = reports[-1]
        
        return {
            "abstract": latest_report.get("abstract", ""),
            "introduction": latest_report.get("introduction", ""),
            "body_sections": latest_report.get("body_sections", []),
            "conclusion": latest_report.get("conclusion", ""),
            "table_of_contents": latest_report.get("table_of_contents", ""),
            "query": latest_report.get("query", ""),
            "run_id": latest_report.get("run_id", "")
        }

    async def get_reports(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Reads all reports from the latest checkpoint of a thread.

        Args:
            thread_id: Session/thread UUID string.

        Returns:
            List of all ReportData dictionaries.
        """
        values = await self._get_channel_values(thread_id)
        if not values:
            return []

        return values.get("reports", [])

    async def get_final_response(self, thread_id: str) -> str:
        """
        Reads the final_response text from the last checkpoint.

        Used for websearch and follow-up intents where no full report
        is generated, only a text response.

        Args:
            thread_id: Session/thread UUID string.

        Returns:
            Final response string or empty string.
        """
        values = await self._get_channel_values(thread_id)
        return values.get("final_response", "") if values else ""

    async def get_planner_queries(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Reads planner_query list from the checkpoint.

        Args:
            thread_id: Session/thread UUID string.

        Returns:
            List of PlannerQuery dicts with query_num and query text.
        """
        values = await self._get_channel_values(thread_id)
        return values.get("planner_query", []) if values else []

    async def get_session_summary(self, thread_id: str) -> Dict[str, Any]:
        """
        Reads a lean summary of the session state for sidebar preview.

        Extracts user_query, intent_type, search_mode, current_phase,
        and whether a report exists from the latest checkpoint.

        Args:
            thread_id: Session/thread UUID string.

        Returns:
            Summary dict with key state fields.
        """
        values = await self._get_channel_values(thread_id)
        if not values:
            return {}

        return {
            "user_query": values.get("user_query", ""),
            "intent_type": values.get("intent_type", ""),
            "search_mode": values.get("search_mode", ""),
            "current_phase": values.get("current_phase", ""),
            "has_report": len(values.get("reports", [])) > 0,
        }

    async def _get_channel_values(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches channel_values from the latest checkpoint for a thread.

        Args:
            thread_id: LangGraph thread identifier.

        Returns:
            Channel values dict or None if no checkpoint exists.
        """
        config = {"configurable": {"thread_id": thread_id}}
        try:
            checkpoint_tuple = await self._checkpointer.aget_tuple(config)
            if checkpoint_tuple and checkpoint_tuple.checkpoint:
                return checkpoint_tuple.checkpoint.get("channel_values", {})
        except Exception as e:
            logger.error(f"Failed to read checkpoint for thread {thread_id}: {e}")
        return None
