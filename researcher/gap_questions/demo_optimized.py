#!/usr/bin/env python3
"""
Simple demo script to test the Gap Questions functionality.
Tests the simplified workflow with web search, data collection, and gap analysis.
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from researcher.gap_questions.gap_questions import GapQuestionsOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple Test Configuration
TEST_CONFIG = {
    "max_depth": 3,
    "max_gaps": 2,
    "max_gap_queries": 1,
    "max_concurrent_queries": 10,
    "max_web_results": 1,  # 1 result per query for simplicity
    "vector_collection_name": "simple_test_gaps"
}

async def test_simple_gap_questions():
    """Test the simple gap questions functionality."""
    print("🧪 Testing Simple Gap Questions Functionality")
    print("="*50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️ Warning: No GOOGLE_API_KEY found - setting test key")
        os.environ['GOOGLE_API_KEY'] = 'test_key_for_demo'
    
    try:
        # Initialize orchestrator
        print("🔧 Initializing Gap Questions Orchestrator...")
        print(f"📋 Configuration:")
        for key, value in TEST_CONFIG.items():
            print(f"   {key}: {value}")
        print()
        
        orchestrator = GapQuestionsOrchestrator(**TEST_CONFIG)
        print("✅ Orchestrator initialized successfully")
        print()
        
        # Test query
        test_query = "Renewable energy trends and challenges"
        print(f"📋 Test Query: {test_query}")
        print("-" * 40)
        
        # Step 1: Generate web search queries
        print("🔍 Step 1: Generating web search queries...")
        web_queries = orchestrator.plan_query_generator.generate_search_queries(test_query, max_queries=3)
        print(f"Generated {len(web_queries)} web search queries:")
        for i, query in enumerate(web_queries, 1):
            print(f"   {i}. {query}")
        print()
        
        # Step 2: Process web search (collect and store data)
        print("🌐 Step 2: Processing web search queries...")
        start_time = time.time()
        web_results = await orchestrator.process_batch_web_search(web_queries)
        web_time = time.time() - start_time
        
        print(f"✅ Web search completed in {web_time:.2f}s")
        print(f"   Collected {len(web_results)} results")
        
        # Show sample results
        if web_results:
            print("   Sample results:")
            for i, result in enumerate(web_results[:2], 1):
                source = result.get('source', 'N/A')
                content_preview = result.get('content', '')[:80] + "..."
                print(f"      {i}. Source: {source}")
                print(f"         Content: {content_preview}")
        print()
        
        # Step 3: Analyze gaps
        print("🔬 Step 3: Analyzing gaps...")
        start_time = time.time()
        gaps = orchestrator.analyze_gaps(test_query)
        gap_time = time.time() - start_time
        
        print(f"✅ Gap analysis completed in {gap_time:.2f}s")
        print(f"   Identified {len(gaps)} gaps:")
        
        if gaps:
            for i, gap in enumerate(gaps, 1):
                print(f"      {i}. {gap}")
        else:
            print("      No gaps identified")
        print()
        
        # Summary
        total_time = web_time + gap_time
        print("📊 Summary:")
        print(f"   Web Queries: {len(web_queries)}")
        print(f"   Web Results: {len(web_results)}")
        print(f"   Identified Gaps: {len(gaps)}")
        print(f"   Total Time: {total_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Simple test failed", exc_info=True)
        return False

async def test_vector_store_basics():
    """Test basic vector store functionality."""
    print("\n🔧 Testing Vector Store Basics")
    print("-" * 30)
    
    try:
        from researcher.gap_questions.search_query_processor.store_update import VectorStoreUpdater
        from researcher.vectore_store import VectorStoreManager, QdrantService
        
        print("📦 Initializing vector store...")
        
        # Initialize components
        qdrant_service = QdrantService(collection_name="simple_vector_test")
        vector_store_manager = VectorStoreManager(vector_store=qdrant_service.vector_store)
        store_updater = VectorStoreUpdater(vector_store_manager=vector_store_manager)
        
        print("✅ Vector store initialized")
        
        # Create simple test data
        test_documents = [
            {"content": "Solar energy is becoming more efficient", "url": "https://example.com/solar"},
            {"content": "Wind power technology advances rapidly", "url": "https://example.com/wind"},
            {"content": "Battery storage solutions improve", "url": "https://example.com/battery"}
        ]
        
        print(f"📝 Testing with {len(test_documents)} documents")
        
        # Test storage
        print("💾 Storing documents...")
        start_time = time.time()
        success = store_updater.update_vector_store(test_documents)
        storage_time = time.time() - start_time
        
        print(f"✅ Storage completed in {storage_time:.2f}s")
        print(f"   Success: {success}")
        
        # Test search
        test_queries = ["renewable energy", "technology"]
        
        print(f"🔍 Testing search with {len(test_queries)} queries...")
        start_time = time.time()
        search_results = store_updater.search_vector_store(test_queries, k=2)
        search_time = time.time() - start_time
        
        print(f"✅ Search completed in {search_time:.2f}s")
        print(f"   Found {len(search_results)} results")
        
        return success
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

async def main():
    """Main test function for simple gap questions functionality."""
    print("🚀 Simple Gap Questions Test")
    print("="*50)
    print("Testing the simplified gap questions workflow.")
    print()
    
    try:
        # Test 1: Main functionality
        print("🧪 Test 1: Gap Questions Workflow")
        test1_success = await test_simple_gap_questions()
        
        # Test 2: Vector store basics
        print("🧪 Test 2: Vector Store Functionality")
        test2_success = await test_vector_store_basics()
        
        # Summary
        print("\n" + "="*50)
        print("📊 Test Results:")
        print(f"   Gap Questions Test: {'✅ PASSED' if test1_success else '❌ FAILED'}")
        print(f"   Vector Store Test: {'✅ PASSED' if test2_success else '❌ FAILED'}")
        
        overall_success = test1_success and test2_success
        print(f"   Overall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        print("\n💡 Features Tested:")
        print("   ✅ Web search query generation")
        print("   ✅ Data collection (1 result per query)")
        print("   ✅ Vector store operations")
        print("   ✅ Gap analysis and identification")
        print("   ✅ Simple workflow integration")
        
        print("\n🔧 Configuration:")
        for key, value in TEST_CONFIG.items():
            print(f"   {key}: {value}")
        
        print("="*50)
        
        return overall_success
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        logger.error("Test failed", exc_info=True)
        return False

if __name__ == "__main__":
    # Set up test environment
    if not os.getenv('GOOGLE_API_KEY'):
        os.environ['GOOGLE_API_KEY'] = 'test_key_for_simple_demo'
    
    # Run the simple tests
    success = asyncio.run(main())
    
    # Exit with appropriate code
    exit(0 if success else 1)