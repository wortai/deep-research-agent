User: I have already made an LangGraph Agent . It's a graph that does some stuff has some tools and some other things. What I am getting problem is I don't know how to give chat memory to this agent and what should my langGraph Architecture should Look like to give this agent chat memory. Both ShortTerm and Longterm.



How this memory will actuallly work with my frontend , How langGraph will know who to get .  For my Backend I am using FastAPi.



I want the Best solution in terms of architecture , speed and production.



I am asking all this in production level so also mention in production things if change when i put in production.



Go in the arcitecture of langGraph , like Node and other stuff , if i need serpate node that tracks of chat memory or retrieve it from some database . Mention the parts when it suppose to get trigger.

Here are some URLS you can use for some documentation if you need .



1) https://docs.langchain.com/oss/python/langgraph/memory 

2) https://docs.langchain.com/oss/python/langgraph/add-memory 

3) https://docs.langchain.com/oss/python/langgraph/memory#short-term-memory 

4) https://docs.langchain.com/oss/python/langgraph/memory#long-term-memory 

5) https://docs.langchain.com/oss/python/langgraph/persistence#threads 



You suppose to explain me everything in simple , how process of getting memory from database will work , when it will get trigger , when it will add . what are production things to keep in mind and all that .
Kimi: I'll help you build a production-ready memory architecture for your LangGraph agent. Let me first read the documentation you provided to give you the most accurate and up-to-date guidance.
Now let me check the "Add Memory" guide for more practical implementation details:
Now let me check the persistence page for understanding threads and checkpoints:
Now I have all the information I need. Let me create a comprehensive guide for you.
---

# LangGraph Memory Architecture: Production-Ready Guide

I'll explain everything step-by-step, from the core concepts to production implementation with FastAPI.

---

## 1. Understanding Memory Types in LangGraph

LangGraph has **two distinct memory systems**:

### Short-Term Memory (Thread-Scoped)
- **What**: Conversation history within a single chat session
- **Scope**: Only available within one `thread_id`
- **Storage**: Checkpoints (snapshots of graph state)
- **Use case**: "What did the user say 2 messages ago?"

### Long-Term Memory (Cross-Thread)
- **What**: User facts, preferences, learned information
- **Scope**: Available across ALL conversations for a user
- **Storage**: Memory Store (JSON documents with namespaces)
- **Use case**: "User is vegetarian, lives in NYC, prefers short answers"

---

## 2. The Complete Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React/Vue/etc)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  Thread ID  │  │  User ID    │  │  Messages   │                 │
│  │  (session)  │  │  (permanent)│  │             │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
└─────────┼────────────────┼────────────────┼────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  POST /chat                                                 │   │
│  │  ├── Receives: user_id, thread_id, message                  │   │
│  │  └── Returns: agent response                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              LANGGRAPH AGENT WITH MEMORY                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │   │
│  │  │  Retrieve   │  │   Agent     │  │   Save      │         │   │
│  │  │  Memory     │──│   Node      │──│  Memory     │         │   │
│  │  │  Node       │  │  (LLM+Tools)│  │   Node      │         │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘         │   │
│  │           │              │                │                 │   │
│  │           ▼              ▼                ▼                 │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              PERSISTENCE LAYER                      │   │   │
│  │  │  ┌──────────────┐        ┌─────────────────────┐   │   │   │
│  │  │  │  CHECKPOINTER│        │    MEMORY STORE     │   │   │   │
│  │  │  │  (Postgres)  │        │    (Postgres/Redis) │   │   │   │
│  │  │  │              │        │                     │   │   │   │
│  │  │  │ Thread 1:    │        │ Namespace:          │   │   │   │
│  │  │  │  - Msg 1     │        │  (user_123,         │   │   │   │
│  │  │  │  - Msg 2     │        │   "memories")       │   │   │   │
│  │  │  │  - Msg 3     │        │   - "likes pizza"   │   │   │   │
│  │  │  │              │        │   - "lives in NYC"  │   │   │   │
│  │  │  └──────────────┘        └─────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. The LangGraph Node Structure

Here's the recommended architecture for your graph:

