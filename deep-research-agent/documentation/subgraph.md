> ## Documentation Index
> Fetch the complete documentation index at: https://docs.langchain.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Subgraphs

This guide explains the mechanics of using subgraphs. A subgraph is a [graph](/oss/python/langgraph/graph-api#graphs) that is used as a [node](/oss/python/langgraph/graph-api#nodes) in another graph.

Subgraphs are useful for:

* Building [multi-agent systems](/oss/python/langchain/multi-agent)
* Re-using a set of nodes in multiple graphs
* Distributing development: when you want different teams to work on different parts of the graph independently, you can define each part as a subgraph, and as long as the subgraph interface (the input and output schemas) is respected, the parent graph can be built without knowing any details of the subgraph

When adding subgraphs, you need to define how the parent graph and the subgraph communicate:

* [Invoke a graph from a node](#invoke-a-graph-from-a-node) — subgraphs are called from inside a node in the parent graph
* [Add a graph as a node](#add-a-graph-as-a-node) — a subgraph is added directly as a node in the parent and **shares [state keys](/oss/python/langgraph/graph-api#state)** with the parent

## Setup

<CodeGroup>
  ```bash pip theme={null}
  pip install -U langgraph
  ```

  ```bash uv theme={null}
  uv add langgraph
  ```
</CodeGroup>

<Tip>
  **Set up LangSmith for LangGraph development**
  Sign up for [LangSmith](https://smith.langchain.com) to quickly spot issues and improve the performance of your LangGraph projects. LangSmith lets you use trace data to debug, test, and monitor your LLM apps built with LangGraph — read more about how to get started [here](https://docs.smith.langchain.com).
</Tip>

## Invoke a graph from a node

A simple way to implement a subgraph is to invoke a graph from inside the node of another graph. In this case subgraphs can have **completely different schemas** from the parent graph (no shared keys). For example, you might want to keep a private message history for each of the agents in a [multi-agent](/oss/python/langchain/multi-agent) system.

If that's the case for your application, you need to define a node **function that invokes the subgraph**. This function needs to transform the input (parent) state to the subgraph state before invoking the subgraph, and transform the results back to the parent state before returning the state update from the node.

```python  theme={null}
from typing_extensions import TypedDict
from langgraph.graph.state import StateGraph, START

class SubgraphState(TypedDict):
    bar: str

# Subgraph

def subgraph_node_1(state: SubgraphState):
    return {"bar": "hi! " + state["bar"]}

subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph = subgraph_builder.compile()

# Parent graph

class State(TypedDict):
    foo: str

def call_subgraph(state: State):
    # Transform the state to the subgraph state
    subgraph_output = subgraph.invoke({"bar": state["foo"]})  # [!code highlight]
    # Transform response back to the parent state
    return {"foo": subgraph_output["bar"]}

builder = StateGraph(State)
builder.add_node("node_1", call_subgraph)
builder.add_edge(START, "node_1")
graph = builder.compile()
```

<Accordion title="Full example: different state schemas">
  ```python  theme={null}
  from typing_extensions import TypedDict
  from langgraph.graph.state import StateGraph, START

  # Define subgraph
  class SubgraphState(TypedDict):
      # note that none of these keys are shared with the parent graph state
      bar: str
      baz: str

  def subgraph_node_1(state: SubgraphState):
      return {"baz": "baz"}

  def subgraph_node_2(state: SubgraphState):
      return {"bar": state["bar"] + state["baz"]}

  subgraph_builder = StateGraph(SubgraphState)
  subgraph_builder.add_node(subgraph_node_1)
  subgraph_builder.add_node(subgraph_node_2)
  subgraph_builder.add_edge(START, "subgraph_node_1")
  subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
  subgraph = subgraph_builder.compile()

  # Define parent graph
  class ParentState(TypedDict):
      foo: str

  def node_1(state: ParentState):
      return {"foo": "hi! " + state["foo"]}

  def node_2(state: ParentState):
      # Transform the state to the subgraph state
      response = subgraph.invoke({"bar": state["foo"]})
      # Transform response back to the parent state
      return {"foo": response["bar"]}


  builder = StateGraph(ParentState)
  builder.add_node("node_1", node_1)
  builder.add_node("node_2", node_2)
  builder.add_edge(START, "node_1")
  builder.add_edge("node_1", "node_2")
  graph = builder.compile()

  for chunk in graph.stream({"foo": "foo"}, subgraphs=True):
      print(chunk)
  ```

  ```
  ((), {'node_1': {'foo': 'hi! foo'}})
  (('node_2:577b710b-64ae-31fb-9455-6a4d4cc2b0b9',), {'subgraph_node_1': {'baz': 'baz'}})
  (('node_2:577b710b-64ae-31fb-9455-6a4d4cc2b0b9',), {'subgraph_node_2': {'bar': 'hi! foobaz'}})
  ((), {'node_2': {'foo': 'hi! foobaz'}})
  ```
</Accordion>

<Accordion title="Full example: different state schemas (two levels of subgraphs)">
  This is an example with two levels of subgraphs: parent -> child -> grandchild.

  ```python  theme={null}
  # Grandchild graph
  from typing_extensions import TypedDict
  from langgraph.graph.state import StateGraph, START, END

  class GrandChildState(TypedDict):
      my_grandchild_key: str

  def grandchild_1(state: GrandChildState) -> GrandChildState:
      # NOTE: child or parent keys will not be accessible here
      return {"my_grandchild_key": state["my_grandchild_key"] + ", how are you"}


  grandchild = StateGraph(GrandChildState)
  grandchild.add_node("grandchild_1", grandchild_1)

  grandchild.add_edge(START, "grandchild_1")
  grandchild.add_edge("grandchild_1", END)

  grandchild_graph = grandchild.compile()

  # Child graph
  class ChildState(TypedDict):
      my_child_key: str

  def call_grandchild_graph(state: ChildState) -> ChildState:
      # NOTE: parent or grandchild keys won't be accessible here
      grandchild_graph_input = {"my_grandchild_key": state["my_child_key"]}
      grandchild_graph_output = grandchild_graph.invoke(grandchild_graph_input)
      return {"my_child_key": grandchild_graph_output["my_grandchild_key"] + " today?"}

  child = StateGraph(ChildState)
  # We're passing a function here instead of just compiled graph (`grandchild_graph`)
  child.add_node("child_1", call_grandchild_graph)
  child.add_edge(START, "child_1")
  child.add_edge("child_1", END)
  child_graph = child.compile()

  # Parent graph
  class ParentState(TypedDict):
      my_key: str

  def parent_1(state: ParentState) -> ParentState:
      # NOTE: child or grandchild keys won't be accessible here
      return {"my_key": "hi " + state["my_key"]}

  def parent_2(state: ParentState) -> ParentState:
      return {"my_key": state["my_key"] + " bye!"}

  def call_child_graph(state: ParentState) -> ParentState:
      child_graph_input = {"my_child_key": state["my_key"]}
      child_graph_output = child_graph.invoke(child_graph_input)
      return {"my_key": child_graph_output["my_child_key"]}

  parent = StateGraph(ParentState)
  parent.add_node("parent_1", parent_1)
  # We're passing a function here instead of just a compiled graph (`child_graph`)
  parent.add_node("child", call_child_graph)
  parent.add_node("parent_2", parent_2)

  parent.add_edge(START, "parent_1")
  parent.add_edge("parent_1", "child")
  parent.add_edge("child", "parent_2")
  parent.add_edge("parent_2", END)

  parent_graph = parent.compile()

  for chunk in parent_graph.stream({"my_key": "Bob"}, subgraphs=True):
      print(chunk)
  ```

  ```
  ((), {'parent_1': {'my_key': 'hi Bob'}})
  (('child:2e26e9ce-602f-862c-aa66-1ea5a4655e3b', 'child_1:781bb3b1-3971-84ce-810b-acf819a03f9c'), {'grandchild_1': {'my_grandchild_key': 'hi Bob, how are you'}})
  (('child:2e26e9ce-602f-862c-aa66-1ea5a4655e3b',), {'child_1': {'my_child_key': 'hi Bob, how are you today?'}})
  ((), {'child': {'my_key': 'hi Bob, how are you today?'}})
  ((), {'parent_2': {'my_key': 'hi Bob, how are you today? bye!'}})
  ```
</Accordion>

## Add a graph as a node

When the parent graph and subgraph can communicate over a shared state key (channel) in the [schema](/oss/python/langgraph/graph-api#state), you can add a graph as a [node](/oss/python/langgraph/graph-api#nodes) in another graph. For example, in [multi-agent](/oss/python/langchain/multi-agent) systems, the agents often communicate over a shared [messages](/oss/python/langgraph/graph-api#why-use-messages) key.

<img src="https://mintcdn.com/langchain-5e9cc07a/ybiAaBfoBvFquMDz/oss/images/subgraph.png?fit=max&auto=format&n=ybiAaBfoBvFquMDz&q=85&s=c280df5c968cd4237b0b5d03823d8946" alt="SQL agent graph" style={{ height: "450px" }} data-og-width="1177" width="1177" data-og-height="818" height="818" data-path="oss/images/subgraph.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/ybiAaBfoBvFquMDz/oss/images/subgraph.png?w=280&fit=max&auto=format&n=ybiAaBfoBvFquMDz&q=85&s=e3d08dae8fb81e15b4d8069a48999eac 280w, https://mintcdn.com/langchain-5e9cc07a/ybiAaBfoBvFquMDz/oss/images/subgraph.png?w=560&fit=max&auto=format&n=ybiAaBfoBvFquMDz&q=85&s=8d8942031ba051119e0cb772ef697e0b 560w, https://mintcdn.com/langchain-5e9cc07a/ybiAaBfoBvFquMDz/oss/images/subgraph.png?w=840&fit=max&auto=format&n=ybiAaBfoBvFquMDz&q=85&s=0d5285bd104c542fe660bc09fed53e5e 840w, https://mintcdn.com/langchain-5e9cc07a/ybiAaBfoBvFquMDz/oss/images/subgraph.png?w=1100&fit=max&auto=format&n=ybiAaBfoBvFquMDz&q=85&s=32bc8ffa0eda13a0f3bb163631774a60 1100w, https://mintcdn.com/langchain-5e9cc07a/ybiAaBfoBvFquMDz/oss/images/subgraph.png?w=1650&fit=max&auto=format&n=ybiAaBfoBvFquMDz&q=85&s=6a511f3b9dc44383614803d32390875a 1650w, https://mintcdn.com/langchain-5e9cc07a/ybiAaBfoBvFquMDz/oss/images/subgraph.png?w=2500&fit=max&auto=format&n=ybiAaBfoBvFquMDz&q=85&s=169d55e154e5ea0146a57373235f768e 2500w" />

If your subgraph shares state keys with the parent graph, you can follow these steps to add it to your graph:

1. Define the subgraph workflow (`subgraph_builder` in the example below) and compile it
2. Pass compiled subgraph to the [`add_node`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph.add_node) method when defining the parent graph workflow

```python  theme={null}
from typing_extensions import TypedDict
from langgraph.graph.state import StateGraph, START

class State(TypedDict):
    foo: str

# Subgraph

def subgraph_node_1(state: State):
    return {"foo": "hi! " + state["foo"]}

subgraph_builder = StateGraph(State)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph = subgraph_builder.compile()

# Parent graph

builder = StateGraph(State)
builder.add_node("node_1", subgraph)  # [!code highlight]
builder.add_edge(START, "node_1")
graph = builder.compile()
```

<Accordion title="Full example: shared state schemas">
  ```python  theme={null}
  from typing_extensions import TypedDict
  from langgraph.graph.state import StateGraph, START

  # Define subgraph
  class SubgraphState(TypedDict):
      foo: str  # shared with parent graph state
      bar: str  # private to SubgraphState

  def subgraph_node_1(state: SubgraphState):
      return {"bar": "bar"}

  def subgraph_node_2(state: SubgraphState):
      # note that this node is using a state key ('bar') that is only available in the subgraph
      # and is sending update on the shared state key ('foo')
      return {"foo": state["foo"] + state["bar"]}

  subgraph_builder = StateGraph(SubgraphState)
  subgraph_builder.add_node(subgraph_node_1)
  subgraph_builder.add_node(subgraph_node_2)
  subgraph_builder.add_edge(START, "subgraph_node_1")
  subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
  subgraph = subgraph_builder.compile()

  # Define parent graph
  class ParentState(TypedDict):
      foo: str

  def node_1(state: ParentState):
      return {"foo": "hi! " + state["foo"]}

  builder = StateGraph(ParentState)
  builder.add_node("node_1", node_1)
  builder.add_node("node_2", subgraph)
  builder.add_edge(START, "node_1")
  builder.add_edge("node_1", "node_2")
  graph = builder.compile()

  for chunk in graph.stream({"foo": "foo"}):
      print(chunk)
  ```

  ```
  {'node_1': {'foo': 'hi! foo'}}
  {'node_2': {'foo': 'hi! foobar'}}
  ```
</Accordion>

## Add persistence

You only need to **provide the checkpointer when compiling the parent graph**. LangGraph will automatically propagate the checkpointer to the child subgraphs.

```python  theme={null}
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

class State(TypedDict):
    foo: str

# Subgraph

def subgraph_node_1(state: State):
    return {"foo": state["foo"] + "bar"}

subgraph_builder = StateGraph(State)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph = subgraph_builder.compile()

# Parent graph

builder = StateGraph(State)
builder.add_node("node_1", subgraph)
builder.add_edge(START, "node_1")

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

If you want the subgraph to **have its own memory**, you can compile it with the appropriate checkpointer option. This is useful in [multi-agent](/oss/python/langchain/multi-agent) systems, if you want agents to keep track of their internal message histories:

```python  theme={null}
subgraph_builder = StateGraph(...)
subgraph = subgraph_builder.compile(checkpointer=True)
```

## View subgraph state

When you enable [persistence](/oss/python/langgraph/persistence), you can [inspect the graph state](/oss/python/langgraph/persistence#checkpoints) (checkpoint) via the appropriate method. To view the subgraph state, you can use the subgraphs option.

You can inspect the graph state via `graph.get_state(config)`. To view the subgraph state, you can use `graph.get_state(config, subgraphs=True)`.

<Warning>
  **Available **only** when interrupted**
  Subgraph state can only be viewed **when the subgraph is interrupted**. Once you resume the graph, you won't be able to access the subgraph state.
</Warning>

<Accordion title="View interrupted subgraph state">
  ```python  theme={null}
  from langgraph.graph import START, StateGraph
  from langgraph.checkpoint.memory import MemorySaver
  from langgraph.types import interrupt, Command
  from typing_extensions import TypedDict

  class State(TypedDict):
      foo: str

  # Subgraph

  def subgraph_node_1(state: State):
      value = interrupt("Provide value:")
      return {"foo": state["foo"] + value}

  subgraph_builder = StateGraph(State)
  subgraph_builder.add_node(subgraph_node_1)
  subgraph_builder.add_edge(START, "subgraph_node_1")

  subgraph = subgraph_builder.compile()

  # Parent graph

  builder = StateGraph(State)
  builder.add_node("node_1", subgraph)
  builder.add_edge(START, "node_1")

  checkpointer = MemorySaver()
  graph = builder.compile(checkpointer=checkpointer)

  config = {"configurable": {"thread_id": "1"}}

  graph.invoke({"foo": ""}, config)
  parent_state = graph.get_state(config)

  # This will be available only when the subgraph is interrupted.
  # Once you resume the graph, you won't be able to access the subgraph state.
  subgraph_state = graph.get_state(config, subgraphs=True).tasks[0].state

  # resume the subgraph
  graph.invoke(Command(resume="bar"), config)
  ```

  1. This will be available only when the subgraph is interrupted. Once you resume the graph, you won't be able to access the subgraph state.
</Accordion>

## Stream subgraph outputs

To include outputs from subgraphs in the streamed outputs, you can set the subgraphs option in the stream method of the parent graph. This will stream outputs from both the parent graph and any subgraphs.

```python  theme={null}
for chunk in graph.stream(
    {"foo": "foo"},
    subgraphs=True, # [!code highlight]
    stream_mode="updates",
):
    print(chunk)
```

<Accordion title="Stream from subgraphs">
  ```python  theme={null}
  from typing_extensions import TypedDict
  from langgraph.graph.state import StateGraph, START

  # Define subgraph
  class SubgraphState(TypedDict):
      foo: str
      bar: str

  def subgraph_node_1(state: SubgraphState):
      return {"bar": "bar"}

  def subgraph_node_2(state: SubgraphState):
      # note that this node is using a state key ('bar') that is only available in the subgraph
      # and is sending update on the shared state key ('foo')
      return {"foo": state["foo"] + state["bar"]}

  subgraph_builder = StateGraph(SubgraphState)
  subgraph_builder.add_node(subgraph_node_1)
  subgraph_builder.add_node(subgraph_node_2)
  subgraph_builder.add_edge(START, "subgraph_node_1")
  subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
  subgraph = subgraph_builder.compile()

  # Define parent graph
  class ParentState(TypedDict):
      foo: str

  def node_1(state: ParentState):
      return {"foo": "hi! " + state["foo"]}

  builder = StateGraph(ParentState)
  builder.add_node("node_1", node_1)
  builder.add_node("node_2", subgraph)
  builder.add_edge(START, "node_1")
  builder.add_edge("node_1", "node_2")
  graph = builder.compile()

  for chunk in graph.stream(
      {"foo": "foo"},
      stream_mode="updates",
      subgraphs=True, # [!code highlight]
  ):
      print(chunk)
  ```

  ```
  ((), {'node_1': {'foo': 'hi! foo'}})
  (('node_2:e58e5673-a661-ebb0-70d4-e298a7fc28b7',), {'subgraph_node_1': {'bar': 'bar'}})
  (('node_2:e58e5673-a661-ebb0-70d4-e298a7fc28b7',), {'subgraph_node_2': {'foo': 'hi! foobar'}})
  ((), {'node_2': {'foo': 'hi! foobar'}})
  ```
</Accordion>

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit this page on GitHub](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/use-subgraphs.mdx) or [file an issue](https://github.com/langchain-ai/docs/issues/new/choose).
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs](/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.
</Tip>
