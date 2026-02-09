# LangGraph Human-in-the-Loop (HITL) - Complete Guide

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Important Variables and Information Flow](#important-variables)
3. [How Thread ID Works](#thread-id-explained)
4. [Code Examples](#code-examples)

---

## Core Concepts

### What is Human-in-the-Loop (HITL)?

HITL allows you to **pause** your graph execution, wait for human input, and then **resume** with that input. Think of it like putting a video on pause and resuming it later.

### The Three Critical Components

1. **Checkpointer**: Saves the graph's state (like a save file in a video game)
2. **Thread ID**: Identifies which conversation/state to load (like a save slot)
3. **Interrupt Function**: Pauses execution and waits for input

---

## Important Variables

### 1. State Variables (Most Important!)

State variables are defined in your TypedDict and are **shared across all nodes** in the graph.

```python
class MyState(TypedDict):
    user_name: str        # Available to all nodes
    age: int              # Available to all nodes  
    is_approved: bool     # Available to all nodes
```

**Key Points:**
- State variables are **persistent** across the entire graph execution
- Updated by returning a dictionary from nodes
- Saved by the checkpointer when interrupted
- Loaded from checkpointer when resumed

**Information Flow:**
```
Node A returns {"user_name": "Alice"} 
   ↓
State is updated: state["user_name"] = "Alice"
   ↓
Node B can access: state["user_name"]  # Gets "Alice"
   ↓
Node B returns {"age": 30}
   ↓
State is updated: state["age"] = 30
   ↓
Both variables available: state["user_name"] and state["age"]
```

### 2. Config Variables

The config dictionary tells the graph which conversation to work with.

```python
config = {
    "configurable": {
        "thread_id": "conversation-123"  # This is the KEY variable!
    }
}
```

**What Thread ID Does:**
- Acts as a **unique identifier** for the conversation
- Used to **save** state to checkpointer
- Used to **load** state from checkpointer
- **Same thread_id** = resume same conversation
- **Different thread_id** = start new conversation

### 3. Interrupt Variables

```python
# The value you pass to interrupt()
result = interrupt("What is your name?")
# Can also be a complex object:
result = interrupt({
    "question": "Approve this?",
    "details": some_data,
    "options": ["yes", "no"]
})
```

**Key Points:**
- Value passed to `interrupt()` shows up in `result["__interrupt__"]`
- Must be JSON-serializable (string, number, dict, list, bool)
- This is what the caller sees when the graph pauses

### 4. Resume Variables

```python
# When resuming, you provide the answer
graph.invoke(Command(resume="Alice"), config=config)
```

**Key Points:**
- The value in `Command(resume=...)` becomes the return value of `interrupt()`
- This is how you send information back into the paused node
- Can be any JSON-serializable value

---

## Thread ID Explained

### How Does the Graph Know It's the Same Conversation?

The **thread_id** is like a database primary key. Here's how it works:

```python
# Scenario 1: Start a conversation
config_a = {"configurable": {"thread_id": "user-alice-001"}}

graph.invoke({"message": "Hello"}, config=config_a)
# Checkpointer saves state under key "user-alice-001"

# Scenario 2: Resume the same conversation
graph.invoke(Command(resume="Continue"), config=config_a)
# Checkpointer loads state from key "user-alice-001"
# Graph continues from where it left off

# Scenario 3: Different conversation
config_b = {"configurable": {"thread_id": "user-bob-002"}}
graph.invoke({"message": "Hi"}, config=b)
# Checkpointer saves under DIFFERENT key "user-bob-002"
# This is a completely separate conversation
```

### Visual Representation

```
Checkpointer (like a database):
┌─────────────────────────────────────────┐
│ thread_id            │ state            │
├─────────────────────────────────────────┤
│ "user-alice-001"     │ {name: "Alice"}  │
│ "user-bob-002"       │ {name: "Bob"}    │
│ "conversation-123"   │ {age: 30}        │
└─────────────────────────────────────────┘

When you call:
  graph.invoke(..., config={"configurable": {"thread_id": "user-alice-001"}})

The graph:
1. Looks up "user-alice-001" in checkpointer
2. Loads the saved state: {name: "Alice"}
3. Continues execution with that state
```

### Common Thread ID Patterns

```python
# Pattern 1: User-based threads
config = {"configurable": {"thread_id": f"user-{user_id}"}}

# Pattern 2: Session-based threads
config = {"configurable": {"thread_id": f"session-{session_id}"}}

# Pattern 3: Task-based threads
config = {"configurable": {"thread_id": f"task-{task_id}"}}

# Pattern 4: Conversation-based threads
config = {"configurable": {"thread_id": f"chat-{timestamp}"}}
```

---

## Code Examples

### Example 1: Basic Interrupt

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# Define state - these variables are shared across nodes
class State(TypedDict):
    user_input: str
    user_name: str
    
def ask_name(state: State):
    # interrupt() pauses here
    name = interrupt("What is your name?")
    
    # When resumed, 'name' contains the resume value
    return {"user_name": name}

# Build graph
builder = StateGraph(State)
builder.add_node("ask_name", ask_name)
builder.add_edge(START, "ask_name")
builder.add_edge("ask_name", END)

# MUST have checkpointer for interrupts
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# Run with thread_id
config = {"configurable": {"thread_id": "conversation-1"}}

# First call - hits interrupt
result = graph.invoke(
    {"user_input": "hello", "user_name": ""},
    config=config
)

print(result["__interrupt__"])  
# Output: [Interrupt(value='What is your name?')]

# Resume with answer
result = graph.invoke(
    Command(resume="Alice"),
    config=config  # SAME thread_id!
)

print(result["user_name"])  # Output: Alice
```

**What's happening:**

1. **Initial invoke**: Graph starts, hits `interrupt()`, pauses
2. **State saved**: Checkpointer saves state under thread_id "conversation-1"
3. **Interrupt returned**: Caller sees the interrupt value
4. **Resume invoke**: Graph loads state from thread_id "conversation-1"
5. **Node re-runs**: `ask_name` runs again from the beginning
6. **Interrupt gets value**: `interrupt()` returns "Alice" instead of pausing
7. **Execution continues**: Node completes and returns updated state

### Example 2: Multiple Interrupts

```python
class ProfileState(TypedDict):
    name: str
    age: int
    city: str

def collect_info(state: ProfileState):
    # Three separate interrupts
    name = interrupt("Enter name:")
    age = interrupt("Enter age:")
    city = interrupt("Enter city:")
    
    return {
        "name": name,
        "age": age,
        "city": city
    }

# Build and compile
builder = StateGraph(ProfileState)
builder.add_node("collect", collect_info)
builder.add_edge(START, "collect")
builder.add_edge("collect", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "profile-1"}}

# Step 1: First interrupt
r1 = graph.invoke({"name": "", "age": 0, "city": ""}, config)
print(r1["__interrupt__"])  # "Enter name:"

# Step 2: Resume with name, hits second interrupt
r2 = graph.invoke(Command(resume="Bob"), config)
print(r2["__interrupt__"])  # "Enter age:"

# Step 3: Resume with age, hits third interrupt
r3 = graph.invoke(Command(resume=30), config)
print(r3["__interrupt__"])  # "Enter city:"

# Step 4: Resume with city, completes
r4 = graph.invoke(Command(resume="NYC"), config)
print(r4)  # {"name": "Bob", "age": 30, "city": "NYC"}
```

**Variable Exchange Flow:**

```
Invocation 1:
  - Node starts
  - Hits: name = interrupt("Enter name:")
  - PAUSE, save state
  - Return: __interrupt__ = "Enter name:"

Invocation 2 (resume="Bob"):
  - Load saved state
  - Node starts AGAIN from beginning
  - name = interrupt("Enter name:") → returns "Bob" (from resume)
  - Hits: age = interrupt("Enter age:")
  - PAUSE, save state
  - Return: __interrupt__ = "Enter age:"

Invocation 3 (resume=30):
  - Load saved state
  - Node starts AGAIN from beginning
  - name = interrupt("Enter name:") → returns "Bob"
  - age = interrupt("Enter age:") → returns 30 (from resume)
  - Hits: city = interrupt("Enter city:")
  - PAUSE, save state

Invocation 4 (resume="NYC"):
  - Load saved state
  - Node starts AGAIN from beginning
  - name = interrupt("Enter name:") → returns "Bob"
  - age = interrupt("Enter age:") → returns 30
  - city = interrupt("Enter city:") → returns "NYC"
  - Completes and returns state update
```

### Example 3: Approval with Routing

```python
from typing import Literal

class ApprovalState(TypedDict):
    action: str
    approved: bool

def approval_node(state: ApprovalState) -> Command[Literal["execute", "cancel"]]:
    # Ask for approval
    decision = interrupt({
        "question": "Approve this action?",
        "action": state["action"]
    })
    
    # Route based on decision
    if decision:
        return Command(
            update={"approved": True},
            goto="execute"
        )
    else:
        return Command(
            update={"approved": False},
            goto="cancel"
        )

def execute_node(state: ApprovalState):
    return {"result": f"Executed: {state['action']}"}

def cancel_node(state: ApprovalState):
    return {"result": f"Cancelled: {state['action']}"}

# Build graph
builder = StateGraph(ApprovalState)
builder.add_node("approval", approval_node)
builder.add_node("execute", execute_node)
builder.add_node("cancel", cancel_node)
builder.add_edge(START, "approval")
builder.add_edge("execute", END)
builder.add_edge("cancel", END)

graph = builder.compile(checkpointer=MemorySaver())

# Example: Approval
config1 = {"configurable": {"thread_id": "action-1"}}
r1 = graph.invoke({"action": "Delete files", "approved": False}, config1)
print(r1["__interrupt__"])

r2 = graph.invoke(Command(resume=True), config1)  # Approve
print(r2)  # Goes to execute_node

# Example: Rejection
config2 = {"configurable": {"thread_id": "action-2"}}
r3 = graph.invoke({"action": "Delete files", "approved": False}, config2)
r4 = graph.invoke(Command(resume=False), config2)  # Reject
print(r4)  # Goes to cancel_node
```

**Variable Routing:**

```
State variables accessible throughout:
- state["action"]: Available in approval_node, execute_node, cancel_node
- state["approved"]: Updated by Command(update=...) in approval_node

Routing via Command:
- Command(goto="execute"): Routes to execute_node
- Command(goto="cancel"): Routes to cancel_node
- Command(update={...}): Updates state variables before routing
```

### Example 4: Edit/Review Pattern

```python
class DocumentState(TypedDict):
    original: str
    edited: str

def review_node(state: DocumentState):
    # Present document for editing
    edited_content = interrupt({
        "instruction": "Review and edit this:",
        "content": state["original"]
    })
    
    return {"edited": edited_content}

builder = StateGraph(DocumentState)
builder.add_node("review", review_node)
builder.add_edge(START, "review")
builder.add_edge("review", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "doc-1"}}

# Initial
result = graph.invoke(
    {"original": "Draft text", "edited": ""},
    config
)
print(result["__interrupt__"])
# Shows: {"instruction": "Review and edit this:", "content": "Draft text"}

# Resume with edited version
result = graph.invoke(
    Command(resume="Improved text"),
    config
)
print(result["edited"])  # "Improved text"
```

### Example 5: Multiple Threads (Different Conversations)

```python
class ChatState(TypedDict):
    messages: list[str]

def chat_node(state: ChatState):
    msg = interrupt("Your message:")
    messages = state["messages"] + [msg]
    return {"messages": messages}

builder = StateGraph(ChatState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile(checkpointer=MemorySaver())

# Conversation 1 (Alice)
config_alice = {"configurable": {"thread_id": "alice-chat"}}
r1 = graph.invoke({"messages": ["Bot: Hi Alice!"]}, config_alice)
r2 = graph.invoke(Command(resume="Hello!"), config_alice)
print(r2["messages"])  # ["Bot: Hi Alice!", "Hello!"]

# Conversation 2 (Bob) - completely separate
config_bob = {"configurable": {"thread_id": "bob-chat"}}
r3 = graph.invoke({"messages": ["Bot: Hi Bob!"]}, config_bob)
r4 = graph.invoke(Command(resume="Hey!"), config_bob)
print(r4["messages"])  # ["Bot: Hi Bob!", "Hey!"]

# Resume Alice's conversation later
r5 = graph.invoke({"messages": r2["messages"]}, config_alice)
# Still has Alice's history because of thread_id!
```

**Thread Isolation:**

```
Checkpointer State:

┌──────────────────────────────────────────────────┐
│ thread_id      │ state                           │
├──────────────────────────────────────────────────┤
│ "alice-chat"   │ {messages: ["Hi Alice", ...]}   │
│ "bob-chat"     │ {messages: ["Hi Bob", ...]}     │
└──────────────────────────────────────────────────┘

Each thread_id maintains completely separate state!
```

---

## Summary: Variable Exchange Patterns

### Pattern 1: Simple Value Exchange

```python
# In node:
value = interrupt("Question?")
return {"state_var": value}

# To resume:
graph.invoke(Command(resume="Answer"), config)
```

### Pattern 2: Complex Object Exchange

```python
# In node:
response = interrupt({
    "question": "Approve?",
    "details": state["data"],
    "options": ["yes", "no"]
})

# To resume:
graph.invoke(Command(resume={"choice": "yes", "comment": "Looks good"}), config)
```

### Pattern 3: Sequential Collection

```python
# In node:
name = interrupt("Name?")
age = interrupt("Age?")
return {"name": name, "age": age}

# To resume (multiple times):
graph.invoke(Command(resume="Alice"), config)  # First interrupt
graph.invoke(Command(resume=30), config)       # Second interrupt
```

### Pattern 4: Conditional Routing

```python
# In node:
decision = interrupt("Choose:")
if decision == "A":
    return Command(goto="node_a", update={"choice": decision})
else:
    return Command(goto="node_b", update={"choice": decision})
```

---

## Key Takeaways

1. **State Variables**: Shared across all nodes, persisted by checkpointer
2. **Thread ID**: Unique identifier for each conversation/workflow
3. **Interrupt**: Pauses execution and returns value to caller
4. **Resume**: Provides value back to paused interrupt
5. **Checkpointer**: Saves/loads state using thread_id as key
6. **Node Re-execution**: Nodes restart from beginning when resumed

### Critical Rules

✅ **DO:**
- Always use same thread_id when resuming
- Keep interrupt calls in same order within a node
- Use simple, JSON-serializable values in interrupts
- Include checkpointer when compiling graph

❌ **DON'T:**
- Don't wrap interrupt() in try/except
- Don't conditionally skip interrupt calls
- Don't pass functions or complex objects to interrupt
- Don't forget to include thread_id in config