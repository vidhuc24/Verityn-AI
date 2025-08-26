#!/usr/bin/env python3
"""
Debug Vector Storage Issue

This script properly tests the vector storage to see exactly what's happening
with document storage and retrieval.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.services.vector_database import vector_db_service

async def debug_vector_storage():
    """Debug the vector storage issue properly."""
    print("🔍 Debugging Vector Storage Issue")
    print("=" * 50)
    
    try:
        # Step 1: Initialize vector database
        print("🔧 Step 1: Initialize Vector Database")
        print("-" * 40)
        await vector_db_service.initialize_collection()
        
        # Check initial state
        collection_info = await vector_db_service.get_collection_info()
        print(f"Initial collection state: {collection_info}")
        
        # Step 2: Process document
        print(f"\n📤 Step 2: Process Document")
        print("-" * 40)
        
        processor = EnhancedDocumentProcessor()
        
        # Use your actual PDF
        pdf_path = "data/synthetic_documents/pdf/SOX_Access_Review_2024.pdf"
        if not os.path.exists(pdf_path):
            print(f"❌ PDF not found: {pdf_path}")
            return False
        
        # Create file object
        class MockUploadFile:
            def __init__(self, filepath):
                self.filename = os.path.basename(filepath)
                self.filepath = filepath
                self.size = os.path.getsize(filepath)
                self.content_type = "application/pdf"
            
            async def read(self):
                with open(self.filepath, 'rb') as f:
                    return f.read()
        
        mock_file = MockUploadFile(pdf_path)
        document_id = "debug_test_document"
        
        # Process document
        result = await processor.process_document(
            file=mock_file,
            document_id=document_id,
            description="Debug test document"
        )
        
        print(f"✅ Document processing result:")
        print(f"   Status: {result.get('status')}")
        print(f"   Chunks: {result.get('chunk_count')}")
        print(f"   Vector storage: {result.get('vector_storage')}")
        
        # Step 3: Check vector database state after processing
        print(f"\n💾 Step 3: Check Vector Database After Processing")
        print("-" * 40)
        
        collection_info_after = await vector_db_service.get_collection_info()
        print(f"Collection state after processing: {collection_info_after}")
        
        # Step 4: Try to retrieve the document
        print(f"\n🔍 Step 4: Try to Retrieve Document")
        print("-" * 40)
        
        stored_chunks = await vector_db_service.get_document_chunks(document_id)
        print(f"Retrieved chunks: {len(stored_chunks) if stored_chunks else 0}")
        
        if stored_chunks:
            print(f"✅ Document found in vector database")
            for i, chunk in enumerate(stored_chunks[:2], 1):
                print(f"   Chunk {i}: {chunk.get('chunk_text', '')[:100]}...")
        else:
            print("❌ Document NOT found in vector database!")
            
            # Try to get any chunks
            print(f"\n🔍 Trying to get ANY chunks from database...")
            try:
                # Check if vector store exists
                if hasattr(vector_db_service, 'vector_store') and vector_db_service.vector_store:
                    print(f"Vector store exists: {type(vector_db_service.vector_store)}")
                    
                    # Try to search for anything
                    search_results = vector_db_service.vector_store.similarity_search("", k=10)
                    print(f"Empty search returned: {len(search_results)} results")
                    
                    if search_results:
                        print(f"First result: {search_results[0].page_content[:100]}...")
                    else:
                        print("No results from empty search")
                else:
                    print("No vector store found")
            except Exception as e:
                print(f"Error checking vector store: {str(e)}")
        
        # Step 5: Test direct search
        print(f"\n🔍 Step 5: Test Direct Search")
        print("-" * 40)
        
        search_results = await vector_db_service.semantic_search(
            query_text="inactive user accounts",
            limit=5,
            score_threshold=0.1
        )
        print(f"Direct search results: {len(search_results)}")
        
        if search_results:
            print(f"✅ Search working! First result: {search_results[0].get('chunk_text', '')[:100]}...")
        else:
            print("❌ Search failed - no results returned")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main debug function."""
    print("🚀 Debugging Vector Storage Issue")
    success = await debug_vector_storage()
    
    if success:
        print(f"\n✅ Debug completed!")
    else:
        print(f"\n❌ Debug failed!")

if __name__ == "__main__":
    asyncio.run(main())
