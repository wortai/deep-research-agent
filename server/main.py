import os
import json
import logging
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graphs.deep_research_agent import DeepResearchAgent
from memory.memory_facade import MemoryFacade
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global State ---
memory_facade: Optional[MemoryFacade] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize memory system on startup."""
    global memory_facade
    db_uri = os.getenv("DATABASE_URL")
    memory_facade = MemoryFacade(db_uri)
    await memory_facade.initialize()
    logger.info("Memory system initialized")
    yield
    # Cleanup if needed

app = FastAPI(lifespan=lifespan)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---

class ChatRequest(BaseModel):
    message: str
    user_id: str
    thread_id: Optional[str] = None
    search_mode: str = "deepsearch"

class HistoryResponse(BaseModel):
    messages: List[Dict[str, Any]]

# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "ok", "memory_initialized": memory_facade is not None}

# Serve Frontend
app.mount("/static", StaticFiles(directory="client"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("client/index.html")

@app.get("/chat/{thread_id}/history")
async def get_chat_history(thread_id: str, limit: int = 50):
    """Retrieve chat history for a thread."""
    if not memory_facade:
        raise HTTPException(status_code=503, detail="Memory system not initialized")
    
    try:
        messages = await memory_facade.short_term.get_conversation_history(thread_id, limit)
        return {"thread_id": thread_id, "messages": messages}
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint.
    Returns events via Server-Sent Events (SSE).
    Events: 'token', 'log', 'plan', 'interrupt', 'done', 'error'
    """
    if not memory_facade:
        raise HTTPException(status_code=503, detail="Memory system not initialized")
    
    # Generate thread_id if not provided
    thread_id = request.thread_id or str(uuid.uuid4())
    
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Yield initial thread ID event
            yield f"data: {json.dumps({'type': 'thread_created', 'thread_id': thread_id})}\n\n"

            # Initialize agent for this request
            # We pass the memory facade so agent uses the shared connection
            agent = DeepResearchAgent(memory=memory_facade)
            
            # Prepare initial state
            # NOTE: We assume new turns invoke the agent with updated inputs.
            # Long-term memory context is handled inside `_create_initial_state` (if we passed memory_context)
            # OR we let the agent handle it.
            # In `DeepResearchAgent.run`, it calls `_create_initial_state` THEN populates memory_context.
            # We must replicate that here.
            
            initial_state = agent._create_initial_state(
                user_query=request.message,
                search_mode=request.search_mode,
                thread_id=thread_id,
                user_id=request.user_id
            )
            
            # Populate Memory Context
            # We do this explicitly because `run_with_streaming` does it.
            # If we just call `astream` on the graph, the graph itself does NOT populate memory context
            # because logic is inside `DeepResearchAgent.run` wrapper, not a node (except maybe planner uses it).
            # The planner node READS it, but doesn't populate it.
            # So we MUST populate it here.
            context = await memory_facade.get_context_for_planner(
                thread_id=thread_id,
                user_id=request.user_id,
                current_query=request.message
            )
            initial_state["memory_context"] = context
            
            config = {"configurable": {"thread_id": thread_id}}
            
            # Stream the graph execution
            # We use `subgraphs=True` to get inner events (researcher progress)
            async for chunk in agent._graph.astream(
                initial_state,
                stream_mode=["updates", "custom"],
                subgraphs=True,
                config=config
            ):
                # Handle chunks
                if len(chunk) == 3:
                    namespace, mode, data = chunk
                elif len(chunk) == 2:
                    mode, data = chunk
                    namespace = ()
                else:
                    logger.warning(f"Unknown chunk format: {len(chunk)}")
                    continue
                
                # --- Custom Events (Logs, Tokens, Progress) ---
                if mode == "custom":
                    # Deep Research Agent streaming usually emits dicts with 'event_type'
                    # e.g. {'event_type': 'agent_progress', ...}
                    # Or simple tokens? wrapper implementation details vary.
                    # Looking at `streaming/stream_event.py`, `StreamEmitter` emits structured dicts.
                    
                    event_type = data.get("event_type")
                    
                    if not event_type and isinstance(data, dict):
                        # Might be raw data?
                        pass

                    # 1. Progress Events (Logs for Frontend)
                    if event_type in ["agent_progress", "subgraph_node_progress", "phase_started"]:
                        yield f"data: {json.dumps({'type': 'log', 'data': data})}\n\n"
                        
                    # 2. Response Tokens (LLM Output)
                    elif event_type == "response_token":
                        token = data.get("payload", {}).get("token", "")
                        if token:
                            # Send minimal payload for tokens to save bandwidth
                            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                            
                    # 3. Report/Artifacts
                    elif event_type == "report_ready":
                        yield f"data: {json.dumps({'type': 'report', 'data': data.get('payload')})}\n\n"

                # --- State Updates ---
                elif mode == "updates":
                    # Check for Interrupts
                    if "__interrupt__" in data:
                        interrupt_data = data["__interrupt__"][0].value
                        plan_display = interrupt_data.get("plan_display", "")
                        # Send interrupt event
                        yield f"data: {json.dumps({'type': 'interrupt', 'plan': plan_display})}\n\n"
                        # We stop streaming here as we wait for user input (via separate 'resume' API call)
                        return

                    # Check for Chat Message Updates (Logs/Plans persisted to state)
                    # Use this to verify persistence or send 'message_stored' events if needed
                    # For now, we rely on 'log' events for real-time, and history API for persistence.

            yield f"data: {json.dumps({'type': 'done', 'thread_id': thread_id})}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Run Server ---
if __name__ == "__main__":
    import uvicorn
    # Clean up environment variables if needed
    uvicorn.run(app, host="0.0.0.0", port=8000)
