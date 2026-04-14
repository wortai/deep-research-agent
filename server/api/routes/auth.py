"""
Authentication endpoints for Google OAuth and JWT-based session verification.

POST /api/auth/google  — Exchange a Google token for a JWT + user profile.
GET  /api/auth/me      — Return the authenticated user's profile (requires JWT).
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from server.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


class GoogleTokenRequest(BaseModel):
    id_token: str | None = Field(
        None, min_length=1, description="Google ID token from frontend"
    )
    access_token: str | None = Field(
        None, min_length=1, description="Google OAuth2 access token from frontend"
    )


@router.post("/api/auth/google")
async def google_auth(request: Request, body: GoogleTokenRequest):
    auth_service = getattr(request.app.state, "auth_service", None)
    if not auth_service:
        raise HTTPException(status_code=503, detail="Auth service not initialized")

    if not body.id_token and not body.access_token:
        raise HTTPException(
            status_code=400,
            detail="Must provide either id_token or access_token",
        )

    try:
        if body.access_token:
            idinfo = await auth_service.verify_google_access_token(body.access_token)
        else:
            idinfo = await auth_service.verify_google_token(body.id_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from None
    except Exception as exc:
        logger.warning("Google token verification failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid Google token") from None

    google_id = idinfo.get("sub")
    email = idinfo.get("email")
    name = idinfo.get("name", "")
    picture = idinfo.get("picture", "")

    if not google_id or not email:
        raise HTTPException(
            status_code=400,
            detail="Google token missing required fields (sub, email)",
        )

    try:
        user = await auth_service.find_or_create_user(google_id, email, name, picture)
    except Exception as exc:
        logger.exception("User creation/lookup failed for google_id=%s", google_id)
        raise HTTPException(
            status_code=500, detail="Failed to create or find user"
        ) from None

    jwt_token = auth_service.create_jwt(user)

    return {"jwt": jwt_token, "user": user}


@router.get("/api/auth/me")
async def get_me(user=Depends(get_current_user)):  # noqa: B008
    """Return the authenticated user's profile.

    Requires Authorization: Bearer <jwt> header.
    """
    return user
