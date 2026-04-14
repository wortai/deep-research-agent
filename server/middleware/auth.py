"""
JWT authentication dependency for FastAPI routes.

Provides `get_current_user` as an opt-in dependency that individual routes
can use via `Depends(get_current_user)`. This is NOT global middleware —
routes must explicitly opt in.

Also provides `verify_ws_token` for WebSocket endpoints, which cannot use
HTTP headers and must pass the JWT as a query parameter.
"""

import logging
from typing import Any, Dict

import jwt
from fastapi import Depends, HTTPException, Request, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """FastAPI dependency that extracts and verifies the current user from a JWT.

    Usage::

        from server.middleware.auth import get_current_user

        @router.get("/protected")
        async def protected(user=Depends(get_current_user)):
            return {"user_id": user["user_id"]}

    Raises:
        HTTPException 503: If auth service is not initialized.
        HTTPException 401: If the token is missing, expired, or invalid.
    """
    auth_service = getattr(request.app.state, "auth_service", None)
    if not auth_service:
        raise HTTPException(status_code=503, detail="Auth service not initialized")

    try:
        payload = auth_service.verify_jwt(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired") from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication token"
        ) from None

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user_id")

    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def verify_ws_token(
    websocket: WebSocket, token: str | None = None
) -> Dict[str, Any]:
    """Verify a JWT from a WebSocket query parameter.

    WebSocket connections cannot set custom HTTP headers, so the frontend
    must pass the JWT as a query parameter: ``/ws/chat/{thread_id}?token=<jwt>``.

    Usage::

        payload = await verify_ws_token(websocket, token)
        user_id = payload["user_id"]

    Args:
        websocket: The WebSocket connection (used to access app.state).
        token: The JWT string extracted from the query parameter.

    Returns:
        The decoded JWT payload dict (contains ``user_id``, ``email``, etc).

    Raises:
        ValueError: If the auth service is not initialized, the token is
            missing, or the token is invalid/expired. The caller should
            close the WebSocket with an appropriate error code.
    """
    auth_service = getattr(websocket.app.state, "auth_service", None)
    if not auth_service:
        raise ValueError("Auth service not initialized")

    if not token:
        raise ValueError("Authentication required")

    try:
        payload = auth_service.verify_jwt(token)
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid authentication token")

    user_id = payload.get("user_id")
    if not user_id:
        raise ValueError("Invalid token: missing user_id")

    # Verify the user still exists in the database
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    return payload
