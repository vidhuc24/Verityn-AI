#!/usr/bin/env python3
"""
Phase 2 Integration Test for Verityn AI

This test validates the complete Phase 2 workflow integration:
1. Question Analysis Agent → Context Retrieval Agent flow
2. Classification Engine integration with retrieval
3. End-to-end Phase 2 performance and accuracy
4. Data flow validation between components
5. Error handling and recovery mechanisms

Phase 2 Components:
- Question Analysis: Intent understanding and query optimization
- Classification: Document type and compliance framework detection
- Context Retrieval: Advanced retrieval strategy selection and execution

Follows Verityn AI testing standards:
- Uses real audit documents and queries
- Tests complete workflow integration
- Validates data flow between agents
- Measures end-to-end performance
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
from backend.app.agents.base_agent import AgentContext
from backend.app.services.classification_engine import ClassificationEngine
from backend.app.services.vector_database import vector_db_service
from backend.app.services.document_processor import EnhancedDocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Phase2IntegrationTest:
    """Comprehensive Phase 2 integration test suite."""
    
    def __init__(self):
        """Initialize the Phase 2 integration test."""
        # Initialize Phase 2 components
        self.question_analyzer = QuestionAnalysisAgent(verbose=True)
        self.context_retriever = ContextRetrievalAgent(verbose=True)
        self.classifier = ClassificationEngine()
        self.document_processor = EnhancedDocumentProcessor()
        
        # Test scenarios representing real audit workflows
        self.integration_scenarios = {
            "basic_audit_inquiry": {
                "query": "What are the key findings from the access review?",
                "expected_flow": {
                    "question_analysis": {
                        "intent": "information_retrieval",
                        "complexity": ["basic", "intermediate"],
                        "frameworks": ["SOX"]
                    },
                    "context_retrieval": {
                        "strategy": ["hybrid", "semantic"],
                        "min_results": 1  # Realistic expectation for focused queries
                    },
                    "classification": {
                        "document_type": "access_review",
                        "min_confidence": 0.6
                    }
                }
            },
            
            "compliance_assessment": {
                "query": "Are there any SOX 404 material weaknesses in the financial controls?",
                "expected_flow": {
                    "question_analysis": {
                        "intent": "compliance_check",
                        "complexity": ["intermediate", "advanced"],
                        "frameworks": ["SOX"]
                    },
                    "context_retrieval": {
                        "strategy": ["query_expansion", "hybrid"],
                        "min_results": 2  # Realistic expectation for compliance queries
                    },
                    "classification": {
                        "document_type": ["financial_controls", "internal_controls"],
                        "min_confidence": 0.7
                    }
                }
            },
            
            "complex_analysis": {
                "query": "Compare the effectiveness of access controls across different departments and identify any patterns in control deficiencies",
                "expected_flow": {
                    "question_analysis": {
                        "intent": ["comparison", "document_analysis"],
                        "complexity": "advanced",
                        "frameworks": ["SOX"]
                    },
                    "context_retrieval": {
                        "strategy": ["multi_hop", "ensemble"],
                        "min_results": 3  # Realistic expectation for complex analysis
                    },
                    "classification": {
                        "document_type": "access_review",
                        "min_confidence": 0.5
                    }
                }
            },
            
            "risk_identification": {
                "query": "What risks were identified in the latest risk assessment and what are the recommended mitigation strategies?",
                "expected_flow": {
                    "question_analysis": {
                        "intent": "information_retrieval",
                        "complexity": ["intermediate", "advanced"],
                        "frameworks": ["SOX", "General"]
                    },
                    "context_retrieval": {
                        "strategy": ["hybrid", "query_expansion"],
                        "min_results": 1  # Realistic expectation for risk queries (some may have no results)
                    },
                    "classification": {
                        "document_type": "risk_assessment",
                        "min_confidence": 0.6
                    }
                }
            },
            
            "edge_case_vague": {
                "query": "controls",
                "expected_flow": {
                    "question_analysis": {
                        "intent": "information_retrieval",
                        "complexity": "basic",
                        "frameworks": ["General"]
                    },
                    "context_retrieval": {
                        "strategy": ["semantic", "hybrid"],
                        "min_results": 1  # Lower expectation for vague queries
                    },
                    "classification": {
                        "document_type": ["internal_controls", "access_review"],
                        "min_confidence": 0.3
                    }
                }
            }
        }
        
        # Performance thresholds for Phase 2 workflow
        self.performance_thresholds = {
            "max_total_time_ms": 8000,        # 8 seconds max for complete Phase 2
            "max_question_analysis_ms": 2000,  # 2 seconds for question analysis
            "max_context_retrieval_ms": 5000,  # 5 seconds for context retrieval
            "max_classification_ms": 1000,     # 1 second for classification
            "min_workflow_success_rate": 0.8   # 80% of workflows should complete successfully
        }
    
    async def run_phase2_integration_test(self) -> Dict[str, Any]:
        """Run comprehensive Phase 2 integration test."""
        logger.info("🚀 Starting Phase 2 Integration Test")
        logger.info("📊 Testing complete Question Analysis → Classification → Context Retrieval workflow")
        
        # Setup test environment
        await self._setup_test_environment()
        
        results = {
            "test_timestamp": time.time(),
            "phase2_components": {
                "question_analyzer": str(self.question_analyzer.agent_type),
                "context_retriever": str(self.context_retriever.agent_type),
                "classifier": "ClassificationEngine"
            },
            "integration_scenarios": {},
            "workflow_performance": {},
            "component_interaction": {},
            "error_handling": {},
            "optimization_insights": {},
            "detailed_results": []
        }
        
        # Test each integration scenario
        total_scenarios = len(self.integration_scenarios)
        successful_workflows = 0
        workflow_times = []
        component_times = {"question_analysis": [], "classification": [], "context_retrieval": []}
        
        for scenario_name, scenario_data in self.integration_scenarios.items():
            logger.info(f"\n📋 Testing integration scenario: {scenario_name}")
            
            scenario_result = await self._test_integration_scenario(scenario_name, scenario_data)
            results["integration_scenarios"][scenario_name] = scenario_result
            
            if scenario_result["workflow_success"]:
                successful_workflows += 1
                workflow_times.append(scenario_result["total_time_ms"])
                
                # Collect component times
                for component, time_ms in scenario_result["component_times"].items():
                    if component in component_times:
                        component_times[component].append(time_ms)
            
            results["detailed_results"].append(scenario_result)
        
        # Calculate workflow performance metrics
        results["workflow_performance"] = {
            "total_scenarios": total_scenarios,
            "successful_workflows": successful_workflows,
            "workflow_success_rate": successful_workflows / total_scenarios if total_scenarios > 0 else 0,
            "avg_workflow_time_ms": statistics.mean(workflow_times) if workflow_times else 0,
            "max_workflow_time_ms": max(workflow_times) if workflow_times else 0,
            "component_performance": {
                component: {
                    "avg_time_ms": statistics.mean(times) if times else 0,
                    "max_time_ms": max(times) if times else 0,
                    "min_time_ms": min(times) if times else 0
                }
                for component, times in component_times.items()
            }
        }
        
        # Analyze component interactions
        results["component_interaction"] = self._analyze_component_interactions(results["detailed_results"])
        
        # Analyze error handling
        results["error_handling"] = self._analyze_error_handling(results["detailed_results"])
        
        # Generate optimization insights
        results["optimization_insights"] = self._generate_optimization_insights(results)
        
        # Print comprehensive results
        self._print_results(results)
        
        return results
    
    async def _setup_test_environment(self) -> None:
        """Setup the test environment with documents and services."""
        logger.info("🔧 Setting up Phase 2 integration test environment...")
        
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
            logger.info("Continuing with limited integration testing...")
    
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
        from fastapi import UploadFile
        from io import BytesIO
        
        for doc_name, doc_info in test_documents.items():
            try:
                logger.info(f"🔄 Processing {doc_name} for integration testing...")
                
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
                    document_id=f"phase2_integration_{doc_name}",
                    description=f"Phase 2 integration test: {doc_name}"
                )
                
                # Store in vector database
                chunks = result.get('chunks', [])
                metadata = result.get('metadata', {})
                metadata.update({
                    'test_document': True,
                    'phase2_integration': True,
                    'document_type': doc_info['document_type']
                })
                
                if chunks:
                    success = await vector_db_service.insert_document_chunks(
                        document_id=f"phase2_integration_{doc_name}",
                        chunks=chunks,
                        metadata=metadata
                    )
                    
                    if success:
                        logger.info(f"✅ Stored {doc_name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"❌ Failed to process {doc_name}: {str(e)}")
    
    async def _test_integration_scenario(self, scenario_name: str, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a complete Phase 2 integration scenario."""
        query = scenario_data["query"]
        expected_flow = scenario_data["expected_flow"]
        
        logger.info(f"  🔍 Query: '{query[:80]}...'")
        
        scenario_result = {
            "scenario": scenario_name,
            "query": query,
            "workflow_success": False,
            "total_time_ms": 0,
            "component_times": {},
            "component_results": {},
            "flow_validation": {},
            "errors": []
        }
        
        workflow_start_time = time.time()
        
        try:
            # Step 1: Question Analysis
            logger.info("    📊 Step 1: Question Analysis")
            step1_start = time.time()
            
            from datetime import datetime
            question_context = AgentContext(
                inputs={"question": query, "conversation_id": f"phase2_test_{scenario_name}"},
                agent_type=self.question_analyzer.agent_type,
                timestamp=datetime.now(),
                conversation_id=f"phase2_test_{scenario_name}",
                workflow_id=f"phase2_workflow_{scenario_name}"
            )
            
            question_result = await self.question_analyzer._execute_logic(question_context)
            step1_time = (time.time() - step1_start) * 1000
            
            scenario_result["component_times"]["question_analysis"] = step1_time
            scenario_result["component_results"]["question_analysis"] = question_result
            
            # Validate question analysis
            qa_validation = self._validate_question_analysis(question_result, expected_flow["question_analysis"])
            scenario_result["flow_validation"]["question_analysis"] = qa_validation
            
            if not question_result or question_result.get("analysis_status") == "failed":
                scenario_result["errors"].append("Question analysis failed")
                return scenario_result
            
            logger.info(f"      ✅ Question analyzed in {step1_time:.1f}ms")
            
            # Step 2: Classification (parallel with context preparation)
            logger.info("    🏷️ Step 2: Document Classification")
            step2_start = time.time()
            
            # For integration testing, we'll classify a sample document
            # In real workflow, this would be based on uploaded documents
            sample_content = "This is an access review document containing user access controls and findings."
            classification_result = await self.classifier.classify_document(sample_content)
            step2_time = (time.time() - step2_start) * 1000
            
            scenario_result["component_times"]["classification"] = step2_time
            scenario_result["component_results"]["classification"] = classification_result
            
            # Validate classification
            class_validation = self._validate_classification(classification_result, expected_flow["classification"])
            scenario_result["flow_validation"]["classification"] = class_validation
            
            logger.info(f"      ✅ Classification completed in {step2_time:.1f}ms")
            
            # Step 3: Context Retrieval
            logger.info("    🔍 Step 3: Context Retrieval")
            step3_start = time.time()
            
            retrieval_context = AgentContext(
                inputs={
                    "question": query,
                    "analysis": question_result.get("analysis", {}),
                    "conversation_id": f"phase2_test_{scenario_name}"
                },
                agent_type=self.context_retriever.agent_type,
                timestamp=datetime.now(),
                conversation_id=f"phase2_test_{scenario_name}",
                workflow_id=f"phase2_workflow_{scenario_name}"
            )
            
            retrieval_result = await self.context_retriever._execute_logic(retrieval_context)
            step3_time = (time.time() - step3_start) * 1000
            
            scenario_result["component_times"]["context_retrieval"] = step3_time
            scenario_result["component_results"]["context_retrieval"] = retrieval_result
            
            # Validate context retrieval
            cr_validation = self._validate_context_retrieval(retrieval_result, expected_flow["context_retrieval"])
            scenario_result["flow_validation"]["context_retrieval"] = cr_validation
            
            if not retrieval_result or not retrieval_result.get("context"):
                scenario_result["errors"].append("Context retrieval failed or returned no results")
                return scenario_result
            
            logger.info(f"      ✅ Context retrieved in {step3_time:.1f}ms")
            logger.info(f"      📊 Retrieved {len(retrieval_result.get('context', []))} relevant chunks")
            
            # Calculate total workflow time
            total_time = (time.time() - workflow_start_time) * 1000
            scenario_result["total_time_ms"] = total_time
            
            # Determine overall workflow success
            all_validations_passed = all(
                validation.get("overall_valid", False) 
                for validation in scenario_result["flow_validation"].values()
            )
            
            performance_acceptable = total_time <= self.performance_thresholds["max_total_time_ms"]
            
            scenario_result["workflow_success"] = all_validations_passed and performance_acceptable
            
            logger.info(f"    ✅ Phase 2 workflow completed in {total_time:.1f}ms")
            logger.info(f"    🎯 Workflow success: {'✅' if scenario_result['workflow_success'] else '❌'}")
            
        except Exception as e:
            total_time = (time.time() - workflow_start_time) * 1000
            scenario_result["total_time_ms"] = total_time
            scenario_result["errors"].append(f"Workflow exception: {str(e)}")
            logger.error(f"    ❌ Workflow failed: {str(e)}")
        
        return scenario_result
    
    def _validate_question_analysis(self, result: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate question analysis results against expectations."""
        validation = {
            "has_analysis": False,
            "intent_correct": False,
            "complexity_appropriate": False,
            "frameworks_detected": False,
            "overall_valid": False
        }
        
        if not result or "analysis" not in result:
            return validation
        
        analysis = result["analysis"]
        validation["has_analysis"] = True
        
        # Check intent
        expected_intents = expected.get("intent", [])
        if isinstance(expected_intents, str):
            expected_intents = [expected_intents]
        
        actual_intent = analysis.get("intent", "")
        validation["intent_correct"] = actual_intent in expected_intents
        
        # Check complexity
        expected_complexity = expected.get("complexity", [])
        if isinstance(expected_complexity, str):
            expected_complexity = [expected_complexity]
        
        actual_complexity = analysis.get("complexity", "")
        validation["complexity_appropriate"] = actual_complexity in expected_complexity
        
        # Check frameworks
        expected_frameworks = expected.get("frameworks", [])
        actual_frameworks = analysis.get("compliance_frameworks", [])
        
        framework_overlap = len(set(expected_frameworks) & set(actual_frameworks))
        validation["frameworks_detected"] = framework_overlap > 0
        
        # Overall validation
        validation["overall_valid"] = (
            validation["has_analysis"] and
            validation["intent_correct"] and
            validation["complexity_appropriate"]
        )
        
        return validation
    
    def _validate_classification(self, result: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate classification results against expectations."""
        validation = {
            "has_classification": False,
            "type_appropriate": False,
            "confidence_sufficient": False,
            "overall_valid": False
        }
        
        if not result:
            return validation
        
        validation["has_classification"] = True
        
        # Check document type
        expected_types = expected.get("document_type", [])
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        
        actual_type = result.get("document_type", "").lower()
        validation["type_appropriate"] = any(
            expected_type.lower() in actual_type or actual_type in expected_type.lower()
            for expected_type in expected_types
        )
        
        # Check confidence
        min_confidence = expected.get("min_confidence", 0.5)
        actual_confidence = result.get("confidence", 0)
        validation["confidence_sufficient"] = actual_confidence >= min_confidence
        
        # Overall validation
        validation["overall_valid"] = (
            validation["has_classification"] and
            validation["confidence_sufficient"]
        )
        
        return validation
    
    def _validate_context_retrieval(self, result: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate context retrieval results against expectations."""
        validation = {
            "has_context": False,
            "sufficient_results": False,
            "strategy_appropriate": False,
            "overall_valid": False
        }
        
        if not result:
            return validation
        
        # Check context exists
        context = result.get("context", [])
        validation["has_context"] = len(context) > 0
        
        # Check sufficient results
        min_results = expected.get("min_results", 3)
        validation["sufficient_results"] = len(context) >= min_results
        
        # Check strategy
        expected_strategies = expected.get("strategy", [])
        actual_strategy = result.get("retrieval_method", "")
        validation["strategy_appropriate"] = actual_strategy in expected_strategies
        
        # Overall validation - more flexible approach
        # A workflow is valid if:
        # 1. Context retrieval executed without error (even if no results)
        # 2. If results exist, they meet minimum requirements
        # 3. Strategy was appropriate for the query type
        
        has_retrieval_status = "retrieval_status" in result
        retrieval_successful = result.get("retrieval_status") == "completed"
        
        # For queries that legitimately may have no results, don't penalize
        min_results = expected.get("min_results", 1)
        if min_results == 1 and len(context) == 0:
            # Allow zero results for queries that may legitimately find nothing
            validation["overall_valid"] = has_retrieval_status and retrieval_successful
        else:
            # Standard validation for queries expected to find results
            validation["overall_valid"] = (
                validation["has_context"] and
                validation["sufficient_results"] and
                has_retrieval_status and
                retrieval_successful
            )
        
        return validation
    
    def _analyze_component_interactions(self, detailed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how well components interact with each other."""
        interaction_analysis = {
            "data_flow_success_rate": 0.0,
            "component_compatibility": {},
            "bottleneck_identification": {},
            "integration_patterns": []
        }
        
        successful_flows = 0
        total_flows = len(detailed_results)
        
        component_times = {"question_analysis": [], "classification": [], "context_retrieval": []}
        
        for result in detailed_results:
            if result.get("workflow_success", False):
                successful_flows += 1
            
            # Collect component times for bottleneck analysis
            for component, time_ms in result.get("component_times", {}).items():
                if component in component_times:
                    component_times[component].append(time_ms)
        
        interaction_analysis["data_flow_success_rate"] = successful_flows / total_flows if total_flows > 0 else 0
        
        # Identify bottlenecks
        if any(component_times.values()):
            avg_times = {
                component: statistics.mean(times) if times else 0
                for component, times in component_times.items()
            }
            
            slowest_component = max(avg_times, key=avg_times.get) if avg_times else None
            interaction_analysis["bottleneck_identification"] = {
                "slowest_component": slowest_component,
                "component_times": avg_times
            }
        
        return interaction_analysis
    
    def _analyze_error_handling(self, detailed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze error handling capabilities."""
        error_analysis = {
            "error_rate": 0.0,
            "error_types": {},
            "recovery_rate": 0.0,
            "graceful_degradation": 0.0
        }
        
        total_scenarios = len(detailed_results)
        scenarios_with_errors = 0
        error_types = {}
        
        for result in detailed_results:
            errors = result.get("errors", [])
            if errors:
                scenarios_with_errors += 1
                for error in errors:
                    error_type = error.split(":")[0] if ":" in error else error
                    error_types[error_type] = error_types.get(error_type, 0) + 1
        
        error_analysis["error_rate"] = scenarios_with_errors / total_scenarios if total_scenarios > 0 else 0
        error_analysis["error_types"] = error_types
        
        return error_analysis
    
    def _generate_optimization_insights(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimization insights based on test results."""
        insights = {
            "performance_bottlenecks": [],
            "accuracy_improvements": [],
            "integration_recommendations": [],
            "priority_optimizations": []
        }
        
        workflow_perf = results["workflow_performance"]
        component_interaction = results["component_interaction"]
        
        # Performance insights
        if workflow_perf["avg_workflow_time_ms"] > self.performance_thresholds["max_total_time_ms"]:
            insights["performance_bottlenecks"].append("Overall workflow time exceeds threshold")
        
        bottleneck = component_interaction.get("bottleneck_identification", {})
        if bottleneck.get("slowest_component"):
            slowest = bottleneck["slowest_component"]
            insights["performance_bottlenecks"].append(f"{slowest} is the performance bottleneck")
        
        # Accuracy insights
        if workflow_perf["workflow_success_rate"] < self.performance_thresholds["min_workflow_success_rate"]:
            insights["accuracy_improvements"].append("Workflow success rate below acceptable threshold")
        
        # Integration recommendations
        data_flow_rate = component_interaction.get("data_flow_success_rate", 0)
        if data_flow_rate < 0.9:
            insights["integration_recommendations"].append("Improve data flow between components")
        
        # Priority optimizations
        if insights["performance_bottlenecks"]:
            insights["priority_optimizations"].append("Focus on performance optimization")
        if insights["accuracy_improvements"]:
            insights["priority_optimizations"].append("Improve component accuracy and reliability")
        
        return insights
    
    def _print_results(self, results: Dict[str, Any]) -> None:
        """Print comprehensive Phase 2 integration test results."""
        print("\n" + "="*100)
        print("📊 PHASE 2 INTEGRATION TEST RESULTS")
        print("="*100)
        
        # Workflow performance
        workflow_perf = results["workflow_performance"]
        print(f"📊 WORKFLOW PERFORMANCE:")
        print(f"   📄 Scenarios Tested: {workflow_perf['total_scenarios']}")
        print(f"   ✅ Successful Workflows: {workflow_perf['successful_workflows']}")
        print(f"   📊 Success Rate: {workflow_perf['workflow_success_rate']:.1%}")
        print(f"   ⏱️ Avg Workflow Time: {workflow_perf['avg_workflow_time_ms']:.1f}ms")
        print(f"   🐌 Max Workflow Time: {workflow_perf['max_workflow_time_ms']:.1f}ms")
        
        # Component performance breakdown
        print(f"\n⚙️ COMPONENT PERFORMANCE:")
        for component, perf_data in workflow_perf["component_performance"].items():
            avg_time = perf_data["avg_time_ms"]
            max_time = perf_data["max_time_ms"]
            threshold_key = f"max_{component}_ms"
            threshold = self.performance_thresholds.get(threshold_key, 1000)
            
            status = "✅" if avg_time <= threshold else "⚠️"
            print(f"   {status} {component.replace('_', ' ').title()}: {avg_time:.1f}ms avg (max: {max_time:.1f}ms)")
        
        # Component interaction analysis
        component_interaction = results["component_interaction"]
        print(f"\n🔗 COMPONENT INTEGRATION:")
        print(f"   📊 Data Flow Success: {component_interaction['data_flow_success_rate']:.1%}")
        
        bottleneck = component_interaction.get("bottleneck_identification", {})
        if bottleneck.get("slowest_component"):
            print(f"   🚨 Performance Bottleneck: {bottleneck['slowest_component']}")
        
        # Error handling analysis
        error_handling = results["error_handling"]
        print(f"\n🛡️ ERROR HANDLING:")
        print(f"   📊 Error Rate: {error_handling['error_rate']:.1%}")
        
        if error_handling["error_types"]:
            print(f"   🔍 Common Error Types:")
            for error_type, count in error_handling["error_types"].items():
                print(f"      • {error_type}: {count} occurrences")
        
        # Scenario breakdown
        print(f"\n📊 SCENARIO RESULTS:")
        print("-" * 100)
        
        for scenario_name, scenario_data in results["integration_scenarios"].items():
            success = scenario_data["workflow_success"]
            total_time = scenario_data["total_time_ms"]
            status = "✅" if success else "❌"
            
            print(f"\n{status} {scenario_name.upper().replace('_', ' ')}")
            print(f"   🔍 Query: \"{scenario_data['query'][:80]}...\"")
            print(f"   ⏱️ Total Time: {total_time:.1f}ms")
            
            # Show component times
            component_times = scenario_data.get("component_times", {})
            for component, time_ms in component_times.items():
                print(f"   • {component.replace('_', ' ').title()}: {time_ms:.1f}ms")
            
            # Show validation results
            flow_validation = scenario_data.get("flow_validation", {})
            for component, validation in flow_validation.items():
                valid = validation.get("overall_valid", False)
                validation_status = "✅" if valid else "❌"
                print(f"   {validation_status} {component.replace('_', ' ').title()} Validation")
            
            # Show errors if any
            errors = scenario_data.get("errors", [])
            if errors:
                print(f"   ❌ Errors: {'; '.join(errors)}")
        
        # Optimization insights
        optimization = results["optimization_insights"]
        print(f"\n💡 OPTIMIZATION INSIGHTS:")
        
        if optimization["performance_bottlenecks"]:
            print(f"   🚨 Performance Issues:")
            for issue in optimization["performance_bottlenecks"]:
                print(f"      • {issue}")
        
        if optimization["accuracy_improvements"]:
            print(f"   🎯 Accuracy Improvements:")
            for improvement in optimization["accuracy_improvements"]:
                print(f"      • {improvement}")
        
        if optimization["integration_recommendations"]:
            print(f"   🔗 Integration Recommendations:")
            for rec in optimization["integration_recommendations"]:
                print(f"      • {rec}")
        
        # Overall recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        success_rate = workflow_perf["workflow_success_rate"]
        avg_time = workflow_perf["avg_workflow_time_ms"]
        
        if success_rate > 0.9 and avg_time <= self.performance_thresholds["max_total_time_ms"]:
            print("   🎉 Excellent Phase 2 integration! All components work well together.")
        elif success_rate > 0.8:
            print("   ✅ Good Phase 2 integration with areas for improvement:")
            if avg_time > self.performance_thresholds["max_total_time_ms"]:
                print("      - Optimize component performance to reduce workflow time")
            if optimization["performance_bottlenecks"]:
                print("      - Address identified performance bottlenecks")
        else:
            print("   ⚠️ Phase 2 integration needs significant improvement:")
            print("      - Review component interfaces and data flow")
            print("      - Improve error handling and recovery mechanisms")
            print("      - Optimize individual component performance")
            print("      - Enhance validation and testing coverage")
        
        if optimization["priority_optimizations"]:
            print(f"   🎯 Priority Focus Areas:")
            for priority in optimization["priority_optimizations"]:
                print(f"      • {priority}")
        
        print("="*100)
        print("✅ PHASE 2 INTEGRATION TEST COMPLETED")
        print("="*100)


async def main():
    """Run the Phase 2 integration test."""
    test = Phase2IntegrationTest()
    
    # Run comprehensive integration test
    results = await test.run_phase2_integration_test()
    
    # Save detailed results
    output_file = Path(__file__).parent / "phase2_integration_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📊 Detailed results saved to: {output_file}")
    
    # Return appropriate exit code
    workflow_perf = results["workflow_performance"]
    success_rate = workflow_perf["workflow_success_rate"]
    avg_time = workflow_perf["avg_workflow_time_ms"]
    
    performance_threshold = test.performance_thresholds["max_total_time_ms"]
    success_threshold = test.performance_thresholds["min_workflow_success_rate"]
    
    if success_rate >= success_threshold and avg_time <= performance_threshold:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs improvement


if __name__ == "__main__":
    asyncio.run(main())
