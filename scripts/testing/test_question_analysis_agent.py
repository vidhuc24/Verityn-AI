#!/usr/bin/env python3
"""
Question Analysis Agent Test for Verityn AI

This test validates the QuestionAnalysisAgent's ability to:
1. Analyze user questions and determine intent accurately
2. Extract key entities and compliance frameworks
3. Generate appropriate search keywords
4. Classify query complexity correctly
5. Handle edge cases and malformed queries

Follows Verityn AI testing standards:
- Uses real audit questions from sox_test_documents/
- Tests realistic query scenarios
- Validates JSON response structure
- Measures analysis accuracy and performance
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

from backend.app.agents.specialized_agents import QuestionAnalysisAgent
from backend.app.agents.base_agent import AgentContext

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QuestionAnalysisAgentTest:
    """Comprehensive test suite for QuestionAnalysisAgent."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.agent = QuestionAnalysisAgent(verbose=True)
        
        # Test question categories based on real audit scenarios
        self.test_questions = {
            "basic_information": [
                "What are the key findings?",
                "What controls were tested?",
                "What compliance issues were found?"
            ],
            
            "compliance_specific": [
                "What SOX 404 controls were tested for revenue recognition?",
                "Are there any material weaknesses in financial reporting controls?"
            ],
            
            "entity_extraction": [
                "What access violations did John Smith have in December 2024?",
                "Show me Amazon's quarterly financial reconciliation results"
            ],
            
            "complex_analysis": [
                "Compare the effectiveness of access controls across all subsidiaries",
                "What is the relationship between IT general controls and application controls?"
            ],
            
            "edge_cases": [
                "",  # Empty query
                "controls",  # Single word
                "What?"  # Vague question
            ]
        }
        
        # Expected analysis patterns for validation
        self.expected_patterns = {
            "basic_information": {
                "intent": "information_retrieval",
                "complexity": ["basic", "intermediate"],
                "frameworks": ["SOX", "General"],
                "entities_expected": False
            },
            "compliance_specific": {
                "intent": ["compliance_check", "information_retrieval"],
                "complexity": ["intermediate", "advanced"],
                "frameworks": ["SOX", "SOC2", "ISO27001", "PCI-DSS"],
                "entities_expected": True
            },
            "entity_extraction": {
                "intent": "information_retrieval",
                "complexity": ["intermediate", "advanced"],
                "frameworks": ["SOX", "General"],
                "entities_expected": True
            },
            "complex_analysis": {
                "intent": ["document_analysis", "comparison"],
                "complexity": "advanced",
                "frameworks": ["SOX", "General"],
                "entities_expected": False
            }
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive question analysis tests."""
        logger.info("🚀 Starting Question Analysis Agent Test")
        logger.info("📊 Testing query intent analysis and entity extraction")
        
        results = {
            "test_timestamp": time.time(),
            "agent_info": {
                "agent_type": str(self.agent.agent_type),
                "model": self.agent.llm_model,
                "temperature": self.agent.temperature
            },
            "test_categories": {},
            "performance_metrics": {},
            "accuracy_analysis": {},
            "edge_case_handling": {},
            "detailed_results": []
        }
        
        # Test each category
        total_questions = 0
        successful_analyses = 0
        analysis_times = []
        
        for category, questions in self.test_questions.items():
            logger.info(f"\n📋 Testing category: {category}")
            category_results = await self._test_question_category(category, questions)
            results["test_categories"][category] = category_results
            
            # Update overall metrics
            total_questions += len(questions)
            successful_analyses += category_results["successful_analyses"]
            analysis_times.extend(category_results["analysis_times"])
            results["detailed_results"].extend(category_results["question_details"])
        
        # Calculate performance metrics
        results["performance_metrics"] = {
            "total_questions": total_questions,
            "success_rate": successful_analyses / total_questions if total_questions > 0 else 0,
            "avg_analysis_time_ms": statistics.mean(analysis_times) if analysis_times else 0,
            "max_analysis_time_ms": max(analysis_times) if analysis_times else 0,
            "min_analysis_time_ms": min(analysis_times) if analysis_times else 0
        }
        
        # Analyze accuracy patterns
        results["accuracy_analysis"] = self._analyze_accuracy(results["detailed_results"])
        
        # Analyze edge case handling
        edge_case_results = results["test_categories"].get("edge_cases", {})
        results["edge_case_handling"] = self._analyze_edge_cases(edge_case_results)
        
        # Print comprehensive results
        self._print_results(results)
        
        return results
    
    async def _test_question_category(self, category: str, questions: List[str]) -> Dict[str, Any]:
        """Test a specific category of questions."""
        category_results = {
            "category": category,
            "total_questions": len(questions),
            "successful_analyses": 0,
            "failed_analyses": 0,
            "analysis_times": [],
            "accuracy_scores": [],
            "question_details": []
        }
        
        for i, question in enumerate(questions, 1):
            logger.info(f"  🔍 Testing question {i}/{len(questions)}: '{question[:60]}...'")
            
            try:
                # Create agent context
                from datetime import datetime
                context = AgentContext(
                    inputs={"question": question, "conversation_id": f"test_{category}_{i}"},
                    agent_type=self.agent.agent_type,
                    timestamp=datetime.now(),
                    conversation_id=f"test_{category}_{i}",
                    workflow_id=f"test_workflow_{category}_{i}"
                )
                
                # Measure analysis time
                start_time = time.time()
                analysis_result = await self.agent._execute_logic(context)
                analysis_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # Validate analysis result
                is_valid, validation_details = self._validate_analysis_result(analysis_result, question)
                
                # Calculate accuracy score for this question
                accuracy_score = self._calculate_accuracy_score(
                    analysis_result, question, category
                )
                
                question_detail = {
                    "question": question,
                    "category": category,
                    "analysis_time_ms": analysis_time,
                    "success": is_valid,
                    "analysis_result": analysis_result,
                    "validation_details": validation_details,
                    "accuracy_score": accuracy_score
                }
                
                if is_valid:
                    category_results["successful_analyses"] += 1
                    category_results["analysis_times"].append(analysis_time)
                    category_results["accuracy_scores"].append(accuracy_score)
                    
                    logger.info(f"    ✅ Analysis completed in {analysis_time:.1f}ms (accuracy: {accuracy_score:.1%})")
                else:
                    category_results["failed_analyses"] += 1
                    logger.warning(f"    ❌ Analysis failed: {validation_details}")
                
                category_results["question_details"].append(question_detail)
                
            except Exception as e:
                logger.error(f"    ❌ Exception during analysis: {str(e)}")
                category_results["failed_analyses"] += 1
                category_results["question_details"].append({
                    "question": question,
                    "category": category,
                    "success": False,
                    "error": str(e)
                })
        
        return category_results
    
    def _validate_analysis_result(self, result: Dict[str, Any], question: str) -> tuple[bool, Dict[str, Any]]:
        """Validate the structure and content of analysis results."""
        validation = {
            "has_analysis": False,
            "required_fields": {},
            "json_structure": False,
            "reasonable_values": {}
        }
        
        # Check if analysis exists
        if "analysis" not in result or not result["analysis"]:
            return False, validation
        
        validation["has_analysis"] = True
        analysis = result["analysis"]
        
        # Check required fields
        required_fields = ["intent", "complexity", "required_documents", 
                          "compliance_frameworks", "entities", "search_keywords"]
        
        for field in required_fields:
            validation["required_fields"][field] = field in analysis
        
        # Check if all required fields are present
        all_fields_present = all(validation["required_fields"].values())
        validation["json_structure"] = all_fields_present
        
        if not all_fields_present:
            return False, validation
        
        # Validate reasonable values
        validation["reasonable_values"] = {
            "intent_valid": analysis.get("intent") in [
                "information_retrieval", "compliance_check", "document_analysis", 
                "comparison", "risk_assessment"
            ],
            "complexity_valid": analysis.get("complexity") in ["basic", "intermediate", "advanced"],
            "has_search_keywords": len(analysis.get("search_keywords", [])) > 0,
            "frameworks_reasonable": len(analysis.get("compliance_frameworks", [])) <= 5,
            "entities_reasonable": len(analysis.get("entities", [])) <= 10
        }
        
        # Overall validation
        is_valid = (
            validation["has_analysis"] and 
            validation["json_structure"] and
            validation["reasonable_values"]["intent_valid"] and
            validation["reasonable_values"]["complexity_valid"]
        )
        
        return is_valid, validation
    
    def _calculate_accuracy_score(self, result: Dict[str, Any], question: str, category: str) -> float:
        """Calculate accuracy score based on expected patterns."""
        if "analysis" not in result:
            return 0.0
        
        analysis = result["analysis"]
        expected = self.expected_patterns.get(category, {})
        score = 0.0
        total_checks = 0
        
        # Check intent accuracy
        expected_intents = expected.get("intent", [])
        if isinstance(expected_intents, str):
            expected_intents = [expected_intents]
        
        if expected_intents and analysis.get("intent") in expected_intents:
            score += 0.25
        total_checks += 0.25
        
        # Check complexity accuracy
        expected_complexity = expected.get("complexity", [])
        if isinstance(expected_complexity, str):
            expected_complexity = [expected_complexity]
        
        if expected_complexity and analysis.get("complexity") in expected_complexity:
            score += 0.25
        total_checks += 0.25
        
        # Check framework detection
        expected_frameworks = expected.get("frameworks", [])
        detected_frameworks = analysis.get("compliance_frameworks", [])
        
        if expected_frameworks:
            framework_overlap = len(set(expected_frameworks) & set(detected_frameworks))
            if framework_overlap > 0:
                score += 0.25 * (framework_overlap / len(expected_frameworks))
        total_checks += 0.25
        
        # Check entity extraction expectation
        entities_expected = expected.get("entities_expected", False)
        has_entities = len(analysis.get("entities", [])) > 0
        
        if (entities_expected and has_entities) or (not entities_expected):
            score += 0.25
        total_checks += 0.25
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _analyze_accuracy(self, detailed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze accuracy patterns across all test results."""
        accuracy_analysis = {
            "overall_accuracy": 0.0,
            "accuracy_by_category": {},
            "common_failures": [],
            "high_performing_patterns": [],
            "improvement_areas": []
        }
        
        # Calculate overall accuracy
        successful_results = [r for r in detailed_results if r.get("success", False)]
        if successful_results:
            accuracy_scores = [r.get("accuracy_score", 0) for r in successful_results]
            accuracy_analysis["overall_accuracy"] = statistics.mean(accuracy_scores)
        
        # Accuracy by category
        categories = set(r.get("category") for r in detailed_results)
        for category in categories:
            category_results = [r for r in detailed_results if r.get("category") == category and r.get("success", False)]
            if category_results:
                category_scores = [r.get("accuracy_score", 0) for r in category_results]
                accuracy_analysis["accuracy_by_category"][category] = {
                    "avg_accuracy": statistics.mean(category_scores),
                    "success_rate": len(category_results) / len([r for r in detailed_results if r.get("category") == category])
                }
        
        # Identify patterns
        low_accuracy_results = [r for r in successful_results if r.get("accuracy_score", 0) < 0.5]
        high_accuracy_results = [r for r in successful_results if r.get("accuracy_score", 0) > 0.8]
        
        # Common failure patterns
        if low_accuracy_results:
            accuracy_analysis["common_failures"] = [
                f"Low accuracy in {r.get('category')} questions" 
                for r in low_accuracy_results[:3]
            ]
        
        # High performing patterns
        if high_accuracy_results:
            accuracy_analysis["high_performing_patterns"] = [
                f"High accuracy in {r.get('category')} questions"
                for r in high_accuracy_results[:3]
            ]
        
        return accuracy_analysis
    
    def _analyze_edge_cases(self, edge_case_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well the agent handles edge cases."""
        edge_analysis = {
            "empty_query_handling": False,
            "single_word_handling": False,
            "vague_query_handling": False,
            "overly_broad_handling": False,
            "overly_specific_handling": False,
            "overall_robustness": 0.0
        }
        
        question_details = edge_case_results.get("question_details", [])
        
        for detail in question_details:
            question = detail.get("question", "")
            success = detail.get("success", False)
            
            if question == "":
                edge_analysis["empty_query_handling"] = success
            elif question == "controls":
                edge_analysis["single_word_handling"] = success
            elif question == "What?":
                edge_analysis["vague_query_handling"] = success
            elif "everything about everything" in question:
                edge_analysis["overly_broad_handling"] = success
            elif len(question) > 200:  # Overly specific
                edge_analysis["overly_specific_handling"] = success
        
        # Calculate overall robustness
        robustness_checks = [
            edge_analysis["empty_query_handling"],
            edge_analysis["single_word_handling"], 
            edge_analysis["vague_query_handling"],
            edge_analysis["overly_broad_handling"],
            edge_analysis["overly_specific_handling"]
        ]
        
        edge_analysis["overall_robustness"] = sum(robustness_checks) / len(robustness_checks)
        
        return edge_analysis
    
    def _print_results(self, results: Dict[str, Any]) -> None:
        """Print comprehensive test results."""
        print("\n" + "="*100)
        print("📊 QUESTION ANALYSIS AGENT TEST RESULTS")
        print("="*100)
        
        # Agent info
        agent_info = results["agent_info"]
        print(f"🤖 Agent: {agent_info['agent_type']}")
        print(f"🧠 Model: {agent_info['model']} (temp: {agent_info['temperature']})")
        
        # Performance metrics
        metrics = results["performance_metrics"]
        print(f"\n📊 PERFORMANCE METRICS:")
        print(f"   📄 Questions Tested: {metrics['total_questions']}")
        print(f"   ✅ Success Rate: {metrics['success_rate']:.1%}")
        print(f"   ⏱️ Avg Analysis Time: {metrics['avg_analysis_time_ms']:.1f}ms")
        print(f"   🚀 Fastest Analysis: {metrics['min_analysis_time_ms']:.1f}ms")
        print(f"   🐌 Slowest Analysis: {metrics['max_analysis_time_ms']:.1f}ms")
        
        # Accuracy analysis
        accuracy = results["accuracy_analysis"]
        print(f"\n🎯 ACCURACY ANALYSIS:")
        print(f"   📊 Overall Accuracy: {accuracy['overall_accuracy']:.1%}")
        
        print(f"   📋 Accuracy by Category:")
        for category, data in accuracy["accuracy_by_category"].items():
            print(f"      {category}: {data['avg_accuracy']:.1%} (success: {data['success_rate']:.1%})")
        
        # Edge case handling
        edge_cases = results["edge_case_handling"]
        print(f"\n🛡️ EDGE CASE HANDLING:")
        print(f"   📊 Overall Robustness: {edge_cases['overall_robustness']:.1%}")
        print(f"   🔍 Empty Query: {'✅' if edge_cases['empty_query_handling'] else '❌'}")
        print(f"   🔍 Single Word: {'✅' if edge_cases['single_word_handling'] else '❌'}")
        print(f"   🔍 Vague Query: {'✅' if edge_cases['vague_query_handling'] else '❌'}")
        print(f"   🔍 Overly Broad: {'✅' if edge_cases['overly_broad_handling'] else '❌'}")
        print(f"   🔍 Overly Specific: {'✅' if edge_cases['overly_specific_handling'] else '❌'}")
        
        # Category breakdown
        print(f"\n📊 DETAILED RESULTS BY CATEGORY:")
        print("-" * 100)
        
        for category, data in results["test_categories"].items():
            success_rate = data["successful_analyses"] / data["total_questions"] if data["total_questions"] > 0 else 0
            status = "✅" if success_rate > 0.8 else "🟡" if success_rate > 0.6 else "❌"
            
            print(f"\n{status} {category.upper().replace('_', ' ')}")
            print(f"   📄 Questions: {data['total_questions']}")
            print(f"   ✅ Successful: {data['successful_analyses']} ({success_rate:.1%})")
            print(f"   ❌ Failed: {data['failed_analyses']}")
            
            if data["analysis_times"]:
                avg_time = statistics.mean(data["analysis_times"])
                print(f"   ⏱️ Avg Time: {avg_time:.1f}ms")
            
            if data["accuracy_scores"]:
                avg_accuracy = statistics.mean(data["accuracy_scores"])
                print(f"   🎯 Avg Accuracy: {avg_accuracy:.1%}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        overall_success = metrics["success_rate"]
        overall_accuracy = accuracy["overall_accuracy"]
        
        if overall_success > 0.9 and overall_accuracy > 0.8:
            print("   🎉 Excellent performance! Question analysis is working well.")
        elif overall_success > 0.7 and overall_accuracy > 0.6:
            print("   ✅ Good performance with room for improvement:")
            if overall_accuracy < 0.8:
                print("      - Fine-tune analysis prompt for better accuracy")
                print("      - Improve entity extraction patterns")
        else:
            print("   ⚠️ Performance needs improvement:")
            print("      - Review and enhance analysis prompt")
            print("      - Add more robust error handling")
            print("      - Improve JSON parsing and fallback logic")
        
        if edge_cases["overall_robustness"] < 0.6:
            print("      - Strengthen edge case handling")
            print("      - Add input validation and sanitization")
        
        print("="*100)
        print("✅ QUESTION ANALYSIS AGENT TEST COMPLETED")
        print("="*100)


async def main():
    """Run the question analysis agent test."""
    test = QuestionAnalysisAgentTest()
    
    # Run comprehensive test
    results = await test.run_comprehensive_test()
    
    # Save detailed results
    output_file = Path(__file__).parent / "question_analysis_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📊 Detailed results saved to: {output_file}")
    
    # Return appropriate exit code based on success rate
    success_rate = results["performance_metrics"]["success_rate"]
    if success_rate > 0.8:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs improvement


if __name__ == "__main__":
    asyncio.run(main())
