"""
Test runner for streaming demonstration.

Tests the graph streaming behavior for different search modes:
- websearch: Quick search without deep research
- deepsearch: Full research with parallel subgraphs

Usage:
    python streaming/test_streaming.py websearch "your query"
    python streaming/test_streaming.py deepsearch "your query"
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.deep_research_agent import DeepResearchAgent


async def test_streaming(search_mode: str, query: str):
    """
    Run the agent with streaming display.
    
    Args:
        search_mode: 'websearch' or 'deepsearch'
        query: The research query to execute.
    """
    print(f"\n🔍 Mode: {search_mode.upper()}")
    print(f"📝 Query: {query}\n")
    print("=" * 60)
    
    agent = DeepResearchAgent()
    
    result = await agent.run_with_streaming(
        user_query=query,
        search_mode=search_mode
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("Examples:")
        print('  python streaming/test_streaming.py websearch "What is Python?"')
        print('  python streaming/test_streaming.py deepsearch "How do neural networks work?"')
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    if mode not in ("websearch", "deepsearch", "extremesearch"):
        print(f"❌ Invalid mode: {mode}")
        print("Valid modes: websearch, deepsearch, extremesearch")
        sys.exit(1)
    
    query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "What is machine learning?"
    
    asyncio.run(test_streaming(mode, query))
