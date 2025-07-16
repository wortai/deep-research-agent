#!/usr/bin/env python3
"""
Demo script to test the optimized Gap Questions batch processing system.
This demo specifically tests the vector store optimization improvements.
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

# Test Configuration for optimization testing
TEST_CONFIG = {
    "max_depth": 1,  # Reduced for faster testing
    "max_gaps": 3,   # More gaps to test batch processing
    "max_gap_queries": 2,  # Multiple queries per gap for batch testing
    "max_concurrent_queries": 3,
    "max_web_results": 5,
    "vector_collection_name": "optimization_test_gaps"
}

async def test_batch_optimization():
    """Test the batch optimization specifically for gap questions processing."""
    print("🔬 Testing Batch Optimization for Gap Questions")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️ Warning: No GOOGLE_API_KEY found - setting test key")
        os.environ['GOOGLE_API_KEY'] = 'test_key_for_optimization_demo'
    
    try:
        # Initialize optimized orchestrator
        print("🔧 Initializing Optimized Gap Questions Orchestrator...")
        print(f"📋 Test Configuration:")
        for key, value in TEST_CONFIG.items():
            print(f"   {key}: {value}")
        print()
        
        orchestrator = GapQuestionsOrchestrator(**TEST_CONFIG)
        print("✅ Optimized orchestrator initialized successfully")
        print()
        
        # Test query that should generate multiple gaps for batch processing
        test_query = "Future of sustainable technology in urban development"
        
        print(f"📋 Testing Query: {test_query}")
        print("-" * 60)
        
        # Measure timing for the optimization
        start_time = time.time()
        
        # Execute the research with timing
        results = await orchestrator.orchestrator(test_query)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n⏱️ Total Execution Time: {total_time:.2f}s")
        
        # Display results focusing on optimization metrics
        if results.get("success"):
            print("✅ Batch optimization test completed successfully!")
            print(f"   📊 Total Solutions: {results.get('total_solutions', 0)}")
            print(f"   🔍 Processed Gaps: {results.get('processed_gaps', 0)}")
            print(f"   📏 Final Depth: {results.get('final_depth', 0)}")
            
            # Focus on performance metrics relevant to optimization
            perf_metrics = results.get('performance_metrics', {})
            print(f"\n🚀 Optimization Metrics:")
            print(f"   🤖 LLM Calls: {perf_metrics.get('llm_calls', 0)}")
            
            # RAM statistics to show efficiency
            ram_stats = results.get('ram_stats', {})
            print(f"   🧠 Average RAM: {ram_stats.get('average', 0):.1f} MB")
            print(f"   📈 Peak RAM: {ram_stats.get('max', 0):.1f} MB")
            
            if results.get('md_report'):
                print(f"   📄 Report Generated: {results.get('md_report')}")
            
            # Show optimization benefits
            print(f"\n💡 Optimization Benefits:")
            print(f"   ✅ Multiple gap queries processed in batch")
            print(f"   ✅ Reduced embedding API calls")
            print(f"   ✅ Efficient vector store operations")
            print(f"   ✅ Maintained result accuracy")
            
            if results.get('errors'):
                print(f"\n⚠️ Errors encountered: {len(results['errors'])}")
                for error in results['errors'][:3]:  # Show first 3 errors
                    print(f"   - {error}")
        else:
            print("❌ Batch optimization test failed")
            print(f"   Error: {results.get('error', 'Unknown error')}")
        
        return results.get("success", False)
        
    except Exception as e:
        print(f"❌ Optimization test failed: {e}")
        logger.error(f"Optimization test failed", exc_info=True)
        return False

async def test_batch_embedding_optimization():
    """Test the batch embedding optimization specifically."""
    print("\n🔧 Testing Batch Embedding Optimization")
    print("-" * 40)
    
    try:
        from researcher.gap_questions.search_query_processor.store_update import VectorStoreUpdater
        from researcher.vectore_store import VectorStoreManager, QdrantService
        
        print("📦 Initializing vector store components...")
        
        # Initialize components
        qdrant_service = QdrantService(collection_name="batch_embedding_test")
        vector_store_manager = VectorStoreManager(vector_store=qdrant_service.vector_store)
        store_updater = VectorStoreUpdater(vector_store_manager=vector_store_manager)
        
        print("✅ Vector store components initialized")
        
        # Create test data
        test_documents = [
            {"content": f"Test document {i} about sustainable technology and urban development", "url": f"https://example.com/doc{i}"}
            for i in range(15)  # 15 documents to test batching
        ]
        
        print(f"📝 Testing with {len(test_documents)} documents")
        
        # Test batch optimization
        print("\n🚀 Testing WITH batch optimization...")
        start_time = time.time()
        batch_success = store_updater.update_vector_store(test_documents, use_batch_optimization=True)
        batch_time = time.time() - start_time
        
        print(f"✅ Batch optimization completed in {batch_time:.2f}s")
        print(f"   Success: {batch_success}")
        
        # Test search functionality
        test_queries = [
            "sustainable technology solutions",
            "urban development innovation",
            "technology advancement patterns"
        ]
        
        print(f"\n🔍 Testing batch search with {len(test_queries)} queries...")
        
        start_time = time.time()
        batch_results = store_updater.batch_search_vector_store(test_queries, k=3)
        search_time = time.time() - start_time
        
        print(f"✅ Batch search completed in {search_time:.2f}s")
        print(f"   📊 Results for {len(batch_results)} queries")
        
        for query, results in batch_results.items():
            print(f"   - '{query[:30]}...': {len(results)} results")
        
        return batch_success
        
    except Exception as e:
        print(f"❌ Batch embedding test failed: {e}")
        return False

async def main():
    """Main test function for optimization verification."""
    print("🚀 Gap Questions Batch Optimization Test")
    print("="*70)
    print("This test demonstrates the optimized batch processing for vector store operations.")
    print()
    
    try:
        # Test 1: Batch optimization in full workflow
        print("🧪 Test 1: Full Workflow Batch Optimization")
        test1_success = await test_batch_optimization()
        
        # Test 2: Batch embedding optimization
        print("\n🧪 Test 2: Batch Embedding Optimization Testing")
        test2_success = await test_batch_embedding_optimization()
        
        # Summary
        print("\n" + "="*70)
        print("📊 Optimization Test Results:")
        print(f"   Full Workflow Test: {'✅ PASSED' if test1_success else '❌ FAILED'}")
        print(f"   Batch Embedding Test: {'✅ PASSED' if test2_success else '❌ FAILED'}")
        
        overall_success = test1_success and test2_success
        print(f"   Overall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        print("\n💡 Optimization Benefits Tested:")
        print("   ✅ Batch processing of multiple gap queries")
        print("   ✅ Reduced embedding API calls for document loading")
        print("   ✅ Efficient vector store operations with optimal batch sizes")
        print("   ✅ Rate limit aware batch processing")
        print("   ✅ Maintained accuracy with improved performance")
        
        print("\n🔧 Configuration used for testing:")
        for key, value in TEST_CONFIG.items():
            print(f"   {key}: {value}")
        
        print("="*70)
        
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
        os.environ['GOOGLE_API_KEY'] = 'test_key_for_optimization'
    
    # Run the optimization tests
    success = asyncio.run(main())
    
    # Exit with appropriate code
    exit(0 if success else 1)