import asyncio
from graphs.states.subgraph_state import AgentGraphState
from websearch_agent.websearch_agent import websearch_agent_node
from response.response_composer import response_node

async def main():
    state: AgentGraphState = {
        "thread_id": "test_thread_1",
        "user_id": "test_user_1",
        "user_query": "painting styles",
        "chat_messages": [],
        "memory_context": {
            "semantic_memories": [],
            "user_profile": None,
            "conversation_summary": None,
        },
        "current_run_id": "test_run_1",
        "search_mode": "websearch",
        "router_thinking": "",
        "improve_in_response": "",
        "total_agents": 0,
        "completed_agents": 0,
        "total_research_steps": 0,
        "completed_research_steps": 0,
        "current_phase": "routing",
        "planner_query": [],
        "clarification_questions": [],
        "clarification_answers": [],
        "clarification_loop_count": 0,
        "plan_feedback": "",
        "plan_approved": False,
        "research_review": [],
        "reports": [],
        "websearch_results": [],
        "analyzed_images": [],
        "response_skill": "",
        "final_response": "",
        "edit_instructions": None,
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
