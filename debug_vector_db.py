#!/usr/bin/env python3
"""
Debug script to check and clean up the vector database.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.vector_database import vector_db_service

async def debug_vector_database():
    """Debug the vector database contents."""
    print("🔍 Debugging Vector Database...")
    
    try:
        # Get collection info
        collection_info = await vector_db_service.get_collection_info()
        print(f"📊 Collection Info: {collection_info}")
        
        # Try to get all documents (this might not work with current implementation)
        print("\n📋 Attempting to list all documents...")
        
        # Since there's no direct method to list all documents, let's try a broad search
        print("🔍 Performing a broad search to see what's in the database...")
        
        # Search for common terms to see what documents exist
        search_results = await vector_db_service.semantic_search(
            query_text="SOX compliance audit",
            limit=20,
            score_threshold=0.1  # Very low threshold to see everything
        )
        
        print(f"📄 Found {len(search_results)} chunks in database")
        
        # Group by document ID
        documents = {}
        for result in search_results:
            doc_id = result.get('document_id', 'unknown')
            if doc_id not in documents:
                documents[doc_id] = []
            documents[doc_id].append(result)
        
        print(f"\n📚 Documents found: {len(documents)}")
        for doc_id, chunks in documents.items():
            print(f"  📄 Document ID: {doc_id}")
            print(f"     Chunks: {len(chunks)}")
            print(f"     Sample content: {chunks[0].get('chunk_text', '')[:100]}...")
            print(f"     Metadata: {chunks[0].get('metadata', {})}")
            print()
        
        # Ask if user wants to clean up
        if documents:
            print("🧹 Would you like to clean up all documents? (y/n)")
            response = input().strip().lower()
            if response == 'y':
                print("🗑️  Cleaning up all documents...")
                for doc_id in documents.keys():
                    success = await vector_db_service.delete_document(doc_id)
                    print(f"  {'✅' if success else '❌'} Deleted document {doc_id}")
                print("✨ Cleanup complete!")
            else:
                print("⏭️  Skipping cleanup")
        else:
            print("✅ Database appears to be empty")
            
    except Exception as e:
        print(f"❌ Error debugging vector database: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_vector_database()) 