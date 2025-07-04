"""
Main entry point for Gap Question Generator.
"""

import os
import traceback
from dotenv import load_dotenv

from .generator import GapQuestionGenerator
from .llm_client import GeminiLLMClient
from .utils import analyze_logs, create_visualization_report


def main(user_query: str = None, max_iterations: int = 3, confidence_threshold: float = 0.85):
    """
    Main execution function
    
    Args:
        user_query: The query to process
        max_iterations: Maximum iterations for gap generation
        confidence_threshold: Confidence threshold for stopping
    """
    print("🚀 Gap Question Generator with Comprehensive Data Tracking")
    print("=" * 60)
    
    # Use default query if none provided
    if not user_query:
        user_query = "What are the latest advancements in large language models?"
    
    try:
        # Initialize
        llm_client = GeminiLLMClient()
        
        generator = GapQuestionGenerator(
            llm_client=llm_client,
            user_query=user_query,
            max_iterations=max_iterations,
            confidence_threshold=confidence_threshold
        )
        
        print(f"Session: {generator.session_id}")
        print(f"Query: {user_query}")
        print("-" * 40)
        
        # Run complete workflow
        results = generator.run()
        
        print("\n📊 Results Summary:")
        for key, value in results.items():
            print(f"  • {key}: {value}")
        
        print(f"\n📋 Output Files:")
        print(f"  • Detailed JSON: {generator.monitor.output_dir}/{generator.session_id}_detailed_log.json")
        print(f"  • Markdown Report: {generator.monitor.output_dir}/{generator.session_id}_detailed_report.md")
        print(f"  • URLs & Content: {generator.monitor.output_dir}/{generator.session_id}_urls_content.json")
        print(f"  • Vector Results: {generator.monitor.output_dir}/{generator.session_id}_vector_results.json")
        
        # Display sample data
        print("\n📌 Sample Data from Processing:")
        if generator.monitor.detailed_queries:
            query_data = generator.monitor.detailed_queries[0]
            print(f"\nFirst Gap Query: {query_data.gap_query}")
            print(f"Vector Queries Generated: {len(query_data.vector_queries)}")
            for vq in query_data.vector_queries[:2]:
                print(f"  - {vq}")
            print(f"URLs Accessed: {len(query_data.urls_accessed)}")
            for url in query_data.urls_accessed[:2]:
                print(f"  - {url}")
            print(f"Insights Extracted: {len(query_data.insights_extracted)}")
            for insight in query_data.insights_extracted[:2]:
                print(f"  - {insight[:100]}...")
        
        # Generate visualization
        print("\n📊 Generating visualization report...")
        viz_file = create_visualization_report(generator.session_id)
        if viz_file:
            print(f"Open {viz_file} in your browser to view interactive charts")
        
        # Analyze logs
        print("\n🔍 Analyzing execution data...")
        analyze_logs(generator.session_id)
        
        return generator
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        print("⚠️  Please set GOOGLE_API_KEY in the .env file")
        print("   Get your key from: https://makersuite.google.com/app/apikey")
        exit(1)
    
    # Run main
    main()