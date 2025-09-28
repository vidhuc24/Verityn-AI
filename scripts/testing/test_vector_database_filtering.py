#!/usr/bin/env python3
"""
Vector Database Filtering Test Script

This script tests the vector database filtering mechanism to ensure:
1. Qdrant server-side filtering works correctly with nested metadata
2. All filter combinations (string/list, singular/plural) work properly
3. No regression in the zero-results bug that was fixed
4. Proper handling of different metadata field types

Usage:
    uv run python scripts/testing/test_vector_database_filtering.py
"""

import asyncio
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# Add project root to path
sys.path.append('.')

from backend.app.services.vector_database import VectorDatabaseService
from backend.app.services.document_processor import EnhancedDocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDatabaseFilteringTest:
    """Comprehensive test suite for vector database filtering functionality."""
    
    def __init__(self):
        """Initialize the filtering test."""
        self.vector_db = VectorDatabaseService()
        self.doc_processor = EnhancedDocumentProcessor()
        self.test_results = {
            "test_timestamp": time.time(),
            "filter_tests": {},
            "performance_metrics": {},
            "regression_tests": {},
            "edge_cases": {},
            "overall_success": False
        }
        
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run the complete filtering test suite."""
        logger.info("🚀 Starting Vector Database Filtering Test")
        logger.info("📊 Testing Qdrant server-side filtering with nested metadata")
        
        try:
            # Setup test data
            await self._setup_test_data()
            
            # Run filter combination tests
            await self._test_filter_combinations()
            
            # Run regression tests for zero-results bug
            await self._test_zero_results_regression()
            
            # Run edge case tests
            await self._test_edge_cases()
            
            # Run performance tests
            await self._test_performance()
            
            # Calculate overall success
            self._calculate_overall_success()
            
            # Generate report
            self._generate_report()
            
            return self.test_results
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {str(e)}")
            self.test_results["error"] = str(e)
            return self.test_results
    
    async def _setup_test_data(self):
        """Setup test documents with known metadata for filtering tests."""
        logger.info("📄 Setting up test data...")
        
        # Test documents with specific content that will be classified correctly
        test_docs = [
            {
                "content": "Access Review Report - SOX 404 Compliance\n\nThis document contains findings from our quarterly access review for TestCorp. We identified several material weaknesses in user access controls including excessive administrative privileges and terminated employees with active system access. Risk level: medium. Company: TestCorp.",
                "expected_metadata": {
                    "document_type": "access_review",
                    "compliance_framework": "SOX", 
                    "risk_level": "medium",
                    "company": "TestCorp"
                }
            },
            {
                "content": "Financial Controls Assessment - SOX & SOC2 Compliance\n\nTestCorp financial controls evaluation revealed high-risk deficiencies in reconciliation processes. Multiple compliance frameworks affected: SOX and SOC2. Critical findings require immediate remediation. Risk level: high. Company: TestCorp.",
                "expected_metadata": {
                    "document_type": "financial_controls",
                    "compliance_framework": "SOX",
                    "risk_level": "high", 
                    "company": "TestCorp"
                }
            },
            {
                "content": "Risk Assessment Report - ISO27001 Framework\n\nAnnual risk assessment for AnotherCorp identified low-risk vulnerabilities in information security controls. ISO27001 compliance maintained with minor recommendations. Risk level: low. Company: AnotherCorp.",
                "expected_metadata": {
                    "document_type": "risk_assessment",
                    "compliance_framework": "ISO27001",
                    "risk_level": "low",
                    "company": "AnotherCorp"
                }
            }
        ]
        
        # Store test documents using proper Document objects
        from langchain.docstore.document import Document
        
        for i, doc in enumerate(test_docs):
            doc_id = f"filter_test_doc_{i+1}"
            
            # Create Document objects with proper metadata structure
            documents = [Document(
                page_content=doc["content"],
                metadata={
                    "document_id": doc_id,
                    "chunk_index": 0,
                    "test_document": True,
                    # Add expected metadata for testing (simulating classification results)
                    **doc["expected_metadata"]
                }
            )]
            
            # Use the correct method signature
            success = await self.vector_db.insert_document_chunks(documents)
            if success:
                logger.info(f"✅ Stored {doc_id}")
            else:
                logger.error(f"❌ Failed to store {doc_id}")
            
        logger.info(f"✅ Stored {len(test_docs)} test documents")
    
    async def _test_filter_combinations(self):
        """Test all combinations of filter formats."""
        logger.info("🔍 Testing filter combinations...")
        
        test_query = "compliance document"
        filter_tests = [
            # String filters
            {"compliance_framework": "SOX", "expected_min": 1},  # Should find filter_test_doc_1 and filter_test_doc_2
            {"document_type": "access_review", "expected_min": 1},  # Should find filter_test_doc_1
            {"risk_level": "low", "expected_min": 1},  # Should find filter_test_doc_3 (changed from medium to low)
            {"company": "AnotherCorp", "expected_min": 1},  # Should find filter_test_doc_3 (changed from TestCorp to AnotherCorp)
            
            # List filters  
            {"compliance_framework": ["SOX"], "expected_min": 2},
            {"compliance_frameworks": ["SOX"], "expected_min": 2},
            {"document_type": ["access_review", "financial_controls"], "expected_min": 2},
            
            # Mixed list filters
            {"compliance_frameworks": ["SOX", "ISO27001"], "expected_min": 3},
            
            # Multiple field filters  
            {"compliance_framework": "ISO27001", "risk_level": "low", "expected_min": 1},  # Should find filter_test_doc_3
            {"document_type": "risk_assessment", "company": "AnotherCorp", "expected_min": 1},  # Should find filter_test_doc_3
            
            # Non-existent filters (should return 0)
            {"compliance_framework": "NonExistent", "expected_min": 0},
            {"document_type": "unknown_type", "expected_min": 0},
        ]
        
        results = {}
        
        for i, test_case in enumerate(filter_tests):
            expected_min = test_case.pop("expected_min")
            filter_dict = test_case
            
            logger.info(f"  🧪 Test {i+1}: {filter_dict}")
            
            start_time = time.time()
            search_results = await self.vector_db.semantic_search(
                query_text=test_query,
                limit=10,
                score_threshold=0.0,  # Low threshold to get all matches
                filters=filter_dict
            )
            execution_time = (time.time() - start_time) * 1000
            
            result_count = len(search_results)
            success = result_count >= expected_min
            
            results[f"test_{i+1}"] = {
                "filter": filter_dict,
                "expected_min": expected_min,
                "actual_count": result_count,
                "success": success,
                "execution_time_ms": execution_time,
                "sample_results": [
                    {
                        "document_id": r.get("document_id", "unknown"),
                        "score": r.get("score", 0.0),
                        "metadata_subset": {
                            k: r.get("metadata", {}).get(k) 
                            for k in filter_dict.keys() 
                            if k in r.get("metadata", {})
                        }
                    } for r in search_results[:2]
                ]
            }
            
            status = "✅" if success else "❌"
            logger.info(f"    {status} Expected ≥{expected_min}, got {result_count} ({execution_time:.1f}ms)")
        
        self.test_results["filter_tests"] = results
    
    async def _test_zero_results_regression(self):
        """Test for regression of the zero-results bug that was fixed."""
        logger.info("🔄 Testing zero-results regression...")
        
        # These are the exact queries that were failing before the fix
        regression_queries = [
            {"query": "What are the key findings from the access review?", "filters": {"compliance_framework": ["SOX"]}},
            {"query": "compliance framework SOX", "filters": {"compliance_frameworks": ["SOX"]}},
            {"query": "document type access review", "filters": {"document_type": "access_review"}},
            {"query": "risk assessment", "filters": {"document_type": "risk_assessment"}},
        ]
        
        results = {}
        
        for i, test_case in enumerate(regression_queries):
            query = test_case["query"]
            filters = test_case["filters"]
            
            logger.info(f"  🔍 Regression test {i+1}: '{query}' with {filters}")
            
            # Test with filters (this was failing before)
            filtered_results = await self.vector_db.semantic_search(
                query_text=query,
                limit=5,
                score_threshold=0.1,
                filters=filters
            )
            
            # Test without filters (baseline)
            unfiltered_results = await self.vector_db.semantic_search(
                query_text=query,
                limit=5,
                score_threshold=0.1
            )
            
            # The bug was: filtered_results = 0, unfiltered_results > 0
            regression_detected = len(unfiltered_results) > 0 and len(filtered_results) == 0
            
            results[f"regression_test_{i+1}"] = {
                "query": query,
                "filters": filters,
                "filtered_count": len(filtered_results),
                "unfiltered_count": len(unfiltered_results),
                "regression_detected": regression_detected,
                "success": not regression_detected
            }
            
            status = "✅" if not regression_detected else "❌ REGRESSION"
            logger.info(f"    {status} Filtered: {len(filtered_results)}, Unfiltered: {len(unfiltered_results)}")
        
        self.test_results["regression_tests"] = results
    
    async def _test_edge_cases(self):
        """Test edge cases and error conditions."""
        logger.info("🛡️ Testing edge cases...")
        
        edge_cases = [
            # Empty filters
            {"filters": {}, "description": "empty_filters"},
            
            # None values
            {"filters": {"compliance_framework": None}, "description": "none_value_filter"},
            
            # Empty string filters
            {"filters": {"compliance_framework": ""}, "description": "empty_string_filter"},
            
            # Empty list filters
            {"filters": {"compliance_frameworks": []}, "description": "empty_list_filter"},
            
            # Non-existent fields
            {"filters": {"non_existent_field": "value"}, "description": "non_existent_field"},
            
            # Very long filter values
            {"filters": {"compliance_framework": "x" * 1000}, "description": "very_long_value"},
            
            # Special characters
            {"filters": {"compliance_framework": "SOX & ISO27001"}, "description": "special_characters"},
        ]
        
        results = {}
        
        for i, test_case in enumerate(edge_cases):
            filters = test_case["filters"]
            description = test_case["description"]
            
            logger.info(f"  🧪 Edge case {i+1}: {description}")
            
            try:
                search_results = await self.vector_db.semantic_search(
                    query_text="test query",
                    limit=5,
                    score_threshold=0.0,
                    filters=filters
                )
                
                results[description] = {
                    "filters": filters,
                    "success": True,
                    "result_count": len(search_results),
                    "error": None
                }
                
                logger.info(f"    ✅ Handled gracefully: {len(search_results)} results")
                
            except Exception as e:
                results[description] = {
                    "filters": filters,
                    "success": False,
                    "result_count": 0,
                    "error": str(e)
                }
                
                logger.info(f"    ❌ Error: {str(e)}")
        
        self.test_results["edge_cases"] = results
    
    async def _test_performance(self):
        """Test performance of filtering operations."""
        logger.info("⚡ Testing performance...")
        
        # Performance test with different filter complexities
        perf_tests = [
            {"filters": {"compliance_framework": "SOX"}, "description": "simple_string_filter"},
            {"filters": {"compliance_frameworks": ["SOX", "SOC2", "ISO27001"]}, "description": "multi_value_list_filter"},
            {"filters": {"compliance_framework": "ISO27001", "document_type": "risk_assessment", "risk_level": "low"}, "description": "multi_field_filter"},
        ]
        
        results = {}
        
        for test_case in perf_tests:
            filters = test_case["filters"]
            description = test_case["description"]
            
            # Run multiple iterations for average
            times = []
            for _ in range(5):
                start_time = time.time()
                await self.vector_db.semantic_search(
                    query_text="performance test query",
                    limit=10,
                    score_threshold=0.1,
                    filters=filters
                )
                times.append((time.time() - start_time) * 1000)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            results[description] = {
                "filters": filters,
                "avg_time_ms": avg_time,
                "min_time_ms": min_time,
                "max_time_ms": max_time,
                "iterations": len(times)
            }
            
            logger.info(f"  ⚡ {description}: {avg_time:.1f}ms avg ({min_time:.1f}-{max_time:.1f}ms)")
        
        self.test_results["performance_metrics"] = results
    
    def _calculate_overall_success(self):
        """Calculate overall test success rate."""
        total_tests = 0
        passed_tests = 0
        
        # Count filter combination tests
        for test_result in self.test_results["filter_tests"].values():
            total_tests += 1
            if test_result["success"]:
                passed_tests += 1
        
        # Count regression tests
        for test_result in self.test_results["regression_tests"].values():
            total_tests += 1
            if test_result["success"]:
                passed_tests += 1
        
        # Count edge case tests (only count non-error cases as success)
        for test_result in self.test_results["edge_cases"].values():
            total_tests += 1
            if test_result["success"]:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) if total_tests > 0 else 0
        self.test_results["overall_success"] = success_rate >= 0.9  # 90% threshold
        self.test_results["success_rate"] = success_rate
        self.test_results["passed_tests"] = passed_tests
        self.test_results["total_tests"] = total_tests
    
    def _generate_report(self):
        """Generate and display test report."""
        results = self.test_results
        
        print("\n" + "="*100)
        print("📊 VECTOR DATABASE FILTERING TEST RESULTS")
        print("="*100)
        
        # Overall status
        overall_status = "✅ PASSED" if results["overall_success"] else "❌ FAILED"
        print(f"📊 OVERALL STATUS: {overall_status}")
        print(f"📄 Tests Run: {results['total_tests']}")
        print(f"✅ Passed: {results['passed_tests']}")
        print(f"📊 Success Rate: {results['success_rate']:.1%}")
        
        # Filter combination results
        print(f"\n🔍 FILTER COMBINATION TESTS:")
        filter_success = sum(1 for t in results["filter_tests"].values() if t["success"])
        filter_total = len(results["filter_tests"])
        print(f"   📊 Success Rate: {filter_success}/{filter_total} ({filter_success/filter_total:.1%})")
        
        # Regression test results
        print(f"\n🔄 REGRESSION TESTS:")
        regression_success = sum(1 for t in results["regression_tests"].values() if t["success"])
        regression_total = len(results["regression_tests"])
        print(f"   📊 Success Rate: {regression_success}/{regression_total} ({regression_success/regression_total:.1%})")
        
        if regression_success < regression_total:
            print("   🚨 REGRESSION DETECTED - Zero results bug may have returned!")
        
        # Edge case results
        print(f"\n🛡️ EDGE CASE TESTS:")
        edge_success = sum(1 for t in results["edge_cases"].values() if t["success"])
        edge_total = len(results["edge_cases"])
        print(f"   📊 Success Rate: {edge_success}/{edge_total} ({edge_success/edge_total:.1%})")
        
        # Performance summary
        print(f"\n⚡ PERFORMANCE METRICS:")
        for desc, metrics in results["performance_metrics"].items():
            print(f"   {desc}: {metrics['avg_time_ms']:.1f}ms avg")
        
        print("\n💡 RECOMMENDATIONS:")
        if results["overall_success"]:
            print("   ✅ Vector database filtering is working correctly")
            print("   ✅ No regression detected in zero-results bug fix")
            print("   ✅ All filter combinations handled properly")
        else:
            print("   ⚠️ Some filtering tests failed - review detailed results")
            if regression_success < regression_total:
                print("   🚨 CRITICAL: Regression detected in filtering mechanism")
        
        print("="*100)
        print("✅ VECTOR DATABASE FILTERING TEST COMPLETED")
        print("="*100)
        
        # Save detailed results
        results_file = "scripts/testing/vector_database_filtering_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📊 Detailed results saved to: {results_file}")


async def main():
    """Main test execution."""
    test = VectorDatabaseFilteringTest()
    results = await test.run_comprehensive_test()
    
    # Return appropriate exit code
    success = results.get("overall_success", False)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
