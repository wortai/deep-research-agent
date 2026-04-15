import os
import sys
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
deep_research_agent_dir = os.path.join(parent_dir, "deep-research-agent")

sys.path.append(parent_dir)
sys.path.append(current_dir)
sys.path.append(deep_research_agent_dir)

env_path = os.path.join(deep_research_agent_dir, ".env")
load_dotenv(env_path, override=False)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from memory.memory_facade import MemoryFacade
from server.api import websocket, routes
from server.storage.database_pool import DatabasePool
from server.storage.session_store import SessionStore
from server.storage.event_store import EventStore
from server.storage.checkpoint_reader import CheckpointReader
from server.services.auth_service import AuthService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

memory_facade: Optional[MemoryFacade] = None
db_pool: Optional[DatabasePool] = None


async def _init_services(app: FastAPI):
    """Background task: initializes DB, memory, and storage."""
    global memory_facade, db_pool
    db_uri = os.getenv("DATABASE_URL")
    cloud_sql_instance = os.getenv("CLOUD_SQL_INSTANCE_CONNECTION_NAME")
    if cloud_sql_instance:
        logger.info("Using Cloud SQL instance: %s", cloud_sql_instance)

    try:
        memory_facade = MemoryFacade(db_uri)
        await memory_facade.initialize()
        logger.info("MemoryFacade initialized successfully")
    except Exception as e:
        logger.error("MemoryFacade initialization failed: %s", e)
        memory_facade = None

    try:
        db_pool = DatabasePool(db_uri)
        await db_pool.open()
        logger.info("DatabasePool opened successfully")
    except Exception as e:
        logger.error("DatabasePool initialization failed: %s", e)
        db_pool = None

    if db_pool:
        app.state.session_store = SessionStore(db_pool.pool)
        app.state.event_store = EventStore(db_pool.pool)
        app.state.auth_service = AuthService(db_pool.pool)
    else:
        app.state.session_store = None
        app.state.event_store = None
        app.state.auth_service = None
        logger.warning("Running without database — session/auth features disabled")

    if memory_facade:
        app.state.checkpoint_reader = CheckpointReader(memory_facade.checkpointer)
    else:
        app.state.checkpoint_reader = None
        logger.warning("Running without memory facade — research features disabled")

    app.state.memory_facade = memory_facade

    logger.info(
        "Startup complete (memory_facade=%s, db_pool=%s)",
        "OK" if memory_facade else "FAILED",
        "OK" if db_pool else "FAILED",
    )

    grok_key = os.getenv("GROK_API_KEY", "")
    google_key = os.getenv("GOOGLE_API_KEY", "")
    if grok_key:
        logger.info("GROK_API_KEY loaded (%s...%s)", grok_key[:4], grok_key[-4:])
    else:
        logger.warning("GROK_API_KEY is NOT set — primary model will fail!")
    if google_key:
        logger.info(
            "GOOGLE_API_KEY loaded (%s...%s) — fallback model available",
            google_key[:4],
            google_key[-4:],
        )
    else:
        logger.warning("GOOGLE_API_KEY is NOT set — no fallback model available!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.memory_facade = None
    app.state.session_store = None
    app.state.event_store = None
    app.state.auth_service = None
    app.state.checkpoint_reader = None
    app.state.active_threads: set[str] = set()

    task = asyncio.create_task(_init_services(app))

    yield

    task.cancel()
    if db_pool:
        await db_pool.close()
    if memory_facade:
        await memory_facade.shutdown()
    logger.info("All systems shut down")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket.router)
app.include_router(routes.router)

client_path = os.path.join(os.path.dirname(__file__), "client")
if os.path.exists(client_path):
    app.mount("/static", StaticFiles(directory=client_path), name="static")


@app.get("/")
async def read_root():
    index_path = os.path.join(client_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Frontend not built/found. Please check server/client directory."
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
