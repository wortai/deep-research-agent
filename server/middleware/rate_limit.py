import logging
import time
from typing import Optional, Union

from fastapi import HTTPException, Request, WebSocket

from redis_streams import RedisClient

logger = logging.getLogger(__name__)


class RateLimiter:
    """Redis sliding-window rate limiter with dual-key support (IP + user_id)."""

    def __init__(self, max_requests: int, window_seconds: int = 60):
        self._max_requests = max_requests
        self._window_seconds = window_seconds

    async def check(
        self,
        source: Union[Request, WebSocket],
        user_id: Optional[str] = None,
    ) -> None:
        """Checks rate limits for both client IP and user_id (if provided).

        Accepts either a Request or a WebSocket. Raises HTTPException(429)
        if either limit is exceeded.
        """
        client_ip = self._get_client_ip(source)
        keys = [f"rate_limit:ip:{client_ip}"]
        if user_id:
            keys.append(f"rate_limit:user:{user_id}")

        redis = RedisClient.get_instance()

        for key in keys:
            allowed, remaining = await self._sliding_window_check(redis, key)
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for {key} "
                    f"(limit={self._max_requests}/{self._window_seconds}s)"
                )
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": self._max_requests,
                        "window_seconds": self._window_seconds,
                        "remaining": remaining,
                    },
                )

    @staticmethod
    def _get_client_ip(source: Union[Request, WebSocket]) -> str:
        scope = source.scope if isinstance(source, WebSocket) else source.scope
        headers = dict(scope.get("headers", []))
        forwarded = headers.get(b"x-forwarded-for", b"").decode()
        if forwarded:
            return forwarded.split(",")[0].strip()

        client = scope.get("client")
        if client:
            return client[0]
        return "unknown"

    async def _sliding_window_check(self, redis: RedisClient, key: str) -> tuple:
        """Sliding window counter using a Redis sorted set.

        Returns (allowed: bool, remaining: int).
        """
        now = time.time()
        window_start = now - self._window_seconds

        raw_redis = redis._redis

        pipe = raw_redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, self._window_seconds + 1)
        results = await pipe.execute()

        current_count = results[1]

        if current_count >= self._max_requests:
            return False, 0

        return True, self._max_requests - current_count - 1
