import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from server.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sessions/{session_id}/events")
async def list_session_events(
    request: Request,
    session_id: str,
    user=Depends(get_current_user),
    limit: int = 200,
):
    """List events for a session.

    Requires a valid JWT in the Authorization header.
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid session_id: must be a UUID, got '{session_id}'",
        )

    event_store = getattr(request.app.state, "event_store", None)
    if not event_store:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    events = await event_store.list_by_session(session_id, limit)
    return {"session_id": session_id, "events": events, "count": len(events)}
