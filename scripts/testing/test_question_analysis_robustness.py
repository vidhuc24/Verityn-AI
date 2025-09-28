#!/usr/bin/env python3
"""
Question Analysis Robustness Test for Verityn AI

This test specifically targets the two critical failure modes identified:
1. Edge Case Handling (25% accuracy) - Tests minimal, vague, and malformed queries
2. Complex Query Intent Classification (37.5% accuracy) - Tests relationship analysis and multi-part queries

The test provides detailed failure analysis and measures improvement accurately to guide
targeted enhancements to the Question Analysis Agent.

Usage:
    uv run python scripts/testing/test_question_analysis_robustness.py
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

from backend.app.agents.specialized_agents import QuestionAnalysisAgent
from backend.app.agents.base_agent import AgentContext, AgentType
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QuestionAnalysisRobustnessTest:
    """Comprehensive test for Question Analysis Agent robustness and accuracy."""
    
    def __init__(self):
        """Initialize the robustness test."""
        self.agent = QuestionAnalysisAgent(verbose=False)
        
        # Edge case test scenarios - targeting 25% accuracy issue
        self.edge_case_scenarios = [
            # Minimal input edge cases
            {
                "query": "",
                "category": "empty_query",
                "expected_behavior": "graceful_fallback",
                "expected_intent": "information_retrieval",
                "expected_complexity": "basic",
                "min_keywords": 0,
                "description": "Empty query should trigger graceful fallback"
            },
            {
                "query": "controls",
                "category": "single_word",
                "expected_behavior": "context_expansion",
                "expected_intent": "information_retrieval", 
                "expected_complexity": "basic",
                "min_keywords": 1,
                "description": "Single word should expand to audit context"
            },
            {
                "query": "What?",
                "category": "vague_question",
                "expected_behavior": "clarification_request",
                "expected_intent": "information_retrieval",
                "expected_complexity": "basic", 
                "min_keywords": 0,
                "description": "Vague question should request clarification"
            },
            {
                "query": "...",
                "category": "punctuation_only",
                "expected_behavior": "graceful_fallback",
                "expected_intent": "information_retrieval",
                "expected_complexity": "basic",
                "min_keywords": 0,
                "description": "Punctuation-only should trigger fallback"
            },
            {
                "query": "audit stuff things",
                "category": "minimal_context",
                "expected_behavior": "context_inference",
                "expected_intent": "information_retrieval",
                "expected_complexity": "basic",
                "min_keywords": 2,
                "description": "Minimal context should infer audit intent"
            },
            {
                "query": "help me understand",
                "category": "help_request",
                "expected_behavior": "guidance_mode",
                "expected_intent": "information_retrieval",
                "expected_complexity": "basic",
                "min_keywords": 1,
                "description": "Help requests should activate guidance mode"
            }
        ]
        
        # Complex analysis scenarios - targeting 37.5% accuracy issue
        self.complex_analysis_scenarios = [
            # Relationship analysis queries
            {
                "query": "What is the relationship between IT general controls and application controls?",
                "category": "relationship_analysis",
                "expected_intent": "relationship_analysis",  # Should be relationship, not information_retrieval
                "expected_complexity": "advanced",  # Should be advanced, not intermediate
                "expected_frameworks": ["SOX", "ISO27001"],
                "expected_entities": ["IT general controls", "application controls"],
                "min_keywords": 3,
                "description": "Should identify relationship analysis intent and advanced complexity"
            },
            {
                "query": "How do risk assessments connect to control deficiencies and remediation plans?",
                "category": "multi_relationship",
                "expected_intent": "relationship_analysis",
                "expected_complexity": "advanced",
                "expected_frameworks": ["SOX"],
                "expected_entities": ["risk assessments", "control deficiencies", "remediation plans"],
                "min_keywords": 4,
                "description": "Multi-entity relationship analysis"
            },
            # Comparative analysis queries
            {
                "query": "Compare the effectiveness of access controls across all subsidiaries",
                "category": "comparative_analysis", 
                "expected_intent": "comparison",
                "expected_complexity": "advanced",
                "expected_frameworks": ["SOX"],
                "expected_entities": ["access controls", "subsidiaries"],
                "min_keywords": 3,
                "description": "Comparative analysis should be correctly identified"
            },
            {
                "query": "Analyze differences between SOX 404 and SOC2 Type II control requirements",
                "category": "framework_comparison",
                "expected_intent": "comparison",
                "expected_complexity": "advanced", 
                "expected_frameworks": ["SOX", "SOC2"],
                "expected_entities": ["SOX 404", "SOC2 Type II"],
                "min_keywords": 4,
                "description": "Framework comparison with specific control types"
            },
            # Multi-part complex queries
            {
                "query": "What material weaknesses were identified in Q3 financial controls and what remediation steps were recommended?",
                "category": "multi_part_query",
                "expected_intent": "information_retrieval",
                "expected_complexity": "advanced",
                "expected_frameworks": ["SOX"],
                "expected_entities": ["Q3", "material weaknesses", "financial controls", "remediation steps"],
                "min_keywords": 5,
                "description": "Multi-part query with temporal and procedural elements"
            },
            {
                "query": "Identify segregation of duties violations in the accounts payable process and assess their impact on SOX compliance",
                "category": "process_analysis",
                "expected_intent": "compliance_assessment",
                "expected_complexity": "advanced",
                "expected_frameworks": ["SOX"],
                "expected_entities": ["segregation of duties", "accounts payable", "violations"],
                "min_keywords": 6,
                "description": "Process-specific compliance assessment"
            }
        ]
        
        # Performance benchmarks
        self.performance_targets = {
            "edge_cases": {
                "target_accuracy": 0.70,  # Improve from 25% to 70%
                "current_baseline": 0.25
            },
            "complex_analysis": {
                "target_accuracy": 0.80,  # Improve from 37.5% to 80%
                "current_baseline": 0.375
            },
            "overall_target": 0.85  # Target overall improvement to 85%
        }
    
    async def run_robustness_test(self) -> Dict[str, Any]:
        """Run comprehensive robustness test."""
        logger.info("🚀 Starting Question Analysis Robustness Test")
        logger.info("🎯 Targeting edge case handling and complex query intent classification")
        
        results = {
            "test_timestamp": time.time(),
            "agent_info": {
                "agent_type": str(self.agent.agent_type),
                "model": self.agent.llm_model,
                "temperature": self.agent.temperature
            },
            "edge_case_results": {},
            "complex_analysis_results": {},
            "performance_analysis": {},
            "improvement_recommendations": [],
            "detailed_failures": []
        }
        
        # Test edge case handling
        logger.info("🛡️ Testing edge case handling...")
        edge_results = await self._test_edge_cases()
        results["edge_case_results"] = edge_results
        
        # Test complex analysis
        logger.info("🧠 Testing complex analysis scenarios...")
        complex_results = await self._test_complex_analysis()
        results["complex_analysis_results"] = complex_results
        
        # Analyze performance
        results["performance_analysis"] = self._analyze_performance(edge_results, complex_results)
        
        # Generate improvement recommendations
        results["improvement_recommendations"] = self._generate_recommendations(results)
        
        # Print comprehensive report
        self._print_results(results)
        
        return results
    
    async def _test_edge_cases(self) -> Dict[str, Any]:
        """Test edge case handling robustness."""
        results = {
            "total_scenarios": len(self.edge_case_scenarios),
            "successful_analyses": 0,
            "failed_analyses": 0,
            "accuracy_scores": [],
            "scenario_details": []
        }
        
        for i, scenario in enumerate(self.edge_case_scenarios):
            logger.info(f"  🧪 Testing edge case {i+1}/{len(self.edge_case_scenarios)}: {scenario['category']}")
            
            try:
                # Create agent context
                
                context = AgentContext(
                    inputs={
                        "question": scenario["query"]
                    },
                    agent_type=AgentType.QUESTION_ANALYZER,
                    timestamp=datetime.now(),
                    conversation_id=f"robustness_edge_{i+1}",
                    workflow_id=f"robustness_test_{int(time.time())}"
                )
                
                # Measure execution time
                start_time = time.time()
                result = await self.agent._execute_logic(context)
                execution_time = (time.time() - start_time) * 1000
                
                # Validate result
                is_valid, accuracy_score, validation_details = self._validate_edge_case_result(
                    result, scenario
                )
                
                scenario_detail = {
                    "scenario": scenario["category"],
                    "query": scenario["query"],
                    "description": scenario["description"],
                    "execution_time_ms": execution_time,
                    "success": result.get("analysis_status") == "completed",
                    "accuracy_score": accuracy_score,
                    "validation_details": validation_details,
                    "analysis_result": result,
                    "expected_behavior": scenario["expected_behavior"]
                }
                
                if is_valid:
                    results["successful_analyses"] += 1
                    results["accuracy_scores"].append(accuracy_score)
                    logger.info(f"    ✅ Passed with {accuracy_score:.1%} accuracy ({execution_time:.1f}ms)")
                else:
                    results["failed_analyses"] += 1
                    logger.warning(f"    ❌ Failed with {accuracy_score:.1%} accuracy ({execution_time:.1f}ms)")
                
                results["scenario_details"].append(scenario_detail)
                
            except Exception as e:
                logger.error(f"    💥 Exception in edge case {i+1}: {str(e)}")
                results["failed_analyses"] += 1
                results["scenario_details"].append({
                    "scenario": scenario["category"],
                    "query": scenario["query"],
                    "success": False,
                    "error": str(e),
                    "accuracy_score": 0.0
                })
        
        return results
    
    async def _test_complex_analysis(self) -> Dict[str, Any]:
        """Test complex analysis scenario handling."""
        results = {
            "total_scenarios": len(self.complex_analysis_scenarios),
            "successful_analyses": 0,
            "failed_analyses": 0,
            "accuracy_scores": [],
            "scenario_details": []
        }
        
        for i, scenario in enumerate(self.complex_analysis_scenarios):
            logger.info(f"  🔍 Testing complex scenario {i+1}/{len(self.complex_analysis_scenarios)}: {scenario['category']}")
            
            try:
                # Create agent context
                
                context = AgentContext(
                    inputs={
                        "question": scenario["query"]
                    },
                    agent_type=AgentType.QUESTION_ANALYZER,
                    timestamp=datetime.now(),
                    conversation_id=f"robustness_complex_{i+1}",
                    workflow_id=f"robustness_test_{int(time.time())}"
                )
                
                # Measure execution time
                start_time = time.time()
                result = await self.agent._execute_logic(context)
                execution_time = (time.time() - start_time) * 1000
                
                # Validate result
                is_valid, accuracy_score, validation_details = self._validate_complex_result(
                    result, scenario
                )
                
                scenario_detail = {
                    "scenario": scenario["category"],
                    "query": scenario["query"],
                    "description": scenario["description"],
                    "execution_time_ms": execution_time,
                    "success": result.get("analysis_status") == "completed",
                    "accuracy_score": accuracy_score,
                    "validation_details": validation_details,
                    "analysis_result": result,
                    "expected_intent": scenario["expected_intent"],
                    "expected_complexity": scenario["expected_complexity"]
                }
                
                if is_valid:
                    results["successful_analyses"] += 1
                    results["accuracy_scores"].append(accuracy_score)
                    logger.info(f"    ✅ Passed with {accuracy_score:.1%} accuracy ({execution_time:.1f}ms)")
                else:
                    results["failed_analyses"] += 1
                    logger.warning(f"    ❌ Failed with {accuracy_score:.1%} accuracy ({execution_time:.1f}ms)")
                
                results["scenario_details"].append(scenario_detail)
                
            except Exception as e:
                logger.error(f"    💥 Exception in complex scenario {i+1}: {str(e)}")
                results["failed_analyses"] += 1
                results["scenario_details"].append({
                    "scenario": scenario["category"],
                    "query": scenario["query"],
                    "success": False,
                    "error": str(e),
                    "accuracy_score": 0.0
                })
        
        return results
    
    def _validate_edge_case_result(self, result: Dict[str, Any], scenario: Dict[str, Any]) -> tuple[bool, float, Dict[str, Any]]:
        """Validate edge case analysis result."""
        validation = {
            "has_analysis": False,
            "graceful_handling": False,
            "appropriate_fallback": False,
            "reasonable_defaults": False
        }
        
        accuracy_components = []
        
        # Check if analysis exists
        if "analysis" in result and result["analysis"]:
            validation["has_analysis"] = True
            accuracy_components.append(1.0)
            analysis = result["analysis"]
            
            # Check graceful handling for edge cases
            if scenario["category"] in ["empty_query", "punctuation_only"]:
                # Should provide reasonable defaults
                if (analysis.get("intent") == scenario["expected_intent"] and
                    analysis.get("complexity") == scenario["expected_complexity"]):
                    validation["graceful_handling"] = True
                    accuracy_components.append(1.0)
                else:
                    accuracy_components.append(0.0)
            
            elif scenario["category"] in ["single_word", "minimal_context"]:
                # Should expand context appropriately
                keywords = analysis.get("search_keywords", [])
                if len(keywords) >= scenario["min_keywords"]:
                    validation["appropriate_fallback"] = True
                    accuracy_components.append(1.0)
                else:
                    accuracy_components.append(0.5)
            
            elif scenario["category"] in ["vague_question", "help_request"]:
                # Should handle vague queries gracefully
                if analysis.get("intent") == scenario["expected_intent"]:
                    validation["reasonable_defaults"] = True
                    accuracy_components.append(1.0)
                else:
                    accuracy_components.append(0.3)
            
            # Check basic structure
            required_fields = ["intent", "complexity", "search_keywords"]
            structure_score = sum(1 for field in required_fields if field in analysis) / len(required_fields)
            accuracy_components.append(structure_score)
            
        else:
            accuracy_components.extend([0.0, 0.0, 0.0])
        
        # Calculate overall accuracy
        accuracy_score = sum(accuracy_components) / len(accuracy_components) if accuracy_components else 0.0
        is_valid = accuracy_score >= 0.5  # 50% threshold for edge cases
        
        return is_valid, accuracy_score, validation
    
    def _validate_complex_result(self, result: Dict[str, Any], scenario: Dict[str, Any]) -> tuple[bool, float, Dict[str, Any]]:
        """Validate complex analysis result."""
        validation = {
            "has_analysis": False,
            "correct_intent": False,
            "correct_complexity": False,
            "appropriate_frameworks": False,
            "entity_extraction": False,
            "sufficient_keywords": False
        }
        
        accuracy_components = []
        
        if "analysis" in result and result["analysis"]:
            validation["has_analysis"] = True
            analysis = result["analysis"]
            
            # Check intent classification (most critical)
            actual_intent = analysis.get("intent", "")
            expected_intent = scenario["expected_intent"]
            if actual_intent == expected_intent:
                validation["correct_intent"] = True
                accuracy_components.append(1.0)
            else:
                # Partial credit for reasonable intent
                if actual_intent in ["information_retrieval", "comparison", "relationship_analysis", "compliance_assessment"]:
                    accuracy_components.append(0.5)
                else:
                    accuracy_components.append(0.0)
            
            # Check complexity assessment
            actual_complexity = analysis.get("complexity", "")
            expected_complexity = scenario["expected_complexity"]
            if actual_complexity == expected_complexity:
                validation["correct_complexity"] = True
                accuracy_components.append(1.0)
            elif actual_complexity in ["intermediate", "advanced"] and expected_complexity == "advanced":
                accuracy_components.append(0.7)  # Partial credit
            else:
                accuracy_components.append(0.0)
            
            # Check framework identification
            actual_frameworks = analysis.get("compliance_frameworks", [])
            expected_frameworks = scenario.get("expected_frameworks", [])
            if expected_frameworks:
                framework_overlap = len(set(actual_frameworks) & set(expected_frameworks))
                framework_score = framework_overlap / len(expected_frameworks) if expected_frameworks else 0
                validation["appropriate_frameworks"] = framework_score > 0.5
                accuracy_components.append(framework_score)
            else:
                accuracy_components.append(1.0)  # No frameworks expected
            
            # Check entity extraction
            actual_entities = analysis.get("entities", [])
            expected_entities = scenario.get("expected_entities", [])
            if expected_entities:
                # Check if key entities are captured (fuzzy matching)
                entity_matches = 0
                for expected_entity in expected_entities:
                    for actual_entity in actual_entities:
                        if expected_entity.lower() in actual_entity.lower() or actual_entity.lower() in expected_entity.lower():
                            entity_matches += 1
                            break
                entity_score = entity_matches / len(expected_entities) if expected_entities else 0
                validation["entity_extraction"] = entity_score > 0.5
                accuracy_components.append(entity_score)
            else:
                accuracy_components.append(1.0)
            
            # Check keyword sufficiency
            keywords = analysis.get("search_keywords", [])
            min_keywords = scenario.get("min_keywords", 1)
            if len(keywords) >= min_keywords:
                validation["sufficient_keywords"] = True
                accuracy_components.append(1.0)
            else:
                accuracy_components.append(len(keywords) / min_keywords if min_keywords > 0 else 0)
        
        else:
            accuracy_components = [0.0] * 5
        
        # Calculate weighted accuracy (intent and complexity are most important)
        weights = [2.0, 2.0, 1.0, 1.0, 1.0]  # Intent, complexity, frameworks, entities, keywords
        weighted_score = sum(score * weight for score, weight in zip(accuracy_components, weights))
        accuracy_score = weighted_score / sum(weights)
        
        is_valid = accuracy_score >= 0.6  # 60% threshold for complex scenarios
        
        return is_valid, accuracy_score, validation
    
    def _analyze_performance(self, edge_results: Dict[str, Any], complex_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall performance against targets."""
        analysis = {
            "edge_case_performance": {},
            "complex_analysis_performance": {},
            "overall_performance": {},
            "improvement_needed": {}
        }
        
        # Edge case performance
        edge_accuracy = statistics.mean(edge_results["accuracy_scores"]) if edge_results["accuracy_scores"] else 0.0
        edge_target = self.performance_targets["edge_cases"]["target_accuracy"]
        edge_baseline = self.performance_targets["edge_cases"]["current_baseline"]
        
        analysis["edge_case_performance"] = {
            "current_accuracy": edge_accuracy,
            "target_accuracy": edge_target,
            "baseline_accuracy": edge_baseline,
            "improvement_from_baseline": edge_accuracy - edge_baseline,
            "gap_to_target": edge_target - edge_accuracy,
            "meets_target": edge_accuracy >= edge_target
        }
        
        # Complex analysis performance
        complex_accuracy = statistics.mean(complex_results["accuracy_scores"]) if complex_results["accuracy_scores"] else 0.0
        complex_target = self.performance_targets["complex_analysis"]["target_accuracy"]
        complex_baseline = self.performance_targets["complex_analysis"]["current_baseline"]
        
        analysis["complex_analysis_performance"] = {
            "current_accuracy": complex_accuracy,
            "target_accuracy": complex_target,
            "baseline_accuracy": complex_baseline,
            "improvement_from_baseline": complex_accuracy - complex_baseline,
            "gap_to_target": complex_target - complex_accuracy,
            "meets_target": complex_accuracy >= complex_target
        }
        
        # Overall performance
        total_scenarios = edge_results["total_scenarios"] + complex_results["total_scenarios"]
        total_successful = edge_results["successful_analyses"] + complex_results["successful_analyses"]
        overall_accuracy = (edge_accuracy + complex_accuracy) / 2
        overall_target = self.performance_targets["overall_target"]
        
        analysis["overall_performance"] = {
            "total_scenarios": total_scenarios,
            "successful_scenarios": total_successful,
            "success_rate": total_successful / total_scenarios if total_scenarios > 0 else 0,
            "overall_accuracy": overall_accuracy,
            "target_accuracy": overall_target,
            "gap_to_target": overall_target - overall_accuracy,
            "meets_target": overall_accuracy >= overall_target
        }
        
        return analysis
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate specific improvement recommendations."""
        recommendations = []
        
        performance = results["performance_analysis"]
        edge_perf = performance["edge_case_performance"]
        complex_perf = performance["complex_analysis_performance"]
        
        # Edge case recommendations
        if not edge_perf["meets_target"]:
            gap = edge_perf["gap_to_target"]
            if gap > 0.3:
                recommendations.append("CRITICAL: Implement robust fallback analysis for edge cases (empty/minimal queries)")
                recommendations.append("Add input validation and query expansion for single-word queries")
            elif gap > 0.1:
                recommendations.append("Enhance graceful degradation for vague and minimal queries")
        
        # Complex analysis recommendations
        if not complex_perf["meets_target"]:
            gap = complex_perf["gap_to_target"]
            if gap > 0.3:
                recommendations.append("CRITICAL: Improve intent classification for relationship and comparison queries")
                recommendations.append("Enhance complexity assessment - many advanced queries marked as intermediate")
            elif gap > 0.1:
                recommendations.append("Fine-tune entity extraction for complex multi-part queries")
        
        # Specific failure pattern recommendations
        edge_details = results["edge_case_results"]["scenario_details"]
        complex_details = results["complex_analysis_results"]["scenario_details"]
        
        # Analyze specific failure patterns
        low_accuracy_edge = [d for d in edge_details if d.get("accuracy_score", 0) < 0.5]
        low_accuracy_complex = [d for d in complex_details if d.get("accuracy_score", 0) < 0.6]
        
        if low_accuracy_edge:
            recommendations.append(f"Fix {len(low_accuracy_edge)} specific edge case failures: {', '.join([d['scenario'] for d in low_accuracy_edge[:3]])}")
        
        if low_accuracy_complex:
            recommendations.append(f"Fix {len(low_accuracy_complex)} specific complex analysis failures: {', '.join([d['scenario'] for d in low_accuracy_complex[:3]])}")
        
        return recommendations
    
    def _print_results(self, results: Dict[str, Any]) -> None:
        """Print comprehensive test results."""
        print("\n" + "="*100)
        print("🎯 QUESTION ANALYSIS ROBUSTNESS TEST RESULTS")
        print("="*100)
        
        performance = results["performance_analysis"]
        
        # Overall status
        overall_perf = performance["overall_performance"]
        status = "✅ MEETS TARGET" if overall_perf["meets_target"] else "❌ NEEDS IMPROVEMENT"
        print(f"📊 OVERALL STATUS: {status}")
        print(f"🎯 Overall Accuracy: {overall_perf['overall_accuracy']:.1%} (Target: {overall_perf['target_accuracy']:.1%})")
        print(f"📈 Success Rate: {overall_perf['success_rate']:.1%}")
        print(f"📊 Gap to Target: {overall_perf['gap_to_target']:.1%}")
        
        # Edge case performance
        edge_perf = performance["edge_case_performance"]
        edge_status = "✅" if edge_perf["meets_target"] else "❌"
        print(f"\n🛡️ EDGE CASE HANDLING: {edge_status}")
        print(f"   📊 Current: {edge_perf['current_accuracy']:.1%} | Target: {edge_perf['target_accuracy']:.1%}")
        print(f"   📈 Improvement from baseline: {edge_perf['improvement_from_baseline']:+.1%}")
        print(f"   📊 Gap to target: {edge_perf['gap_to_target']:.1%}")
        
        # Complex analysis performance
        complex_perf = performance["complex_analysis_performance"]
        complex_status = "✅" if complex_perf["meets_target"] else "❌"
        print(f"\n🧠 COMPLEX ANALYSIS: {complex_status}")
        print(f"   📊 Current: {complex_perf['current_accuracy']:.1%} | Target: {complex_perf['target_accuracy']:.1%}")
        print(f"   📈 Improvement from baseline: {complex_perf['improvement_from_baseline']:+.1%}")
        print(f"   📊 Gap to target: {complex_perf['gap_to_target']:.1%}")
        
        # Detailed scenario results
        print(f"\n📋 EDGE CASE SCENARIO BREAKDOWN:")
        for detail in results["edge_case_results"]["scenario_details"]:
            status = "✅" if detail.get("accuracy_score", 0) >= 0.5 else "❌"
            accuracy = detail.get("accuracy_score", 0)
            scenario = detail.get("scenario", "unknown")
            print(f"   {status} {scenario}: {accuracy:.1%}")
        
        print(f"\n📋 COMPLEX ANALYSIS SCENARIO BREAKDOWN:")
        for detail in results["complex_analysis_results"]["scenario_details"]:
            status = "✅" if detail.get("accuracy_score", 0) >= 0.6 else "❌"
            accuracy = detail.get("accuracy_score", 0)
            scenario = detail.get("scenario", "unknown")
            print(f"   {status} {scenario}: {accuracy:.1%}")
        
        # Improvement recommendations
        recommendations = results["improvement_recommendations"]
        if recommendations:
            print(f"\n💡 IMPROVEMENT RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("="*100)
        print("✅ QUESTION ANALYSIS ROBUSTNESS TEST COMPLETED")
        print("="*100)


async def main():
    """Run the robustness test."""
    test = QuestionAnalysisRobustnessTest()
    
    # Run comprehensive test
    results = await test.run_robustness_test()
    
    # Save detailed results
    output_file = Path(__file__).parent / "question_analysis_robustness_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📊 Detailed results saved to: {output_file}")
    
    # Return appropriate exit code based on performance
    overall_perf = results["performance_analysis"]["overall_performance"]
    success = overall_perf["meets_target"]
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
