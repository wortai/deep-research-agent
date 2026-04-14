import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from server.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sessions/{session_id}/report")
async def get_session_report(
    request: Request,
    session_id: str,
    user=Depends(get_current_user),
):
    """Get the report for a session.

    Requires a valid JWT in the Authorization header.
    """
    checkpoint_reader = getattr(request.app.state, "checkpoint_reader", None)
    if not checkpoint_reader:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    reports = await checkpoint_reader.get_reports(session_id)
    if not reports:
        raise HTTPException(status_code=404, detail="No report found for this session")

    return {"session_id": session_id, "reports": reports}
