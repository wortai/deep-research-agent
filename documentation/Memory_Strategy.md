# Memory and State Management Strategy

This document outlines the architectural strategy for memory management, state handling, and application data persistence within the WORT Engine project. It addresses concerns regarding short-term vs. long-term memory, LangGraph persistence, application databases, and frontend streaming.

## 1. Short-Term vs. Long-Term Memory Architecture
**Assessment:** The current approach using `MemoryFacade` to separate short-term and long-term memory is an excellent approach. 

* **Short-Term Memory:** Handles the immediate context of the conversation. It ensures the LLM has the necessary continuity of the current thread.
* **Long-Term Memory:** Handles semantic retrieval (facts, preferences, past context) across multiple sessions.

This separation prevents the LLM's context window from overflowing (which causes distraction and higher costs) while still providing relevant background knowledge via Vector Search.

## 2. Managing Chat History with LangGraph
**The Problem:** You are uncertain if LangGraph's Postgres checkpointer is the right tool for saving frontend chat history, and you are carefully considering what you add to your state.

**The Strategy:**
Yes, the standard LangGraph Postgres checkpointer **is exactly the right tool** for short-term conversation persistence. However, your state structure needs clear boundaries to prevent polluting the LLM's prompt.

* **Split State Responsibilities into TWO lists:**
  1. **`messages` (LLM Context):** A strict list of LangChain Message objects (`HumanMessage`, `AIMessage`, `ToolMessage`, `SystemMessage`). This list is given *directly* to the LLM. Do **not** put UI-specific elements like internal router logs, planner steps, or raw JSON reports in this list, or the LLM will get confused and hallucinate. You can use LangGraph's built-in tools (like `trim_messages` or `RemoveMessage`) to handle truncating this list as it gets large.
  2. **`ui_history` or `frontend_events` (Frontend Context):** A separate array in your `AgentGraphState` (e.g., `ui_history: Annotated[List[Dict], operator.add]`). When you want an event to persist visually in the frontend when a user refreshes the page (like a "Planner crafted 5 queries" log, or a specific reasoning step), you append a structured dictionary here.

**How it works on reload:** When a user opens an old thread, your backend reads the LangGraph state for that `thread_id` and sends the `ui_history` (and standard `messages`) to the React frontend to reconstruct the visual chat flow, keeping internal variables separate.

## 3. Application Persistence vs. LangGraph Checkpointer (Users, Auth, Settings)
**The Problem:** Your application will be adding authentication and other non-graph user data, and you need to know if this goes inside LangGraph.

**The Strategy: Separate Application Tables (or a Separate Database)**
You **must** separate your application business logic from LangGraph's checkpointer. 

* **LangGraph Checkpointer:** Stores opaque "blobs" of graph state tied to a `thread_id`. It is terrible for answering queries like *"Get all users who signed up today"* or *"Update the password for user_123"*.
* **Application DB (FastAPI / SQLModel / SQLAlchemy):** Create standard relational tables (`users`, `organizations`, `billing`, `api_keys`). You can put these tables inside the *same* Postgres database as LangGraph, but they should be separate tables (or a separate schema entirely).

**How they interconnect:**
* Your FastAPI backend handles Auth natively using the Application DB.
* Once a request is authenticated, FastAPI passes the `thread_id` and `user_id` down into LangGraph's config.
* `MemoryFacade` uses the `user_id` to reliably query your Application tables or Long-Term Memory nodes to build contexts.

## 4. Message Schema and Streaming Cycle
**The Problem:** You stream selective data in `stream_service.py`, but the `ChatMessage` schema currently mixes logs, plans, and reports, making it feel flawed.

**The Strategy:**
Your instinct is correct. A unified `ChatMessage` mixing `"chat"`, `"log"`, `"plan"`, and `"report"` is an anti-pattern for LLM prompt context.

### 4.1 Decoupling the LangChain Message from the UI Event
Currently, you might be appending `ChatMessage(type="log", ...)` to your graph state. When this list of messages is passed to the LLM (like `ChatOpenAI`), the model is forced to interpret these artificial UI logs as actual conversation history, which degrades performance and consumes tokens.

