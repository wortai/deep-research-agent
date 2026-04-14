import logging

from fastapi import APIRouter, WebSocket

from server.middleware.auth import verify_ws_token
from server.services.stream_service import StreamService
from server.core.connection import ConnectionManager
from server.middleware import RateLimiter

logger = logging.getLogger(__name__)

router = APIRouter()
manager = ConnectionManager()

websearch_limiter = RateLimiter(max_requests=20, window_seconds=60)
deepsearch_limiter = RateLimiter(max_requests=5, window_seconds=60)

# WebSocket close codes
_WS_AUTH_REQUIRED = 1008  # Policy violation — authentication required
_WS_INTERNAL_ERROR = 1011  # Internal server error


@router.websocket("/ws/chat/{thread_id}")
async def websocket_endpoint(
    websocket: WebSocket, thread_id: str, token: str | None = None
):
    """WebSocket endpoint for the chat interface.

    Requires a valid JWT passed as a query parameter:
        /ws/chat/{thread_id}?token=<jwt>

    The token is verified before the connection is accepted. If verification
    fails, the connection is closed with an appropriate error code.
    """
    # --- Authenticate before accepting the connection ---
    try:
        payload = await verify_ws_token(websocket, token)
    except ValueError as exc:
        reason = str(exc)
        logger.warning("WebSocket auth failed: %s", reason)
        await websocket.close(code=_WS_AUTH_REQUIRED, reason=reason)
        return
    except Exception as exc:
        logger.error("WebSocket auth internal error: %s", exc, exc_info=True)
        await websocket.close(code=_WS_INTERNAL_ERROR, reason="Internal error")
        return

    user_id = payload["user_id"]
    logger.info("WebSocket authenticated: user_id=%s, thread_id=%s", user_id, thread_id)

    # --- Accept the connection (done in StreamService via ConnectionManager) ---

    app_state = websocket.app.state
    memory_facade = getattr(app_state, "memory_facade", None)
    session_store = getattr(app_state, "session_store", None)
    event_store = getattr(app_state, "event_store", None)

    service = StreamService(
        websocket=websocket,
        manager=manager,
        memory_facade=memory_facade,
        session_store=session_store,
        event_store=event_store,
        websearch_limiter=websearch_limiter,
        deepsearch_limiter=deepsearch_limiter,
    )
    await service.handle_websocket(thread_id=thread_id, user_id=user_id)