```python
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import operator

# ============================================================
# STATE DEFINITION
# ============================================================
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: str
    # Add any other state you need
    retrieved_memories: List[dict]  # Memories fetched from store

# ============================================================
# NODE 1: LOAD LONG-TERM MEMORY (Triggered FIRST)
# ============================================================
def load_memory_node(state: AgentState, config, *, store):
    """
    This node runs FIRST on every request.
    It retrieves relevant memories from the Memory Store.
    """
    user_id = state["user_id"]
    
    # Search for relevant memories based on the latest user message
    latest_message = state["messages"][-1].content if state["messages"] else ""
    
    # Semantic search in memory store
    namespace = (user_id, "memories")
    memories = store.search(
        namespace,
        query=latest_message,
        limit=5  # Get top 5 relevant memories
    )
    
    # Also get user profile if exists
    profile = store.get(namespace, "profile")
    
    return {
        "retrieved_memories": [
            {"content": m.value, "score": m.score} for m in memories
        ]
    }

# ============================================================
# NODE 2: AGENT NODE (Your existing logic)
# ============================================================
def agent_node(state: AgentState, config, *, store):
    """
    Your main agent logic.
    Uses retrieved memories + conversation history.
    """
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4")
    
    # Build system prompt with memories
    memories_text = "\n".join([
        f"- {m['content']}" for m in state.get("retrieved_memories", [])
    ])
    
    system_prompt = f"""You are a helpful assistant.
    
User memories (use these to personalize responses):
{memories_text}

Be friendly and reference these memories naturally when relevant.
"""
    
    # Prepare messages for LLM
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend([{"role": m.type, "content": m.content} for m in state["messages"]])
    
    # Call LLM (or your existing agent logic)
    response = llm.invoke(messages)
    
    return {"messages": [AIMessage(content=response.content)]}

# ============================================================
# NODE 3: SAVE MEMORY (Triggered LAST - optional)
# ============================================================
def save_memory_node(state: AgentState, config, *, store):
    """
    This node runs AFTER the agent responds.
    It extracts and saves important facts to long-term memory.
    """
    user_id = state["user_id"]
    namespace = (user_id, "memories")
    
    # Use LLM to extract memories from the conversation
    llm = ChatOpenAI(model="gpt-4")
    
    conversation = "\n".join([
        f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
        for m in state["messages"][-4:]  # Last 2 exchanges
    ])
    
    extraction_prompt = f"""Analyze this conversation and extract key facts about the user.
Only extract concrete, useful facts (preferences, personal info, context).
Return as a JSON list of memories. If nothing new to remember, return [].

Conversation:
{conversation}

Memories to extract:"""
    
    try:
        result = llm.invoke(extraction_prompt)
        # Parse and save each memory
        import json
        memories = json.loads(result.content)
        
        for memory in memories:
            memory_id = str(uuid.uuid4())
            store.put(
                namespace,
                memory_id,
                {"fact": memory, "created_at": datetime.now().isoformat()}
            )
    except:
        pass  # Fail silently - don't break the chat if memory fails
    
    return {}  # No state changes

# ============================================================
# BUILD THE GRAPH
# ============================================================
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("load_memory", load_memory_node)
builder.add_node("agent", agent_node)
builder.add_node("save_memory", save_memory_node)

# Define flow
builder.add_edge(START, "load_memory")
builder.add_edge("load_memory", "agent")
builder.add_edge("agent", "save_memory")
builder.add_edge("save_memory", END)

# ============================================================
# COMPILE WITH PERSISTENCE
# ============================================================

# For Production: Postgres
DB_URI = "postgresql://user:pass@localhost:5432/db"

# Checkpointer for SHORT-TERM memory (conversation history)
checkpointer = PostgresSaver.from_conn_string(DB_URI)

# Store for LONG-TERM memory (user facts)
store = PostgresStore.from_conn_string(
    DB_URI,
    index={
        "embed": OpenAIEmbeddings(model="text-embedding-3-small"),
        "dims": 1536
    }
)

graph = builder.compile(checkpointer=checkpointer, store=store)
```

---

## 4. FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, AsyncGenerator
from contextlib import asynccontextmanager
import json

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================
class ChatRequest(BaseModel):
    message: str
    user_id: str           # Permanent user identifier (from your auth)
    thread_id: str         # Session/conversation ID
    clear_history: bool = False  # Optional: start fresh

class ChatResponse(BaseModel):
    response: str
    thread_id: str

# ============================================================
# CHAT ENDPOINT (Non-streaming)
# ============================================================
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    
    - user_id: Identifies WHO the user is (for long-term memory)
    - thread_id: Identifies WHICH conversation (for short-term memory)
    """
    try:
        # Prepare config with BOTH identifiers
        config = {
            "configurable": {
                "user_id": request.user_id,
                "thread_id": request.thread_id
            }
        }
        
        # Clear history if requested
        if request.clear_history:
            # Delete all checkpoints for this thread
            # (Implementation depends on your checkpointer)
            pass
        
        # Prepare input state
        input_state = {
            "messages": [HumanMessage(content=request.message)],
            "user_id": request.user_id,
            "retrieved_memories": []
        }
        
        # Run the graph
        result = await graph.ainvoke(input_state, config)
        
        # Extract the AI's response
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        last_response = ai_messages[-1].content if ai_messages else "No response"
        
        return ChatResponse(
            response=last_response,
            thread_id=request.thread_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# STREAMING CHAT ENDPOINT (For real-time responses)
# ============================================================
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming version for real-time token delivery.
    """
    from fastapi.responses import StreamingResponse
    
    config = {
        "configurable": {
            "user_id": request.user_id,
            "thread_id": request.thread_id
        }
    }
    
    input_state = {
        "messages": [HumanMessage(content=request.message)],
        "user_id": request.user_id,
        "retrieved_memories": []
    }
    
    async def generate() -> AsyncGenerator[str, None]:
        async for chunk in graph.astream(input_state, config, stream_mode="messages"):
            if isinstance(chunk[0], AIMessage):
                yield f"data: {json.dumps({'token': chunk[0].content})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

# ============================================================
# MEMORY MANAGEMENT ENDPOINTS
# ============================================================
@app.get("/memory/{user_id}")
async def get_user_memories(user_id: str):
    """Get all memories for a user."""
    namespace = (user_id, "memories")
    memories = store.search(namespace, limit=100)
    return {
        "memories": [
            {"id": m.key, "content": m.value, "score": m.score}
            for m in memories
        ]
    }

@app.delete("/memory/{user_id}/{memory_id}")
async def delete_memory(user_id: str, memory_id: str):
    """Delete a specific memory."""
    namespace = (user_id, "memories")
    # Implementation depends on your store
    return {"status": "deleted"}

@app.get("/threads/{user_id}")
async def get_user_threads(user_id: str):
    """Get all conversation threads for a user."""
    # Query your checkpointer database
    # This is pseudo-code - actual implementation varies
    threads = []  # Fetch from Postgres
    return {"threads": threads}

# ============================================================
# HEALTH CHECK
# ============================================================
@app.get("/health")
async def health():
    return {"status": "healthy", "graph": "ready"}
