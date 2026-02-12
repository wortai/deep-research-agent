"""
Test runner for streaming demonstration with checkpoint resumption.

Tests the graph streaming behavior for different search modes:
- websearch: Quick search without deep research
- deepsearch: Full research with parallel subgraphs

Usage:
    python streaming/test_streaming.py websearch "your query"
    python streaming/test_streaming.py deepsearch "your query"
    
Resume after error (uses saved thread_id):
    python streaming/test_streaming.py resume
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.deep_research_agent import DeepResearchAgent

THREAD_FILE = ".last_thread_id"


def save_thread_id(thread_id: str, query: str, mode: str):
    """Save thread_id to file for resume capability."""
    with open(THREAD_FILE, "w") as f:
        json.dump({"thread_id": thread_id, "query": query, "mode": mode}, f)


def load_thread_info() -> dict:
    """Load saved thread info for resume."""
    if not os.path.exists(THREAD_FILE):
        return None
    with open(THREAD_FILE, "r") as f:
        return json.load(f)


async def test_streaming(search_mode: str, query: str, resume_thread_id: str = None):
    """
    Run the agent with streaming display.
    
    Args:
        search_mode: 'websearch' or 'deepsearch'
        query: The research query to execute.
        resume_thread_id: Optional thread_id to resume from.
    """
    print(f"\n🔍 Mode: {search_mode.upper()}")
    print(f"📝 Query: {query}")
    if resume_thread_id:
        print(f"🔄 Resuming from thread: {resume_thread_id}")
    print("\n" + "=" * 60)
    
    agent = DeepResearchAgent()
    
    # Generate or reuse thread_id
    import uuid
    thread_id = resume_thread_id or str(uuid.uuid4())
    
    # Save for potential resume
    save_thread_id(thread_id, query, search_mode)
    print(f"💾 Thread ID: {thread_id}")
    
    try:
        result = await agent.run_with_streaming(
            user_query=query,
            search_mode=search_mode,
            thread_id=thread_id,
            resume=resume_thread_id is not None
        )
        
        print("\n" + "=" * 60)
        print("📊 Result Summary:")
        print("=" * 60)
        
        if result.get("final_response"):
            print(f"\n{result['final_response'][:500]}...")
        elif result.get("report_abstract"):
            print(f"\nAbstract: {result['report_abstract'][:300]}...")
        else:
            print("\nNo response generated.")
        
        print(f"\n📁 Report saved to: {result.get('final_report_path', 'N/A')}")
        
        # Clean up thread file on success
        if os.path.exists(THREAD_FILE):
            os.remove(THREAD_FILE)
            
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print(f"\n💡 To resume from last checkpoint, run:")
        print(f"   python streaming/test_streaming.py resume")
        raise


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("Examples:")
        print('  python streaming/test_streaming.py websearch "What is Python?"')
        print('  python streaming/test_streaming.py deepsearch "How do neural networks work?"')
        print('  python streaming/test_streaming.py resume')
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    # Handle resume mode
    if mode == "resume":
        thread_info = load_thread_info()
        if not thread_info:
            print("❌ No saved thread found. Run a query first.")
            sys.exit(1)
        
        print(f"🔄 Resuming thread: {thread_info['thread_id']}")
        asyncio.run(test_streaming(
            thread_info["mode"],
            thread_info["query"],
            resume_thread_id=thread_info["thread_id"]
        ))
    else:
        if mode not in ("websearch", "deepsearch", "extremesearch"):
            print(f"❌ Invalid mode: {mode}")
            print("Valid modes: websearch, deepsearch, extremesearch, resume")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "What is machine learning?"
        asyncio.run(test_streaming(mode, query))
