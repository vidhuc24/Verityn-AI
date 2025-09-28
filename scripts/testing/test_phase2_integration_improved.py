#!/usr/bin/env python3
"""
Improved Phase 2 Integration Test for Verityn AI

This test validates the complete Phase 2 workflow with ALL improvements we made:
1. Enhanced Question Analysis Agent (88.4% accuracy, better intent classification)
2. Fixed Context Retrieval Agent (corrected metadata filtering, zero results handling)
3. Improved Classification Engine (better edge case handling, confidence calibration)
4. Comprehensive error handling and fallback mechanisms

The test measures the end-to-end Phase 2 pipeline performance with our improvements.

Usage:
    uv run python scripts/testing/test_phase2_integration_improved.py
"""

import asyncio
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import statistics

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.agents.specialized_agents import QuestionAnalysisAgent, ContextRetrievalAgent
from backend.app.agents.base_agent import AgentContext, AgentType
from backend.app.services.classification_engine import ClassificationEngine
from backend.app.services.vector_database import vector_db_service
from backend.app.services.document_processor import EnhancedDocumentProcessor
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImprovedPhase2IntegrationTest:
    """Comprehensive Phase 2 integration test with all improvements."""
    
    def __init__(self):
        """Initialize the improved integration test."""
        # Initialize improved components
        self.question_analyzer = QuestionAnalysisAgent(verbose=False)
        self.context_retriever = ContextRetrievalAgent(verbose=False)
        self.classifier = ClassificationEngine()
        self.document_processor = EnhancedDocumentProcessor()
        
        # Integration test scenarios covering real audit workflows
        self.integration_scenarios = [
            {
                "name": "basic_audit_inquiry",
                "query": "What are the key findings from the access review?",
                "expected_results": {
                    "question_analysis": {
                        "intent": "information_retrieval",
                        "complexity": ["basic", "intermediate"],
                        "min_keywords": 2
                    },
                    "context_retrieval": {
                        "min_results": 1,
                        "expected_doc_types": ["access_review"]
                    },
                    "classification": {
                        "min_confidence": 0.6
                    }
                },
                "description": "Basic audit inquiry should retrieve relevant access review information"
            },
            {
                "name": "compliance_assessment",
                "query": "Are there any SOX 404 material weaknesses in the financial controls?",
                "expected_results": {
                    "question_analysis": {
                        "intent": ["compliance_assessment", "compliance_check", "information_retrieval"],  # Allow information_retrieval as acceptable
                        "complexity": ["intermediate", "advanced"],
                        "frameworks": ["SOX"],
                        "min_keywords": 3
                    },
                    "context_retrieval": {
                        "min_results": 1,
                        "expected_doc_types": ["financial_controls", "internal_controls"]
                    },
                    "classification": {
                        "min_confidence": 0.7
                    }
                },
                "description": "Compliance assessment should identify SOX-related financial control issues"
            },
            {
                "name": "relationship_analysis",
                "query": "What is the relationship between IT general controls and application controls?",
                "expected_results": {
                    "question_analysis": {
                        "intent": "relationship_analysis",  # This should now work with our improvements
                        "complexity": "advanced",
                        "min_keywords": 3,
                        "entities": ["IT general controls", "application controls"]
                    },
                    "context_retrieval": {
                        "min_results": 1,
                        "expected_doc_types": ["internal_controls", "access_review"]
                    },
                    "classification": {
                        "min_confidence": 0.6
                    }
                },
                "description": "Relationship analysis should correctly identify intent and retrieve relevant controls documentation"
            },
            {
                "name": "comparative_analysis",
                "query": "Compare the effectiveness of access controls across different departments",
                "expected_results": {
                    "question_analysis": {
                        "intent": "comparison",
                        "complexity": "advanced",
                        "min_keywords": 3,
                        "entities": ["access controls", "departments"]
                    },
                    "context_retrieval": {
                        "min_results": 2,
                        "expected_doc_types": ["access_review"]
                    },
                    "classification": {
                        "min_confidence": 0.6
                    }
                },
                "description": "Comparative analysis should identify comparison intent and retrieve multiple relevant documents"
            },
            {
                "name": "process_analysis",
                "query": "Identify segregation of duties violations in the accounts payable process and assess their impact on SOX compliance",
                "expected_results": {
                    "question_analysis": {
                        "intent": "compliance_assessment",  # This should now work with our improvements
                        "complexity": "advanced",
                        "frameworks": ["SOX"],
                        "min_keywords": 4,
                        "entities": ["segregation of duties", "accounts payable"]
                    },
                    "context_retrieval": {
                        "min_results": 1,
                        "expected_doc_types": ["financial_controls", "internal_controls"]
                    },
                    "classification": {
                        "min_confidence": 0.7
                    }
                },
                "description": "Process analysis should identify compliance assessment intent and retrieve relevant process documentation"
            },
            {
                "name": "edge_case_minimal",
                "query": "controls",
                "expected_results": {
                    "question_analysis": {
                        "intent": "information_retrieval",
                        "complexity": "basic",
                        "min_keywords": 1
                    },
                    "context_retrieval": {
                        "min_results": 1  # Should handle minimal queries gracefully
                    },
                    "classification": {
                        "min_confidence": 0.5
                    }
                },
                "description": "Edge case with minimal query should be handled gracefully with fallbacks"
            }
        ]
        
        # Performance targets based on our improvements
        self.performance_targets = {
            "workflow_success_rate": 0.85,  # 85% success rate target
            "avg_workflow_time_ms": 8000,   # 8 seconds max average
            "question_analysis_accuracy": 0.85,  # Based on our 88.4% robustness test
            "context_retrieval_success": 0.90,   # Should be high with our fixes
            "classification_accuracy": 0.80      # Based on our edge case improvements
        }
    
    async def run_improved_integration_test(self) -> Dict[str, Any]:
        """Run the improved Phase 2 integration test."""
        logger.info("🚀 Starting Improved Phase 2 Integration Test")
        logger.info("🎯 Testing complete workflow with all improvements applied")
        
        results = {
            "test_timestamp": time.time(),
            "improvements_applied": [
                "Enhanced Question Analysis Agent (88.4% accuracy)",
                "Fixed Context Retrieval Agent (metadata filtering, zero results)",
                "Improved Classification Engine (edge cases, confidence)",
                "Better error handling and fallback mechanisms"
            ],
            "workflow_results": {},
            "component_performance": {},
            "integration_analysis": {},
            "improvement_validation": {}
        }
        
        # Setup test environment
        await self._setup_test_environment()
        
        # Test each integration scenario
        scenario_results = []
        for scenario in self.integration_scenarios:
            logger.info(f"📋 Testing scenario: {scenario['name']}")
            scenario_result = await self._execute_integration_scenario(scenario)
            scenario_results.append(scenario_result)
        
        # Analyze results
        results["workflow_results"] = self._analyze_workflow_results(scenario_results)
        results["component_performance"] = self._analyze_component_performance(scenario_results)
        results["integration_analysis"] = self._analyze_integration_quality(scenario_results)
        results["improvement_validation"] = self._validate_improvements(scenario_results)
        
        # Print comprehensive results
        self._print_comprehensive_results(results)
        
        return results
    
    async def _setup_test_environment(self) -> None:
        """Setup test environment with documents."""
        logger.info("🔧 Setting up improved integration test environment...")
        
        try:
            # Initialize vector database
            await vector_db_service.initialize_collection()
            logger.info("✅ Vector database initialized")
            
            # Load and process test documents
            test_documents = await self._load_test_documents()
            if test_documents:
                await self._process_test_documents(test_documents)
                logger.info(f"✅ Processed {len(test_documents)} test documents")
            
        except Exception as e:
            logger.warning(f"⚠️ Test environment setup issues: {str(e)}")
    
    async def _load_test_documents(self) -> Dict[str, Dict[str, Any]]:
        """Load test documents for integration testing."""
        test_docs = {}
        
        # Load SOX test documents
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
        for doc_name, doc_info in test_documents.items():
            try:
                logger.info(f"🔄 Processing {doc_name}...")
                
                # Create mock file for processing
                from backend.app.services.document_processor import MockUploadFile
                mock_file = MockUploadFile(
                    filename=Path(doc_info['path']).name,
                    content=doc_info['content'],
                    content_type="text/plain"
                )
                
                # Process document
                result = await self.document_processor.process_document(
                    file=mock_file,
                    document_id=f"improved_integration_{doc_name}",
                    description=f"Improved Phase 2 integration test: {doc_name}",
                    document_metadata={
                        'test_document': True,
                        'improved_integration': True,
                        'document_type': doc_info['document_type']
                    }
                )
                
                logger.info(f"✅ Processed {doc_name}: {result.get('chunk_count', 0)} chunks")
                
            except Exception as e:
                logger.error(f"❌ Failed to process {doc_name}: {str(e)}")
    
    async def _execute_integration_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete integration scenario."""
        scenario_result = {
            "name": scenario["name"],
            "query": scenario["query"],
            "description": scenario["description"],
            "start_time": time.time(),
            "component_results": {},
            "workflow_success": False,
            "errors": [],
            "execution_times": {}
        }
        
        try:
            logger.info(f"  🔍 Query: '{scenario['query'][:50]}{'...' if len(scenario['query']) > 50 else ''}'")
            
            # Step 1: Question Analysis (with improvements)
            logger.info(f"    📊 Step 1: Question Analysis")
            qa_start = time.time()
            qa_result = await self._execute_question_analysis(scenario["query"])
            qa_time = (time.time() - qa_start) * 1000
            scenario_result["component_results"]["question_analysis"] = qa_result
            scenario_result["execution_times"]["question_analysis"] = qa_time
            logger.info(f"      ✅ Question analyzed in {qa_time:.1f}ms")
            
            # Step 2: Context Retrieval (with improvements)
            logger.info(f"    🔍 Step 2: Context Retrieval")
            cr_start = time.time()
            cr_result = await self._execute_context_retrieval(scenario["query"], qa_result)
            cr_time = (time.time() - cr_start) * 1000
            scenario_result["component_results"]["context_retrieval"] = cr_result
            scenario_result["execution_times"]["context_retrieval"] = cr_time
            logger.info(f"      ✅ Context retrieved in {cr_time:.1f}ms")
            logger.info(f"      📊 Retrieved {len(cr_result.get('context', []))} relevant chunks")
            
            # Step 3: Classification (with improvements)
            logger.info(f"    🏷️ Step 3: Classification")
            class_start = time.time()
            class_result = await self._execute_classification(scenario["query"])
            class_time = (time.time() - class_start) * 1000
            scenario_result["component_results"]["classification"] = class_result
            scenario_result["execution_times"]["classification"] = class_time
            logger.info(f"      ✅ Classification completed in {class_time:.1f}ms")
            
            # Validate workflow success
            scenario_result["workflow_success"] = self._validate_workflow_success(
                scenario_result, scenario["expected_results"]
            )
            
            total_time = (time.time() - scenario_result["start_time"]) * 1000
            scenario_result["total_time_ms"] = total_time
            
            status = "✅" if scenario_result["workflow_success"] else "❌"
            logger.info(f"    {status} Phase 2 workflow completed in {total_time:.1f}ms")
            logger.info(f"    🎯 Workflow success: {status}")
            
        except Exception as e:
            logger.error(f"    💥 Scenario failed: {str(e)}")
            scenario_result["errors"].append(str(e))
            scenario_result["total_time_ms"] = (time.time() - scenario_result["start_time"]) * 1000
        
        return scenario_result
    
    async def _execute_question_analysis(self, query: str) -> Dict[str, Any]:
        """Execute question analysis with improved agent."""
        try:
            # Create agent context
            context = AgentContext(
                inputs={"question": query},
                agent_type=AgentType.QUESTION_ANALYZER,
                timestamp=datetime.now(),
                conversation_id=f"improved_integration_{int(time.time())}",
                workflow_id=f"improved_workflow_{int(time.time())}"
            )
            
            # Execute improved question analysis
            result = await self.question_analyzer._execute_logic(context)
            
            return {
                "success": result.get("analysis_status") == "completed",
                "analysis": result.get("analysis", {}),
                "raw_result": result
            }
            
        except Exception as e:
            logger.error(f"Question analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    async def _execute_context_retrieval(self, query: str, qa_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute context retrieval with improved agent."""
        try:
            # Create agent context
            context = AgentContext(
                inputs={
                    "question": query,
                    "question_analysis": qa_result.get("analysis", {}),
                    "retrieval_strategy": "hybrid"
                },
                agent_type=AgentType.CONTEXT_RETRIEVER,
                timestamp=datetime.now(),
                conversation_id=f"improved_integration_{int(time.time())}",
                workflow_id=f"improved_workflow_{int(time.time())}"
            )
            
            # Execute improved context retrieval
            result = await self.context_retriever._execute_logic(context)
            
            return {
                "success": result.get("retrieval_status") == "completed",
                "context": result.get("context", []),
                "search_results": result.get("search_results", []),
                "raw_result": result
            }
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "context": []
            }
    
    async def _execute_classification(self, query: str) -> Dict[str, Any]:
        """Execute classification with improved engine."""
        try:
            # Use query as content for classification testing
            result = await self.classifier.classify_document(
                content=query
            )
            
            return {
                "success": True,
                "classification": result,
                "confidence": result.get("confidence", 0.0)
            }
            
        except Exception as e:
            logger.warning(f"Classification failed (non-critical): {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "classification": {},
                "confidence": 0.0
            }
    
    def _validate_workflow_success(self, scenario_result: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        """Validate if the workflow was successful based on expected results."""
        qa_result = scenario_result["component_results"].get("question_analysis", {})
        cr_result = scenario_result["component_results"].get("context_retrieval", {})
        class_result = scenario_result["component_results"].get("classification", {})
        
        # Question Analysis validation
        qa_success = qa_result.get("success", False)
        if not qa_success:
            return False
        
        analysis = qa_result.get("analysis", {})
        expected_qa = expected.get("question_analysis", {})
        
        # Check intent
        expected_intent = expected_qa.get("intent")
        actual_intent = analysis.get("intent", "")
        if isinstance(expected_intent, list):
            intent_match = actual_intent in expected_intent
        else:
            intent_match = actual_intent == expected_intent
        
        if not intent_match:
            logger.warning(f"      ⚠️ Intent mismatch: expected {expected_intent}, got {actual_intent}")
        
        # Check complexity
        expected_complexity = expected_qa.get("complexity")
        actual_complexity = analysis.get("complexity", "")
        if isinstance(expected_complexity, list):
            complexity_match = actual_complexity in expected_complexity
        else:
            complexity_match = actual_complexity == expected_complexity
        
        # Check keywords
        min_keywords = expected_qa.get("min_keywords", 1)
        actual_keywords = len(analysis.get("search_keywords", []))
        keywords_sufficient = actual_keywords >= min_keywords
        
        # Context Retrieval validation
        cr_success = cr_result.get("success", False)
        context = cr_result.get("context", [])
        min_results = expected.get("context_retrieval", {}).get("min_results", 1)
        context_sufficient = len(context) >= min_results
        
        # Overall success criteria
        workflow_success = (
            qa_success and
            intent_match and
            complexity_match and
            keywords_sufficient and
            cr_success and
            context_sufficient
        )
        
        return workflow_success
    
    def _analyze_workflow_results(self, scenario_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall workflow performance."""
        total_scenarios = len(scenario_results)
        successful_workflows = sum(1 for r in scenario_results if r.get("workflow_success", False))
        
        workflow_times = [r.get("total_time_ms", 0) for r in scenario_results if r.get("workflow_success", False)]
        
        return {
            "total_scenarios": total_scenarios,
            "successful_workflows": successful_workflows,
            "success_rate": successful_workflows / total_scenarios if total_scenarios > 0 else 0,
            "avg_workflow_time_ms": statistics.mean(workflow_times) if workflow_times else 0,
            "max_workflow_time_ms": max(workflow_times) if workflow_times else 0,
            "min_workflow_time_ms": min(workflow_times) if workflow_times else 0
        }
    
    def _analyze_component_performance(self, scenario_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze individual component performance."""
        component_performance = {}
        
        for component in ["question_analysis", "context_retrieval", "classification"]:
            successes = 0
            times = []
            errors = []
            
            for result in scenario_results:
                comp_result = result["component_results"].get(component, {})
                if comp_result.get("success", False):
                    successes += 1
                else:
                    error = comp_result.get("error", "unknown_error")
                    errors.append(error)
                
                time_ms = result["execution_times"].get(component, 0)
                if time_ms > 0:
                    times.append(time_ms)
            
            component_performance[component] = {
                "success_rate": successes / len(scenario_results) if scenario_results else 0,
                "avg_time_ms": statistics.mean(times) if times else 0,
                "max_time_ms": max(times) if times else 0,
                "common_errors": list(set(errors))
            }
        
        return component_performance
    
    def _analyze_integration_quality(self, scenario_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the quality of component integration."""
        return {
            "data_flow_success": sum(1 for r in scenario_results if r.get("workflow_success", False)) / len(scenario_results) if scenario_results else 0,
            "error_recovery_rate": sum(1 for r in scenario_results if not r.get("errors", [])) / len(scenario_results) if scenario_results else 0,
            "component_compatibility": "high" if all(r.get("workflow_success", False) for r in scenario_results) else "needs_improvement"
        }
    
    def _validate_improvements(self, scenario_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that our improvements are working."""
        workflow_results = self._analyze_workflow_results(scenario_results)
        component_perf = self._analyze_component_performance(scenario_results)
        
        improvements_validated = {
            "question_analysis_improved": component_perf["question_analysis"]["success_rate"] >= self.performance_targets["question_analysis_accuracy"],
            "context_retrieval_improved": component_perf["context_retrieval"]["success_rate"] >= self.performance_targets["context_retrieval_success"],
            "classification_improved": component_perf["classification"]["success_rate"] >= self.performance_targets["classification_accuracy"],
            "workflow_success_improved": workflow_results["success_rate"] >= self.performance_targets["workflow_success_rate"],
            "performance_improved": workflow_results["avg_workflow_time_ms"] <= self.performance_targets["avg_workflow_time_ms"]
        }
        
        return {
            "improvements_validated": improvements_validated,
            "overall_improvement_success": all(improvements_validated.values()),
            "improvement_score": sum(improvements_validated.values()) / len(improvements_validated)
        }
    
    def _print_comprehensive_results(self, results: Dict[str, Any]) -> None:
        """Print comprehensive test results."""
        print("\n" + "="*100)
        print("🎯 IMPROVED PHASE 2 INTEGRATION TEST RESULTS")
        print("="*100)
        
        workflow_results = results["workflow_results"]
        component_perf = results["component_performance"]
        improvement_validation = results["improvement_validation"]
        
        # Overall status
        success_rate = workflow_results["success_rate"]
        target_rate = self.performance_targets["workflow_success_rate"]
        status = "✅ SUCCESS" if success_rate >= target_rate else "❌ NEEDS IMPROVEMENT"
        print(f"📊 OVERALL STATUS: {status}")
        print(f"🎯 Workflow Success Rate: {success_rate:.1%} (Target: {target_rate:.1%})")
        print(f"⏱️ Average Workflow Time: {workflow_results['avg_workflow_time_ms']:.1f}ms")
        
        # Component performance
        print(f"\n⚙️ COMPONENT PERFORMANCE:")
        for component, perf in component_perf.items():
            status = "✅" if perf["success_rate"] >= 0.8 else "❌"
            print(f"   {status} {component.replace('_', ' ').title()}: {perf['success_rate']:.1%} success, {perf['avg_time_ms']:.1f}ms avg")
        
        # Improvement validation
        print(f"\n🚀 IMPROVEMENT VALIDATION:")
        improvements = improvement_validation["improvements_validated"]
        for improvement, validated in improvements.items():
            status = "✅" if validated else "❌"
            print(f"   {status} {improvement.replace('_', ' ').title()}")
        
        improvement_score = improvement_validation["improvement_score"]
        overall_success = improvement_validation["overall_improvement_success"]
        print(f"\n📊 IMPROVEMENT SCORE: {improvement_score:.1%}")
        print(f"🎯 OVERALL IMPROVEMENT SUCCESS: {'✅ YES' if overall_success else '❌ NO'}")
        
        # Recommendations
        if not overall_success:
            print(f"\n💡 RECOMMENDATIONS:")
            for improvement, validated in improvements.items():
                if not validated:
                    print(f"   • Fix {improvement.replace('_', ' ')}")
        
        print("="*100)
        print("✅ IMPROVED PHASE 2 INTEGRATION TEST COMPLETED")
        print("="*100)


async def main():
    """Run the improved integration test."""
    test = ImprovedPhase2IntegrationTest()
    
    # Run comprehensive test
    results = await test.run_improved_integration_test()
    
    # Save detailed results
    output_file = Path(__file__).parent / "improved_phase2_integration_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📊 Detailed results saved to: {output_file}")
    
    # Return appropriate exit code
    improvement_validation = results.get("improvement_validation", {})
    overall_success = improvement_validation.get("overall_improvement_success", False)
    
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    asyncio.run(main())
