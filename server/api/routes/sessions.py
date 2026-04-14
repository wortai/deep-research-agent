import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from server.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sessions")
async def list_sessions(
    request: Request,
    user=Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    """List sessions for the authenticated user.

    Requires a valid JWT in the Authorization header.
    """
    user_id = user["user_id"]
    session_store = getattr(request.app.state, "session_store", None)
    if not session_store:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    sessions = await session_store.list_by_user(user_id, limit, offset)
    return {"sessions": sessions, "count": len(sessions)}


@router.patch("/sessions/{session_id}")
async def rename_session(
    request: Request,
    session_id: str,
    user=Depends(get_current_user),
):
    """Rename a session for the authenticated user.

    Requires a valid JWT in the Authorization header.
    """
    session_store = getattr(request.app.state, "session_store", None)
    if not session_store:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    body = await request.json()
    title = body.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    await session_store.rename(session_id, title)
    return {"session_id": session_id, "title": title}


@router.delete("/sessions/{session_id}")
async def archive_session(
    request: Request,
    session_id: str,
    user=Depends(get_current_user),
):
    """Archive a session for the authenticated user.

    Requires a valid JWT in the Authorization header.
    """
    session_store = getattr(request.app.state, "session_store", None)
    if not session_store:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    await session_store.archive(session_id)
    return {"session_id": session_id, "status": "archived"}
