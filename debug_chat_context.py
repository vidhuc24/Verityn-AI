#!/usr/bin/env python3
"""
Debug script to trace chat context retrieval and see what's actually being passed to the AI.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.chat_engine import chat_engine
from backend.app.services.vector_database import vector_db_service

async def debug_chat_context():
    """Debug the chat context retrieval process."""
    print("🔍 Debugging Chat Context Retrieval...")
    
    try:
        # Test question (similar to what you asked)
        test_question = "What are the key compliance issues identified in the audit?"
        
        print(f"📝 Test Question: {test_question}")
        print("\n" + "="*60)
        
        # Step 1: Check what context is retrieved
        print("🔍 Step 1: Retrieving context from vector database...")
        context_results = await chat_engine._retrieve_context(
            query=test_question,
            document_id=None,  # No specific document filter
            filters=None
        )
        
        print(f"📄 Retrieved {len(context_results)} context chunks")
        
        if context_results:
            print("\n📋 Context Results:")
            for i, result in enumerate(context_results, 1):
                print(f"\n--- Chunk {i} ---")
                print(f"Document ID: {result.get('document_id', 'N/A')}")
                print(f"Score: {result.get('score', 'N/A')}")
                print(f"Metadata: {result.get('metadata', {})}")
                print(f"Content Preview: {result.get('chunk_text', '')[:200]}...")
        else:
            print("❌ No context results found!")
        
        print("\n" + "="*60)
        
        # Step 2: Check how context is formatted
        print("🔍 Step 2: Formatting context for AI...")
        formatted_context = chat_engine._format_context(context_results)
        print(f"📝 Formatted Context Length: {len(formatted_context)} characters")
        print("\n📋 Formatted Context Preview:")
        print(formatted_context[:1000] + "..." if len(formatted_context) > 1000 else formatted_context)
        
        print("\n" + "="*60)
        
        # Step 3: Check conversation history
        print("🔍 Step 3: Checking conversation history...")
        conversation_id = "debug_test_conv"
        chat_history = chat_engine._get_conversation_history(conversation_id)
        print(f"📝 Chat History: {chat_history}")
        
        print("\n" + "="*60)
        
        # Step 4: Check what sources would be formatted
        print("🔍 Step 4: Checking source formatting...")
        sources = chat_engine._format_sources(context_results)
        print(f"📄 Sources to be returned: {len(sources)}")
        for i, source in enumerate(sources, 1):
            print(f"\n--- Source {i} ---")
            print(f"Document ID: {source.get('document_id', 'N/A')}")
            print(f"Title: {source.get('title', 'N/A')}")
            print(f"Content Preview: {source.get('content', '')[:100]}...")
        
        print("\n" + "="*60)
        print("✅ Debug complete!")
        
    except Exception as e:
        print(f"❌ Error debugging chat context: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_chat_context()) 