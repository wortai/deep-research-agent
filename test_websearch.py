import asyncio
from graphs.states.subgraph_state import AgentGraphState
from websearch_agent.websearch_agent import websearch_agent_node
from response.response_composer import response_node

async def main():
    state: AgentGraphState = {
        "user_query": "painting styles",
        "chat_messages": [],
        "intent_type": "websearch",
        "current_run_id": "test_run_1",
    }
    
    # 1. Run Websearch Agent
    print("--- RUNNING WEBSEARCH AGENT ---")
    websearch_update = await websearch_agent_node(state)
    state.update(websearch_update)
    
    # Check intermediate structure
    results = state.get("websearch_results", [])[0].get("results", [])
    print(f"\nExtracted {len(results)} structured results.")
    for i, res in enumerate(results):
        print(f"Result {i+1} Images:", len(res.get("images", [])))
    
    # 2. Run Response Composer
    print("\n--- RUNNING RESPONSE COMPOSER ---")
    response_update = await response_node(state)
    print("\nFINAL LLM RESPONSE:")
    print(response_update.get("chat_messages", [{}])[0].get("content", ""))

if __name__ == "__main__":
    asyncio.run(main())
