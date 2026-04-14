"""
Event store for wort.chat_events table operations.

Persists UI-visible events for session replay: user queries, router thinking,
plans, agent summaries, and assistant responses. Excludes ephemeral streaming
tokens and per-tick progress updates.
"""

import logging
import uuid
from typing import Optional, List, Dict, Any
from uuid import UUID

from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


class EventStore:
    """
    Insert and query operations on wort.chat_events.

    Events are ordered per-session via event_order and typed
    by event_type for frontend rendering decisions.
    """

    def __init__(self, pool: AsyncConnectionPool):
        """
        Args:
            pool: Shared async connection pool from DatabasePool.
        """
        self._pool = pool

    async def insert(
        self,
        session_id: str,
        event_type: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Appends a single event to the session timeline.

        Automatically assigns the next event_order by counting
        existing events for the session.

        Args:
            session_id: Session/thread UUID string.
            event_type: One of: user_query, router_thinking, plan, plan_feedback,
                        agent_summary, writer_summary, report_ready, assistant_response.
            content: Text/markdown content of the event (nullable for report_ready).
            metadata: Additional structured data as JSONB.

        Returns:
            The created event as a dictionary.
        """
        event_id = str(uuid.uuid4())
        meta = metadata or {}

        async with self._pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """
                    INSERT INTO wort.chat_events
                        (event_id, session_id, event_order, event_type, content, metadata)
                    VALUES (
                        %s, %s,
                        COALESCE(
                            (SELECT MAX(event_order) + 1
                             FROM wort.chat_events WHERE session_id = %s),
                            1
                        ),
                        %s, %s, %s::jsonb
                    )
                    RETURNING *
                    """,
                    (event_id, session_id, session_id, event_type, content, _to_json(meta)),
                )
                row = await cur.fetchone()
                await conn.commit()
                return self._serialize(row)

    async def insert_batch(
        self,
        session_id: str,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Inserts multiple events in a single transaction with sequential ordering.

        Each event dict must have 'event_type' and optionally 'content' and 'metadata'.

        Args:
            session_id: Session/thread UUID string.
            events: List of event dicts to insert.

        Returns:
            List of created event dicts.
        """
        if not events:
            return []

        results = []
        async with self._pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """
                    SELECT COALESCE(MAX(event_order), 0) as max_order
                    FROM wort.chat_events WHERE session_id = %s
                    """,
                    (session_id,),
                )
                row = await cur.fetchone()
                next_order = (row["max_order"] if row else 0) + 1

                for event in events:
                    event_id = str(uuid.uuid4())
                    meta = event.get("metadata") or {}
                    await cur.execute(
                        """
                        INSERT INTO wort.chat_events
                            (event_id, session_id, event_order, event_type, content, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                        RETURNING *
                        """,
                        (
                            event_id,
                            session_id,
                            next_order,
                            event["event_type"],
                            event.get("content"),
                            _to_json(meta),
                        ),
                    )
                    result_row = await cur.fetchone()
                    results.append(self._serialize(result_row))
                    next_order += 1

                await conn.commit()
        return results

    async def list_by_session(
        self, session_id: str, limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Returns all events for a session in chronological order.

        Used by the frontend to reconstruct session history after
        page refresh or when opening a past session.

        Args:
            session_id: Session/thread UUID string.
            limit: Max events to return.

        Returns:
            List of event dicts ordered by event_order ASC.
        """
        async with self._pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """
                    SELECT * FROM wort.chat_events
                    WHERE session_id = %s
                    ORDER BY event_order ASC
                    LIMIT %s
                    """,
                    (session_id, limit),
                )
                rows = await cur.fetchall()
                return [self._serialize(r) for r in rows]

    @staticmethod
    def _serialize(row: Dict) -> Dict[str, Any]:
        """Converts UUID and datetime fields for JSON serialization."""
        result = dict(row)
        for key in ("event_id", "session_id"):
            if key in result and isinstance(result[key], UUID):
                result[key] = str(result[key])
        if "created_at" in result:
            result["created_at"] = result["created_at"].isoformat()
        return result


def _to_json(data: Dict) -> str:
    """Converts a dict to a JSON string for JSONB parameter binding."""
    import json
    return json.dumps(data, default=str)
