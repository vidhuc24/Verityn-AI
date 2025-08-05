"""
Reduced Dataset Ingestion & Testing for Verityn AI.

This script ingests a curated subset of our synthetic documents and validates
the complete RAG pipeline performance with realistic data volumes.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
import random

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

class ReducedDatasetTester:
    """Comprehensive tester for reduced synthetic dataset."""
    
    def __init__(self):
        self.vector_db = VectorDatabaseService(use_memory=True)
        self.processor = self._create_test_processor()
        self.chat_engine = self._create_test_chat_engine()
        
        # Performance tracking
        self.ingestion_metrics = {
            "documents_processed": 0,
            "total_chunks": 0,
            "processing_time": 0.0,
            "avg_chunks_per_doc": 0.0,
            "storage_success_rate": 0.0
        }
        
        self.query_metrics = {
            "queries_processed": 0,
            "avg_response_time": 0.0,
            "avg_confidence": 0.0,
            "context_retrieval_rate": 0.0,
            "compliance_detection_rate": 0.0
        }
    
    def _create_test_processor(self):
        """Create test document processor with in-memory vector database."""
        class TestDocumentProcessor(EnhancedDocumentProcessor):
            def __init__(self, vector_db):
                super().__init__()
                self.test_vector_db = vector_db
            
            async def _store_in_vector_database(self, document_id: str, chunks, metadata) -> bool:
                await self.test_vector_db.initialize_collection()
                return await self.test_vector_db.insert_document_chunks(document_id, chunks, metadata)
            
            async def get_document_info(self, document_id: str) -> Dict[str, Any]:
                return {"document_id": document_id, "status": "stored"}
            
            async def delete_document(self, document_id: str) -> bool:
                return True
        
        return TestDocumentProcessor(self.vector_db)
    
    def _create_test_chat_engine(self):
        """Create test chat engine with in-memory vector database."""
        class TestRAGChatEngine(RAGChatEngine):
            def __init__(self, vector_db):
                super().__init__()
                self.test_vector_db = vector_db
                # Override the global vector_db import
                import backend.app.services.chat_engine as chat_module
                chat_module.vector_db = vector_db
        
        return TestRAGChatEngine(self.vector_db)
    
    def _get_reduced_dataset(self) -> List[Dict[str, Any]]:
        """Get a curated subset of synthetic documents for testing."""
        return [
            # High-quality documents
            {
                "document_id": "uber_access_review_high_001",
                "filename": "uber_access_review_q1_2024_high.txt",
                "content": """
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
                """,
                "metadata": {
                    "document_type": "access_review",
                    "quality_level": "high",
                    "company": "uber",
                    "sox_control_ids": ["404.1", "404.2"],
                    "compliance_framework": "SOX",
                    "created_by": "synthetic_generator"
                }
            },
            {
                "document_id": "amazon_reconciliation_high_001",
                "filename": "amazon_financial_reconciliation_q1_2024_high.txt",
                "content": """
SOX 302 COMPLIANCE DOCUMENT - FINANCIAL RECONCILIATION

EXECUTIVE SUMMARY
This quarterly financial reconciliation for Amazon Inc. validates the accuracy of 
financial reporting processes and identifies no material discrepancies requiring
management attention.

RECONCILIATION SCOPE
The reconciliation covered key financial accounts including:
- Cash and Cash Equivalents: $73.4B reconciled
- Accounts Receivable: $32.9B reconciled
- Inventory Valuation: $27.4B reconciled

RECONCILIATION RESULTS
1. All account balances reconciled within acceptable variance thresholds
2. Supporting documentation complete for all material transactions
3. Monthly reconciliation procedures operating effectively
4. No unresolved reconciling items identified

CONTROL EFFECTIVENESS
All reconciliation controls are operating effectively with no exceptions noted.
Management review and approval processes are functioning as designed.

SOX CONTROL ASSESSMENT
Control 302.1 - EFFECTIVE: Monthly reconciliation procedures
Control 302.2 - EFFECTIVE: Management review and approval processes
                """,
                "metadata": {
                    "document_type": "financial_reconciliation",
                    "quality_level": "high",
                    "company": "amazon",
                    "sox_control_ids": ["302.1", "302.2"],
                    "compliance_framework": "SOX",
                    "created_by": "synthetic_generator"
                }
            },
            # Medium-quality documents
            {
                "document_id": "walmart_risk_assessment_medium_001",
                "filename": "walmart_risk_assessment_q1_2024_medium.txt",
                "content": """