```

---

## 5. Frontend Integration Flow

```javascript
// ============================================
// FRONTEND EXAMPLE (React)
// ============================================

class ChatService {
  constructor() {
    // Generate or retrieve from localStorage
    this.userId = localStorage.getItem('user_id') || this.generateUserId();
    this.threadId = localStorage.getItem('thread_id') || this.generateThreadId();
  }
  
  generateUserId() {
    const id = 'user_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('user_id', id);
    return id;
  }
  
  generateThreadId() {
    const id = 'thread_' + Date.now();
    localStorage.setItem('thread_id', id);
    return id;
  }
  
  // Start a new conversation (keeps user_id, new thread_id)
  startNewChat() {
    this.threadId = this.generateThreadId();
    return this.threadId;
  }
  
  async sendMessage(message) {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        user_id: this.userId,      // Always the same user
        thread_id: this.threadId   // Same for this conversation
      })
    });
    
    return await response.json();
  }
  
  // Streaming for real-time responses
  async *streamMessage(message) {
    const response = await fetch('/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        user_id: this.userId,
        thread_id: this.threadId
      })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          yield data;
        }
      }
    }
  }
}

// ============================================
// USAGE IN REACT COMPONENT
// ============================================

function ChatComponent() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const chatService = useRef(new ChatService());
  
  const sendMessage = async () => {
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    
    // Option 1: Non-streaming
    const response = await chatService.current.sendMessage(userMsg);
    setMessages(prev => [...prev, { role: 'ai', content: response.response }]);
  };
  
  const startNewChat = () => {
    chatService.current.startNewChat();
    setMessages([]);
  };
  
  return (
    <div>
      <button onClick={startNewChat}>New Chat</button>
      {/* Chat UI */}
    </div>
  );
}
```

---

## 6. When Memory Gets Triggered

```
┌────────────────────────────────────────────────────────────────┐
│                    REQUEST LIFECYCLE                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. FRONTEND sends: {user_id: "u123", thread_id: "t456",      │
│                     message: "I love Italian food"}            │
│                      ▼                                         │
│  2. FASTAPI receives request                                   │
│                      ▼                                         │
│  3. LANGGRAPH STARTS                                           │
│     ┌─────────────────────────────────────────────────────┐   │
│     │  CHECKPOINTER loads checkpoint for thread "t456"    │   │
│     │  → Restores messages from previous turns            │   │
│     └─────────────────────────────────────────────────────┘   │
│                      ▼                                         │
│  4. NODE: load_memory                                          │
│     ┌─────────────────────────────────────────────────────┐   │
│     │  • Search memory store: namespace=("u123",          │   │
│     │    "memories"), query="I love Italian food"         │   │
│     │  • Returns: ["User likes pizza", "User lives       │   │
│     │    in NYC"]                                         │   │
│     │  • Stores in state["retrieved_memories"]            │   │
│     └─────────────────────────────────────────────────────┘   │
│                      ▼                                         │
│  5. NODE: agent                                                │
│     ┌─────────────────────────────────────────────────────┐   │
│     │  • LLM receives: system_prompt + memories +         │   │
│     │    conversation_history + new_message               │   │
│     │  • LLM generates response                           │   │
│     │  • Response added to state["messages"]              │   │
│     └─────────────────────────────────────────────────────┘   │
│                      ▼                                         │
│  6. NODE: save_memory (optional - can be async/background)    │
│     ┌─────────────────────────────────────────────────────┐   │
│     │  • LLM analyzes conversation                        │   │
│     │  • Extracts: "User likes Italian food"              │   │
│     │  • store.put(namespace=("u123", "memories"),        │   │
│     │    key=uuid(), value={"fact": "likes Italian"})     │   │
│     └─────────────────────────────────────────────────────┘   │
│                      ▼                                         │
│  7. CHECKPOINTER saves new checkpoint for thread "t456"        │
│     → Now includes the new message in short-term memory        │
│                      ▼                                         │
│  8. Response returned to frontend                              │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 7. Production Database Setup

### Postgres Schema (for both checkpointer and store)

```sql
-- Checkpointer tables (auto-created by PostgresSaver)
CREATE TABLE checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint BYTEA,
    metadata BYTEA,
    PRIMARY KEY (thread_id, checkpoint_id)
);

-- Store tables (auto-created by PostgresStore with index)
CREATE TABLE store (
    prefix TEXT NOT NULL,  -- namespace as text[]
    key TEXT NOT NULL,
    value JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (prefix, key)
);

-- For semantic search (if using embeddings)
CREATE INDEX idx_store_embedding ON store USING ivfflat (embedding vector_cosine_ops);
```

### Docker Compose for Local Development

```yaml
version: '3.8'
services:
  postgres:
    image: ankane/pgvector:latest  # Includes pgvector for embeddings
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: langgraph
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## 8. Production Checklist

| Area | Development | Production |
|------|-------------|------------|
| **Checkpointer** | `InMemorySaver()` | `PostgresSaver` or `AsyncPostgresSaver` |
| **Memory Store** | `InMemoryStore()` | `PostgresStore` or `RedisStore` |
| **Embeddings** | Local/Ollama | OpenAI/Cohere with caching |
| **Connection** | New connection per request | Connection pooling (use `asyncpg`) |
| **Error Handling** | Fail loudly | Graceful degradation (chat works even if memory fails) |
| **Security** | None | Encryption at rest (`EncryptedSerializer`) |
| **Monitoring** | Print statements | LangSmith tracing + structured logging |
| **Scaling** | Single instance | Multiple instances with shared DB |

### Production Code Changes

```python
# ============================================================
# PRODUCTION: Async + Connection Pooling
# ============================================================
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore
import asyncpg

# Use connection pool
pool = asyncpg.create_pool(
    "postgresql://user:pass@localhost/db",
    min_size=5,
    max_size=20
)

# Async checkpointer
checkpointer = AsyncPostgresSaver(pool)

# Async store with embeddings
store = AsyncPostgresStore(
    pool,
    index={
        "embed": OpenAIEmbeddings(model="text-embedding-3-small"),
        "dims": 1536
    }
)

# ============================================================
# PRODUCTION: Encryption
# ============================================================
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer

# Set LANGGRAPH_AES_KEY in environment
encrypted_serde = EncryptedSerializer.from_pycryptodome_aes()

checkpointer = PostgresSaver.from_conn_string(
    DB_URI,
    serde=encrypted_serde
)

# ============================================================
# PRODUCTION: Background Memory Writing (Recommended)
# ============================================================
"""
Instead of save_memory_node in the hot path, use:
1. Celery task that runs after chat completes
2. Or LangGraph's `send` API for background tasks
3. Or a separate memory-service that processes conversations

This keeps chat latency low while still saving memories.
"""
```

---

## 9. Quick Reference: Key Concepts

| Concept | What It Is | How to Access |
|---------|-----------|---------------|
| `thread_id` | Conversation session ID | `config["configurable"]["thread_id"]` |
| `user_id` | Permanent user identifier | `config["configurable"]["user_id"]` |
| `namespace` | Memory organization path | `(user_id, "memories")` |
| `checkpointer` | Saves conversation state | Passed to `compile(checkpointer=...)` |
| `store` | Saves long-term memories | Passed to `compile(store=...)` |
| `store.put()` | Save a memory | `store.put(namespace, key, value)` |
| `store.search()` | Find memories by similarity | `store.search(namespace, query="...")` |
| `store.get()` | Get specific memory | `store.get(namespace, key)` |

---

## Summary

1. **Short-term memory** is handled automatically by the checkpointer via `thread_id`
2. **Long-term memory** requires explicit nodes to `load` and `save` using the `store`
3. **Frontend sends** both `user_id` (permanent) and `thread_id` (session) on every request
4. **Load memory node** runs first to fetch relevant context
5. **Save memory node** runs last (or in background) to extract and store facts
6. **Production** uses Postgres for both checkpointer and store, with async operations and encryption

Would you like me to elaborate on any specific part, such as the background memory writing approach, or help you implement a specific piece of this architecture?
User: I see we using the   messages: Annotated[List[BaseMessage], operator.add] the baseMessage in our messages . How would a custom State Definition of Base message will look like . How these custom messages will be updated . 

How do we  use short-term and Long-term memory , what I mean is how do i connect the cloud URL , what should I use. What are different ways of retrieving memory and using them , what I means is how should we decide , when to trim messages or use llm to summarize and should we make different methods . 

How we will show the chats in the frontEnd , will we acess directly through the states of LangGraph.
Kimi: Excellent questions! Let me break down each part with practical examples.

---

## 1. Custom State with Custom Messages

When you need more than just `BaseMessage`, you can create custom message types and state structures:

```python
from typing import TypedDict, Annotated, List, Optional, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
import operator

# ============================================================
# CUSTOM MESSAGE TYPES
# ============================================================

class CustomMessage(TypedDict):
    """Custom message structure with metadata"""
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    timestamp: str  # ISO format
    message_id: str  # Unique ID
    metadata: dict  # Custom fields like tokens used, latency, etc.
    attachments: Optional[List[dict]]  # Files, images, etc.

# ============================================================
# CUSTOM STATE DEFINITION
# ============================================================

class CustomAgentState(TypedDict):
    # Core messages - using custom structure
    messages: Annotated[List[CustomMessage], operator.add]
    
    # Conversation metadata
    conversation_id: str
    user_id: str
    
    # Retrieved memories
    long_term_memories: List[dict]
    
    # Token tracking
    total_tokens: int
    max_tokens: int  # When to trigger summarization
    
    # Summarized history (when messages get too long)
    summary: Optional[str]
    
    # Pending tool calls
    pending_tools: List[dict]
    
    # User context
    user_context: dict  # Preferences, current task, etc.

# ============================================================
# MESSAGE HELPERS
# ============================================================

from datetime import datetime
import uuid

def create_user_message(content: str, attachments: List[dict] = None) -> CustomMessage:
    """Factory for user messages"""
    return CustomMessage(
        role="user",
        content=content,
        timestamp=datetime.now().isoformat(),
        message_id=str(uuid.uuid4()),
        metadata={"source": "web_chat"},
        attachments=attachments or []
    )

def create_assistant_message(content: str, metadata: dict = None) -> CustomMessage:
    """Factory for assistant messages"""
    return CustomMessage(
        role="assistant",
        content=content,
        timestamp=datetime.now().isoformat(),
        message_id=str(uuid.uuid4()),
        metadata=metadata or {},
        attachments=None
    )

def create_tool_message(content: str, tool_call_id: str) -> CustomMessage:
    """Factory for tool responses"""
    return CustomMessage(
        role="tool",
        content=content,
        timestamp=datetime.now().isoformat(),
        message_id=str(uuid.uuid4()),
        metadata={"tool_call_id": tool_call_id},
        attachments=None
    )

# ============================================================
# CUSTOM REDUCER (Advanced - for updating existing messages)
# ============================================================

def message_reducer(existing: List[CustomMessage], new_messages: List[CustomMessage]) -> List[CustomMessage]:
    """
    Custom reducer that:
    1. Adds new messages
    2. Updates existing messages if same ID
    3. Removes messages marked for deletion
    """
    result = {msg["message_id"]: msg for msg in existing}
    
    for msg in new_messages:
        if msg.get("_delete"):  # Special flag to remove
            result.pop(msg["message_id"], None)
        else:
            result[msg["message_id"]] = msg
    
    # Sort by timestamp
    return sorted(result.values(), key=lambda x: x["timestamp"])

# Use custom reducer
class AdvancedAgentState(TypedDict):
    messages: Annotated[List[CustomMessage], message_reducer]

# ============================================================
# UPDATING CUSTOM MESSAGES IN NODES
# ============================================================

def update_message_node(state: CustomAgentState):
    """Example: Update an existing message's metadata"""
    
    messages = state["messages"]
    
    # Find message to update
    for msg in messages:
        if msg["message_id"] == "some-id":
            # Update metadata
            msg["metadata"]["edited"] = True
            msg["metadata"]["edit_timestamp"] = datetime.now().isoformat()
    
    return {"messages": messages}  # Return updated list

def delete_message_node(state: CustomAgentState):
    """Example: Delete a message"""
    
    # Mark for deletion (custom reducer handles this)
    messages_to_delete = [
        {**msg, "_delete": True} 
        for msg in state["messages"] 
        if msg.get("should_delete")
    ]
    
    return {"messages": messages_to_delete}
```

---

## 2. Cloud Database Connections

### Short-Term Memory (Checkpointer)

```python
# ============================================================
# POSTGRES (Recommended for Production)
# ============================================================

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import asyncpg

# Option 1: Sync (simpler, blocking)
def get_sync_checkpointer():
    DB_URI = "postgresql://user:password@your-db-host.amazonaws.com:5432/dbname?sslmode=require"
    
    return PostgresSaver.from_conn_string(DB_URI)

# Option 2: Async (better for FastAPI)
async def get_async_checkpointer():
    DB_URI = "postgresql://user:password@your-db-host.amazonaws.com:5432/dbname?sslmode=require"
    
    # Connection pooling for production
    pool = await asyncpg.create_pool(
        DB_URI,
        min_size=5,
        max_size=20,
        command_timeout=60,
        server_settings={
            'jit': 'off'  # Disable JIT for faster small queries
        }
    )
    
    return AsyncPostgresSaver(pool)

# ============================================================
# REDIS (For high-performance caching)
# ============================================================

from langgraph.checkpoint.redis import RedisSaver

def get_redis_checkpointer():
    REDIS_URL = "redis://your-redis-host:6379/0"
    
    return RedisSaver.from_conn_string(REDIS_URL)

# ============================================================
# MONGODB (If you prefer document store)
# ============================================================

from langgraph.checkpoint.mongodb import MongoDBSaver

def get_mongodb_checkpointer():
    MONGO_URI = "mongodb+srv://user:pass@cluster.mongodb.net/langgraph"
    
    return MongoDBSaver.from_conn_string(MONGO_URI, db_name="langgraph")
```

### Long-Term Memory (Store)

```python
# ============================================================
# POSTGRES STORE (with semantic search)
# ============================================================

from langgraph.store.postgres import PostgresStore, AsyncPostgresStore
from langchain_openai import OpenAIEmbeddings

def get_postgres_store():
    DB_URI = "postgresql://user:password@your-db-host.amazonaws.com:5432/dbname"
    
    # For sync usage
    store = PostgresStore.from_conn_string(
        DB_URI,
        index={
            "embed": OpenAIEmbeddings(model="text-embedding-3-small"),
            "dims": 1536,
            "fields": ["content", "fact"]  # Which fields to embed
        }
    )
    
    return store

async def get_async_postgres_store():
    DB_URI = "postgresql://user:password@your-db-host.amazonaws.com:5432/dbname"
    
    pool = await asyncpg.create_pool(DB_URI)
    
    store = AsyncPostgresStore(
        pool,
        index={
            "embed": OpenAIEmbeddings(model="text-embedding-3-small"),
            "dims": 1536
        }
    )
    
    return store

# ============================================================
# REDIS STORE (faster, but no built-in semantic search)
# ============================================================

from langgraph.store.redis import RedisStore

def get_redis_store():
    REDIS_URL = "redis://your-redis-host:6379/0"
    
    # Redis store - faster for simple key-value
    # Note: For semantic search with Redis, you'd use Redis Vector DB
    return RedisStore.from_conn_string(REDIS_URL)

# ============================================================
# PINECONE/WEAVIATE (Dedicated vector DBs)
# ============================================================

# For advanced semantic search, you might use LangChain's vector stores
# and manually integrate with LangGraph store interface

from langchain_pinecone import PineconeVectorStore

class PineconeMemoryStore:
    """Custom store wrapper for Pinecone"""
    
    def __init__(self, index_name: str):
        self.vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=OpenAIEmbeddings()
        )
    
    def put(self, namespace: tuple, key: str, value: dict):
        """Store memory with metadata"""
        self.vectorstore.add_texts(
            texts=[value.get("content", "")],
            metadatas=[{**value, "namespace": namespace, "key": key}],
            ids=[f"{namespace}:{key}"]
        )
    
    def search(self, namespace: tuple, query: str, limit: int = 5):
        """Semantic search"""
        results = self.vectorstore.similarity_search(
            query, 
            k=limit,
            filter={"namespace": namespace}
        )
        return results
