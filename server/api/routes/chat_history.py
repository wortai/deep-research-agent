import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from server.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/chat/{thread_id}/history")
async def get_chat_history(
    request: Request,
    thread_id: str,
    user=Depends(get_current_user),
    limit: int = 50,
):
    """Get chat history for a thread.

    Requires a valid JWT in the Authorization header.
    """
    memory_facade = getattr(request.app.state, "memory_facade", None)
    if not memory_facade:
        raise HTTPException(status_code=503, detail="Memory system not initialized")

    try:
        messages = await memory_facade.short_term.get_conversation_history(
            thread_id, limit
        )
        return {"thread_id": thread_id, "messages": messages}
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