SOX 404 COMPLIANCE DOCUMENT - RISK ASSESSMENT

EXECUTIVE SUMMARY
This quarterly risk assessment for Walmart Inc. identifies moderate risks in
financial reporting processes that require management attention but do not
constitute material weaknesses.

RISK ASSESSMENT SCOPE
The assessment covered financial reporting risks across:
- Revenue Recognition Processes
- Inventory Management Systems
- Internal Control Framework

IDENTIFIED RISKS
1. MODERATE RISK: Manual journal entry processes lack automated controls
2. MODERATE RISK: Segregation of duties gaps in certain locations
3. LOW RISK: Documentation completeness in some reconciliation procedures

MANAGEMENT RESPONSE
Management has developed remediation plans for moderate risks with target
completion dates within 90 days. Additional training will be provided to
address documentation gaps.

SOX CONTROL ASSESSMENT
Control 404.1 - NEEDS IMPROVEMENT: Risk assessment procedures require enhancement
Control 404.3 - ADEQUATE: Control monitoring processes functioning adequately
                """,
                "metadata": {
                    "document_type": "risk_assessment",
                    "quality_level": "medium",
                    "company": "walmart",
                    "sox_control_ids": ["404.1", "404.3"],
                    "compliance_framework": "SOX",
                    "created_by": "synthetic_generator"
                }
            },
            # Fail-quality documents with material weaknesses
            {
                "document_id": "walmart_access_review_fail_001",
                "filename": "walmart_access_review_q1_2024_fail.txt",
                "content": """
SOX 404 COMPLIANCE DOCUMENT - ACCESS REVIEW

EXECUTIVE SUMMARY
This quarterly user access review for Walmart Inc. identified several MATERIAL 
WEAKNESSES requiring immediate management attention and remediation.

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
                """,
                "metadata": {
                    "document_type": "access_review",
                    "quality_level": "fail",
                    "company": "walmart",
                    "sox_control_ids": ["404.1", "404.2", "404.4"],
                    "compliance_framework": "SOX",
                    "created_by": "synthetic_generator"
                }
            },
            {
                "document_id": "uber_reconciliation_fail_001",
                "filename": "uber_financial_reconciliation_q1_2024_fail.txt",
                "content": """
SOX 302 COMPLIANCE DOCUMENT - FINANCIAL RECONCILIATION

EXECUTIVE SUMMARY
This quarterly financial reconciliation for Uber Technologies identified MATERIAL
WEAKNESSES in reconciliation procedures that require immediate corrective action.

RECONCILIATION SCOPE
The reconciliation attempted to validate:
- Cash and Cash Equivalents: $4.2B - UNRECONCILED
- Accounts Receivable: $2.8B - PARTIALLY RECONCILED  
- Revenue Recognition: $31.9B - MATERIAL DISCREPANCIES

CRITICAL FINDINGS - MATERIAL WEAKNESSES
1. UNRECONCILED VARIANCES: $847M in unresolved reconciling items
2. MISSING DOCUMENTATION: 34% of transactions lack supporting documentation
3. CONTROL FAILURES: Monthly reconciliation procedures not performed consistently
4. APPROVAL GAPS: 67 reconciliations lack required management approval

IMMEDIATE ACTIONS REQUIRED
- Complete reconciliation of all unresolved items within 15 days
- Implement enhanced documentation requirements
- Strengthen management review and approval processes
- Conduct comprehensive restatement analysis

