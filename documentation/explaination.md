# WORT Storage and State Architecture Explained

This document explains the differences between sessions and events, why we store them this way, and how the main LangGraph state works. 

## 1. The Real Difference: `session_store` vs `event_store`

You noticed two different files (`session_store.py` and `event_store.py`) and two different tables (`sessions` and `chat-events` in `wort.json`). Here is the core difference:

- **`session_store` (The Folder)**: Stores the high-level summary of a conversation. It tracks the `title`, `user_id`, `status` (active/completed), and whether a report has been generated. 
- **`event_store` (The Pages inside the Folder)**: Stores the actual timeline of events *inside* that session. This includes user questions, the router's internal thinking, and the assistant's responses. 

### Why are we storing it this way? Is it efficient?
**Yes, this is heavily optimized and highly efficient.** 
By separating them into two tables, we prevent the application from loading massive amounts of chat history just to display the left-hand sidebar UI. 
- When the user opens the app, we only query the `sessions` table to efficiently render the sidebar. 
- We only query the `chat_events` table when the user actually clicks on a specific session.

Additionally, we purposefully exclude "ephemeral" data (like word-by-word streaming tokens or minor progress ticks) from the `chat_events` table so we don't bloat the database. 

## 2. The Genius of `checkpoint_reader.py` (No Unnecessary Storage)

You also mentioned `checkpoint_reader.py`. This file proves that you are **not** storing unnecessary things. 

A naive approach would be to save the massive, multi-page generated research reports into your own `reports` database table. Instead, LangGraph already saves the current state in its native "Checkpoints". 
`checkpoint_reader.py` simply reaches directly into the LangGraph checkpoints to extract the `reports` or `final_response`:
```python
# From checkpoint_reader.py
async def get_report(self, thread_id: str):
    # Directly fetches the massive report from LangGraph's 
    # internal memory instead of duplicating it in our DB!
    values = await self._get_channel_values(thread_id)
    # ...
```
This means zero data duplication for heavy reports. 

## 3. How `wort.json` Schema works together

If you look at `wort.json`:
1. **Sessions Table:** Notice fields like `"title": "I want to know about top 5 companies..."` and `"has_report": "false"`. It gives you everything you need for the UI sidebar.
2. **Chat-Events Table:** Notice the `session_id` field links back to the Sessions table. Also notice `event_order` (1, 2, 3...) and `event_type` (`user_query`, `router_thinking`, `assistant_response`). This allows the frontend to easily rebuild the chat timeline in the exact right sequence and use different UI components for "thinking" vs "responding".

## 4. Understanding Our Main LangGraph State (`subgraph_state.py`)

The `subgraph_state.py` defines everything your agent "remembers" at any given second while it runs. 
The defining class is `AgentGraphState`. Here are the most important parts of the logic:

### A. Annotations and `operator.add`
```python
reports: Annotated[List[ReportData], operator.add]
```
The `Annotated[..., operator.add]` syntax is crucial. It tells LangGraph that every time a new report is generated, it shouldn't *overwrite* the old reports. Instead, it should `add` (append) it to the list. This creates a continuous memory of everything generated.

### B. Progress and Phase Tracking
```python
current_phase: Literal["routing", "planning", "human_review", "researching", "writing", "publishing", "responding"]
```
This field tells the system exactly where the agent is in its workflow. It prevents the graph from getting lost and allows your UI to show a nice "Current Status: Researching..." indicator to the user.

### C. Chat Messages (Short-Term Memory)
```python
chat_messages: Annotated[List[Dict], operator.add]
```
While `event_store` saves things permanently to the database, `chat_messages` is the active, short-term memory fed directly into the LLM during the current turn. It holds the tool calls and results so the AI has immediate context.

## Summary
You have built a very clean, decoupled architecture:
1. **LangGraph State (`subgraph_state.py`)**: The active "RAM" while the AI is thinking.
2. **Event Store**: The permanent ledger of the chat timeline.
3. **Session Store**: The lightweight index for the UI sidebar.
4. **Checkpoint Reader**: The clever hack to avoid duplicating bulky reports in your database.

---

## 5. Memory System: How Long-Term and Short-Term Context Work Together

You asked specifically about how chat messages are retrieved as history and how the "memory" works across different files. Your memory architecture is coordinated by the `MemoryFacade` (`deep-research-agent/memory/memory_facade.py`), which orchestrates two separate but deeply connected systems: **Short-Term Memory** and **Long-Term Memory**.

### A. Short-Term Memory (The "Working RAM")
Located in `deep-research-agent/memory/short_term.py`.

