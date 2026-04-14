from fastapi import APIRouter

from server.api.routes.health import router as health_router
from server.api.routes.sessions import router as sessions_router
from server.api.routes.events import router as events_router
from server.api.routes.reports import router as reports_router
from server.api.routes.chat_history import router as chat_history_router
from server.api.routes.pdf import router as pdf_router
from server.api.routes.auth import router as auth_router

router = APIRouter()
router.include_router(health_router)
router.include_router(sessions_router)
router.include_router(events_router)
router.include_router(reports_router)
router.include_router(chat_history_router)
router.include_router(pdf_router)
router.include_router(auth_router)

__all__ = ["router"]
