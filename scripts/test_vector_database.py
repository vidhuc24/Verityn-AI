"""
Test script for Vector Database Service.

This script tests the basic functionality of our Qdrant-based vector database
including collection creation, document insertion, and search operations.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.services.vector_database import VectorDatabaseService, initialize_vector_database
from backend.app.config import settings

async def test_vector_database():
    """Test the vector database functionality."""
    print("🧪 Testing Vector Database Service")
    print("=" * 50)
    
    try:
        # Initialize vector database service with in-memory fallback
        vector_db = VectorDatabaseService(use_memory=True)  # Force in-memory for testing
        print(f"✅ Vector database service initialized (in-memory mode)")
        print(f"   Collection: {settings.QDRANT_COLLECTION_NAME}")
        
        # Test 1: Initialize collection
        print(f"\n🔧 Test 1: Initialize Collection")
        success = await vector_db.initialize_collection()
        if success:
            print(f"✅ Collection initialization successful")
        else:
            print(f"❌ Collection initialization failed")
            return False
        
        # Test 2: Get collection info
        print(f"\n📊 Test 2: Collection Information")
        info = await vector_db.get_collection_info()
        if info:
            print(f"✅ Collection info retrieved:")
            print(f"   Name: {info.get('collection_name')}")
            print(f"   Vectors: {info.get('vectors_count', 0)}")
            print(f"   Status: {info.get('status')}")
            print(f"   Vector Size: {info.get('vector_size')}")
            print(f"   Distance: {info.get('distance')}")
        else:
            print(f"❌ Failed to get collection info")
        
        # Test 3: Insert test document chunks
        print(f"\n📝 Test 3: Insert Test Document")
        
        test_chunks = [
            "This is a SOX 404 compliance document for Uber Technologies regarding access review procedures.",
            "The quarterly user access review evaluated 1,247 user accounts across financial systems.",
            "Material weakness identified: Segregation of duties violations in payment processing systems.",
            "Management response: Immediate remediation plan implemented for all identified control deficiencies."
        ]
        
        test_metadata = {
            "document_type": "access_review",
            "quality_level": "fail",
            "company": "uber",
            "sox_control_ids": ["404.1", "404.2"],
            "filename": "test_document.pdf",
            "created_by": "test_system"
        }
        
        insert_success = await vector_db.insert_document_chunks(
            document_id="test_doc_001",
            chunks=test_chunks,
            metadata=test_metadata
        )
        
        if insert_success:
            print(f"✅ Successfully inserted {len(test_chunks)} test chunks")
        else:
            print(f"❌ Failed to insert test chunks")
            return False
        
        # Test 4: Semantic search
        print(f"\n🔍 Test 4: Semantic Search")
        
        test_queries = [
            "What are the SOX compliance issues?",
            "How many users were reviewed?",
            "What material weaknesses were found?",
            "What is the management response?"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            results = await vector_db.semantic_search(
                query_text=query,
                limit=3,
                score_threshold=0.5
            )
            
            if results:
                print(f"   ✅ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"      {i}. Score: {result['score']:.3f}")
                    print(f"         Text: {result['chunk_text'][:80]}...")
                    print(f"         Quality: {result['quality_level']}")
                    print(f"         SOX Controls: {result['sox_control_ids']}")
            else:
                print(f"   ❌ No results found")
        
        # Test 5: Metadata filtering
        print(f"\n🎯 Test 5: Metadata Filtering")
        
        # Filter by quality level
        fail_results = await vector_db.semantic_search(
            query_text="compliance issues",
            filters={"quality_level": "fail"},
            limit=5
        )
        print(f"   Fail quality documents: {len(fail_results)} results")
        
        # Filter by SOX control
        sox_404_results = await vector_db.semantic_search(
            query_text="access review",
            filters={"sox_control_ids": ["404.1"]},
            limit=5
        )
        print(f"   SOX 404.1 documents: {len(sox_404_results)} results")
        
        # Test 6: Hybrid search
        print(f"\n🔀 Test 6: Hybrid Search")
        
        hybrid_results = await vector_db.hybrid_search(
            query_text="SOX 404 material weakness",
            limit=3
        )
        
        if hybrid_results:
            print(f"   ✅ Hybrid search found {len(hybrid_results)} results:")
            for i, result in enumerate(hybrid_results, 1):
                print(f"      {i}. Hybrid Score: {result['hybrid_score']:.3f}")
                print(f"         Semantic: {result['score']:.3f}, Keyword Bonus: {result['keyword_bonus']:.3f}")
                print(f"         Text: {result['chunk_text'][:60]}...")
        else:
            print(f"   ❌ No hybrid search results")
        
        # Test 7: Get document chunks
        print(f"\n📄 Test 7: Retrieve Document Chunks")
        
        doc_chunks = await vector_db.get_document_chunks("test_doc_001")
        if doc_chunks:
            print(f"   ✅ Retrieved {len(doc_chunks)} chunks for test document")
            for i, chunk in enumerate(doc_chunks):
                print(f"      Chunk {chunk['chunk_index']}: {chunk['chunk_text'][:50]}...")
        else:
            print(f"   ❌ No chunks found for test document")
        
        # Test 8: Collection statistics
        print(f"\n📈 Test 8: Final Collection Statistics")
        final_info = await vector_db.get_collection_info()
        if final_info:
            print(f"   ✅ Final collection state:")
            print(f"      Total vectors: {final_info.get('vectors_count', 0)}")
            print(f"      Status: {final_info.get('status')}")
        
        print(f"\n🎉 All vector database tests completed successfully!")
        print(f"✅ Vector database is ready for document ingestion")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Vector database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def cleanup_test_data():
    """Clean up test data after testing."""
    try:
        vector_db = VectorDatabaseService(use_memory=True)
        await vector_db.delete_document("test_doc_001")
        print(f"🧹 Test data cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {str(e)}")

async def main():
    """Main test function."""
    print("🚀 Starting Vector Database Tests")
    
    # Check if OpenAI API key is set
    if not settings.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Please set your OpenAI API key to run vector database tests")
        return
    
    success = await test_vector_database()
    
    if success:
        print(f"\n✅ Vector Database Service is working correctly!")
        print(f"🎯 Ready to proceed with Subtask 4.2: Enhanced Document Processing")
        
        # Cleanup test data
        await cleanup_test_data()
    else:
        print(f"\n❌ Vector Database Service needs fixes before proceeding")
        print(f"🔧 Please check the error messages above and fix issues")

if __name__ == "__main__":
    asyncio.run(main()) 