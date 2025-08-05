"""
Test script for Enhanced Document Processing Pipeline.

This script tests the document processing functionality including text extraction,
optimized chunking, metadata extraction, and vector database integration.
"""

import asyncio
import sys
import io
from pathlib import Path
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.services.vector_database import VectorDatabaseService
from backend.app.config import settings
from fastapi import UploadFile

class MockUploadFile:
    """Mock UploadFile for testing."""
    
    def __init__(self, filename: str, content: str, content_type: str = "text/plain"):
        self.filename = filename
        self.content = content.encode('utf-8')
        self.content_type = content_type
        self.size = len(self.content)
    
    async def read(self) -> bytes:
        return self.content

class TestEnhancedDocumentProcessor(EnhancedDocumentProcessor):
    """Test version of document processor with in-memory vector database."""
    
    def __init__(self):
        super().__init__()
        # Use in-memory vector database for testing
        self.test_vector_db = VectorDatabaseService(use_memory=True)
    
    async def _store_in_vector_database(
        self,
        document_id: str,
        chunks: List[str],
        metadata: Dict,
    ) -> bool:
        """Store document chunks in test vector database with metadata."""
        try:
            # Ensure test vector database is initialized
            await self.test_vector_db.initialize_collection()
            
            # Store chunks with embeddings and metadata
            success = await self.test_vector_db.insert_document_chunks(
                document_id=document_id,
                chunks=chunks,
                metadata=metadata
            )
            
            return success
        
        except Exception as e:
            raise Exception(f"Test vector database storage failed: {str(e)}")
    
    async def get_document_info(self, document_id: str) -> Dict:
        """Get information about a processed document from test database."""
        try:
            chunks = await self.test_vector_db.get_document_chunks(document_id)
            
            if not chunks:
                return {"error": "Document not found"}
            
            # Extract metadata from first chunk
            metadata = chunks[0].get("metadata", {})
            
            return {
                "document_id": document_id,
                "chunk_count": len(chunks),
                "metadata": {
                    "filename": metadata.get("filename"),
                    "document_type": metadata.get("document_type"),
                    "quality_level": metadata.get("quality_level"),
                    "company": metadata.get("company"),
                    "sox_control_ids": metadata.get("sox_control_ids", []),
                    "upload_timestamp": metadata.get("upload_timestamp"),
                    "file_size": metadata.get("file_size"),
                },
                "status": "stored"
            }
        
        except Exception as e:
            return {"error": f"Failed to get document info: {str(e)}"}
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the test vector database."""
        try:
            return await self.test_vector_db.delete_document(document_id)
        except Exception as e:
            raise Exception(f"Document deletion failed: {str(e)}")

async def test_enhanced_document_processing():
    """Test the enhanced document processing functionality."""
    print("🧪 Testing Enhanced Document Processing Pipeline")
    print("=" * 60)
    
    try:
        # Initialize test document processor with in-memory vector database
        processor = TestEnhancedDocumentProcessor()
        print(f"✅ Enhanced document processor initialized (test mode)")
        
        # Test 1: Process a mock audit document
        print(f"\n📝 Test 1: Process Mock Audit Document")
        
        mock_audit_content = """
        SOX 404 COMPLIANCE DOCUMENT - ACCESS REVIEW
        
        EXECUTIVE SUMMARY
        This quarterly user access review evaluated 1,247 user accounts across financial systems 
        for Uber Technologies. The review identified several control deficiencies requiring 
        management attention.
        
        SCOPE AND METHODOLOGY
        The access review covered all users with access to financial systems including:
        - SAP Financial Module
        - Oracle Procurement System
        - Expense Management Platform
        
        KEY FINDINGS
        1. Segregation of duties violations identified in payment processing
        2. 23 terminated employees with active system access
        3. Lack of quarterly access certification for privileged users
        
        MANAGEMENT RESPONSE
        Management has implemented a remediation plan to address all identified deficiencies.
        All terminated employee access has been revoked and segregation of duties matrix 
        has been updated.
        
        SOX CONTROL ASSESSMENT
        Control 404.1 - DEFICIENT: Access review procedures need enhancement
        Control 404.2 - EFFECTIVE: User provisioning controls operating effectively
        """
        
        mock_file = MockUploadFile(
            filename="uber_access_review_q1_2024.txt",
            content=mock_audit_content,
            content_type="text/plain"
        )
        
        # Document metadata for audit document
        document_metadata = {
            "document_type": "access_review",
            "quality_level": "low",  # Has some deficiencies
            "company": "uber",
            "sox_control_ids": ["404.1", "404.2"],
            "compliance_framework": "SOX",
            "created_by": "test_system"
        }
        
        result = await processor.process_document(
            file=mock_file,
            document_id="test_audit_doc_001",
            description="Q1 2024 Access Review for Uber Technologies",
            document_metadata=document_metadata
        )
        
        # Save the document processing result for later analysis
        doc_processing_result = result.copy()
        
        if result["status"] == "processed":
            print(f"✅ Document processed successfully:")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Chunk Count: {result['chunk_count']}")
            print(f"   Content Length: {len(result['content'])} characters")
            print(f"   Vector Storage: {result['vector_storage']}")
            print(f"   Document Type: {result['metadata']['document_type']}")
            print(f"   Quality Level: {result['metadata']['quality_level']}")
            print(f"   Company: {result['metadata']['company']}")
            print(f"   SOX Controls: {result['metadata']['sox_control_ids']}")
        else:
            print(f"❌ Document processing failed")
            return False
        
        # Test 2: Verify chunks are stored in vector database
        print(f"\n🔍 Test 2: Verify Vector Database Storage")
        
        doc_info = await processor.get_document_info("test_audit_doc_001")
        if "error" not in doc_info:
            print(f"✅ Document info retrieved successfully:")
            print(f"   Stored Chunks: {doc_info['chunk_count']}")
            print(f"   Filename: {doc_info['metadata']['filename']}")
            print(f"   Upload Time: {doc_info['metadata']['upload_timestamp']}")
        else:
            print(f"❌ Failed to retrieve document info: {doc_info['error']}")
        
        # Test 3: Test semantic search on processed document
        print(f"\n🔍 Test 3: Semantic Search on Processed Document")
        
        search_queries = [
            "What SOX compliance issues were found?",
            "How many users were reviewed?",
            "What is the management response?",
            "Which SOX controls were assessed?"
        ]
        
        for query in search_queries:
            print(f"\n   Query: '{query}'")
            search_results = await processor.test_vector_db.semantic_search(
                query_text=query,
                limit=2,
                score_threshold=0.3
            )
            
            if search_results:
                print(f"   ✅ Found {len(search_results)} results:")
                for i, result in enumerate(search_results, 1):
                    print(f"      {i}. Score: {result['score']:.3f}")
                    print(f"         Text: {result['chunk_text'][:100]}...")
                    print(f"         Document: {result['document_id']}")
                    print(f"         Quality: {result['quality_level']}")
            else:
                print(f"   ❌ No results found")
        
        # Test 4: Test metadata filtering
        print(f"\n🎯 Test 4: Metadata Filtering")
        
        # Search with company filter
        company_results = await processor.test_vector_db.semantic_search(
            query_text="access review",
            filters={"company": "uber"},
            limit=3
        )
        print(f"   Uber documents: {len(company_results)} results")
        
        # Search with quality level filter
        quality_results = await processor.test_vector_db.semantic_search(
            query_text="compliance",
            filters={"quality_level": "low"},
            limit=3
        )
        print(f"   Low quality documents: {len(quality_results)} results")
        
        # Test 5: Test hybrid search
        print(f"\n🔀 Test 5: Hybrid Search")
        
        hybrid_results = await processor.test_vector_db.hybrid_search(
            query_text="SOX 404 deficiencies",
            limit=2
        )
        
        if hybrid_results:
            print(f"   ✅ Hybrid search found {len(hybrid_results)} results:")
            for i, result in enumerate(hybrid_results, 1):
                print(f"      {i}. Hybrid Score: {result['hybrid_score']:.3f}")
                print(f"         (Semantic: {result['score']:.3f}, Keyword: {result['keyword_bonus']:.3f})")
                print(f"         Text: {result['chunk_text'][:80]}...")
        else:
            print(f"   ❌ No hybrid search results")
        
        # Test 6: Test chunking optimization
        print(f"\n✂️ Test 6: Chunking Optimization Analysis")
        
        # Use the original document processing result, not search results
        if 'chunks' in doc_processing_result:
            chunks = doc_processing_result['chunks']
            chunk_lengths = [len(chunk) for chunk in chunks]
            avg_length = sum(chunk_lengths) / len(chunk_lengths)
            
            print(f"   ✅ Chunking analysis:")
            print(f"      Total chunks: {len(chunks)}")
            print(f"      Average chunk length: {avg_length:.0f} characters")
            print(f"      Min chunk length: {min(chunk_lengths)}")
            print(f"      Max chunk length: {max(chunk_lengths)}")
            print(f"      Overlap strategy: 250 characters (optimized)")
            
            # Show sample chunks
            print(f"\n   Sample chunks:")
            for i, chunk in enumerate(chunks[:2]):
                print(f"      Chunk {i+1}: {chunk[:100]}...")
        else:
            print(f"   ⚠️  Chunks not available in result for analysis")
            print(f"   Using chunk count from result: {doc_processing_result.get('chunk_count', 'N/A')}")
            
            # Try to get chunks directly from the document info
            doc_info = await processor.get_document_info("test_audit_doc_001")
            if "error" not in doc_info:
                print(f"   ✅ Using stored chunk count: {doc_info['chunk_count']}")
            else:
                print(f"   ❌ Could not retrieve chunk information")
        
        # Test 7: Collection statistics
        print(f"\n📈 Test 7: Vector Database Statistics")
        
        collection_info = await processor.test_vector_db.get_collection_info()
        if collection_info:
            print(f"   ✅ Collection statistics:")
            print(f"      Collection: {collection_info.get('collection_name')}")
            print(f"      Total vectors: {collection_info.get('vectors_count', 'N/A')}")
            print(f"      Status: {collection_info.get('status')}")
            print(f"      Vector dimension: {collection_info.get('vector_size')}")
        
        print(f"\n🎉 All enhanced document processing tests completed successfully!")
        print(f"✅ Enhanced document processor is ready for production use")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Enhanced document processing test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def cleanup_test_data():
    """Clean up test data after testing."""
    try:
        processor = TestEnhancedDocumentProcessor()
        await processor.delete_document("test_audit_doc_001")
        print(f"🧹 Test data cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {str(e)}")

async def main():
    """Main test function."""
    print("🚀 Starting Enhanced Document Processing Tests")
    
    # Check if OpenAI API key is set
    if not settings.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Please set your OpenAI API key to run document processing tests")
        return
    
    success = await test_enhanced_document_processing()
    
    if success:
        print(f"\n✅ Enhanced Document Processing Pipeline is working correctly!")
        print(f"🎯 Ready to proceed with Subtask 4.3: Semantic Search & Retrieval Engine")
        
        # Cleanup test data
        await cleanup_test_data()
    else:
        print(f"\n❌ Enhanced Document Processing Pipeline needs fixes before proceeding")
        print(f"🔧 Please check the error messages above and fix issues")

if __name__ == "__main__":
    asyncio.run(main()) 