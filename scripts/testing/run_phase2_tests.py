#!/usr/bin/env python3
"""
Phase 2 Test Runner and Optimization Analysis

This script runs all Phase 2 tests and provides comprehensive optimization
recommendations based on the results.

Tests included:
1. Question Analysis Agent Test
2. Context Retrieval Agent Test  
3. Classification Enhancement Test
4. Phase 2 Integration Test

Provides optimization insights for:
- Performance bottlenecks
- Accuracy improvements
- Integration optimizations
- Component-specific recommendations
"""

import asyncio
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Phase2TestRunner:
    """Comprehensive Phase 2 test runner with optimization analysis."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.test_scripts = {
            "question_analysis": {
                "script": "test_question_analysis_agent.py",
                "name": "Question Analysis Agent",
                "weight": 0.3  # Weight in overall score
            },
            "context_retrieval": {
                "script": "test_context_retrieval_agent.py", 
                "name": "Context Retrieval Agent",
                "weight": 0.3
            },
            "classification_enhancement": {
                "script": "test_classification_enhancement.py",
                "name": "Classification Enhancement",
                "weight": 0.2
            },
            "phase2_integration": {
                "script": "test_phase2_integration.py",
                "name": "Phase 2 Integration",
                "weight": 0.2
            }
        }
        
        self.results_dir = Path(__file__).parent
        self.optimization_thresholds = {
            "excellent": 0.9,
            "good": 0.8,
            "needs_improvement": 0.7
        }
    
    async def run_all_phase2_tests(self) -> Dict[str, Any]:
        """Run all Phase 2 tests and collect results."""
        logger.info("🚀 Starting Comprehensive Phase 2 Testing")
        logger.info("📊 Running all Phase 2 component tests...")
        
        overall_results = {
            "test_timestamp": time.time(),
            "test_results": {},
            "execution_summary": {},
            "optimization_analysis": {},
            "recommendations": {}
        }
        
        successful_tests = 0
        total_tests = len(self.test_scripts)
        test_scores = {}
        
        for test_id, test_config in self.test_scripts.items():
            logger.info(f"\n📋 Running {test_config['name']}...")
            
            test_result = await self._run_single_test(test_id, test_config)
            overall_results["test_results"][test_id] = test_result
            
            if test_result["success"]:
                successful_tests += 1
                test_scores[test_id] = test_result.get("score", 0.5)
            else:
                test_scores[test_id] = 0.0
            
            logger.info(f"    {'✅' if test_result['success'] else '❌'} {test_config['name']}: "
                       f"{'PASSED' if test_result['success'] else 'FAILED'}")
        
        # Calculate execution summary
        overall_results["execution_summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "overall_score": self._calculate_weighted_score(test_scores),
            "test_scores": test_scores
        }
        
        # Perform optimization analysis
        overall_results["optimization_analysis"] = self._analyze_optimization_opportunities(overall_results)
        
        # Generate recommendations
        overall_results["recommendations"] = self._generate_comprehensive_recommendations(overall_results)
        
        # Print comprehensive results
        self._print_comprehensive_results(overall_results)
        
        return overall_results
    
    async def _run_single_test(self, test_id: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test script and collect results."""
        script_path = self.results_dir / test_config["script"]
        
        test_result = {
            "test_id": test_id,
            "test_name": test_config["name"],
            "success": False,
            "exit_code": None,
            "execution_time_ms": 0,
            "score": 0.0,
            "detailed_results": {},
            "errors": []
        }
        
        try:
            start_time = time.time()
            
            # Run the test script
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, cwd=project_root)
            
            execution_time = (time.time() - start_time) * 1000
            test_result["execution_time_ms"] = execution_time
            test_result["exit_code"] = result.returncode
            test_result["success"] = result.returncode == 0
            
            # Try to load detailed results from JSON file
            results_file = self.results_dir / f"{test_id}_test_results.json"
            if results_file.exists():
                try:
                    with open(results_file, 'r') as f:
                        detailed_results = json.load(f)
                    test_result["detailed_results"] = detailed_results
                    
                    # Extract score from detailed results
                    test_result["score"] = self._extract_test_score(test_id, detailed_results)
                    
                except Exception as e:
                    logger.warning(f"Failed to load detailed results for {test_id}: {str(e)}")
            
            # Capture any errors from stdout/stderr
            if result.stderr:
                test_result["errors"].append(result.stderr.strip())
            
            logger.info(f"    ⏱️ Execution time: {execution_time:.1f}ms")
            
        except Exception as e:
            test_result["errors"].append(f"Test execution failed: {str(e)}")
            logger.error(f"    ❌ Test execution failed: {str(e)}")
        
        return test_result
    
    def _extract_test_score(self, test_id: str, detailed_results: Dict[str, Any]) -> float:
        """Extract a normalized score from detailed test results."""
        try:
            if test_id == "question_analysis":
                performance = detailed_results.get("performance_metrics", {})
                accuracy = detailed_results.get("accuracy_analysis", {})
                
                success_rate = performance.get("success_rate", 0)
                overall_accuracy = accuracy.get("overall_accuracy", 0)
                
                return (success_rate + overall_accuracy) / 2
            
            elif test_id == "context_retrieval":
                performance = detailed_results.get("performance_metrics", {})
                strategy_accuracy = detailed_results.get("retrieval_strategy_accuracy", {})
                
                success_rate = performance.get("success_rate", 0)
                if strategy_accuracy:
                    avg_strategy_accuracy = sum(data.get("accuracy", 0) for data in strategy_accuracy.values()) / len(strategy_accuracy)
                else:
                    avg_strategy_accuracy = 0
                
                return (success_rate + avg_strategy_accuracy) / 2
            
            elif test_id == "classification_enhancement":
                performance = detailed_results.get("performance_metrics", {})
                
                overall_success = performance.get("overall_success_rate", 0)
                type_accuracy = performance.get("document_type_accuracy", 0)
                edge_case_handling = performance.get("edge_case_handling_rate", 0)
                
                return (overall_success + type_accuracy + edge_case_handling) / 3
            
            elif test_id == "phase2_integration":
                workflow_perf = detailed_results.get("workflow_performance", {})
                
                success_rate = workflow_perf.get("workflow_success_rate", 0)
                return success_rate
            
            else:
                return 0.5  # Default score
                
        except Exception as e:
            logger.warning(f"Failed to extract score for {test_id}: {str(e)}")
            return 0.0
    
    def _calculate_weighted_score(self, test_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score."""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for test_id, score in test_scores.items():
            if test_id in self.test_scripts:
                weight = self.test_scripts[test_id]["weight"]
                weighted_sum += score * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _analyze_optimization_opportunities(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze optimization opportunities across all tests."""
        analysis = {
            "performance_bottlenecks": [],
            "accuracy_gaps": [],
            "integration_issues": [],
            "component_rankings": {},
            "priority_areas": []
        }
        
        test_results = results["test_results"]
        test_scores = results["execution_summary"]["test_scores"]
        
        # Rank components by performance
        sorted_components = sorted(test_scores.items(), key=lambda x: x[1], reverse=True)
        analysis["component_rankings"] = {
            component: {"rank": i+1, "score": score}
            for i, (component, score) in enumerate(sorted_components)
        }
        
        # Identify bottlenecks and issues
        for test_id, score in test_scores.items():
            test_name = self.test_scripts[test_id]["name"]
            
            if score < self.optimization_thresholds["needs_improvement"]:
                analysis["priority_areas"].append(f"{test_name} needs significant improvement")
                
                if test_id == "question_analysis":
                    analysis["accuracy_gaps"].append("Question analysis accuracy is low")
                elif test_id == "context_retrieval":
                    analysis["performance_bottlenecks"].append("Context retrieval performance issues")
                elif test_id == "classification_enhancement":
                    analysis["accuracy_gaps"].append("Classification accuracy needs improvement")
                elif test_id == "phase2_integration":
                    analysis["integration_issues"].append("Phase 2 workflow integration problems")
            
            elif score < self.optimization_thresholds["good"]:
                if test_id == "phase2_integration":
                    analysis["integration_issues"].append("Phase 2 integration has room for improvement")
        
        # Check for execution time issues
        for test_id, test_result in test_results.items():
            execution_time = test_result.get("execution_time_ms", 0)
            if execution_time > 30000:  # 30 seconds
                analysis["performance_bottlenecks"].append(f"{test_result['test_name']} has slow execution time")
        
        return analysis
    
    def _generate_comprehensive_recommendations(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive optimization recommendations."""
        recommendations = {
            "immediate_actions": [],
            "short_term_improvements": [],
            "long_term_optimizations": [],
            "component_specific": {},
            "priority_order": []
        }
        
        overall_score = results["execution_summary"]["overall_score"]
        optimization_analysis = results["optimization_analysis"]
        
        # Overall recommendations based on score
        if overall_score >= self.optimization_thresholds["excellent"]:
            recommendations["immediate_actions"].append("✅ Excellent Phase 2 performance - maintain current quality")
            recommendations["short_term_improvements"].append("Consider minor optimizations for edge cases")
        
        elif overall_score >= self.optimization_thresholds["good"]:
            recommendations["immediate_actions"].append("✅ Good Phase 2 performance with optimization opportunities")
            recommendations["short_term_improvements"].append("Focus on identified bottlenecks and accuracy gaps")
        
        else:
            recommendations["immediate_actions"].append("🚨 Phase 2 needs significant improvement")
            recommendations["immediate_actions"].append("Review component implementations and error handling")
        
        # Component-specific recommendations
        component_rankings = optimization_analysis["component_rankings"]
        
        for test_id, ranking_data in component_rankings.items():
            test_name = self.test_scripts[test_id]["name"]
            score = ranking_data["score"]
            rank = ranking_data["rank"]
            
            component_recs = []
            
            if score < self.optimization_thresholds["needs_improvement"]:
                component_recs.append(f"🚨 Critical: {test_name} requires immediate attention")
                
                if test_id == "question_analysis":
                    component_recs.extend([
                        "Review and enhance question analysis prompt",
                        "Improve JSON parsing and error handling",
                        "Add more robust entity extraction"
                    ])
                
                elif test_id == "context_retrieval":
                    component_recs.extend([
                        "Optimize retrieval strategy selection logic",
                        "Improve advanced retrieval service integration",
                        "Enhance vector database query performance"
                    ])
                
                elif test_id == "classification_enhancement":
                    component_recs.extend([
                        "Improve classification accuracy with better training data",
                        "Enhance confidence scoring calibration",
                        "Strengthen edge case handling"
                    ])
                
                elif test_id == "phase2_integration":
                    component_recs.extend([
                        "Fix workflow integration issues",
                        "Improve component communication",
                        "Add better error recovery mechanisms"
                    ])
            
            elif score < self.optimization_thresholds["good"]:
                component_recs.append(f"⚠️ {test_name} has room for improvement")
                component_recs.append("Fine-tune performance and accuracy")
            
            else:
                component_recs.append(f"✅ {test_name} performing well")
                component_recs.append("Minor optimizations for edge cases")
            
            recommendations["component_specific"][test_id] = {
                "component": test_name,
                "score": score,
                "rank": rank,
                "recommendations": component_recs
            }
        
        # Priority order based on impact and urgency
        priority_components = sorted(
            component_rankings.items(),
            key=lambda x: (x[1]["score"], -self.test_scripts[x[0]]["weight"])
        )
        
        recommendations["priority_order"] = [
            {
                "component": self.test_scripts[test_id]["name"],
                "test_id": test_id,
                "score": ranking_data["score"],
                "weight": self.test_scripts[test_id]["weight"],
                "urgency": "High" if ranking_data["score"] < 0.7 else "Medium" if ranking_data["score"] < 0.8 else "Low"
            }
            for test_id, ranking_data in priority_components
        ]
        
        return recommendations
    
    def _print_comprehensive_results(self, results: Dict[str, Any]) -> None:
        """Print comprehensive Phase 2 test results and recommendations."""
        print("\n" + "="*120)
        print("📊 COMPREHENSIVE PHASE 2 TESTING RESULTS")
        print("="*120)
        
        # Execution summary
        summary = results["execution_summary"]
        overall_score = summary["overall_score"]
        
        status = (
            "🎉 EXCELLENT" if overall_score >= self.optimization_thresholds["excellent"]
            else "✅ GOOD" if overall_score >= self.optimization_thresholds["good"]
            else "⚠️ NEEDS IMPROVEMENT"
        )
        
        print(f"📊 OVERALL STATUS: {status}")
        print(f"📄 Tests Run: {summary['total_tests']}")
        print(f"✅ Successful: {summary['successful_tests']}")
        print(f"📊 Success Rate: {summary['success_rate']:.1%}")
        print(f"🎯 Overall Score: {overall_score:.1%}")
        
        # Individual test results
        print(f"\n📊 INDIVIDUAL TEST RESULTS:")
        print("-" * 120)
        
        for test_id, test_result in results["test_results"].items():
            test_name = test_result["test_name"]
            success = test_result["success"]
            score = test_result.get("score", 0)
            execution_time = test_result["execution_time_ms"]
            
            status = "✅" if success else "❌"
            print(f"\n{status} {test_name.upper()}")
            print(f"   📊 Score: {score:.1%}")
            print(f"   ⏱️ Execution Time: {execution_time:.1f}ms")
            print(f"   🎯 Status: {'PASSED' if success else 'FAILED'}")
            
            if test_result.get("errors"):
                print(f"   ❌ Errors: {'; '.join(test_result['errors'][:2])}")
        
        # Component rankings
        optimization = results["optimization_analysis"]
        rankings = optimization["component_rankings"]
        
        print(f"\n🏆 COMPONENT PERFORMANCE RANKING:")
        for test_id, ranking_data in sorted(rankings.items(), key=lambda x: x[1]["rank"]):
            test_name = self.test_scripts[test_id]["name"]
            rank = ranking_data["rank"]
            score = ranking_data["score"]
            
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "📊"
            print(f"   {medal} #{rank}: {test_name} ({score:.1%})")
        
        # Optimization analysis
        if optimization["priority_areas"]:
            print(f"\n🚨 PRIORITY AREAS FOR IMPROVEMENT:")
            for area in optimization["priority_areas"]:
                print(f"   • {area}")
        
        if optimization["performance_bottlenecks"]:
            print(f"\n⚡ PERFORMANCE BOTTLENECKS:")
            for bottleneck in optimization["performance_bottlenecks"]:
                print(f"   • {bottleneck}")
        
        if optimization["accuracy_gaps"]:
            print(f"\n🎯 ACCURACY GAPS:")
            for gap in optimization["accuracy_gaps"]:
                print(f"   • {gap}")
        
        # Recommendations
        recommendations = results["recommendations"]
        
        print(f"\n💡 COMPREHENSIVE RECOMMENDATIONS:")
        print("-" * 120)
        
        if recommendations["immediate_actions"]:
            print(f"\n🚨 IMMEDIATE ACTIONS:")
            for action in recommendations["immediate_actions"]:
                print(f"   • {action}")
        
        if recommendations["short_term_improvements"]:
            print(f"\n📋 SHORT-TERM IMPROVEMENTS (1-2 weeks):")
            for improvement in recommendations["short_term_improvements"]:
                print(f"   • {improvement}")
        
        # Component-specific recommendations
        print(f"\n🔧 COMPONENT-SPECIFIC RECOMMENDATIONS:")
        priority_order = recommendations["priority_order"]
        
        for component_data in priority_order:
            component = component_data["component"]
            urgency = component_data["urgency"]
            score = component_data["score"]
            
            urgency_icon = "🚨" if urgency == "High" else "⚠️" if urgency == "Medium" else "💡"
            
            print(f"\n{urgency_icon} {component.upper()} (Score: {score:.1%}, Urgency: {urgency})")
            
            test_id = component_data["test_id"]
            component_recs = recommendations["component_specific"][test_id]["recommendations"]
            
            for rec in component_recs:
                print(f"   • {rec}")
        
        print("\n" + "="*120)
        print("✅ COMPREHENSIVE PHASE 2 TESTING COMPLETED")
        print("="*120)


async def main():
    """Run comprehensive Phase 2 testing with optimization analysis."""
    runner = Phase2TestRunner()
    
    # Run all Phase 2 tests
    results = await runner.run_all_phase2_tests()
    
    # Save comprehensive results
    output_file = Path(__file__).parent / "phase2_comprehensive_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📊 Comprehensive results saved to: {output_file}")
    
    # Return exit code based on overall performance
    overall_score = results["execution_summary"]["overall_score"]
    if overall_score >= runner.optimization_thresholds["good"]:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs improvement


if __name__ == "__main__":
    asyncio.run(main())
