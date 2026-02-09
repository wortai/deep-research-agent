"""
Demo script for testing the terminal streaming display.

Run this to see the progress bar visualization without
invoking the full research agent (no API calls required).
"""

import asyncio
import time
from streaming import TerminalDisplay, StreamConsumer


async def demo_terminal_display():
    """Simulate agent progress with terminal display."""
    display = TerminalDisplay()
    consumer = StreamConsumer(display)
    
    display.set_phase("routing")
    await asyncio.sleep(0.5)
    
    display.set_phase("planning")
    await asyncio.sleep(0.5)
    
    display.set_total_queries(3)
    display.set_phase("researching")
    
    queries = [
        "How do neural networks learn from data?",
        "What are activation functions?",
        "Explain backpropagation in detail"
    ]
    
    for query_num, query in enumerate(queries):
        display.update_agent(
            query_num=query_num,
            query=query,
            percentage=0,
            phase="starting",
            current_step="Initializing research..."
        )
    
    await asyncio.sleep(0.3)
    
    for i in range(0, 101, 10):
        for query_num in range(3):
            progress = min(100, i + (query_num * 15))
            current_step = "Searching..." if progress < 30 else (
                "Resolving..." if progress < 60 else (
                    "Reviewing..." if progress < 90 else "Completing..."
                )
            )
            display.update_agent(
                query_num=query_num,
                query=queries[query_num],
                percentage=progress,
                phase=current_step.replace("...", "").lower(),
                current_step=current_step
            )
        await asyncio.sleep(0.2)
    
    display.set_phase("writing")
    await asyncio.sleep(0.5)
    
    display.set_phase("publishing")
    await asyncio.sleep(0.3)
    
    display.finish("Demo complete! All agents finished successfully.")


if __name__ == "__main__":
    print("\n🚀 Starting Terminal Display Demo...\n")
    asyncio.run(demo_terminal_display())
