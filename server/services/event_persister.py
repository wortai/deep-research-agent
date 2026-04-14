"""
Persistence layer for streaming events.

Handles write-through persistence of chat events and session metadata
during WebSocket streaming. Called by StreamService as events occur.
"""

import logging
from typing import Any, Dict, Optional

from server.storage.session_store import SessionStore
from server.storage.event_store import EventStore

logger = logging.getLogger(__name__)


class EventPersister:
    """
    Persists UI-visible events to wort schema during streaming.

    Wraps SessionStore and EventStore with silent error handling
    so persistence failures never interrupt WebSocket streaming.
    """

    def __init__(
        self,
        session_store: Optional[SessionStore] = None,
        event_store: Optional[EventStore] = None,
    ):
        self._session_store = session_store
        self._event_store = event_store

    @property
    def is_enabled(self) -> bool:
        """Returns True if both stores are available for persistence."""
        return self._session_store is not None and self._event_store is not None

    async def persist_session_start(
        self, thread_id: str, user_id: str, user_message: str, search_mode: str
    ) -> None:
        """Creates a wort.sessions row and a user_query event."""
        if not self.is_enabled:
            return

        try:
            title = user_message[:80].strip() or "New Research"
            await self._session_store.create(
                session_id=thread_id,
                user_id=user_id,
                title=title,
                search_mode=search_mode,
            )
            await self._event_store.insert(
                session_id=thread_id,
                event_type="user_query",
                content=user_message,
                metadata={"search_mode": search_mode},
            )
        except Exception as e:
            logger.error(f"Failed to persist session start: {e}")

    async def persist_event(
        self,
        thread_id: str,
        event_type: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Inserts a single chat event into wort.chat_events."""
        if not self._event_store:
            return

        try:
            await self._event_store.insert(
                session_id=thread_id,
                event_type=event_type,
                content=content,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Failed to persist event {event_type}: {e}")

    async def mark_report_ready(self, thread_id: str) -> None:
        """Sets has_report=true on the session after writer completes."""
        if self._session_store:
            try:
                await self._session_store.mark_report_ready(thread_id)
            except Exception as e:
                logger.error(f"Failed to mark report ready: {e}")

    async def mark_completed(self, thread_id: str) -> None:
        """Sets session status to 'completed' after response_node finishes."""
        if self._session_store:
            try:
                await self._session_store.mark_completed(thread_id)
            except Exception as e:
                logger.error(f"Failed to mark session completed: {e}")

    async def update_intent(self, thread_id: str, intent_type: str) -> None:
        """Records the classified intent on the session after router_node runs."""
        if self._session_store:
            try:
                await self._session_store.update_intent(thread_id, intent_type)
            except Exception as e:
                logger.error(f"Failed to update intent: {e}")