**Solution:** Limit `chat_messages` strictly to conversational turns (Human requests and AI text responses).
Create a *new* state key dedicated to UI events.

**Updated State Definition (`subgraph_state.py`):**
```python
class UIEvent(TypedDict):
    event_id: str
    timestamp: str
    event_type: Literal["log", "plan", "report_update", "progress"]
    payload: Dict[str, Any]

class AgentGraphState(TypedDict):
    # ... other keys ...
    
    # Strictly for LLM Context (Langchain native messages)
    chat_messages: Annotated[List[BaseMessage], operator.add]
    
    # Strictly for Frontend Rendering (UI History)
    ui_history: Annotated[List[UIEvent], operator.add]
```

### 4.2 How Nodes Update State
LangGraph nodes should modify the native state variables for their domain. They don't need to push pseudo-chat-messages.

For example, when the `planner_node` generates a plan:
```python
def planner_node(state: AgentGraphState):
    # ... generate plan ...
    new_ui_event = UIEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        event_type="plan",
        payload={"query_num": 5, "details": "Crafted 5 research queries"}
    )
    return {
        "planner_query": generated_queries, # Native state update
        "ui_history": [new_ui_event]        # Append to UI history
    }
```

### 4.3 Streaming via `stream_service.py` is Correct!
You are already using `stream_mode=["updates", "custom", "messages"]` which is exactly the LangGraph paradigm. The WebSocket successfully sends real-time `"custom"` events and `"updates"` for phase changes directly to the frontend.

### 4.4 Persisting the UI Stream for Page Refreshes
Because the frontend renders items streamed over WebSocket directly, the UI only looks perfect as long as the socket is active. If the user refreshes the page, the WebSocket history is gone.

**The Reconciliation Engine:**
To solve this, rely on the `ui_history` array. Whenever a node does something the user *must* see on a refresh, it appends a payload to `ui_history`.

On page load, the frontend must hit a REST endpoint (e.g., `/api/threads/{thread_id}/history`) before opening the WebSocket.

**Backend REST Endpoint Example (`routes.py`):**
```python
@router.get("/api/threads/{thread_id}/history")
async def get_thread_history(thread_id: str):
    # 1. Fetch the latest state from the LangGraph Checkpointer
    state_dict = await memory_facade.get_conversation_state(thread_id)
    if not state_dict:
        return {"events": []}
        
    # 2. Extract standard messages and UI history
    messages = state_dict.get("chat_messages", [])
    ui_history = state_dict.get("ui_history", [])
    
    # 3. Transform Langchain messages into a UI-friendly format
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "timestamp": msg.additional_kwargs.get("timestamp"), # Ensure you save timestamps!
            "event_type": "chat",
            "role": msg.type,
            "content": msg.content
        })
        
    # 4. Merge and sort chronologically
    combined_timeline = formatted_messages + ui_history
    combined_timeline.sort(key=lambda x: x.get("timestamp", ""))
    
    return {"events": combined_timeline}
```

**Frontend Initialization:**
1. User opens `/chat/123`.
2. React runs `useEffect` to fetch `/api/threads/123/history`.
3. React populates the UI timeline with the chronologically sorted `events`.
4. React opens the WebSocket connection to `/ws/chat/123`.
5. The backend streams *new* events (`"custom"`, `"messages"`, `"updates"`) over the socket.
6. React appends these new real-time events to the bottom of the timeline.

This architecture ensures your LLM prompt remains perfectly clean, while your UI accurately reflects both historical and real-time agent progress.

## Summary Recommendations
1. **Continue using LangGraph Checkpointers (Postgres) for thread history.**
2. **Restrict LLM `messages` to purely User, AI, and Tool conversational blocks.** Use built-in Langchain types (`HumanMessage`, `AIMessage`).
3. **Use a separate state key (like `ui_history`) for logs, plans, and events** to decouple LLM context from UI rendering logic.
4. **Use traditional relational tables (Application DB) for user authentication and business requirements**, passing `user_id` into LangGraph as a configuration variable.
