import json
import logging
import os
from typing import Any, Dict, List

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Singleton Redis client for async stream operations (XADD / XREAD BLOCK / DEL).

    Reads connection details from environment variables. Provides the underlying
    connection used by ChunkRouter (to write) and StreamService (to read and manage lifecycle).
    """

    _instance: "RedisClient | None" = None

    def __new__(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        password = os.getenv("REDIS_PASSWORD") or None
        username = os.getenv("REDIS_USERNAME", "default")

        if host == "localhost" and not password:
            redis_url = f"redis://{host}:{port}/0"
        else:
            redis_url = f"redis://{username}:{password}@{host}:{port}/0"

        logger.info(f"[RedisClient] Connecting to {host}:{port}")
        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "RedisClient":
        """Returns (and lazily creates) the process-wide singleton."""
        if cls._instance is None:
            cls._instance = RedisClient()
        return cls._instance

    async def ping(self) -> None:
        """Verifies the connection is alive."""
        try:
            await self._redis.ping()
            logger.info("[RedisClient] Connection verified.")
        except Exception as exc:
            logger.error(f"[RedisClient] Connection failed: {exc}")
            raise

    async def xadd(self, stream_name: str, message: Dict[str, Any]) -> str:
        try:
            payload = {"data": json.dumps(message)}
            return await self._redis.xadd(stream_name, payload)
        except Exception as exc:
            logger.error(f"[RedisClient] XADD error on '{stream_name}': {exc}")
            return ""

    async def xread_block(
        self, stream_name: str, last_id: str, block_ms: int = 1000
    ) -> List[tuple]:
        """
        Blocking read that returns all messages after last_id.

        Blocks for up to block_ms milliseconds. Called by StreamService._redis_reader_loop
        to consume the stream and forward it to WebSocket clients.
        """
        try:
            result = await self._redis.xread({stream_name: last_id}, block=block_ms)
            if not result:
                return []

            parsed: List[tuple] = []
            for _stream, messages in result:
                for msg_id, payload in messages:
                    raw = payload.get("data")
                    if raw is None:
                        continue
                    try:
                        parsed.append((msg_id, json.loads(raw)))
                    except json.JSONDecodeError:
                        logger.warning(
                            f"[RedisClient] JSON decode failed on stream='{stream_name}' id={msg_id}"
                        )

            return parsed
        except Exception as exc:
            logger.error(f"[RedisClient] XREAD error on '{stream_name}': {exc}")
            return []

    async def delete_stream(self, stream_name: str) -> None:
        try:
            await self._redis.delete(stream_name)
            logger.info(f"[RedisClient] Deleted stream '{stream_name}'")
        except Exception as exc:
            logger.error(f"[RedisClient] Error deleting stream '{stream_name}': {exc}")
