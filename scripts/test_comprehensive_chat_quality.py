#!/usr/bin/env python3
"""
Comprehensive Chat Quality Test Script for Verityn AI

This script tests the document processing and multi-agent workflow phases,
then allows interactive testing of the chat interface with the SOX Access Review document.

Usage: python test_comprehensive_chat_quality.py
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.services.vector_database import VectorDatabaseService
from backend.app.workflows.multi_agent_workflow import MultiAgentWorkflow
from backend.app.services.chat_engine import RAGChatEngine
from backend.app.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockUploadFile:
    """Mock UploadFile for testing with actual PDF file."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.content_type = "application/pdf"
        
        # Get file size
        self.size = os.path.getsize(file_path)
    
    async def read(self) -> bytes:
        """Read the actual PDF file content."""
        with open(self.file_path, 'rb') as f:
            return f.read()

class ComprehensiveChatTest:
    """Comprehensive test for document processing and chat quality."""
    
    def __init__(self):
        """Initialize the test environment."""
        self.document_processor = None
        self.vector_db = None
        self.workflow = None
        self.chat_engine = None
        self.document_id = None
        self.test_results = {
            "document_processing": {},
            "vector_storage": {},
            "workflow_execution": {},
            "chat_quality": {}
        }
    
    async def setup_test_environment(self):
        """Set up the test environment with local in-memory Qdrant."""
        print("🔧 Setting up test environment...")
        
        try:
            # Initialize local in-memory Qdrant (not fake vector store)
            self.vector_db = VectorDatabaseService(use_memory=True)  # Use in-memory Qdrant
            await self.vector_db.initialize_collection()
            
            # Override the global vector_db_service so all components use our test instance
            import backend.app.services.vector_database as vector_module
            vector_module.vector_db_service = self.vector_db
            
            # Also override the global instance in the document processor module
            import backend.app.services.document_processor as doc_module
            doc_module.vector_db_service = self.vector_db
            
            # Create document processor - it will now use our test vector database
            self.document_processor = EnhancedDocumentProcessor()
            
            # Initialize multi-agent workflow
            self.workflow = MultiAgentWorkflow(verbose=True, single_document_mode=True)
            
            # Initialize chat engine - it will now use our test vector database
            self.chat_engine = RAGChatEngine()
            
            # CRITICAL FIX: Override the chat engine's vector database reference
            # The chat engine has its own internal reference that needs to be updated
            self.chat_engine._retrieve_context = self._retrieve_context_from_test_db
            
            print("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup test environment: {str(e)}")
            return False
    
    async def _retrieve_context_from_test_db(self, query: str, document_id: str = None, filters: Dict = None) -> List[Dict]:
        """Override the chat engine's context retrieval to use our test vector database."""
        try:
            print(f"🔍 Retrieving context for query: {query[:50]}...")
            
            # Use our test vector database instance
            if document_id:
                # Get specific document chunks
                chunks = await self.vector_db.get_document_chunks(document_id)
                print(f"📄 Retrieved {len(chunks)} chunks for document {document_id}")
            else:
                # For general queries, get chunks from our test database
                # This simulates the hybrid search that would happen in production
                chunks = await self.vector_db.get_document_chunks(self.document_id)
                print(f"📄 Retrieved {len(chunks)} chunks for general query")
            
            if chunks:
                # Convert to the format expected by the chat engine
                results = []
                for chunk in chunks:
                    # Skip placeholder chunks
                    if chunk.get('chunk_text') == "Document chunks stored in memory":
                        continue
                        
                    results.append({
                        'chunk_text': chunk.get('chunk_text', ''),
                        'document_id': chunk.get('document_id', self.document_id),
                        'metadata': chunk.get('metadata', {}),
                        'score': 0.95,  # High relevance score for test
                        'document_type': chunk.get('metadata', {}).get('document_type', 'access_review'),
                        'company': chunk.get('metadata', {}).get('company', 'unknown'),
                        'sox_control_ids': chunk.get('metadata', {}).get('sox_control_ids', [])
                    })
                
                print(f"✅ Returning {len(results)} context chunks to chat engine")
                return results
            else:
                print("⚠️ No chunks found in test vector database")
                return []
                
        except Exception as e:
            print(f"❌ Error in context retrieval: {str(e)}")
            return []
    
    async def test_document_processing(self, pdf_path: str):
        """Test Phase 1: Document processing and storage."""
        print(f"\n📄 Testing Document Processing: {pdf_path}")
        print("=" * 60)
        
        try:
            # Create mock upload file
            mock_file = MockUploadFile(pdf_path)
            
            # Generate document ID
            import uuid
            self.document_id = str(uuid.uuid4())
            
            print(f"📝 Document ID: {self.document_id}")
            print(f"📁 Filename: {mock_file.filename}")
            print(f"📊 File Size: {mock_file.size:,} bytes")
            
            # Process document
            print("\n🔄 Processing document...")
            result = await self.document_processor.process_document(
                file=mock_file,
                document_id=self.document_id,
                description="SOX Access Review 2024 - Test Document"
            )
            
            # Store results
            self.test_results["document_processing"] = {
                "status": result.get("status"),
                "chunk_count": result.get("chunk_count"),
                "vector_storage": result.get("vector_storage"),
                "classification": result.get("classification"),
                "metadata": result.get("metadata")
            }
            
            # Display results
            print(f"✅ Processing Status: {result.get('status')}")
            print(f"📊 Chunks Created: {result.get('chunk_count')}")
            print(f"💾 Vector Storage: {result.get('vector_storage')}")
            
            if result.get("classification"):
                classification = result["classification"]
                print(f"🏷️  Document Type: {classification.get('document_type', 'Unknown')}")
                print(f"⚠️  Risk Level: {classification.get('risk_level', 'Unknown')}")
                print(f"🔒 Compliance Frameworks: {', '.join(classification.get('compliance_frameworks', []))}")
            
            print("✅ Document processing test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Document processing test failed: {str(e)}")
            self.test_results["document_processing"]["error"] = str(e)
            return False
    
    async def test_vector_storage(self):
        """Test vector storage and retrieval."""
        print(f"\n💾 Testing Vector Storage")
        print("=" * 60)
        
        try:
            # Use the same vector database instance that was used during document processing
            # The document processor uses the global vector_db_service, so we should too
            from backend.app.services.vector_database import vector_db_service
            
            # Test retrieval of stored chunks
            chunks = await vector_db_service.get_document_chunks(self.document_id)
            
            if chunks:
                print(f"✅ Retrieved {len(chunks)} chunks from vector database")
                
                # Display sample chunk
                if chunks:
                    sample_chunk = chunks[0]
                    print(f"\n📄 Sample Chunk Preview:")
                    print(f"   Content: {sample_chunk.get('chunk_text', '')[:100]}...")
                    print(f"   Metadata: {sample_chunk.get('metadata', {}).get('filename', 'Unknown')}")
                
                self.test_results["vector_storage"] = {
                    "status": "success",
                    "chunks_retrieved": len(chunks),
                    "sample_chunk": sample_chunk.get('chunk_text', '')[:100] if chunks else None
                }
                
                return True
            else:
                print("❌ No chunks retrieved from vector database")
                self.test_results["vector_storage"]["status"] = "failed"
                return False
                
        except Exception as e:
            print(f"❌ Vector storage test failed: {str(e)}")
            self.test_results["vector_storage"]["error"] = str(e)
            return False
    
    async def examine_chunk_content(self):
        """Examine the content of each chunk to identify chunking issues."""
        print(f"\n🔍 Examining Chunk Content")
        print("=" * 60)
        
        try:
            from backend.app.services.vector_database import vector_db_service
            
            # Get all chunks
            chunks = await vector_db_service.get_document_chunks(self.document_id)
            
            if not chunks:
                print("❌ No chunks found to examine")
                return
            
            print(f"📊 Found {len(chunks)} chunks to examine")
            print("=" * 60)
            
            # Search for specific information in chunks
            target_phrases = [
                "15 inactive user accounts",
                "inactive user accounts",
                "90-day timeframe",
                "User Access Management",
                "security risk",
                "unauthorized access"
            ]
            
            found_phrases = []
            
            for i, chunk in enumerate(chunks):
                chunk_text = chunk.get('chunk_text', '')
                chunk_metadata = chunk.get('metadata', {})
                
                print(f"\n📄 Chunk {i+1}:")
                print(f"   ID: {chunk.get('id', 'N/A')}")
                print(f"   Index: {chunk.get('chunk_index', 'N/A')}")
                print(f"   Length: {len(chunk_text)} characters")
                print(f"   Content Preview:")
                print(f"   {'-' * 50}")
                print(f"   {chunk_text}")
                print(f"   {'-' * 50}")
                
                # Check for target phrases in this chunk
                chunk_found_phrases = []
                for phrase in target_phrases:
                    if phrase.lower() in chunk_text.lower():
                        chunk_found_phrases.append(phrase)
                        found_phrases.append({
                            'chunk': i+1,
                            'phrase': phrase,
                            'context': chunk_text[chunk_text.lower().find(phrase.lower())-50:chunk_text.lower().find(phrase.lower())+len(phrase)+50]
                        })
                
                if chunk_found_phrases:
                    print(f"   🎯 Found phrases: {', '.join(chunk_found_phrases)}")
                else:
                    print(f"   ⚠️  No target phrases found")
                
                print()
            
            # Summary of findings
            print("=" * 60)
            print("📋 CHUNK ANALYSIS SUMMARY")
            print("=" * 60)
            
            if found_phrases:
                print("✅ Target information found in chunks:")
                for finding in found_phrases:
                    print(f"   • Chunk {finding['chunk']}: '{finding['phrase']}'")
                    print(f"     Context: ...{finding['context']}...")
                    print()
            else:
                print("❌ No target information found in any chunks!")
                print("   This indicates a serious chunking problem.")
            
            # Check for chunking issues
            print("🔍 CHUNKING ANALYSIS:")
            total_content_length = sum(len(chunk.get('chunk_text', '')) for chunk in chunks)
            avg_chunk_length = total_content_length / len(chunks) if chunks else 0
            
            print(f"   Total content length: {total_content_length:,} characters")
            print(f"   Average chunk length: {avg_chunk_length:.0f} characters")
            print(f"   Number of chunks: {len(chunks)}")
            
            # Look for potential chunking problems
            short_chunks = [chunk for chunk in chunks if len(chunk.get('chunk_text', '')) < 100]
            if short_chunks:
                print(f"   ⚠️  {len(short_chunks)} chunks are very short (<100 chars) - potential chunking issue")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to examine chunk content: {str(e)}")
            return False
    
    async def test_multi_agent_workflow(self, test_question: str):
        """Test Phase 2: Multi-agent workflow execution."""
        print(f"\n🤖 Testing Multi-Agent Workflow")
        print("=" * 60)
        
        try:
            print(f"❓ Test Question: {test_question}")
            
            # Execute workflow
            print("\n🔄 Executing multi-agent workflow...")
            workflow_result = await self.workflow.execute(
                question=test_question,
                document_id=self.document_id,
                single_document_mode=True
            )
            
            # Store results
            self.test_results["workflow_execution"] = {
                "status": workflow_result.get("status"),
                "workflow_id": workflow_result.get("workflow_id"),
                "execution_time": workflow_result.get("metadata", {}).get("workflow_execution_time"),
                "response_length": len(workflow_result.get("response", "")),
                "response_preview": workflow_result.get("response", "")[:200] + "..." if workflow_result.get("response") else None
            }
            
            # Display results
            print(f"✅ Workflow Status: {workflow_result.get('status')}")
            print(f"🆔 Workflow ID: {workflow_result.get('workflow_id')}")
            print(f"⏱️  Execution Time: {workflow_result.get('metadata', {}).get('workflow_execution_time', 0):.2f}s")
            
            if workflow_result.get("response"):
                print(f"\n📝 Response Preview:")
                print(f"   {workflow_result.get('response', '')[:200]}...")
            
            print("✅ Multi-agent workflow test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Multi-agent workflow test failed: {str(e)}")
            self.test_results["workflow_execution"]["error"] = str(e)
            return False
    
    async def interactive_chat_testing(self):
        """Interactive chat testing with user questions."""
        print(f"\n💬 Interactive Chat Testing")
        print("=" * 60)
        print("🎯 The system is ready for your questions!")
        print("💡 Ask questions about the SOX Access Review document")
        print("💡 Type 'chunks' to examine chunk content")
        print("💡 Type 'status' to see test results summary")
        print("🚫 Type 'quit' to exit the interactive testing")
        print("-" * 60)
        
        while True:
            try:
                # Get user question
                question = input("\n❓ Your Question: ").strip()
                
                if question.lower() == 'quit':
                    print("👋 Exiting interactive testing...")
                    break
                
                if question.lower() == 'status':
                    self._display_test_status()
                    continue
                
                if question.lower() == 'chunks':
                    await self.examine_chunk_content()
                    continue
                
                if not question:
                    print("⚠️  Please enter a question")
                    continue
                
                print(f"\n🔄 Processing your question: {question}")
                print("-" * 40)
                
                # Test with chat engine
                chat_result = await self.chat_engine.process_message(
                    message=question,
                    document_id=self.document_id
                )
                
                # Display response
                if chat_result.get("message", {}).get("content"):
                    response = chat_result["message"]["content"]
                    print(f"\n🤖 AI Response:")
                    print(response)
                    
                    # Store chat quality metrics
                    self.test_results["chat_quality"][question] = {
                        "response_length": len(response),
                        "has_context": "document" in response.lower() or "finding" in response.lower(),
                        "timestamp": asyncio.get_event_loop().time()
                    }
                    
                else:
                    print("❌ No response generated")
                
                # Display suggested questions if available
                if chat_result.get("suggested_questions"):
                    print(f"\n💡 Suggested Follow-up Questions:")
                    for i, suggestion in enumerate(chat_result["suggested_questions"][:3], 1):
                        print(f"   {i}. {suggestion}")
                
                print("-" * 40)
                
            except KeyboardInterrupt:
                print("\n\n👋 Exiting interactive testing...")
                break
            except Exception as e:
                print(f"❌ Error processing question: {str(e)}")
    
    def _display_test_status(self):
        """Display current test status."""
        print(f"\n📊 Test Status Summary")
        print("=" * 60)
        
        # Document Processing
        doc_status = self.test_results["document_processing"]
        print(f"📄 Document Processing: {doc_status.get('status', 'Not tested')}")
        if doc_status.get('chunk_count'):
            print(f"   📊 Chunks: {doc_status['chunk_count']}")
        
        # Vector Storage
        vec_status = self.test_results["vector_storage"]
        print(f"💾 Vector Storage: {vec_status.get('status', 'Not tested')}")
        if vec_status.get('chunks_retrieved'):
            print(f"   📊 Chunks Retrieved: {vec_status['chunks_retrieved']}")
        
        # Workflow Execution
        wf_status = self.test_results["workflow_execution"]
        print(f"🤖 Workflow Execution: {wf_status.get('status', 'Not tested')}")
        if wf_status.get('execution_time'):
            print(f"   ⏱️  Time: {wf_status['execution_time']:.2f}s")
        
        # Chat Quality
        chat_questions = len(self.test_results["chat_quality"])
        print(f"💬 Chat Testing: {chat_questions} questions tested")
        
        print("-" * 60)
    
    async def run_comprehensive_test(self, pdf_path: str):
        """Run the complete comprehensive test."""
        print("🚀 Starting Comprehensive Chat Quality Test")
        print("=" * 80)
        
        try:
            # Setup
            if not await self.setup_test_environment():
                return False
            
            # Phase 1: Document Processing
            if not await self.test_document_processing(pdf_path):
                return False
            
            # Phase 2: Vector Storage
            if not await self.test_vector_storage():
                return False
            
            # Phase 2.5: Examine Chunk Content (NEW)
            await self.examine_chunk_content()
            
            # Phase 3: Multi-Agent Workflow (with sample question)
            sample_question = "What are the key findings in this access review?"
            if not await self.test_multi_agent_workflow(sample_question):
                return False
            
            # Phase 4: Interactive Chat Testing
            await self.interactive_chat_testing()
            
            # Final status
            print(f"\n🏁 Test Session Complete")
            print("=" * 60)
            self._display_test_status()
            
            return True
            
        except Exception as e:
            print(f"❌ Comprehensive test failed: {str(e)}")
            return False

async def main():
    """Main test execution function."""
    # PDF path
    pdf_path = "/Users/ashapondicherry/Desktop/VDU/_Projects/AIE_Bootcamp/Verityn-AI/data/synthetic_documents/pdf/SOX_Access_Review_2024.pdf"
    
    # Verify PDF exists
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        print("Please ensure the SOX Access Review PDF is available at the specified path")
        return
    
    # Create and run test
    test = ComprehensiveChatTest()
    success = await test.run_comprehensive_test(pdf_path)
    
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    # Run the test
    asyncio.run(main())