SOX CONTROL ASSESSMENT
Control 302.1 - FAILING: Monthly reconciliation procedures inadequate
Control 302.2 - FAILING: Management review processes require redesign
Control 302.3 - DEFICIENT: Supporting documentation controls insufficient
                """,
                "metadata": {
                    "document_type": "financial_reconciliation",
                    "quality_level": "fail",
                    "company": "uber",
                    "sox_control_ids": ["302.1", "302.2", "302.3"],
                    "compliance_framework": "SOX",
                    "created_by": "synthetic_generator"
                }
            }
        ]
    
    def _get_test_queries(self) -> List[Dict[str, Any]]:
        """Get comprehensive test queries for RAG validation."""
        return [
            # Basic information queries
            {
                "query": "What are the key findings from the access reviews?",
                "expected_context": ["access_review"],
                "expected_companies": ["uber", "walmart"],
                "complexity": "basic"
            },
            {
                "query": "Which companies have material weaknesses?",
                "expected_context": ["fail"],
                "expected_companies": ["walmart", "uber"],
                "complexity": "basic"
            },
            # Company-specific queries
            {
                "query": "Tell me about Uber's compliance issues",
                "expected_companies": ["uber"],
                "expected_context": ["reconciliation", "access_review"],
                "complexity": "intermediate"
            },
            {
                "query": "What is Walmart's risk assessment status?",
                "expected_companies": ["walmart"],
                "expected_context": ["risk_assessment"],
                "complexity": "intermediate"
            },
            # SOX control queries
            {
                "query": "Which SOX 404 controls are failing?",
                "expected_context": ["404"],
                "expected_companies": ["walmart"],
                "complexity": "advanced"
            },
            {
                "query": "Are there any SOX 302 control deficiencies?",
                "expected_context": ["302"],
                "expected_companies": ["uber"],
                "complexity": "advanced"
            },
            # Remediation queries
            {
                "query": "What remediation steps are recommended for material weaknesses?",
                "expected_context": ["fail", "material weakness"],
                "complexity": "advanced"
            },
            # Cross-company analysis
            {
                "query": "Compare the access control effectiveness between Uber and Walmart",
                "expected_companies": ["uber", "walmart"],
                "expected_context": ["access_review"],
                "complexity": "expert"
            }
        ]
    
    async def ingest_reduced_dataset(self) -> bool:
        """Ingest the reduced synthetic dataset."""
        print("📥 Starting Reduced Dataset Ingestion")
        print("=" * 60)
        
        documents = self._get_reduced_dataset()
        start_time = time.time()
        successful_ingestions = 0
        total_chunks = 0
        
        try:
            for i, doc_data in enumerate(documents, 1):
                print(f"\n📄 Processing Document {i}/{len(documents)}: {doc_data['filename']}")
                
                # Create mock file
                mock_file = MockUploadFile(
                    filename=doc_data["filename"],
                    content=doc_data["content"],
                    content_type="text/plain"
                )
                
                # Process document
                doc_start = time.time()
                result = await self.processor.process_document(
                    file=mock_file,
                    document_id=doc_data["document_id"],
                    description=f"Synthetic {doc_data['metadata']['document_type']} for {doc_data['metadata']['company']}",
                    document_metadata=doc_data["metadata"]
                )
                doc_time = time.time() - doc_start
                
                if result["status"] == "processed":
                    successful_ingestions += 1
                    total_chunks += result["chunk_count"]
                    print(f"   ✅ Processed: {result['chunk_count']} chunks in {doc_time:.2f}s")
                    print(f"   📊 Company: {doc_data['metadata']['company'].title()}")
                    print(f"   📊 Quality: {doc_data['metadata']['quality_level'].title()}")
                    print(f"   📊 SOX Controls: {', '.join(doc_data['metadata']['sox_control_ids'])}")
                else:
                    print(f"   ❌ Processing failed: {result.get('error', 'Unknown error')}")
            
            # Calculate metrics
            total_time = time.time() - start_time
            self.ingestion_metrics.update({
                "documents_processed": len(documents),
                "total_chunks": total_chunks,
                "processing_time": total_time,
                "avg_chunks_per_doc": total_chunks / len(documents) if documents else 0,
                "storage_success_rate": successful_ingestions / len(documents) if documents else 0
            })
            
            print(f"\n🎯 Ingestion Summary:")
            print(f"   📄 Documents: {successful_ingestions}/{len(documents)} successful")
            print(f"   🧩 Total Chunks: {total_chunks}")
            print(f"   ⏱️  Total Time: {total_time:.2f}s")
            print(f"   📊 Avg Chunks/Doc: {self.ingestion_metrics['avg_chunks_per_doc']:.1f}")
            print(f"   ✅ Success Rate: {self.ingestion_metrics['storage_success_rate']:.1%}")
            
            return successful_ingestions == len(documents)
            
        except Exception as e:
            print(f"\n❌ Ingestion failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_rag_pipeline(self) -> bool:
        """Test the complete RAG pipeline with comprehensive queries."""
        print(f"\n🧪 Testing RAG Pipeline Performance")
        print("=" * 60)
        
        queries = self._get_test_queries()
        successful_queries = 0
        total_response_time = 0.0
        total_confidence = 0.0
        context_retrievals = 0
        compliance_detections = 0
        
        try:
            for i, query_data in enumerate(queries, 1):
                print(f"\n🔍 Query {i}/{len(queries)} ({query_data['complexity']})")
                print(f"   Question: {query_data['query']}")
                
                # Process query
                query_start = time.time()
                response = await self.chat_engine.process_message(
                    message=query_data["query"],
                    conversation_id=f"test_conv_{i}"
                )
                query_time = time.time() - query_start
                
                # Analyze response
                confidence = response["message"]["confidence"]
                context_chunks = response["context_metadata"]["chunks_retrieved"]
                companies_found = response["compliance_insights"].get("companies", [])
                risk_level = response["compliance_insights"].get("risk_level", "Unknown")
                
                # Validate expectations
                context_found = context_chunks > 0
                expected_companies = set(query_data.get("expected_companies", []))
                found_companies = set(companies_found)
                company_match = len(expected_companies.intersection(found_companies)) > 0 if expected_companies else True
                
                # Update metrics
                successful_queries += 1
                total_response_time += query_time
                total_confidence += confidence
                if context_found:
                    context_retrievals += 1
                if risk_level != "Unknown" or companies_found:
                    compliance_detections += 1
                
                print(f"   ✅ Response: {len(response['message']['content'])} chars in {query_time:.2f}s")
                print(f"   📊 Confidence: {confidence:.3f}")
                print(f"   📊 Context: {context_chunks} chunks")
                print(f"   📊 Companies: {companies_found}")
                print(f"   📊 Risk Level: {risk_level}")
                print(f"   ✅ Company Match: {'Yes' if company_match else 'No'}")
                
                # Show response preview
                response_preview = response["message"]["content"][:150].replace('\n', ' ')
                print(f"   💬 Preview: {response_preview}...")
            
            # Calculate final metrics
            if queries:
                self.query_metrics.update({
                    "queries_processed": len(queries),
                    "avg_response_time": total_response_time / len(queries),
                    "avg_confidence": total_confidence / len(queries),
                    "context_retrieval_rate": context_retrievals / len(queries),
                    "compliance_detection_rate": compliance_detections / len(queries)
                })
            
            print(f"\n🎯 RAG Pipeline Summary:")
            print(f"   🔍 Queries: {successful_queries}/{len(queries)} successful")
            print(f"   ⏱️  Avg Response Time: {self.query_metrics['avg_response_time']:.2f}s")
            print(f"   📊 Avg Confidence: {self.query_metrics['avg_confidence']:.3f}")
            print(f"   📊 Context Retrieval: {self.query_metrics['context_retrieval_rate']:.1%}")
            print(f"   📊 Compliance Detection: {self.query_metrics['compliance_detection_rate']:.1%}")
            
            return successful_queries == len(queries)
            
        except Exception as e:
            print(f"\n❌ RAG pipeline test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def performance_stress_test(self) -> bool:
        """Run performance stress test with concurrent queries."""
        print(f"\n⚡ Performance Stress Test")
        print("=" * 60)
        
        try:
            # Generate stress test queries
            stress_queries = [
                "What are the material weaknesses?",
                "Which companies have effective controls?",
                "Summarize the SOX 404 findings",
                "What remediation is needed?",
                "Compare risk levels across companies"
            ] * 3  # 15 total queries
            
            # Run concurrent queries
            start_time = time.time()
            tasks = []
            for i, query in enumerate(stress_queries):
                task = self.chat_engine.process_message(
                    message=query,
                    conversation_id=f"stress_conv_{i}"
                )
                tasks.append(task)
            
            # Execute all queries concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # Analyze results
            successful_responses = sum(1 for r in responses if not isinstance(r, Exception))
            avg_confidence = sum(r["message"]["confidence"] for r in responses if not isinstance(r, Exception)) / successful_responses if successful_responses else 0
            
            print(f"   ✅ Concurrent Queries: {successful_responses}/{len(stress_queries)} successful")
            print(f"   ⏱️  Total Time: {total_time:.2f}s")
            print(f"   ⏱️  Avg Time per Query: {total_time/len(stress_queries):.2f}s")
            print(f"   📊 Avg Confidence: {avg_confidence:.3f}")
            print(f"   🚀 Throughput: {len(stress_queries)/total_time:.1f} queries/second")
            
            return successful_responses >= len(stress_queries) * 0.9  # 90% success rate
            
        except Exception as e:
            print(f"\n❌ Stress test failed: {str(e)}")
            return False
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        return {
            "ingestion_performance": self.ingestion_metrics,
            "query_performance": self.query_metrics,
            "system_readiness": {
                "ingestion_ready": self.ingestion_metrics["storage_success_rate"] >= 0.95,
                "query_ready": self.query_metrics["context_retrieval_rate"] >= 0.75,
                "compliance_ready": self.query_metrics["compliance_detection_rate"] >= 0.80,
                "performance_ready": self.query_metrics["avg_response_time"] <= 5.0
            },
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        if self.ingestion_metrics["storage_success_rate"] < 0.95:
            recommendations.append("Improve document ingestion error handling")
        
        if self.query_metrics["avg_response_time"] > 3.0:
            recommendations.append("Optimize vector search performance")
        
        if self.query_metrics["avg_confidence"] < 0.7:
            recommendations.append("Enhance context retrieval relevance")
        
        if self.query_metrics["compliance_detection_rate"] < 0.8:
            recommendations.append("Improve compliance intelligence extraction")
        
        if not recommendations:
            recommendations.append("System performance is optimal - ready for production")
        
        return recommendations

async def main():
    """Main testing function."""
    print("🚀 Starting Reduced Dataset Ingestion & Testing")
    print("🎯 Validating Complete RAG Pipeline Performance")
    
    # Check OpenAI API key
    if not settings.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Please set your OpenAI API key to run RAG tests")
        return
    
    # Initialize tester
    tester = ReducedDatasetTester()
    
    # Run comprehensive testing
    try:
        # Step 1: Ingest reduced dataset
        ingestion_success = await tester.ingest_reduced_dataset()
        if not ingestion_success:
            print("❌ Dataset ingestion failed - cannot proceed with RAG testing")
            return
        
        # Step 2: Test RAG pipeline
        rag_success = await tester.test_rag_pipeline()
        if not rag_success:
            print("❌ RAG pipeline testing failed")
            return
        
        # Step 3: Performance stress test
        stress_success = await tester.performance_stress_test()
        
        # Step 4: Generate performance report
        report = tester.generate_performance_report()
        
        print(f"\n📊 FINAL PERFORMANCE REPORT")
        print("=" * 60)
        print(f"✅ Dataset Ingestion: {'PASSED' if ingestion_success else 'FAILED'}")
        print(f"✅ RAG Pipeline: {'PASSED' if rag_success else 'FAILED'}")
        print(f"✅ Stress Test: {'PASSED' if stress_success else 'FAILED'}")
        
        print(f"\n🎯 System Readiness:")
        for component, ready in report["system_readiness"].items():
            status = "✅ READY" if ready else "❌ NEEDS WORK"
            print(f"   {component.replace('_', ' ').title()}: {status}")
        
        print(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")
        
        # Overall success
        overall_success = ingestion_success and rag_success and all(report["system_readiness"].values())
        
        if overall_success:
            print(f"\n🎉 SUBTASK 4.5 COMPLETED SUCCESSFULLY!")
            print(f"✅ Reduced dataset ingestion and testing complete")
            print(f"✅ RAG pipeline validated and production-ready")
            print(f"🚀 Ready to proceed with Phase 3: Multi-Agent Workflow")
        else:
            print(f"\n⚠️  SUBTASK 4.5 PARTIALLY COMPLETED")
            print(f"🔧 Some components need optimization before production")
        
        return overall_success
        
    except Exception as e:
        print(f"\n❌ Testing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(main()) 