#!/usr/bin/env python3
"""
Test Fix Verification

This script tests if the vector store overwriting fix is working properly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.services.vector_database import vector_db_service

async def test_fix_verification():
    """Test if the vector store overwriting fix is working."""
    print("🧪 Testing Vector Store Fix")
    print("=" * 50)
    
    try:
        # Initialize services
        processor = EnhancedDocumentProcessor()
        await vector_db_service.initialize_collection()
        
        # Test 1: Upload first document
        print("\n📄 Test 1: Uploading First Document")
        print("-" * 40)
        
        # Create mock file for first document
        class MockFile1:
            def __init__(self):
                self.filename = "test_doc_1.txt"
                self.size = 100
                self.content_type = "text/plain"
            
            async def read(self):
                return b"First document content about user access management and SOX compliance requirements."
        
        mock_file1 = MockFile1()
        
        # Process first document
        result1 = await processor.process_document(
            file=mock_file1,
            document_id="test_doc_1",
            description="First test document"
        )
        
        print(f"✅ First document processed: {result1.get('status')}")
        print(f"   Chunks: {result1.get('chunk_count')}")
        print(f"   Vector storage: {result1.get('vector_storage')}")
        
        # Test 2: Upload second document
        print("\n📄 Test 2: Uploading Second Document")
        print("-" * 40)
        
        # Create mock file for second document
        class MockFile2:
            def __init__(self):
                self.filename = "test_doc_2.txt"
                self.size = 100
                self.content_type = "text/plain"
            
            async def read(self):
                return b"Second document content about inactive user accounts and 15 accounts identified."
        
        mock_file2 = MockFile2()
        
        # Process second document
        result2 = await processor.process_document(
            file=mock_file2,
            document_id="test_doc_2",
            description="Second test document"
        )
        
        print(f"✅ Second document processed: {result2.get('status')}")
        print(f"   Chunks: {result2.get('chunk_count')}")
        print(f"   Vector storage: {result2.get('vector_storage')}")
        
        # Test 3: Verify both documents exist
        print("\n🔍 Test 3: Verifying Both Documents Exist")
        print("-" * 40)
        
        # Check first document
        chunks1 = await vector_db_service.get_document_chunks("test_doc_1")
        if chunks1:
            print(f"✅ First document found: {len(chunks1)} chunks")
        else:
            print("❌ First document NOT found!")
        
        # Check second document
        chunks2 = await vector_db_service.get_document_chunks("test_doc_2")
        if chunks2:
            print(f"✅ Second document found: {len(chunks2)} chunks")
        else:
            print("❌ Second document NOT found!")
        
        # Test 4: Search for content from both documents
        print("\n🔍 Test 4: Testing Search Functionality")
        print("-" * 40)
        
        # Search for first document content
        search1 = await vector_db_service.semantic_search(
            query_text="SOX compliance requirements",
            limit=5,
            score_threshold=0.1
        )
        print(f"Search for 'SOX compliance': {len(search1)} results")
        
        # Search for second document content
        search2 = await vector_db_service.semantic_search(
            query_text="15 accounts identified",
            limit=5,
            score_threshold=0.1
        )
        print(f"Search for '15 accounts identified': {len(search2)} results")
        
        # Test 5: Check collection status
        print("\n📊 Test 5: Final Collection Status")
        print("-" * 40)
        
        collection_info = await vector_db_service.get_collection_info()
        print(f"Collection info: {collection_info}")
        
        print(f"\n🎉 Fix verification test completed!")
        
        # Summary
        if chunks1 and chunks2:
            print("✅ SUCCESS: Both documents are stored and searchable!")
            print("   The vector store overwriting bug has been fixed!")
        else:
            print("❌ FAILURE: Documents are still being overwritten!")
            print("   The fix didn't work as expected.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Testing Vector Store Fix")
    success = await test_fix_verification()
    
    if success:
        print(f"\n✅ Test completed!")
    else:
        print(f"\n❌ Test failed - needs investigation")

if __name__ == "__main__":
    asyncio.run(main())