```

---

## 3. Memory Management Strategies

Here's a comprehensive approach with different retrieval and management methods:

```python
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langchain_openai import ChatOpenAI
from typing import Literal

# ============================================================
# STRATEGY 1: SIMPLE TRIMMING (Fast, predictable)
# ============================================================

def trim_conversation_history(
    messages: List[BaseMessage],
    strategy: Literal["last", "first"] = "last",
    max_tokens: int = 4000
) -> List[BaseMessage]:
    """
    Simple trimming - keep only recent messages.
    Best for: Most applications, fast responses
    """
    return trim_messages(
        messages,
        strategy=strategy,  # "last" = keep most recent
        token_counter=count_tokens_approximately,
        max_tokens=max_tokens,
        start_on="human",  # Start with user message
        end_on=("human", "tool"),  # End with user or tool
        include_system=True  # Always keep system message
    )

# ============================================================
# STRATEGY 2: SMART TRIMMING (Keep important messages)
# ============================================================

def smart_trim_messages(
    messages: List[BaseMessage],
    max_tokens: int = 4000
) -> List[BaseMessage]:
    """
    Smart trimming that preserves:
    - System message
    - First message (context)
    - Last 3 exchanges (recent context)
    - Messages with tool calls (important actions)
    """
    if len(messages) <= 4:
        return messages
    
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    first_msg = [messages[0]] if messages else []
    
    # Keep messages with tool calls (important actions)
    tool_msgs = [
        m for m in messages 
        if isinstance(m, AIMessage) and getattr(m, 'tool_calls', None)
    ]
    
    # Keep last 6 messages (3 exchanges)
    recent_msgs = messages[-6:] if len(messages) > 6 else messages
    
    # Combine and deduplicate
    important = list({id(m): m for m in system_msgs + first_msg + tool_msgs + recent_msgs}.values())
    
    # Sort by original order
    important.sort(key=lambda m: messages.index(m))
    
    # Trim if still too long
    return trim_messages(
        important,
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=max_tokens
    )

