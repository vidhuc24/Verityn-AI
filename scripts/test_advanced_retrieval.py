#!/usr/bin/env python3
"""
Test Script for Advanced Retrieval Techniques in Verityn AI.

This script validates that advanced retrieval techniques are working correctly
and compares their performance following bootcamp Session 9 patterns.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.advanced_retrieval import advanced_retrieval_service
from backend.app.services.vector_database import VectorDatabaseService
from backend.app.agents.specialized_agents import ContextRetrievalAgent
from langchain.schema import Document
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedRetrievalTester:
    """Test advanced retrieval functionality."""
    
    def __init__(self):
        self.vector_db = VectorDatabaseService(use_memory=True)
        self.context_agent = ContextRetrievalAgent(verbose=True)
        
    async def setup_test_data(self):
        """Setup test documents for retrieval testing."""
        print("🔧 Setting up test data...")
        
        # Create test documents with audit-specific content
        test_documents = [
            Document(
                page_content="Access Review Findings: Material weakness identified in user access controls for financial systems. SOX 404 controls ineffective. Users have excessive permissions that violate segregation of duties.",
                metadata={
                    "document_type": "access_review",
                    "company": "Test Company A",
                    "compliance_framework": "SOX",
                    "risk_level": "high",
                    "sox_controls": ["404.1", "404.2"]
                }
            ),
            Document(
                page_content="Financial Reconciliation Report: Month-end close process shows discrepancies in account reconciliations. Control testing reveals deficiencies in approval workflows for journal entries.",
                metadata={
                    "document_type": "financial_reconciliation",
                    "company": "Test Company A", 
                    "compliance_framework": "SOX",
                    "risk_level": "medium",
                    "sox_controls": ["404.1"]
                }
            ),
            Document(
                page_content="Risk Assessment Summary: Overall risk level is medium. Key risks include IT security vulnerabilities and inadequate internal controls. Material weaknesses identified in IT general controls.",
                metadata={
                    "document_type": "risk_assessment",
                    "company": "Test Company B",
                    "compliance_framework": "SOX",
                    "risk_level": "medium",
                    "sox_controls": ["404.1", "404.2"]
                }
            ),
            Document(
                page_content="SOX 404 Testing Results: Internal controls over financial reporting are effective. No material weaknesses identified. All key controls tested passed with satisfactory results.",
                metadata={
                    "document_type": "control_testing",
                    "company": "Test Company C",
                    "compliance_framework": "SOX",
                    "risk_level": "low",
                    "sox_controls": ["404.1", "404.2", "302.1"]
                }
            ),
            Document(
                page_content="Material Weakness Disclosure: Significant deficiency in IT access controls identified. Users have inappropriate access to financial systems. Remediation plan in progress.",
                metadata={
                    "document_type": "material_weakness",
                    "company": "Test Company D",
                    "compliance_framework": "SOX",
                    "risk_level": "high",
                    "sox_controls": ["404.1"]
                }
            )
        ]
        
        # Initialize vector database
        await self.vector_db.initialize_collection()
        
        # Add documents to vector database
        for i, doc in enumerate(test_documents):
            await self.vector_db.insert_document_chunks(
                document_id=f"test_doc_{i+1}",
                chunks=[doc.page_content],
                metadata=doc.metadata
            )
        
        # Initialize advanced retrievers
        await advanced_retrieval_service.initialize_retrievers(test_documents)
        
        print(f"✅ Test data setup completed with {len(test_documents)} documents")
        return test_documents
    
    async def test_hybrid_search(self):
        """Test hybrid search combining semantic and keyword approaches."""
        print("\n🔍 Testing Hybrid Search")
        print("=" * 50)
        
        query = "What are the material weaknesses in access controls?"
        
        try:
            results = await advanced_retrieval_service.hybrid_search(
                query=query,
                limit=5,
                semantic_weight=0.7,
                keyword_weight=0.3
            )
            
            print(f"📊 Query: {query}")
            print(f"📈 Results: {len(results)} documents found")
            
            for i, result in enumerate(results[:3]):
                print(f"  {i+1}. Score: {result.get('combined_score', 0):.3f}")
                print(f"     Content: {result.get('chunk_text', '')[:100]}...")
                print(f"     Metadata: {result.get('metadata', {}).get('document_type', 'Unknown')}")
            
            return len(results) > 0
            
        except Exception as e:
            print(f"❌ Hybrid search failed: {str(e)}")
            return False
    
    async def test_query_expansion(self):
        """Test query expansion for audit terminology."""
        print("\n🔍 Testing Query Expansion")
        print("=" * 50)
        
        query = "What are the SOX compliance issues?"
        
        try:
            results = await advanced_retrieval_service.query_expansion_search(
                query=query,
                limit=5,
                expansion_terms=["SOX 404", "internal controls"]
            )
            
            print(f"📊 Query: {query}")
            print(f"📈 Results: {len(results)} documents found")
            
            for i, result in enumerate(results[:3]):
                print(f"  {i+1}. Score: {result.get('score', 0):.3f}")
                print(f"     Content: {result.get('chunk_text', '')[:100]}...")
                print(f"     Metadata: {result.get('metadata', {}).get('document_type', 'Unknown')}")
            
            return len(results) > 0
            
        except Exception as e:
            print(f"❌ Query expansion failed: {str(e)}")
            return False
    
    async def test_multi_hop_retrieval(self):
        """Test multi-hop retrieval for complex queries."""
        print("\n🔍 Testing Multi-Hop Retrieval")
        print("=" * 50)
        
        query = "Compare access control issues across different companies"
        
        try:
            results = await advanced_retrieval_service.multi_hop_retrieval(
                query=query,
                limit=5,
                max_hops=2
            )
            
            print(f"📊 Query: {query}")
            print(f"📈 Results: {len(results)} documents found")
            
            for i, result in enumerate(results[:3]):
                print(f"  {i+1}. Score: {result.get('score', 0):.3f}")
                print(f"     Content: {result.get('chunk_text', '')[:100]}...")
                print(f"     Metadata: {result.get('metadata', {}).get('document_type', 'Unknown')}")
            
            return len(results) > 0
            
        except Exception as e:
            print(f"❌ Multi-hop retrieval failed: {str(e)}")
            return False
    
    async def test_ensemble_retrieval(self):
        """Test ensemble retrieval combining multiple techniques."""
        print("\n🔍 Testing Ensemble Retrieval")
        print("=" * 50)
        
        query = "What are the key findings from audit reports?"
        
        try:
            results = await advanced_retrieval_service.ensemble_retrieval(
                query=query,
                limit=5
            )
            
            print(f"📊 Query: {query}")
            print(f"📈 Results: {len(results)} documents found")
            
            for i, result in enumerate(results[:3]):
                print(f"  {i+1}. Score: {result.get('score', 0):.3f}")
                print(f"     Content: {result.get('chunk_text', '')[:100]}...")
                print(f"     Method: {result.get('retrieval_method', 'Unknown')}")
            
            return len(results) > 0
            
        except Exception as e:
            print(f"❌ Ensemble retrieval failed: {str(e)}")
            return False
    
    async def test_context_retrieval_agent(self):
        """Test the enhanced context retrieval agent."""
        print("\n🤖 Testing Enhanced Context Retrieval Agent")
        print("=" * 50)
        
        test_cases = [
            {
                "question": "What are the material weaknesses in SOX controls?",
                "analysis": {
                    "complexity": "advanced",
                    "compliance_frameworks": ["SOX"],
                    "search_keywords": ["material weakness", "SOX", "controls"]
                }
            },
            {
                "question": "Compare access control effectiveness between companies",
                "analysis": {
                    "complexity": "advanced", 
                    "compliance_frameworks": ["SOX"],
                    "search_keywords": ["access control", "effectiveness", "companies"]
                }
            },
            {
                "question": "What are the key findings from access reviews?",
                "analysis": {
                    "complexity": "intermediate",
                    "compliance_frameworks": ["SOX"],
                    "search_keywords": ["access review", "findings"]
                }
            }
        ]
        
        results = {}
        
        for i, test_case in enumerate(test_cases):
            print(f"\n🧪 Test Case {i+1}: {test_case['question']}")
            
            try:
                result = await self.context_agent.execute({
                    "question": test_case["question"],
                    "analysis": test_case["analysis"]
                })
                
                if result.get("retrieval_status") == "completed":
                    print(f"  ✅ Strategy: {result.get('retrieval_strategy', 'Unknown')}")
                    print(f"  📊 Method: {result.get('retrieval_method', 'Unknown')}")
                    print(f"  📈 Results: {result.get('result_count', 0)} documents")
                    results[f"test_case_{i+1}"] = True
                else:
                    print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
                    results[f"test_case_{i+1}"] = False
                    
            except Exception as e:
                print(f"  ❌ Exception: {str(e)}")
                results[f"test_case_{i+1}"] = False
        
        return all(results.values())
    
    async def test_retrieval_comparison(self):
        """Test comparison of different retrieval techniques."""
        print("\n📊 Testing Retrieval Technique Comparison")
        print("=" * 50)
        
        query = "What are the SOX compliance issues and material weaknesses?"
        
        try:
            comparison = await advanced_retrieval_service.compare_retrieval_techniques(
                query=query,
                limit=5
            )
            
            print(f"📊 Query: {comparison['query']}")
            print(f"⏰ Timestamp: {comparison['timestamp']}")
            
            for technique, data in comparison.get("techniques", {}).items():
                if "error" in data:
                    print(f"  ❌ {technique}: {data['error']}")
                else:
                    print(f"  ✅ {technique}: {data['result_count']} results, avg score: {data['avg_score']:.3f}")
            
            return len(comparison.get("techniques", {})) > 0
            
        except Exception as e:
            print(f"❌ Retrieval comparison failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all advanced retrieval tests."""
        print("🚀 Starting Advanced Retrieval Tests")
        print("🎯 Validating Multiple Retrieval Techniques")
        print("=" * 60)
        
        # Setup test data
        await self.setup_test_data()
        
        tests = [
            ("Hybrid Search", self.test_hybrid_search),
            ("Query Expansion", self.test_query_expansion),
            ("Multi-Hop Retrieval", self.test_multi_hop_retrieval),
            ("Ensemble Retrieval", self.test_ensemble_retrieval),
            ("Context Retrieval Agent", self.test_context_retrieval_agent),
            ("Retrieval Comparison", self.test_retrieval_comparison)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                print(f"\n🧪 Running {test_name} Test...")
                success = await test_func()
                results[test_name] = success
                print(f"{'✅' if success else '❌'} {test_name}: {'PASS' if success else 'FAIL'}")
            except Exception as e:
                print(f"❌ {test_name}: FAIL - {str(e)}")
                results[test_name] = False
        
        # Generate summary
        self._generate_test_summary(results)
        
        return all(results.values())
    
    def _generate_test_summary(self, results):
        """Generate test summary report."""
        print("\n📊 Advanced Retrieval Test Summary")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        print(f"\n📈 Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All advanced retrieval tests passed!")
            print("✅ Multiple retrieval techniques are working correctly")
            print("✅ Context retrieval agent is enhanced with advanced techniques")
        else:
            print("⚠️  Some tests failed - check configuration and setup")
        
        # Print technique overview
        print("\n🔧 Advanced Retrieval Techniques Implemented:")
        techniques = [
            "Hybrid Search (Semantic + BM25)",
            "Query Expansion (Audit-specific terms)",
            "Multi-Hop Retrieval (Cross-document)",
            "Ensemble Retrieval (Multiple methods)",
            "Contextual Compression (Reranking)",
            "Intelligent Strategy Selection"
        ]
        
        for technique in techniques:
            print(f"   • {technique}")


async def main():
    """Main test execution."""
    tester = AdvancedRetrievalTester()
    
    try:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 SUBTASK 5.3 COMPLETED SUCCESSFULLY!")
            print("✅ Advanced retrieval techniques are working correctly")
            print("✅ Multiple retrieval strategies implemented")
            print("✅ Context retrieval agent enhanced")
            print("🚀 Ready to proceed with Subtask 5.4: RAGAS Evaluation Framework")
        else:
            print("\n⚠️  Some tests failed - please check configuration")
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 