This relies on LangGraph's `AsyncPostgresSaver` (or `MemorySaver` as a fallback). Every time a message is generated, it gets appended to the `chat_messages` array in your `AgentGraphState`. 
- **What it does**: It gives the LLM the immediate context of the current conversation (the active thread).
- **How it stays efficient**: It has built-in trimming algorithms (`trim_by_token_count`, `smart_trim`). If a conversation gets too long (exceeds token limits), the short-term memory strategically purges the middle of the conversation but guarantees that the initial user query, system instructions, and most recent messages are kept so the AI doesn't lose track of its current task. 

### B. Long-Term Memory (The "Semantic Brain")
Located in `deep-research-agent/memory/long_term.py`.

This is for facts that should persist *forever*, across entirely different sessions and threads. It stores user facts, preferences, and decisions in a vectorized format.
- **How it extracts facts**: At the end of every turn, `MemoryFacade.process_turn` intercepts the chat history and asks a lightweight LLM (like `gemini-2.0-flash`) to *extract facts*. It looks for things like "the user prefers Python" or "the user is looking for long-term investments." It saves these explicit facts into Long-Term Memory.

### C. Retrieving It All for Context (`get_context_for_planner`)
When you launch a new step (like the `planner_node` generating a research plan), the system needs to know both *what just happened* and *what the user generally prefers*. 

Here is how `MemoryFacade.get_context_for_planner` beautifully combines them:
1. **Semantic Search (Long-Term)**: It looks at the current question and searches the Long-Term Memory for the top 5 most relevant facts about the user.
2. **User Profile (Long-Term)**: It fetches hardcoded profile details.
3. **Recent History (Short-Term)**: It fetches the active discussion. If the active discussion is too long, the short-term memory immediately asks an LLM to generate a `conversation_summary`.

It packages all three of these into a single MemoryContext object and formats it into a prompt string via `build_context_prompt()`. This injected context prevents the LLM from constantly asking the user the same questions over and over again, making the AI feel genuinely personalized and smart.

---

## 6. Where Are Messages Stored? `chat_messages` vs `event_store`

You asked exactly *where* and *why* messages are stored differently in LangGraph vs your Application Database.

### `event_store` (The Visual Timeline)
- **Where is it stored?** In your Postgres database, inside the `wort.chat_events` table (as seen in `wort.json`).
- **What is its schema?** It uses structured fields tailored for a UI: `event_id`, `session_id`, `event_order`, `event_type` (like "user_query" or "router_thinking"), and `content`.
- **Why do we prefer it for UI?** It is strictly for generating the visual chat on the frontend. It isolates the "pretty" things (like showing the user that the router is thinking) from the messy internal backend logic. You can fetch it instantly via standard SQL `SELECT * FROM wort.chat_events` without having to wake up LangGraph.

### `chat_messages` (The LLM Brain)
- **Where is it stored?** This is stored *deep inside LangGraph's native checkpoints*. If you look at `tableinfo.json`, you will see massive rows like `"checkpoint_ns": ""`, `"channel": "chat_messages"`, and a huge blob byte string. This is LangGraph's internal `AsyncPostgresSaver` writing raw Python state directly into binary blobs in Postgres.
- **What is its schema?** It does *not* use a clean SQL schema. It uses LangChain's native `BaseMessage` components (like `HumanMessage`, `AIMessage`, `ToolMessage`).
- **Why do we prefer it for the LLM?** When the LLM (like OpenAI or Gemini) needs to answer a question, it only accepts a strict list of role-based messages. If you fed the LLM your UI's `event_store` (which includes messy logs like "planner generated 5 queries"), the LLM would get confused and hallucinate because it thinks those UI logs are part of the real conversation. The `chat_messages` list is kept completely pure so the LLM remains highly intelligent.

### How do we retrieve `chat_messages`?
Normally, LangGraph handles this completely automatically. When you start a run with `{ "configurable": { "thread_id": "123" } }`, LangGraph's `AsyncPostgresSaver` finds the correct checkpoint blob in the database, deserializes the binary byte string, and rehydrates the `chat_messages` array directly into your `AgentGraphState`.

However, if you ever need to manually fetch them (e.g., for short-term memory trimming), you do exactly what is done in `deep-research-agent/memory/short_term.py`:
```python
# From short_term.py -> get_conversation_history()
config = {"configurable": {"thread_id": thread_id}}
checkpoint = await self._checkpointer.aget_tuple(config)
messages = checkpoint.checkpoint.get("channel_values", {}).get("chat_messages", [])
```
It securely fetches the blob from Postgres and extracts just the `chat_messages` channel.
