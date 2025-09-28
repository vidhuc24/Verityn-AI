#!/usr/bin/env python3
"""
Context Retrieval Agent Test for Verityn AI

This test validates the ContextRetrievalAgent's ability to:
1. Select appropriate retrieval strategies based on query complexity
2. Execute advanced retrieval techniques (hybrid, query expansion, multi-hop, ensemble)
3. Filter and rank results effectively
4. Handle different compliance frameworks and document types
5. Optimize retrieval performance

Follows Verityn AI testing standards:
- Uses real audit documents from sox_test_documents/
- Tests all advanced retrieval techniques
- Validates retrieval strategy selection logic
- Measures retrieval performance and relevance
"""

import asyncio
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import logging
import statistics

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.agents.specialized_agents import ContextRetrievalAgent
from backend.app.agents.base_agent import AgentContext
from backend.app.services.advanced_retrieval import advanced_retrieval_service
from backend.app.services.vector_database import vector_db_service
from backend.app.services.document_processor import EnhancedDocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ContextRetrievalAgentTest:
    """Comprehensive test suite for ContextRetrievalAgent."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.agent = ContextRetrievalAgent(verbose=True)
        self.document_processor = EnhancedDocumentProcessor()
        
        # Test scenarios with expected retrieval strategies
        self.test_scenarios = {
            "hybrid_queries": {
                "queries": [
                    "What access review findings were identified?",
                    "Show me financial reconciliation issues"
                ],
                "expected_strategy": "hybrid",
                "expected_complexity": ["basic", "intermediate"],
                "analysis_context": {
                    "intent": "information_retrieval",
                    "complexity": "intermediate",
                    "compliance_frameworks": ["SOX"],
                    "search_keywords": ["access", "review", "findings"]
                }
            },
            
            "query_expansion_queries": {
                "queries": [
                    "What SOX compliance issues were found?",
                    "Are there material weaknesses in the controls?"
                ],
                "expected_strategy": "query_expansion",
                "expected_complexity": ["intermediate", "advanced"],
                "analysis_context": {
                    "intent": "compliance_check",
                    "complexity": "intermediate",
                    "compliance_frameworks": ["SOX"],
                    "search_keywords": ["SOX", "compliance", "material", "weakness"]
                }
            },
            
            "multi_hop_queries": {
                "queries": [
                    "Compare the effectiveness of access controls across all departments",
                    "What is the relationship between IT controls and financial reporting?",
                    "How do risk assessments connect to control deficiencies?",
                    "Analyze the connection between user access and segregation of duties"
                ],
                "expected_strategy": "multi_hop",
                "expected_complexity": ["advanced"],
                "analysis_context": {
                    "intent": "comparison",
                    "complexity": "advanced",
                    "compliance_frameworks": ["SOX"],
                    "search_keywords": ["compare", "relationship", "connection"]
                }
            },
            
            "ensemble_queries": {
                "queries": [
                    "What are the overall audit findings?",
                    "Summarize the control testing results",
                    "What issues were identified during the review?",
                    "Provide an overview of the compliance assessment"
                ],
                "expected_strategy": "ensemble",
                "expected_complexity": ["intermediate"],
                "analysis_context": {
                    "intent": "document_analysis",
                    "complexity": "intermediate",
                    "compliance_frameworks": ["SOX"],
                    "search_keywords": ["audit", "findings", "control", "testing"]
                }
            },
            
            "semantic_fallback": {
                "queries": [
                    "simple query",
                    "basic information",
                    "show data",
                    "what happened"
                ],
                "expected_strategy": "semantic",
                "expected_complexity": ["basic"],
                "analysis_context": {
                    "intent": "information_retrieval",
                    "complexity": "basic",
                    "compliance_frameworks": ["General"],
                    "search_keywords": ["simple", "query"]
                }
            }
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            "max_retrieval_time_ms": 3000,  # 3 seconds max
            "min_results_returned": 3,      # At least 3 relevant results
            "min_relevance_score": 0.3,     # Minimum relevance threshold
            "max_memory_usage_mb": 200      # Memory usage limit
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive context retrieval tests."""
        logger.info("🚀 Starting Context Retrieval Agent Test")
        logger.info("📊 Testing advanced retrieval strategies and performance")
        
        # Initialize vector database and load test documents
        await self._setup_test_environment()
        
        results = {
            "test_timestamp": time.time(),
            "agent_info": {
                "agent_type": str(self.agent.agent_type),
                "model": self.agent.llm_model,
                "temperature": self.agent.temperature
            },
            "test_scenarios": {},
            "retrieval_strategy_accuracy": {},
            "performance_metrics": {},
            "retrieval_technique_comparison": {},
            "detailed_results": []
        }
        
        # Test each scenario category
        total_queries = 0
        successful_retrievals = 0
        retrieval_times = []
        strategy_accuracy = {}
        
        for scenario_name, scenario_data in self.test_scenarios.items():
            logger.info(f"\n📋 Testing scenario: {scenario_name}")
            scenario_results = await self._test_retrieval_scenario(scenario_name, scenario_data)
            results["test_scenarios"][scenario_name] = scenario_results
            
            # Update overall metrics
            total_queries += len(scenario_data["queries"])
            successful_retrievals += scenario_results["successful_retrievals"]
            retrieval_times.extend(scenario_results["retrieval_times"])
            
            # Track strategy accuracy
            expected_strategy = scenario_data["expected_strategy"]
            correct_strategies = scenario_results["correct_strategy_selections"]
            strategy_accuracy[expected_strategy] = {
                "expected": len(scenario_data["queries"]),
                "correct": correct_strategies,
                "accuracy": correct_strategies / len(scenario_data["queries"]) if scenario_data["queries"] else 0
            }
            
            results["detailed_results"].extend(scenario_results["query_details"])
        
        # Calculate performance metrics
        results["performance_metrics"] = {
            "total_queries": total_queries,
            "success_rate": successful_retrievals / total_queries if total_queries > 0 else 0,
            "avg_retrieval_time_ms": statistics.mean(retrieval_times) if retrieval_times else 0,
            "max_retrieval_time_ms": max(retrieval_times) if retrieval_times else 0,
            "min_retrieval_time_ms": min(retrieval_times) if retrieval_times else 0
        }
        
        # Strategy accuracy analysis
        results["retrieval_strategy_accuracy"] = strategy_accuracy
        
        # Compare retrieval techniques
        results["retrieval_technique_comparison"] = await self._compare_retrieval_techniques()
        
        # Print comprehensive results
        self._print_results(results)
        
        return results
    
    async def _setup_test_environment(self) -> None:
        """Set up the test environment with documents and retrievers."""
        logger.info("🔧 Setting up test environment...")
        
        try:
            # Initialize vector database
            await vector_db_service.initialize_collection()
            logger.info("✅ Vector database initialized")
            
            # Load and process test documents
            test_documents = await self._load_test_documents()
            if test_documents:
                await self._process_test_documents(test_documents)
                logger.info(f"✅ Processed {len(test_documents)} test documents")
            
            # Initialize advanced retrieval service
            await advanced_retrieval_service.initialize_retrievers()
            logger.info("✅ Advanced retrieval service initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Test environment setup had issues: {str(e)}")
            logger.info("Continuing with limited testing capabilities...")
    
    async def _load_test_documents(self) -> Dict[str, Dict[str, Any]]:
        """Load test documents for retrieval testing."""
        test_docs = {}
        
        # Load SOX test documents (TXT files for reliability)
        sox_files = [
            "data/sox_test_documents/sox_access_review_2024.txt",
            "data/sox_test_documents/sox_internal_controls_2024.txt",
            "data/sox_test_documents/sox_financial_controls_2024.txt",
            "data/sox_test_documents/sox_risk_assessment_2024.txt"
        ]
        
        for file_path in sox_files:
            try:
                if Path(file_path).exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if content and content.strip():
                        doc_name = Path(file_path).stem
                        test_docs[doc_name] = {
                            'path': file_path,
                            'content': content,
                            'type': 'txt',
                            'document_type': self._infer_document_type(file_path)
                        }
                        logger.info(f"✅ Loaded {doc_name} ({len(content)} chars)")
                
            except Exception as e:
                logger.error(f"❌ Failed to load {file_path}: {str(e)}")
        
        return test_docs
    
    def _infer_document_type(self, file_path: str) -> str:
        """Infer document type from file path."""
        path_lower = file_path.lower()
        if "access" in path_lower:
            return "access_review"
        elif "financial" in path_lower:
            return "financial_controls"
        elif "internal" in path_lower:
            return "internal_controls"
        elif "risk" in path_lower:
            return "risk_assessment"
        else:
            return "audit_report"
    
    async def _process_test_documents(self, test_documents: Dict[str, Dict[str, Any]]) -> None:
        """Process test documents into vector database."""
        from fastapi import UploadFile
        from io import BytesIO
        
        processed_count = 0
        
        for doc_name, doc_info in test_documents.items():
            try:
                logger.info(f"🔄 Processing {doc_name}...")
                
                # Read file content
                with open(doc_info['path'], 'rb') as f:
                    file_content = f.read()
                
                # Create mock UploadFile
                mock_file = UploadFile(
                    file=BytesIO(file_content),
                    filename=Path(doc_info['path']).name
                )
                
                # Process document
                result = await self.document_processor.process_document(
                    file=mock_file,
                    document_id=f"test_retrieval_{doc_name}",
                    description=f"Test document for retrieval: {doc_name}"
                )
                
                # Store in vector database
                chunks = result.get('chunks', [])
                metadata = result.get('metadata', {})
                metadata.update({
                    'test_document': True,
                    'document_type': doc_info['document_type']
                })
                
                if chunks:
                    success = await vector_db_service.insert_document_chunks(
                        document_id=f"test_retrieval_{doc_name}",
                        chunks=chunks,
                        metadata=metadata
                    )
                    
                    if success:
                        processed_count += 1
                        logger.info(f"✅ Stored {doc_name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"❌ Failed to process {doc_name}: {str(e)}")
        
        logger.info(f"📊 Document processing complete: {processed_count}/{len(test_documents)} documents")
    
    async def _test_retrieval_scenario(self, scenario_name: str, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific retrieval scenario."""
        scenario_results = {
            "scenario": scenario_name,
            "total_queries": len(scenario_data["queries"]),
            "successful_retrievals": 0,
            "failed_retrievals": 0,
            "correct_strategy_selections": 0,
            "retrieval_times": [],
            "relevance_scores": [],
            "query_details": []
        }
        
        expected_strategy = scenario_data["expected_strategy"]
        analysis_context = scenario_data["analysis_context"]
        
        for i, query in enumerate(scenario_data["queries"], 1):
            logger.info(f"  🔍 Testing query {i}/{len(scenario_data['queries'])}: '{query[:60]}...'")
            
            try:
                # Create agent context with analysis data
                from datetime import datetime
                context = AgentContext(
                    inputs={
                        "question": query,
                        "analysis": analysis_context,
                        "conversation_id": f"test_{scenario_name}_{i}"
                    },
                    agent_type=self.agent.agent_type,
                    timestamp=datetime.now(),
                    conversation_id=f"test_{scenario_name}_{i}",
                    workflow_id=f"test_workflow_{scenario_name}_{i}"
                )
                
                # Measure retrieval time
                start_time = time.time()
                retrieval_result = await self.agent._execute_logic(context)
                retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # Validate retrieval result
                is_successful, validation_details = self._validate_retrieval_result(retrieval_result)
                
                # Check strategy selection accuracy
                selected_strategy = retrieval_result.get("retrieval_method", "unknown")
                strategy_correct = selected_strategy == expected_strategy
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(retrieval_result, query)
                
                query_detail = {
                    "query": query,
                    "scenario": scenario_name,
                    "retrieval_time_ms": retrieval_time,
                    "success": is_successful,
                    "expected_strategy": expected_strategy,
                    "selected_strategy": selected_strategy,
                    "strategy_correct": strategy_correct,
                    "relevance_score": relevance_score,
                    "results_count": len(retrieval_result.get("context", [])),
                    "validation_details": validation_details,
                    "retrieval_result": retrieval_result
                }
                
                if is_successful:
                    scenario_results["successful_retrievals"] += 1
                    scenario_results["retrieval_times"].append(retrieval_time)
                    scenario_results["relevance_scores"].append(relevance_score)
                    
                    logger.info(f"    ✅ Retrieved {query_detail['results_count']} results in {retrieval_time:.1f}ms")
                    logger.info(f"    🎯 Strategy: {selected_strategy} ({'✅' if strategy_correct else '❌'})")
                    logger.info(f"    📊 Relevance: {relevance_score:.1%}")
                else:
                    scenario_results["failed_retrievals"] += 1
                    logger.warning(f"    ❌ Retrieval failed: {validation_details}")
                
                if strategy_correct:
                    scenario_results["correct_strategy_selections"] += 1
                
                scenario_results["query_details"].append(query_detail)
                
            except Exception as e:
                logger.error(f"    ❌ Exception during retrieval: {str(e)}")
                scenario_results["failed_retrievals"] += 1
                scenario_results["query_details"].append({
                    "query": query,
                    "scenario": scenario_name,
                    "success": False,
                    "error": str(e)
                })
        
        return scenario_results
    
    def _validate_retrieval_result(self, result: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Validate the structure and quality of retrieval results."""
        validation = {
            "has_context": False,
            "has_method": False,
            "sufficient_results": False,
            "performance_acceptable": False
        }
        
        # Check if context exists
        context = result.get("context", [])
        validation["has_context"] = len(context) > 0
        
        # Check if retrieval method is specified
        validation["has_method"] = "retrieval_method" in result
        
        # Check if we have sufficient results
        validation["sufficient_results"] = len(context) >= self.performance_thresholds["min_results_returned"]
        
        # Check performance (if timing data available)
        retrieval_time = result.get("retrieval_time_ms", 0)
        validation["performance_acceptable"] = retrieval_time <= self.performance_thresholds["max_retrieval_time_ms"]
        
        # Overall validation
        is_valid = (
            validation["has_context"] and
            validation["has_method"] and
            validation["sufficient_results"]
        )
        
        return is_valid, validation
    
    def _calculate_relevance_score(self, result: Dict[str, Any], query: str) -> float:
        """Calculate relevance score for retrieval results."""
        context = result.get("context", [])
        if not context:
            return 0.0
        
        query_terms = set(query.lower().split())
        relevance_scores = []
        
        for item in context:
            # Get chunk text from different possible field names
            chunk_text = (
                item.get("chunk_text", "") or
                item.get("content", "") or
                item.get("text", "") or
                str(item)
            ).lower()
            
            if chunk_text:
                chunk_terms = set(chunk_text.split())
                
                # Calculate term overlap
                common_terms = query_terms.intersection(chunk_terms)
                term_overlap = len(common_terms) / len(query_terms) if query_terms else 0
                
                # Boost for audit-specific terms
                audit_terms = {'control', 'compliance', 'audit', 'risk', 'sox', 'finding', 'deficiency'}
                audit_overlap = len(query_terms.intersection(audit_terms))
                chunk_audit_overlap = len(chunk_terms.intersection(audit_terms))
                
                audit_boost = 0.2 if (audit_overlap > 0 and chunk_audit_overlap > 0) else 0
                
                # Use score from result if available
                result_score = item.get("score", 0.5)
                
                # Combined relevance score
                combined_score = (
                    0.4 * term_overlap +
                    0.3 * min(result_score, 1.0) +
                    0.3 * audit_boost
                )
                
                relevance_scores.append(combined_score)
        
        return statistics.mean(relevance_scores) if relevance_scores else 0.0
    
    async def _compare_retrieval_techniques(self) -> Dict[str, Any]:
        """Compare different retrieval techniques performance."""
        logger.info("🔍 Comparing retrieval techniques...")
        
        test_queries = [
            "What SOX compliance issues were found?",
            "What access control deficiencies were identified?",
            "Show me the risk assessment findings"
        ]
        
        comparison_results = {
            "test_queries": test_queries,
            "technique_performance": {},
            "best_technique": None,
            "performance_summary": {}
        }
        
        techniques = [
            ("hybrid", "Hybrid Search"),
            ("query_expansion", "Query Expansion"),
            ("multi_hop", "Multi-Hop Retrieval"),
            ("ensemble", "Ensemble Retrieval"),
            ("semantic", "Semantic Search")
        ]
        
        technique_scores = {}
        
        for technique_id, technique_name in techniques:
            logger.info(f"  🧪 Testing {technique_name}...")
            
            technique_results = {
                "technique_name": technique_name,
                "avg_results_count": 0,
                "avg_relevance_score": 0,
                "avg_retrieval_time_ms": 0,
                "success_rate": 0,
                "query_results": []
            }
            
            successful_queries = 0
            total_results = []
            total_relevance = []
            total_times = []
            
            for query in test_queries:
                try:
                    # Test the specific technique
                    start_time = time.time()
                    
                    if technique_id == "hybrid":
                        results = await advanced_retrieval_service.hybrid_search(query, limit=5)
                    elif technique_id == "query_expansion":
                        results = await advanced_retrieval_service.query_expansion_search(query, limit=5)
                    elif technique_id == "multi_hop":
                        results = await advanced_retrieval_service.multi_hop_retrieval(query, limit=5)
                    elif technique_id == "ensemble":
                        results = await advanced_retrieval_service.ensemble_retrieval(query, limit=5)
                    else:  # semantic fallback
                        results = await vector_db_service.semantic_search(query, limit=5)
                    
                    retrieval_time = (time.time() - start_time) * 1000
                    
                    # Calculate metrics
                    results_count = len(results)
                    relevance_score = self._calculate_relevance_score({"context": results}, query)
                    
                    technique_results["query_results"].append({
                        "query": query,
                        "results_count": results_count,
                        "relevance_score": relevance_score,
                        "retrieval_time_ms": retrieval_time
                    })
                    
                    total_results.append(results_count)
                    total_relevance.append(relevance_score)
                    total_times.append(retrieval_time)
                    successful_queries += 1
                    
                except Exception as e:
                    logger.warning(f"    ⚠️ {technique_name} failed for query '{query}': {str(e)}")
                    technique_results["query_results"].append({
                        "query": query,
                        "error": str(e)
                    })
            
            # Calculate averages
            if total_results:
                technique_results["avg_results_count"] = statistics.mean(total_results)
                technique_results["avg_relevance_score"] = statistics.mean(total_relevance)
                technique_results["avg_retrieval_time_ms"] = statistics.mean(total_times)
                technique_results["success_rate"] = successful_queries / len(test_queries)
                
                # Overall technique score (weighted combination)
                technique_score = (
                    0.4 * technique_results["avg_relevance_score"] +
                    0.3 * technique_results["success_rate"] +
                    0.2 * min(1.0, technique_results["avg_results_count"] / 5) +
                    0.1 * max(0, 1.0 - (technique_results["avg_retrieval_time_ms"] / 3000))  # Penalty for slow retrieval
                )
                
                technique_scores[technique_id] = technique_score
                technique_results["overall_score"] = technique_score
            
            comparison_results["technique_performance"][technique_id] = technique_results
        
        # Determine best technique
        if technique_scores:
            best_technique_id = max(technique_scores, key=technique_scores.get)
            comparison_results["best_technique"] = {
                "technique_id": best_technique_id,
                "technique_name": dict(techniques)[best_technique_id],
                "score": technique_scores[best_technique_id]
            }
        
        return comparison_results
    
    def _print_results(self, results: Dict[str, Any]) -> None:
        """Print comprehensive test results."""
        print("\n" + "="*100)
        print("📊 CONTEXT RETRIEVAL AGENT TEST RESULTS")
        print("="*100)
        
        # Agent info
        agent_info = results["agent_info"]
        print(f"🤖 Agent: {agent_info['agent_type']}")
        print(f"🧠 Model: {agent_info['model']} (temp: {agent_info['temperature']})")
        
        # Performance metrics
        metrics = results["performance_metrics"]
        print(f"\n📊 PERFORMANCE METRICS:")
        print(f"   📄 Queries Tested: {metrics['total_queries']}")
        print(f"   ✅ Success Rate: {metrics['success_rate']:.1%}")
        print(f"   ⏱️ Avg Retrieval Time: {metrics['avg_retrieval_time_ms']:.1f}ms")
        print(f"   🚀 Fastest Retrieval: {metrics['min_retrieval_time_ms']:.1f}ms")
        print(f"   🐌 Slowest Retrieval: {metrics['max_retrieval_time_ms']:.1f}ms")
        
        # Strategy accuracy
        strategy_accuracy = results["retrieval_strategy_accuracy"]
        print(f"\n🎯 RETRIEVAL STRATEGY ACCURACY:")
        overall_strategy_accuracy = []
        
        for strategy, data in strategy_accuracy.items():
            accuracy = data["accuracy"]
            overall_strategy_accuracy.append(accuracy)
            status = "✅" if accuracy > 0.8 else "🟡" if accuracy > 0.6 else "❌"
            print(f"   {status} {strategy.upper()}: {accuracy:.1%} ({data['correct']}/{data['expected']})")
        
        if overall_strategy_accuracy:
            avg_strategy_accuracy = statistics.mean(overall_strategy_accuracy)
            print(f"   📊 Overall Strategy Accuracy: {avg_strategy_accuracy:.1%}")
        
        # Technique comparison
        technique_comparison = results["retrieval_technique_comparison"]
        if "best_technique" in technique_comparison and technique_comparison["best_technique"]:
            best_technique = technique_comparison["best_technique"]
            print(f"\n🏆 BEST RETRIEVAL TECHNIQUE:")
            print(f"   🥇 Winner: {best_technique['technique_name']} (score: {best_technique['score']:.3f})")
            
            print(f"\n📊 TECHNIQUE PERFORMANCE COMPARISON:")
            for technique_id, data in technique_comparison["technique_performance"].items():
                if "overall_score" in data:
                    score = data["overall_score"]
                    status = "🥇" if technique_id == best_technique["technique_id"] else "🥈" if score > 0.7 else "🥉"
                    print(f"   {status} {data['technique_name']}: {score:.3f}")
                    print(f"      • Success Rate: {data['success_rate']:.1%}")
                    print(f"      • Avg Relevance: {data['avg_relevance_score']:.1%}")
                    print(f"      • Avg Results: {data['avg_results_count']:.1f}")
                    print(f"      • Avg Time: {data['avg_retrieval_time_ms']:.1f}ms")
        
        # Scenario breakdown
        print(f"\n📊 DETAILED RESULTS BY SCENARIO:")
        print("-" * 100)
        
        for scenario, data in results["test_scenarios"].items():
            success_rate = data["successful_retrievals"] / data["total_queries"] if data["total_queries"] > 0 else 0
            strategy_accuracy_rate = data["correct_strategy_selections"] / data["total_queries"] if data["total_queries"] > 0 else 0
            
            status = "✅" if success_rate > 0.8 else "🟡" if success_rate > 0.6 else "❌"
            
            print(f"\n{status} {scenario.upper().replace('_', ' ')}")
            print(f"   📄 Queries: {data['total_queries']}")
            print(f"   ✅ Successful: {data['successful_retrievals']} ({success_rate:.1%})")
            print(f"   🎯 Strategy Accuracy: {strategy_accuracy_rate:.1%}")
            
            if data["retrieval_times"]:
                avg_time = statistics.mean(data["retrieval_times"])
                print(f"   ⏱️ Avg Time: {avg_time:.1f}ms")
            
            if data["relevance_scores"]:
                avg_relevance = statistics.mean(data["relevance_scores"])
                print(f"   📊 Avg Relevance: {avg_relevance:.1%}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        overall_success = metrics["success_rate"]
        avg_strategy_accuracy = statistics.mean(overall_strategy_accuracy) if overall_strategy_accuracy else 0
        
        if overall_success > 0.9 and avg_strategy_accuracy > 0.8:
            print("   🎉 Excellent performance! Context retrieval is working optimally.")
        elif overall_success > 0.7 and avg_strategy_accuracy > 0.6:
            print("   ✅ Good performance with areas for improvement:")
            if avg_strategy_accuracy < 0.8:
                print("      - Fine-tune strategy selection logic")
                print("      - Improve query analysis integration")
            if metrics["avg_retrieval_time_ms"] > 2000:
                print("      - Optimize retrieval performance")
                print("      - Consider caching for frequently accessed content")
        else:
            print("   ⚠️ Performance needs significant improvement:")
            print("      - Review and enhance retrieval strategy logic")
            print("      - Improve advanced retrieval service integration")
            print("      - Add more robust error handling")
            print("      - Optimize vector database queries")
        
        if technique_comparison.get("best_technique"):
            best = technique_comparison["best_technique"]
            print(f"   💡 Consider prioritizing {best['technique_name']} for better results")
        
        print("="*100)
        print("✅ CONTEXT RETRIEVAL AGENT TEST COMPLETED")
        print("="*100)


async def main():
    """Run the context retrieval agent test."""
    test = ContextRetrievalAgentTest()
    
    # Run comprehensive test
    results = await test.run_comprehensive_test()
    
    # Save detailed results
    output_file = Path(__file__).parent / "context_retrieval_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📊 Detailed results saved to: {output_file}")
    
    # Return appropriate exit code based on success rate
    success_rate = results["performance_metrics"]["success_rate"]
    strategy_accuracy = results["retrieval_strategy_accuracy"]
    avg_strategy_accuracy = statistics.mean([data["accuracy"] for data in strategy_accuracy.values()]) if strategy_accuracy else 0
    
    if success_rate > 0.8 and avg_strategy_accuracy > 0.7:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs improvement


if __name__ == "__main__":
    asyncio.run(main())
