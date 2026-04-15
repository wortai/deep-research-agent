"""
Session store for wort.sessions table operations.

Handles creation, listing, status updates, and metadata changes
for research sessions that map 1:1 to LangGraph thread_ids.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


class SessionStore:
    """
    CRUD operations on wort.sessions.

    Each session maps to a LangGraph thread_id. Provides methods
    for sidebar listing, status transitions, and report flagging.
    """

    def __init__(self, pool: AsyncConnectionPool):
        self._pool = pool

    async def create(
        self,
        session_id: str,
        user_id: str,
        title: str,
        search_mode: str = "deepsearch",
    ) -> Dict[str, Any]:
        """Creates a new session row. session_id must equal the LangGraph thread_id."""
        async with self._pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """
                    INSERT INTO wort.sessions (session_id, user_id, title, search_mode)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (session_id) DO NOTHING
                    RETURNING *
                    """,
                    (session_id, user_id, title, search_mode),
                )
                row = await cur.fetchone()
                await conn.commit()

                if row:
                    logger.info(f"Created session {session_id}")
                    return self._serialize(row)

                return await self.get(session_id)

    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a single session by ID."""
        async with self._pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    "SELECT * FROM wort.sessions WHERE session_id = %s",
                    (session_id,),
                )
                row = await cur.fetchone()
                return self._serialize(row) if row else None

    async def list_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Lists sessions for a user, newest first. Used for sidebar display."""
        async with self._pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """
                    SELECT * FROM wort.sessions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (user_id, limit, offset),
                )
                rows = await cur.fetchall()
                return [self._serialize(r) for r in rows]

    async def mark_report_ready(self, session_id: str) -> None:
        """Sets has_report=true after writer_node produces a report."""
        async with self._pool.connection() as conn:
            await conn.execute(
                "UPDATE wort.sessions SET has_report = TRUE WHERE session_id = %s",
                (session_id,),
            )
            await conn.commit()

    async def mark_completed(self, session_id: str) -> None:
        """Sets status='completed' when the graph run finishes."""
        async with self._pool.connection() as conn:
            await conn.execute(
                "UPDATE wort.sessions SET status = 'completed' WHERE session_id = %s",
                (session_id,),
            )
            await conn.commit()

    async def update_usage(
        self,
        session_id: str,
        user_id: str,
        input_tokens: int,
        output_tokens: int,
        total_cost: float,
    ) -> None:
        """Updates token and cost usage for the session, deducts cost from user credits.

        Credit conversion: 100 credits = $1.00 (1 credit = $0.01).
        The total_cost arrives in raw USD from CostTracker, so we multiply
        by 100 to convert to the credit unit before deducting.
        """
        if total_cost == 0 and input_tokens == 0 and output_tokens == 0:
            return

        # Convert raw USD cost to credits: 100 credits = $1.00
        credits_to_deduct = total_cost * 100

        async with self._pool.connection() as conn:
            await conn.execute(
                """
                UPDATE wort.sessions
                SET input_tokens = COALESCE(input_tokens, 0) + %s,
                    output_tokens = COALESCE(output_tokens, 0) + %s,
                    total_cost = COALESCE(total_cost, 0) + %s
                WHERE session_id = %s
                """,
                (input_tokens, output_tokens, total_cost, session_id),
            )

            await conn.execute(
                """
                UPDATE wort.users
                SET credits = COALESCE(credits, 0) - %s
                WHERE user_id = %s
                """,
                (credits_to_deduct, user_id),
            )
            await conn.commit()

    async def update_intent(self, session_id: str, intent_type: str) -> None:
        """Records the classified intent after router_node runs."""
        async with self._pool.connection() as conn:
            await conn.execute(
                "UPDATE wort.sessions SET intent_type = %s WHERE session_id = %s",
                (intent_type, session_id),
            )
            await conn.commit()

    async def rename(self, session_id: str, title: str) -> None:
        """Updates the session title (user-editable from sidebar)."""
        async with self._pool.connection() as conn:
            await conn.execute(
                "UPDATE wort.sessions SET title = %s WHERE session_id = %s",
                (title, session_id),
            )
            await conn.commit()

    async def archive(self, session_id: str) -> None:
        """Soft-deletes a session by setting status='archived'."""
        async with self._pool.connection() as conn:
            await conn.execute(
                "UPDATE wort.sessions SET status = 'archived' WHERE session_id = %s",
                (session_id,),
            )
            await conn.commit()

    @staticmethod
    def _serialize(row: Dict) -> Dict[str, Any]:
        """Converts UUID fields to strings for JSON serialization."""
        result = dict(row)
        for key in ("session_id", "user_id"):
            if key in result and isinstance(result[key], UUID):
                result[key] = str(result[key])
        if "created_at" in result:
            result["created_at"] = result["created_at"].isoformat()
        if "updated_at" in result:
            result["updated_at"] = result["updated_at"].isoformat()
        return result
