import logging
import uuid

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


@router.get("/sessions/{session_id}/status")
async def get_session_status(
    request: Request,
    session_id: str,
    user=Depends(get_current_user),
):
    """Get processing status for a session.

    Checks the in-memory active_threads set to determine if a graph
    task is currently running for this thread. Falls back to checkpoint
    phase detection if active_threads is unavailable.
    Requires a valid JWT in the Authorization header.
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid session_id: must be a UUID, got '{session_id}'",
        )

    # Primary check: in-memory tracking of running graph tasks
    active_threads = getattr(request.app.state, "active_threads", set())
    is_processing = session_id in active_threads

    checkpoint_reader = getattr(request.app.state, "checkpoint_reader", None)
    has_reports = False
    current_phase = None

    if checkpoint_reader:
        values = await checkpoint_reader._get_channel_values(session_id)
        if values:
            current_phase = values.get("current_phase", "") or None
            reports = values.get("reports", [])
            has_reports = len(reports) > 0

    return {
        "session_id": session_id,
        "is_processing": is_processing,
        "current_phase": current_phase,
        "has_reports": has_reports,
    }