# ============================================================
# STRATEGY 3: SUMMARIZATION (For very long conversations)
# ============================================================

class ConversationSummarizer:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini")  # Cheaper for summarization
    
    def should_summarize(self, messages: List[BaseMessage], threshold: int = 6000) -> bool:
        """Check if conversation needs summarization"""
        token_count = count_tokens_approximately(messages)
        return token_count > threshold
    
    def summarize(self, messages: List[BaseMessage]) -> str:
        """Create summary of older messages"""
        
        # Keep recent messages for context
        recent = messages[-4:]  # Last 2 exchanges
        to_summarize = messages[:-4]  # Everything else
        
        if not to_summarize:
            return ""
        
        prompt = f"""Summarize the following conversation concisely. 
Include key facts, decisions, and context that would be needed to continue:

{self._format_messages(to_summarize)}

Summary:"""
        
        summary = self.llm.invoke(prompt).content
        return summary
    
    def _format_messages(self, messages: List[BaseMessage]) -> str:
        return "\n".join([
            f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content[:200]}"
            for m in messages
        ])

# ============================================================
# STRATEGY 4: HYBRID APPROACH (Recommended for Production)
# ============================================================

class HybridMemoryManager:
    """
    Combines multiple strategies based on conversation length:
    - 0-10 messages: Use all
    - 10-20 messages: Smart trim
    - 20+ messages: Summarize older + keep recent
    """
    
    def __init__(self):
        self.summarizer = ConversationSummarizer()
    
    def prepare_messages(
        self, 
        messages: List[BaseMessage],
        summary: Optional[str] = None
    ) -> tuple[List[BaseMessage], Optional[str]]:
        """
        Returns: (messages_to_send, new_summary_if_updated)
        """
        msg_count = len(messages)
        token_count = count_tokens_approximately(messages)
        
        # Strategy based on conversation length
        if msg_count <= 10 and token_count < 4000:
            # Short conversation - use all messages
            return messages, None
        
        elif msg_count <= 20 and token_count < 6000:
            # Medium conversation - smart trim
            trimmed = smart_trim_messages(messages, max_tokens=4000)
            return trimmed, None
        
        else:
            # Long conversation - summarize
            if self.summarizer.should_summarize(messages):
                new_summary = self.summarizer.summarize(messages)
                
                # Create system message with summary
                summary_msg = SystemMessage(
                    content=f"Previous conversation summary: {new_summary}"
                )
                
                # Keep only last 4 messages
                recent = messages[-4:]
                
                return [summary_msg] + recent, new_summary
        
        return messages, None

