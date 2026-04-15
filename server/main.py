import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv

# Add project root and deep-research-agent to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
deep_research_agent_dir = os.path.join(parent_dir, "deep-research-agent")

sys.path.append(parent_dir)  # Resolve 'server' package
sys.path.append(current_dir)  # Resolve 'redis_streams', 'server' subpackages
sys.path.append(deep_research_agent_dir)  # Resolve 'graphs', 'memory', etc.

# Explicitly load .env from deep-research-agent directory
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global State ---
# Attached to app.state in lifespan
memory_facade: Optional[MemoryFacade] = None
db_pool: Optional[DatabasePool] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize memory and storage systems on startup."""
    global memory_facade, db_pool
    db_uri = os.getenv("DATABASE_URL")
    cloud_sql_instance = os.getenv("CLOUD_SQL_INSTANCE_CONNECTION_NAME")
    if cloud_sql_instance:
        logger.info("Using Cloud SQL instance: %s", cloud_sql_instance)

    memory_facade = MemoryFacade(db_uri)
    await memory_facade.initialize()

    db_pool = DatabasePool(db_uri)
    await db_pool.open()

    session_store = SessionStore(db_pool.pool)
    event_store = EventStore(db_pool.pool)
    auth_service = AuthService(db_pool.pool)
    checkpoint_reader = CheckpointReader(memory_facade.checkpointer)

    app.state.memory_facade = memory_facade
    app.state.session_store = session_store
    app.state.event_store = event_store
    app.state.auth_service = auth_service
    app.state.checkpoint_reader = checkpoint_reader
    app.state.active_threads: set[str] = set()  # Tracks threads with running graph tasks

    logger.info("Memory and storage systems initialized")

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
    yield

    if db_pool:
        await db_pool.close()
    if memory_facade:
        await memory_facade.shutdown()
    logger.info("All systems shut down")


app = FastAPI(lifespan=lifespan)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(websocket.router)
app.include_router(routes.router)

# Serve Frontend
# Make client path absolute relative to this file
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
