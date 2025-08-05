#!/usr/bin/env python3
"""
Comprehensive debug script to trace the entire chat process.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.chat_engine import chat_engine

async def debug_full_chat():
    """Debug the entire chat process."""
    print("🔍 Debugging Full Chat Process...")
    
    try:
        # Test question
        test_question = "What are the key compliance issues identified in the audit?"
        
        print(f"📝 Test Question: {test_question}")
        print("\n" + "="*60)
        
        # Step 1: Process the message through the full pipeline
        print("🔍 Step 1: Processing message through full pipeline...")
        
        result = await chat_engine.process_message(
            message=test_question,
            document_id=None,
            conversation_id="debug_test_conv",
            include_web_search=True
        )
        
        print(f"✅ Message processed successfully!")
        print(f"📄 Response: {result['message']['content'][:500]}...")
        print(f"🎯 Confidence: {result['message']['confidence']}")
        print(f"📚 Sources: {len(result['message']['sources'])}")
        
        print("\n" + "="*60)
        
        # Step 2: Check the actual sources returned
        print("🔍 Step 2: Checking actual sources returned...")
        sources = result['message']['sources']
        if sources:
            for i, source in enumerate(sources, 1):
                print(f"\n--- Source {i} ---")
                print(f"Document ID: {source.get('document_id', 'N/A')}")
                print(f"Title: {source.get('title', 'N/A')}")
                print(f"Content: {source.get('content', 'N/A')[:100]}...")
        else:
            print("❌ No sources returned!")
        
        print("\n" + "="*60)
        
        # Step 3: Check context metadata
        print("🔍 Step 3: Checking context metadata...")
        context_metadata = result.get('context_metadata', {})
        print(f"📊 Context Metadata: {context_metadata}")
        
        print("\n" + "="*60)
        
        # Step 4: Check compliance insights
        print("🔍 Step 4: Checking compliance insights...")
        compliance_insights = result.get('compliance_insights', {})
        print(f"📋 Compliance Insights: {compliance_insights}")
        
        print("\n" + "="*60)
        print("✅ Full debug complete!")
        
    except Exception as e:
        print(f"❌ Error debugging full chat: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_full_chat()) 