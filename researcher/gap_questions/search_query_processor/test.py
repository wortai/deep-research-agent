import asyncio
import logging
from dotenv import load_dotenv
from .query_processor import QueryProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_full_workflow():
    """Test the complete query processing workflow."""
    logger.info("=" * 60)
    logger.info("Testing Full Query Processing Workflow")
    logger.info("=" * 60)
    
    try:
        # Initialize processor
        processor = QueryProcessor(
            collection_name="test_collection",
            max_results=5
        )
        
        # Test query
        query = "latest advancements in large language models"
        vector_search_queries = [
            "What are the main advancements in large language models?",
            "Recent LLM innovations and breakthroughs",
            "Key developments in transformer models"
        ]
        
        logger.info(f"Processing query: '{query}'")
        
        # Run full workflow
        results = await processor.process_query(
            query=query,
            max_web_results=5,
            vector_search_queries=vector_search_queries
        )
        
        # Display results
        if results:
            logger.info(f"Successfully retrieved {len(results)} results")
            for i, result in enumerate(results[:3], 1):  # Show first 3 results
                logger.info(f"\nResult {i}:")
                logger.info(f"Source: {result['source']}")
                logger.info(f"Content preview: {result['content'][:200]}...")
        else:
            logger.warning("No results returned from workflow")
            
        return results
        
    except Exception as e:
        logger.error(f"Full workflow test failed: {e}")
        return None


async def test_error_handling():
    """Test error handling with invalid inputs."""
    logger.info("=" * 60)
    logger.info("Testing Error Handling")
    logger.info("=" * 60)
    
    processor = QueryProcessor()
    
    # Test cases for invalid queries
    invalid_queries = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("  \t\n  ", "Mixed whitespace"),
    ]
    
    for query, description in invalid_queries:
        logger.info(f"\nTesting with {description.lower()}...")
        try:
            results = await processor.process_query(query)
            logger.info(f"✅ {description}: Handled gracefully, returned {len(results) if results else 0} results")
        except Exception as e:
            logger.info(f"✅ {description}: Exception handled: {e}")
    
    # Test WebSearch validation directly
    logger.info("\nTesting WebSearch direct validation...")
    try:
        from researcher.web_search import WebSearch
        web_search = WebSearch(query="", max_results=1)
        logger.error("❌ WebSearch should have raised ValueError for empty query")
    except ValueError as e:
        logger.info(f"✅ WebSearch validation: Correctly raised ValueError: {e}")
    except Exception as e:
        logger.error(f"❌ WebSearch validation: Unexpected exception: {e}")

async def run_all_tests():
    """Run all test functions."""
    logger.info("Starting Query Processor Tests")
    logger.info("=" * 80)
    
    # Test 1: Full workflow
    full_results = await test_full_workflow()
    
    # Test 2: Error handling and validation
    await test_error_handling()
    
    # Summary
    logger.info("=" * 80)
    logger.info("Test Summary:")
    logger.info(f"Full workflow: {'PASSED' if full_results else 'FAILED'}")
    logger.info("Error handling and validation: COMPLETED")
    logger.info("=" * 80)

if __name__ == "__main__":
    # Run tests
    asyncio.run(run_all_tests())