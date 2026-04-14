# Streaming Cycle Deep Dive

## Overview
This document details the exact streaming logic for each node in the `deep-research-agent`, how the backend `StreamService` translates these events, and how the Frontend `useChat` hook consumes them.

---

## 1. Node-Level Emissions (Deep Research Agent)

### A. Router Node (`router/intent_router.py`)
*   **Logic**: Uses LLM to classify intent (`websearch`, `deepsearch`, etc.).
*   **Emission**:
    *   **Log**: Returns `router_thinking` in the state update.
    *   **Backend Handling**: `StreamService` detects `router_node` update, extracts `router_thinking`, and sends a `type: "log"` event with `event_type: "router_log"`.
    *   **Frontend**: `handleLogEvent` sees `"router_log"` and renders a "Thinking..." bubble.

### B. Planner Node (`planner/plan.py`)
*   **Logic**: Generates a research plan.
*   **Emission**:
    *   **Tokens**: Uses `StreamEmitter` to stream raw tokens of the plan *reasoning* via `messages` mode (visible as standard text).
    *   **State**: Returns `planner_query` (list of steps) in the final state.
    *   **Backend Handling**: `StreamService` detects `planner_node` update, extracts `planner_query`, and sends `type: "plan"`.
    *   **Frontend**: `handlePlan` receives the JSON plan and renders a structured Plan UI.

### C. Researcher-Reviewer Subgraph (`graphs/subgraphs/researcher_reviewer_subgraph.py`)
*   **Logic**: Runs parallel research tasks (`researcher`, `reviewer`, `resolver`).
*   **Emission**:
    *   **Custom Events**: Uses `StreamEmitter.emit_subgraph_node_progress` to emit `SUBGRAPH_NODE_PROGRESS` events.
    *   **Payload**: Contains `query_num`, `status`, `percentage`, and metadata (e.g., `results_count`).
    *   **Backend Handling**: `StreamService` listens to `custom` stream mode. Passes these events as `type: "log"` containing the raw event data.
    *   **Frontend**: `handleLogEvent` listens for `event_type`. 
        *   **CRITICAL MISMATCH**: Code analysis suggests frontend expects `event_type: "agent_progress"` but backend emits `"subgraph_node_progress"`. This requires alignment for progress bars to update correctly.

### D. Writer Node (`writer/report_writer.py`)
*   **Logic**: Generates Markdown report sections.
*   **Emission**:
    *   **State**: Returns complex `report_body`, `report_introduction`, etc.
    *   **Backend Handling**: `StreamService` detects `writer_node` update, packs sections into a JSON object, and sends `type: "report"`.
    *   **Frontend**: `handleReport` triggers. 
        *   **Note**: Backend sends report *content* structure, but frontend checks for `reportData.md_path`. This property is missing in the `writer_node` update event, meaning this specific event might not trigger the report download link UI.

### E. Publisher Node (`publisher/publisher.py`)
*   **Logic**: Generates PDF/DOCX files.
*   **Emission**:
    *   **State**: Updates `final_report_path` in global state.
    *   **Backend Handling**: Currently **Ignored** by `StreamService` (no explicit handler for `publisher_node`).
    *   **Frontend**: Implicitly handled via the *Response Node* (see below).

### F. Response Node (`response/response_composer.py`)
*   **Logic**: Generates final answer using the Report and PDF path.
*   **Emission**:
    *   **Tokens**: Streams the final response text (e.g., "Here is your report: [link]").
    *   **Backend Handling**: `StreamService` captures standard LLM tokens via `messages` mode and sends `type: "token"`.
    *   **Frontend**: `handleToken` appends text to the chat bubble. The specific PDF link is typically delivered as part of this text stream.

---

## 2. Event Translation Table

| Node Source | Graph Event | StreamService Translation | Frontend JSON Payload | Frontend Handler |
| :--- | :--- | :--- | :--- | :--- |
| **Router** | State Update (`router_thinking`) | `{"type": "log", "data": {"event_type": "router_log", "message": ...}}` | `type: "log"` | `handleLogEvent` -> Adds "Thinking" bubble |
| **Planner** | State Update (`planner_query`) | `{"type": "plan", "data": [...]}` | `type: "plan"` | `handlePlan` -> Adds Plan Card |
| **Subgraph** | Custom Event (`SUBGRAPH_NODE_PROGRESS`) | `{"type": "log", "data": {"event_type": "subgraph_node_progress", ...}}` | `type: "log"` | `handleLogEvent` -> *Expects "agent_progress"* (Mismatch) |
| **Writer** | State Update (`report_body`) | `{"type": "report", "data": {"body": ...}}` | `type: "report"` | `handleReport` -> *Expects `md_path`* (Mismatch) |
| **Response** | LLM Stream (`content`) | `{"type": "token", "content": "..."}` | `type: "token"` | `handleToken` -> Appends text |
| **Interrupt** | `__interrupt__` value | `{"type": "interrupt", "plan": "..."}` | `type: "interrupt"` | `setIsInterrupted` -> Shows Review Modal |

---

## 3. Key Observations for Developers
1.  **Progress Bar Alignment**: Ensure `frontend_events.py` event types match what `useChat.ts` expects (`agent_progress` vs `subgraph_node_progress`). The frontend currently listens for `agent_progress` to update the progress bars, but the backend emits `subgraph_node_progress`.
2.  **Report Linking**: The `type: "report"` event carries the *content*, but the specific PDF link is delivered via the conversational `type: "token"` stream from the Response node.
3.  **Token Streaming**: `StreamService` explicitly filters out tokens from `router_node` to keep the "thinking" logic internal/clean, identifying it via metadata (`langgraph_node: "router_node"`).
