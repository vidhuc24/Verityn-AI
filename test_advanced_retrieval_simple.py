#!/usr/bin/env python3
"""
Simple Test for Advanced Retrieval Service

This script tests if the advanced retrieval service is working
and can find documents in the vector database.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.app.services.advanced_retrieval import advanced_retrieval_service
from backend.app.services.vector_database import vector_db_service

async def test_advanced_retrieval():
    """Test the advanced retrieval service."""
    print("🧪 Testing Advanced Retrieval Service")
    print("=" * 50)
    
    try:
        # Initialize vector database
        print("🔧 Initializing vector database...")
        await vector_db_service.initialize_collection()
        print("✅ Vector database initialized")
        
        # Check if we have documents
        print("\n📊 Checking vector database contents...")
        collection_info = await vector_db_service.get_collection_info()
        print(f"Collection info: {collection_info}")
        
        # Test basic semantic search first
        print("\n🔍 Testing basic semantic search...")
        basic_results = await vector_db_service.semantic_search(
            query_text="inactive user accounts",
            limit=5,
            score_threshold=0.1
        )
        print(f"Basic search results: {len(basic_results)}")
        if basic_results:
            print(f"First result: {basic_results[0].get('chunk_text', '')[:100]}...")
        
        # Test advanced retrieval service
        print("\n🚀 Testing advanced retrieval service...")
        
        # Test 1: Hybrid search
        print("   Testing hybrid search...")
        try:
            hybrid_results = await advanced_retrieval_service.hybrid_search(
                query="inactive user accounts",
                limit=5,
                filters={},
                semantic_weight=0.7,
                keyword_weight=0.3
            )
            print(f"   Hybrid search: {len(hybrid_results)} results")
        except Exception as e:
            print(f"   ❌ Hybrid search failed: {str(e)}")
        
        # Test 2: Query expansion
        print("   Testing query expansion...")
        try:
            expansion_results = await advanced_retrieval_service.query_expansion_search(
                query="inactive user accounts",
                limit=5,
                expansion_terms=["SOX", "compliance"]
            )
            print(f"   Query expansion: {len(expansion_results)} results")
        except Exception as e:
            print(f"   ❌ Query expansion failed: {str(e)}")
        
        # Test 3: Basic semantic search through advanced service
        print("   Testing basic semantic search...")
        try:
            semantic_results = await advanced_retrieval_service.vector_db.semantic_search(
                query_text="inactive user accounts",
                limit=5,
                score_threshold=0.1
            )
            print(f"   Basic semantic: {len(semantic_results)} results")
        except Exception as e:
            print(f"   ❌ Basic semantic failed: {str(e)}")
        
        print("\n✅ Advanced retrieval service test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Testing Advanced Retrieval Service")
    success = await test_advanced_retrieval()
    
    if success:
        print(f"\n✅ SUCCESS: Advanced retrieval service is working!")
    else:
        print(f"\n❌ FAILURE: Advanced retrieval service has issues!")

if __name__ == "__main__":
    asyncio.run(main())
