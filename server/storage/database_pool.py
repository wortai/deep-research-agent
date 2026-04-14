"""
Async connection pool for the wort application schema.

Manages a dedicated psycopg AsyncConnectionPool for CRUD operations
on wort.users, wort.sessions, and wort.chat_events. Separate from the
LangGraph checkpointer pool managed by ShortTermMemory.
"""

import os
import logging
from typing import Optional

from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)


class DatabasePool:
    """
    Async connection pool for wort schema operations.

    Provides open/close lifecycle and a context manager for acquiring
    connections with automatic transaction commit/rollback.
    """

    def __init__(self, db_uri: Optional[str] = None, max_size: int = 10):
        self._db_uri = db_uri or os.getenv("DATABASE_URL")
        self._max_size = max_size
        self._pool: Optional[AsyncConnectionPool] = None

    async def open(self) -> None:
        """Opens the connection pool. Must be called once during application startup."""
        if self._pool is not None:
            return

        conn_kwargs = {
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        }
        self._pool = AsyncConnectionPool(
            conninfo=self._db_uri,
            max_size=self._max_size,
            open=False,
            kwargs=conn_kwargs,
            check=AsyncConnectionPool.check_connection,
        )
        await self._pool.open()
        logger.info("DatabasePool opened and migration applied")

    async def close(self) -> None:
        """Drains and closes all connections in the pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("DatabasePool closed")

    @property
    def pool(self) -> AsyncConnectionPool:
        """Returns the underlying pool for direct use by store classes."""
        if self._pool is None:
            raise RuntimeError("DatabasePool not opened. Call open() first.")
        return self._pool