# ============================================================
# NODE IMPLEMENTATION
# ============================================================

def manage_memory_node(state: AgentState):
    """
    Node that manages short-term memory before calling LLM.
    Run this BEFORE the agent node.
    """
    messages = state["messages"]
    current_summary = state.get("summary")
    
    manager = HybridMemoryManager()
    
    # Prepare messages for LLM
    prepared_messages, new_summary = manager.prepare_messages(messages, current_summary)
    
    # Update state
    updates = {"processed_messages": prepared_messages}
    if new_summary:
        updates["summary"] = new_summary
    
    return updates
```

---

## 4. Complete FastAPI with Frontend Chat History

```python
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
import json
from datetime import datetime

app = FastAPI()

# ============================================================
# MODELS
# ============================================================

class ChatMessage(BaseModel):
    message_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    metadata: Optional[dict] = None

class ChatRequest(BaseModel):
    message: str
    user_id: str
    thread_id: str

class ChatResponse(BaseModel):
    message_id: str
    content: str
    thread_id: str
    timestamp: str

class ThreadHistoryResponse(BaseModel):
    thread_id: str
    messages: List[ChatMessage]
    message_count: int
    created_at: Optional[str] = None

# ============================================================
# ENDPOINT: SEND MESSAGE (Streaming)
# ============================================================

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Main chat endpoint with streaming"""
    
    config = {
        "configurable": {
            "user_id": request.user_id,
            "thread_id": request.thread_id
        }
    }
    
    input_state = {
        "messages": [HumanMessage(content=request.message)],
        "user_id": request.user_id
    }
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events"""
        
        # First, send any retrieved memories (optional)
        # This helps frontend show "AI is recalling..."
        
        full_response = []
        
        async for chunk in graph.astream(input_state, config, stream_mode="messages"):
            if isinstance(chunk[0], AIMessage):
                content = chunk[0].content
                full_response.append(content)
                
                # Send token
                yield f"data: {json.dumps({
                    'type': 'token',
                    'content': content
                })}\n\n"
        
        # Send completion with full message ID
        yield f"data: {json.dumps({
            'type': 'complete',
            'message_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        })}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# ============================================================
