#!/usr/bin/env python3
"""
Debug Upload Flow

This script tests the complete flow from upload to chat to identify
where the document_id is getting lost.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.services.vector_database import vector_db_service
from backend.app.workflows.multi_agent_workflow import MultiAgentWorkflow

async def debug_upload_flow():
    """Debug the complete upload-to-chat flow."""
    print("🔍 Debugging Upload-to-Chat Flow")
    print("=" * 60)
    
    try:
        # Step 1: Upload and process document (simulate frontend upload)
        print("📤 Step 1: Upload and Process Document")
        print("-" * 40)
        
        processor = EnhancedDocumentProcessor()
        await vector_db_service.initialize_collection()
        
        # Use your actual PDF
        pdf_path = "data/synthetic_documents/pdf/SOX_Access_Review_2024.pdf"
        if not os.path.exists(pdf_path):
            print(f"❌ PDF not found: {pdf_path}")
            return False
        
        # Create file object (simulate frontend upload)
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
        
        print(f"✅ Document processed:")
        print(f"   Document ID: {document_id}")
        print(f"   Status: {result.get('status')}")
        print(f"   Chunks: {result.get('chunk_count')}")
        print(f"   Vector storage: {result.get('vector_storage')}")
        
        # Step 2: Verify document is in vector database
        print(f"\n💾 Step 2: Verify Vector Database Storage")
        print("-" * 40)
        
        stored_chunks = await vector_db_service.get_document_chunks(document_id)
        if stored_chunks:
            print(f"✅ Document found in vector database: {len(stored_chunks)} chunks")
        else:
            print("❌ Document NOT found in vector database!")
            return False
        
        # Step 3: Test workflow with document_id (simulate chat)
        print(f"\n🤖 Step 3: Test Multi-Agent Workflow with Document ID")
        print("-" * 40)
        
        workflow = MultiAgentWorkflow(verbose=True, single_document_mode=True)
        
        # Test question about your specific content
        test_question = "How many inactive user accounts have been identified?"
        
        print(f"Question: {test_question}")
        print(f"Document ID: {document_id}")
        
        # Execute workflow
        workflow_result = await workflow.execute(
            question=test_question,
            conversation_id="debug_conversation",
            document_id=document_id  # This is the key!
        )
        
        print(f"\n✅ Workflow executed:")
        print(f"   Status: {workflow_result.get('status')}")
        print(f"   Response length: {len(workflow_result.get('response', ''))}")
        print(f"   Workflow ID: {workflow_result.get('workflow_id')}")
        
        # Show the actual response
        response = workflow_result.get('response', '')
        print(f"\n📝 Response Preview:")
        print(f"   {response[:200]}...")
        
        # Step 4: Check if response contains your specific content
        print(f"\n🔍 Step 4: Verify Response Quality")
        print("-" * 40)
        
        if "15" in response or "inactive" in response.lower() or "90-day" in response:
            print("✅ SUCCESS: Response contains your specific content!")
        else:
            print("❌ FAILURE: Response does NOT contain your specific content")
            print("   This means the workflow is not finding your document")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main debug function."""
    print("🚀 Debugging Your Upload-to-Chat Flow")
    success = await debug_upload_flow()
    
    if success:
        print(f"\n✅ SUCCESS: Found the issue!")
        print(f"🎯 The problem is in the frontend-backend communication")
    else:
        print(f"\n❌ FAILURE: Found a different issue!")

if __name__ == "__main__":
    asyncio.run(main())
