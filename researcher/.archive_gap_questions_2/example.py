"""
Example usage of the Gap Question Generator
"""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv

from .main import GapQuestionGenerator

# Load environment variables
load_dotenv()


async def main():
    """Example usage of the Gap Question Generator"""
    
    # Get API key from environment or use directly
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Please set GOOGLE_API_KEY in your .env file")
    
    # Initialize the generator with API key
    generator = GapQuestionGenerator(
        llm_client=api_key,  # Pass API key as string
        user_query="What are the latest advancements in large language models?",
        max_iterations=3,
        max_depth=2,
        max_gap_queries_per_parent=2,
        confidence_threshold=0.85,
        collection_name="llm_research",
        file_logging=True,
        terminal_logging=True
    )
    
    # Alternative: Initialize with client instance
    # from llm_client import GeminiLLMClient
    # client = GeminiLLMClient(api_key=api_key)
    # generator = GapQuestionGenerator(llm_client=client, ...)
    
    # Run the gap question generation process
    print("Starting Gap Question Generation...")
    results = await generator.run()
    
    # Create results dictionary for JSON export
    results_data = {
        "metadata": {
            "user_query": "What are the latest advancements in large language models?",
            "timestamp": datetime.now().isoformat(),
            "session_id": generator.session_id,
            "execution_summary": {
                "total_queries_processed": results.total_queries_processed,
                "max_level_reached": results.max_level_reached,
                "final_confidence": results.final_confidence,
                "stop_condition": results.stop_condition.value,
                "execution_time_seconds": results.execution_time
            }
        },
        "gap_queries_with_answers": results.gap_queries_with_answers
    }
    
    # Save results to JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gap_question_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"EXECUTION COMPLETED")
    print(f"{'='*50}")
    print(f"Total Q&As Generated: {results.total_queries_processed}")
    print(f"Max Level Reached: {results.max_level_reached}")
    print(f"Final Confidence: {results.final_confidence:.2f}")
    print(f"Stop Condition: {results.stop_condition.value}")
    print(f"Execution Time: {results.execution_time:.2f} seconds")
    print(f"\n📄 Results saved to: {filename}")
    print(f"📁 Execution logs: {generator.monitor.output_dir}")


if __name__ == "__main__":
    asyncio.run(main())