# ENDPOINT: GET THREAD HISTORY
# ============================================================

@app.get("/threads/{thread_id}/messages", response_model=ThreadHistoryResponse)
async def get_thread_messages(
    thread_id: str,
    user_id: str = Query(..., description="User ID for verification"),
    limit: int = Query(50, le=100),
    before: Optional[str] = None  # Pagination
):
    """
    Get chat history for a specific thread.
    Frontend calls this when loading a conversation.
    """
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    try:
        # Get state from checkpointer
        state = await graph.aget_state(config)
        
        if not state or not state.values:
            return ThreadHistoryResponse(
                thread_id=thread_id,
                messages=[],
                message_count=0
            )
        
        # Extract messages from state
        raw_messages = state.values.get("messages", [])
        
        # Convert to response format
        messages = []
        for msg in raw_messages:
            if isinstance(msg, (HumanMessage, AIMessage)):
                messages.append(ChatMessage(
                    message_id=getattr(msg, 'id', str(uuid.uuid4())),
                    role="user" if isinstance(msg, HumanMessage) else "assistant",
                    content=msg.content,
                    timestamp=getattr(msg, 'additional_kwargs', {}).get('timestamp', datetime.now().isoformat()),
                    metadata=getattr(msg, 'additional_kwargs', {})
                ))
        
        # Paginate if needed
        if before:
            messages = [m for m in messages if m.timestamp < before]
        
        messages = messages[-limit:]  # Get last N
        
        return ThreadHistoryResponse(
            thread_id=thread_id,
            messages=messages,
            message_count=len(messages),
            created_at=messages[0].timestamp if messages else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# ENDPOINT: GET ALL USER THREADS
# ============================================================

@app.get("/users/{user_id}/threads")
async def get_user_threads(user_id: str):
    """
    Get all conversation threads for a user.
    Frontend shows this as a sidebar list.
    """
    
    # Query your database directly
    # (Checkpointer stores thread IDs)
    
    query = """
        SELECT DISTINCT thread_id, 
               MIN(timestamp) as created_at,
               COUNT(*) as message_count
        FROM checkpoints
        WHERE thread_id LIKE %s
        GROUP BY thread_id
        ORDER BY created_at DESC
    """
    
    # Execute query and return formatted threads
    threads = []  # Your DB query result
    
    return {
        "threads": [
            {
                "thread_id": t["thread_id"],
                "created_at": t["created_at"],
                "message_count": t["message_count"],
                "preview": "Last message preview..."  # Get from last checkpoint
            }
            for t in threads
        ]
    }

# ============================================================
# ENDPOINT: DELETE MESSAGE (Edit/Delete functionality)
# ============================================================

@app.delete("/threads/{thread_id}/messages/{message_id}")
async def delete_message(
    thread_id: str,
    message_id: str,
    user_id: str = Query(...)
):
    """
    Delete a specific message and all subsequent messages.
    Useful for "edit and resend" functionality.
    """
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    # Get current state
    state = await graph.aget_state(config)
    
    # Filter out the message and everything after it
    messages = state.values.get("messages", [])
    message_ids = [getattr(m, 'id', None) for m in messages]
    
    try:
        idx = message_ids.index(message_id)
        # Keep only messages before the deleted one
        new_messages = messages[:idx]
        
        # Update state
        await graph.aupdate_state(config, {"messages": new_messages})
        
        return {"status": "deleted", "remaining_messages": len(new_messages)}
        
    except ValueError:
        raise HTTPException(status_code=404, detail="Message not found")

# ============================================================
# WEBSOCKET ALTERNATIVE (For real-time bidirectional)
# ============================================================

from fastapi import WebSocket

@app.websocket("/ws/chat/{thread_id}")
async def websocket_chat(websocket: WebSocket, thread_id: str):
    """WebSocket for real-time chat with typing indicators"""
    
    await websocket.accept()
    
    # Authenticate user
    user_id = await websocket.receive_text()  # Or from token
    
    config = {
        "configurable": {
            "user_id": user_id,
            "thread_id": thread_id
        }
    }
    
    try:
        while True:
            # Receive message from frontend
            data = await websocket.receive_json()
            message = data.get("message")
            
            # Send "typing" indicator
            await websocket.send_json({"type": "typing", "status": "start"})
            
            # Process through graph
            input_state = {
                "messages": [HumanMessage(content=message)],
                "user_id": user_id
            }
            
            full_response = []
            async for chunk in graph.astream(input_state, config, stream_mode="messages"):
                if isinstance(chunk[0], AIMessage):
                    token = chunk[0].content
                    full_response.append(token)
                    await websocket.send_json({
                        "type": "token",
                        "content": token
                    })
            
            # Send completion
            await websocket.send_json({
                "type": "complete",
                "content": "".join(full_response),
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()
```

---

## 5. Frontend Integration

```javascript
// ============================================================
// CHAT SERVICE - Complete Implementation
// ============================================================

class ChatService {
  constructor() {
    this.userId = this.getOrCreateUserId();
    this.threadId = this.getOrCreateThreadId();
    this.eventSource = null;
  }

  getOrCreateUserId() {
    let id = localStorage.getItem('chat_user_id');
    if (!id) {
      id = 'user_' + crypto.randomUUID();
      localStorage.setItem('chat_user_id', id);
    }
    return id;
  }

  getOrCreateThreadId() {
    let id = sessionStorage.getItem('chat_thread_id');
    if (!id) {
      id = 'thread_' + Date.now();
      sessionStorage.setItem('chat_thread_id', id);
    }
    return id;
  }

  // Start new conversation
  startNewChat() {
    this.threadId = 'thread_' + Date.now();
    sessionStorage.setItem('chat_thread_id', this.threadId);
    return this.threadId;
  }

  // Load chat history
  async loadHistory() {
    const response = await fetch(
      `/threads/${this.threadId}/messages?user_id=${this.userId}`
    );
    const data = await response.json();
    return data.messages;
  }

  // Load all user's conversations
  async loadConversations() {
    const response = await fetch(`/users/${this.userId}/threads`);
    const data = await response.json();
    return data.threads;
  }

  // Send message with streaming
  async sendMessage(message, onToken, onComplete, onError) {
    const response = await fetch('/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        user_id: this.userId,
        thread_id: this.threadId
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'token') {
                onToken(data.content);
              } else if (data.type === 'complete') {
                onComplete(data);
              }
            } catch (e) {
              console.error('Parse error:', e);
            }
          }
        }
      }
    } catch (error) {
      onError(error);
    }
  }

  // Delete message and regenerate
  async deleteAndRegenerate(messageId) {
    const response = await fetch(
      `/threads/${this.threadId}/messages/${messageId}?user_id=${this.userId}`,
      { method: 'DELETE' }
    );
    return response.json();
  }
}

