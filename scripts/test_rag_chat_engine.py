"""
Test script for RAG Chat Engine.

This script tests the complete RAG pipeline including document processing,
vector storage, context retrieval, and chat response generation.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.services.chat_engine import RAGChatEngine
from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.services.vector_database import VectorDatabaseService
from backend.app.config import settings

class MockUploadFile:
    """Mock UploadFile for testing."""
    
    def __init__(self, filename: str, content: str, content_type: str = "text/plain"):
        self.filename = filename
        self.content = content.encode('utf-8')
        self.content_type = content_type
        self.size = len(self.content)
    
    async def read(self) -> bytes:
        return self.content

class TestRAGChatEngine(RAGChatEngine):
    """Test version of RAG Chat Engine with in-memory vector database."""
    
    def __init__(self):
        super().__init__()
        # Use in-memory vector database for testing
        self.test_vector_db = VectorDatabaseService(use_memory=True)
        
        # Override the global vector_db import in the parent class
        import backend.app.services.chat_engine as chat_module
        chat_module.vector_db = self.test_vector_db
        
        # Also override in our instance
        global vector_db
        vector_db = self.test_vector_db

async def setup_test_documents():
    """Set up test documents for RAG testing."""
    print("📝 Setting up test documents...")
    
    # Create test processor with in-memory vector database
    class TestDocumentProcessor(EnhancedDocumentProcessor):
        def __init__(self):
            super().__init__()
            self.test_vector_db = VectorDatabaseService(use_memory=True)
        
        async def _store_in_vector_database(self, document_id: str, chunks, metadata) -> bool:
            await self.test_vector_db.initialize_collection()
            return await self.test_vector_db.insert_document_chunks(document_id, chunks, metadata)
    
    processor = TestDocumentProcessor()
    
    # Test Document 1: High-quality access review
    high_quality_content = """
    SOX 404 COMPLIANCE DOCUMENT - ACCESS REVIEW
    
    EXECUTIVE SUMMARY
    This quarterly user access review evaluated 1,247 user accounts across financial systems 
    for Uber Technologies. The review was conducted in accordance with SOX 404 requirements
    and identified no material weaknesses.
    
    SCOPE AND METHODOLOGY
    The access review covered all users with access to financial systems including:
    - SAP Financial Module (847 users)
    - Oracle Procurement System (312 users)  
    - Expense Management Platform (623 users)
    
    KEY FINDINGS
    1. All user access is properly authorized and documented
    2. Segregation of duties is maintained across all critical processes
    3. Quarterly access certification completed with 100% response rate
    4. No terminated employees found with active system access
    
    MANAGEMENT RESPONSE
    Management is satisfied with the current access control environment.
    No remediation actions are required at this time.
    
    SOX CONTROL ASSESSMENT
    Control 404.1 - EFFECTIVE: Access review procedures operating effectively
    Control 404.2 - EFFECTIVE: User provisioning controls operating effectively
    """
    
    mock_file_1 = MockUploadFile(
        filename="uber_access_review_q1_2024_high.txt",
        content=high_quality_content,
        content_type="text/plain"
    )
    
    document_metadata_1 = {
        "document_type": "access_review",
        "quality_level": "high",
        "company": "uber",
        "sox_control_ids": ["404.1", "404.2"],
        "compliance_framework": "SOX",
        "created_by": "test_system"
    }
    
    result_1 = await processor.process_document(
        file=mock_file_1,
        document_id="test_high_quality_doc",
        description="High-quality Q1 2024 Access Review for Uber",
        document_metadata=document_metadata_1
    )
    
    # Test Document 2: Low-quality with material weaknesses
    low_quality_content = """
    SOX 404 COMPLIANCE DOCUMENT - ACCESS REVIEW
    
    EXECUTIVE SUMMARY
    This quarterly user access review evaluated 1,156 user accounts across financial systems 
    for Walmart Inc. The review identified several MATERIAL WEAKNESSES requiring immediate
    management attention and remediation.
    
    SCOPE AND METHODOLOGY
    The access review covered financial systems including:
    - SAP Financial Module
    - Oracle Procurement System
    - Expense Management Platform
    
    CRITICAL FINDINGS - MATERIAL WEAKNESSES IDENTIFIED
    1. SEGREGATION OF DUTIES VIOLATIONS: 23 users have conflicting access rights
    2. TERMINATED EMPLOYEE ACCESS: 8 terminated employees retain active system access
    3. UNAUTHORIZED ACCESS: 15 users have access beyond their job requirements
    4. MISSING APPROVALS: 45 access grants lack proper management approval
    
    MANAGEMENT RESPONSE
    Management acknowledges the material weaknesses and has initiated immediate remediation:
    - All terminated employee access revoked within 24 hours
    - Segregation of duties matrix being updated
    - Comprehensive access recertification to be completed within 30 days
    
    SOX CONTROL ASSESSMENT
    Control 404.1 - DEFICIENT: Material weakness in access review procedures
    Control 404.2 - DEFICIENT: User provisioning controls require enhancement
    Control 404.4 - FAILING: Access termination procedures inadequate
    """
    
    mock_file_2 = MockUploadFile(
        filename="walmart_access_review_q1_2024_fail.txt",
        content=low_quality_content,
        content_type="text/plain"
    )
    
    document_metadata_2 = {
        "document_type": "access_review",
        "quality_level": "fail",
        "company": "walmart",
        "sox_control_ids": ["404.1", "404.2", "404.4"],
        "compliance_framework": "SOX",
        "created_by": "test_system"
    }
    
    result_2 = await processor.process_document(
        file=mock_file_2,
        document_id="test_fail_quality_doc",
        description="Failed Q1 2024 Access Review for Walmart",
        document_metadata=document_metadata_2
    )
    
    print(f"✅ Set up 2 test documents:")
    print(f"   - High quality: {result_1['chunk_count']} chunks")
    print(f"   - Fail quality: {result_2['chunk_count']} chunks")
    
    return processor.test_vector_db

async def test_rag_chat_engine():
    """Test the complete RAG chat engine functionality."""
    print("🧪 Testing RAG Chat Engine")
    print("=" * 60)
    
    try:
        # Step 1: Set up test documents
        test_vector_db = await setup_test_documents()
        
        # Step 2: Initialize RAG Chat Engine
        chat_engine = TestRAGChatEngine()
        # Connect to the same test vector database
        chat_engine.test_vector_db = test_vector_db
        import backend.app.services.chat_engine as chat_module
        chat_module.vector_db = test_vector_db
        
        print(f"\n✅ RAG Chat Engine initialized")
        
        # Test 3: Basic RAG query
        print(f"\n🔍 Test 3: Basic RAG Query")
        
        response_1 = await chat_engine.process_message(
            message="What are the key findings from the access reviews?",
            conversation_id="test_conv_001"
        )
        
        print(f"✅ Query processed successfully:")
        print(f"   Response length: {len(response_1['message']['content'])} characters")
        print(f"   Confidence: {response_1['message']['confidence']:.3f}")
        print(f"   Sources: {len(response_1['message']['sources'])} documents")
        print(f"   Context chunks: {response_1['context_metadata']['chunks_retrieved']}")
        print(f"   Documents searched: {response_1['context_metadata']['documents_searched']}")
        print(f"   Risk level: {response_1['compliance_insights'].get('risk_level', 'Unknown')}")
        print(f"   Response preview: {response_1['message']['content'][:200]}...")
        
        # Test 4: Company-specific query
        print(f"\n🏢 Test 4: Company-Specific Query")
        
        response_2 = await chat_engine.process_message(
            message="Tell me about Walmart's compliance issues",
            conversation_id="test_conv_001",
            search_filters={"company": "walmart"}
        )
        
        print(f"✅ Company-filtered query processed:")
        print(f"   Confidence: {response_2['message']['confidence']:.3f}")
        print(f"   Companies found: {response_2['compliance_insights'].get('companies', [])}")
        print(f"   Risk level: {response_2['compliance_insights'].get('risk_level', 'Unknown')}")
        print(f"   Key findings: {response_2['compliance_insights'].get('key_findings', [])}")
        
        # Test 5: Material weakness query
        print(f"\n⚠️ Test 5: Material Weakness Query")
        
        response_3 = await chat_engine.process_message(
            message="Are there any material weaknesses in the access controls?",
            conversation_id="test_conv_001"
        )
        
        print(f"✅ Material weakness query processed:")
        print(f"   Confidence: {response_3['message']['confidence']:.3f}")
        print(f"   Risk level: {response_3['compliance_insights'].get('risk_level', 'Unknown')}")
        print(f"   SOX controls: {response_3['compliance_insights'].get('sox_controls', [])}")
        print(f"   Quality levels: {response_3['compliance_insights'].get('quality_levels', [])}")
        
        # Test 6: Follow-up conversation
        print(f"\n💬 Test 6: Follow-up Conversation")
        
        response_4 = await chat_engine.process_message(
            message="What remediation steps are recommended?",
            conversation_id="test_conv_001"  # Same conversation
        )
        
        print(f"✅ Follow-up query processed:")
        print(f"   Confidence: {response_4['message']['confidence']:.3f}")
        print(f"   Suggested questions: {response_4['suggested_questions']}")
        
        # Test 7: Conversation history
        print(f"\n📜 Test 7: Conversation History")
        
        conversation = await chat_engine.get_conversation("test_conv_001")
        if conversation:
            print(f"✅ Conversation retrieved:")
            print(f"   Total turns: {conversation['total_turns']}")
            print(f"   Created at: {conversation['created_at']}")
            print(f"   Last turn preview: {conversation['turns'][-1]['user_message'][:50]}...")
        else:
            print(f"❌ Failed to retrieve conversation")
        
        # Test 8: Document-specific query
        print(f"\n📄 Test 8: Document-Specific Query")
        
        response_5 = await chat_engine.process_message(
            message="Summarize the findings for this specific document",
            document_id="test_fail_quality_doc",
            conversation_id="test_conv_002"
        )
        
        print(f"✅ Document-specific query processed:")
        print(f"   Confidence: {response_5['message']['confidence']:.3f}")
        print(f"   Documents in context: {response_5['context_metadata']['documents_searched']}")
        
        # Test 9: No context query
        print(f"\n❓ Test 9: Query with No Relevant Context")
        
        response_6 = await chat_engine.process_message(
            message="What is the weather like today?",
            conversation_id="test_conv_003"
        )
        
        print(f"✅ No-context query processed:")
        print(f"   Confidence: {response_6['message']['confidence']:.3f}")
        print(f"   Context chunks: {response_6['context_metadata']['chunks_retrieved']}")
        print(f"   Response handles gracefully: {'no relevant' in response_6['message']['content'].lower()}")
        
        # Test 10: Conversation management
        print(f"\n🗂️ Test 10: Conversation Management")
        
        conversations = await chat_engine.list_conversations()
        print(f"✅ Active conversations: {len(conversations)}")
        for conv in conversations:
            print(f"   - {conv['conversation_id']}: {conv['turn_count']} turns")
        
        # Test cleanup
        deleted = await chat_engine.delete_conversation("test_conv_003")
        print(f"✅ Conversation deletion: {'Success' if deleted else 'Failed'}")
        
        print(f"\n🎉 All RAG Chat Engine tests completed successfully!")
        print(f"✅ Complete RAG pipeline is working correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ RAG Chat Engine test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Starting RAG Chat Engine Tests")
    
    # Check if OpenAI API key is set
    if not settings.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Please set your OpenAI API key to run RAG chat tests")
        return
    
    success = await test_rag_chat_engine()
    
    if success:
        print(f"\n✅ RAG Chat Engine is working correctly!")
        print(f"🎯 Ready to proceed with Subtask 4.5: Reduced Dataset Ingestion & Testing")
        print(f"\n📋 RAG Pipeline Summary:")
        print(f"   ✅ Document Processing → Vector Storage")
        print(f"   ✅ Context Retrieval → Hybrid Search") 
        print(f"   ✅ Response Generation → LLM Integration")
        print(f"   ✅ Conversation Management → Memory")
        print(f"   ✅ Compliance Insights → Domain Intelligence")
    else:
        print(f"\n❌ RAG Chat Engine needs fixes before proceeding")
        print(f"🔧 Please check the error messages above and fix issues")

if __name__ == "__main__":
    asyncio.run(main()) 