// ============================================================
// REACT HOOK
// ============================================================

import { useState, useEffect, useCallback, useRef } from 'react';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const service = useRef(new ChatService());

  // Load history on mount
  useEffect(() => {
    loadHistory();
    loadConversations();
  }, []);

  const loadHistory = async () => {
    const history = await service.current.loadHistory();
    setMessages(history);
  };

  const loadConversations = async () => {
    const convs = await service.current.loadConversations();
    setConversations(convs);
  };

  const sendMessage = useCallback(async (content) => {
    // Add user message immediately
    const userMessage = {
      message_id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    let assistantContent = '';
    const assistantMessage = {
      message_id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, assistantMessage]);

    await service.current.sendMessage(
      content,
      // onToken
      (token) => {
        assistantContent += token;
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...assistantMessage,
            content: assistantContent
          };
          return updated;
        });
      },
      // onComplete
      (data) => {
        setIsLoading(false);
      },
      // onError
      (error) => {
        console.error('Chat error:', error);
        setIsLoading(false);
      }
    );
  }, []);

  const startNewChat = useCallback(() => {
    service.current.startNewChat();
    setMessages([]);
  }, []);

  const switchThread = useCallback((threadId) => {
    service.current.threadId = threadId;
    sessionStorage.setItem('chat_thread_id', threadId);
    loadHistory();
  }, []);

  return {
    messages,
    isLoading,
    conversations,
    sendMessage,
    startNewChat,
    switchThread,
    currentThread: service.current.threadId
  };
}

// ============================================================
// REACT COMPONENT
// ============================================================

function ChatInterface() {
  const {
    messages,
    isLoading,
    conversations,
    sendMessage,
    startNewChat,
    switchThread,
    currentThread
  } = useChat();
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
  };

  return (
    <div className="chat-container">
      {/* Sidebar with conversations */}
      <aside className="sidebar">
        <button onClick={startNewChat}>+ New Chat</button>
        <div className="conversations">
          {conversations.map(conv => (
            <div
              key={conv.thread_id}
              className={conv.thread_id === currentThread ? 'active' : ''}
              onClick={() => switchThread(conv.thread_id)}
            >
              <p>{conv.preview || 'New conversation'}</p>
              <span>{new Date(conv.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      </aside>

      {/* Chat area */}
      <main className="chat-area">
        <div className="messages">
          {messages.map(msg => (
            <div key={msg.message_id} className={`message ${msg.role}`}>
              <div className="content">{msg.content}</div>
              <span className="time">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
            </div>
          ))}
          {isLoading && <div className="typing">AI is typing...</div>}
        </div>

        <form onSubmit={handleSubmit}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type a message..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>Send</button>
        </form>
      </main>
    </div>
  );
}
```

---

## Summary Table

| Aspect | Approach | When to Use |
|--------|----------|-------------|
| **Custom Messages** | `TypedDict` with metadata | When you need timestamps, IDs, attachments |
| **Message Updates** | Custom reducer function | Edit/delete functionality |
| **Short-term Memory** | Postgres/Redis checkpointer | Always in production |
| **Long-term Memory** | Postgres store with embeddings | User facts, preferences |
| **Cloud Connection** | Connection pooling with async | All production deployments |
| **Trimming** | `trim_messages()` | < 20 messages, predictable |
| **Summarization** | LLM-based summary | > 20 messages, complex context |
| **Hybrid** | Combine both | Recommended default |
| **Frontend History** | `/threads/{id}/messages` endpoint | Initial load, pagination |
| **Real-time** | SSE or WebSocket | Streaming responses |

Would you like me to dive deeper into any specific part, like the WebSocket implementation or the custom reducer patterns?
