#!/usr/bin/env python3
"""
Enhanced Classification Agent Test for Verityn AI

This test enhances the existing classification testing with:
1. Edge case handling (empty, malformed, ambiguous documents)
2. Confidence threshold validation
3. Document type accuracy across different formats
4. Compliance framework detection accuracy
5. Performance under various document conditions

Follows Verityn AI testing standards:
- Uses real audit documents from sox_test_documents/
- Tests edge cases with actual document variations
- Validates confidence scoring accuracy
- Measures classification consistency
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

from backend.app.services.classification_engine import ClassificationEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedClassificationTest:
    """Enhanced classification testing with edge cases and confidence validation."""
    
    def __init__(self):
        """Initialize the enhanced classification test."""
        self.classifier = ClassificationEngine()
        
        # Test document categories with expected classifications
        self.test_documents = {}
        self.expected_classifications = {}
        
        # Confidence thresholds for validation
        self.confidence_thresholds = {
            "high_confidence": 0.8,      # Clear, unambiguous documents
            "medium_confidence": 0.6,    # Somewhat ambiguous documents
            "low_confidence": 0.4,       # Ambiguous or edge case documents
            "minimum_acceptable": 0.3    # Minimum threshold for any classification
        }
        
        # Edge case scenarios to test
        self.edge_case_tests = {
            "empty_content": "",
            "minimal_content": "audit report",
            "mixed_content": "This document contains access review information as well as financial reconciliation data and risk assessment findings.",
            "non_audit_content": "This is a recipe for chocolate cake with flour, sugar, and eggs.",
            "technical_jargon": "API endpoint configuration for microservices architecture with Docker containers and Kubernetes orchestration.",
            "foreign_language": "Este es un documento de auditoría en español con controles internos.",
            "corrupted_text": "Aud1t R3p0rt w1th c0ntr0l5 4nd f1nd1ng5 @#$%^&*()",
            "very_long_content": "audit " * 1000 + "controls " * 1000 + "compliance " * 1000
        }
    
    async def run_enhanced_classification_test(self) -> Dict[str, Any]:
        """Run enhanced classification tests with edge cases and confidence validation."""
        logger.info("🚀 Starting Enhanced Classification Test")
        logger.info("📊 Testing classification accuracy, confidence, and edge cases")
        
        results = {
            "test_timestamp": time.time(),
            "classifier_info": {
                "model": "Classification Engine",
                "confidence_thresholds": self.confidence_thresholds
            },
            "document_classification_tests": {},
            "edge_case_tests": {},
            "confidence_analysis": {},
            "performance_metrics": {},
            "detailed_results": []
        }
        
        # Load and test real documents
        await self._load_test_documents()
        document_results = await self._test_document_classifications()
        results["document_classification_tests"] = document_results
        
        # Test edge cases
        edge_case_results = await self._test_edge_cases()
        results["edge_case_tests"] = edge_case_results
        
        # Analyze confidence patterns
        results["confidence_analysis"] = self._analyze_confidence_patterns(
            document_results, edge_case_results
        )
        
        # Calculate performance metrics
        results["performance_metrics"] = self._calculate_performance_metrics(
            document_results, edge_case_results
        )
        
        # Combine all detailed results
        results["detailed_results"] = (
            document_results.get("classification_details", []) +
            edge_case_results.get("edge_case_details", [])
        )
        
        # Print comprehensive results
        self._print_results(results)
        
        return results
    
    async def _load_test_documents(self) -> None:
        """Load test documents with known expected classifications."""
        logger.info("📄 Loading test documents...")
        
        # SOX test documents with expected types
        document_configs = [
            {
                "path": "data/sox_test_documents/sox_access_review_2024.txt",
                "expected_type": "access_review",
                "expected_framework": "SOX",
                "expected_confidence": "high"
            },
            {
                "path": "data/sox_test_documents/sox_internal_controls_2024.txt",
                "expected_type": "internal_controls",
                "expected_framework": "SOX",
                "expected_confidence": "high"
            },
            {
                "path": "data/sox_test_documents/sox_financial_controls_2024.txt",
                "expected_type": "financial_controls",
                "expected_framework": "SOX",
                "expected_confidence": "high"
            },
            {
                "path": "data/sox_test_documents/sox_risk_assessment_2024.txt",
                "expected_type": "risk_assessment",
                "expected_framework": "SOX",
                "expected_confidence": "high"
            }
        ]
        
        # Add JSON versions for format testing
        json_configs = [
            {
                "path": "data/sox_test_documents/json/sox_access_review_2024.json",
                "expected_type": "access_review",
                "expected_framework": "SOX",
                "expected_confidence": "medium"  # JSON might be harder to classify
            },
            {
                "path": "data/sox_test_documents/json/sox_internal_controls_2024.json",
                "expected_type": "internal_controls",
                "expected_framework": "SOX",
                "expected_confidence": "medium"
            }
        ]
        
        all_configs = document_configs + json_configs
        
        for config in all_configs:
            try:
                file_path = Path(config["path"])
                if file_path.exists():
                    if file_path.suffix == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Extract text content from JSON structure
                            content = self._extract_text_from_json(data)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    if content and content.strip():
                        doc_name = file_path.stem
                        self.test_documents[doc_name] = {
                            "content": content,
                            "format": file_path.suffix[1:],  # Remove the dot
                            "path": str(file_path)
                        }
                        self.expected_classifications[doc_name] = {
                            "document_type": config["expected_type"],
                            "compliance_framework": config["expected_framework"],
                            "expected_confidence_level": config["expected_confidence"]
                        }
                        logger.info(f"✅ Loaded {doc_name} ({len(content)} chars, {file_path.suffix})")
                
            except Exception as e:
                logger.error(f"❌ Failed to load {config['path']}: {str(e)}")
        
        logger.info(f"📊 Loaded {len(self.test_documents)} test documents")
    
    def _extract_text_from_json(self, json_data: Any) -> str:
        """Extract readable text content from JSON data."""
        if isinstance(json_data, dict):
            text_parts = []
            for key, value in json_data.items():
                if isinstance(value, str) and len(value) > 10:
                    text_parts.append(f"{key}: {value}")
                elif isinstance(value, (dict, list)):
                    nested_text = self._extract_text_from_json(value)
                    if nested_text:
                        text_parts.append(nested_text)
            return " ".join(text_parts)
        elif isinstance(json_data, list):
            text_parts = []
            for item in json_data:
                nested_text = self._extract_text_from_json(item)
                if nested_text:
                    text_parts.append(nested_text)
            return " ".join(text_parts)
        elif isinstance(json_data, str):
            return json_data
        else:
            return str(json_data)
    
    async def _test_document_classifications(self) -> Dict[str, Any]:
        """Test classification accuracy on real documents."""
        logger.info("🏷️ Testing document classifications...")
        
        results = {
            "total_documents": len(self.test_documents),
            "successful_classifications": 0,
            "failed_classifications": 0,
            "type_accuracy": 0,
            "framework_accuracy": 0,
            "confidence_distribution": {},
            "classification_details": []
        }
        
        correct_types = 0
        correct_frameworks = 0
        confidence_levels = []
        classification_times = []
        
        for doc_name, doc_data in self.test_documents.items():
            logger.info(f"  🔍 Classifying {doc_name}...")
            
            try:
                content = doc_data["content"]
                expected = self.expected_classifications[doc_name]
                
                # Measure classification time
                start_time = time.time()
                classification_result = await self.classifier.classify_document(content)
                classification_time = (time.time() - start_time) * 1000
                
                # Validate classification result
                is_successful, validation_details = self._validate_classification_result(
                    classification_result, expected
                )
                
                # Calculate accuracy scores
                type_correct = (
                    classification_result.get("document_type", "").lower() == 
                    expected["document_type"].lower()
                ) if classification_result else False
                
                # Check both singular and plural framework fields
                expected_framework = expected["compliance_framework"].lower()
                actual_frameworks = classification_result.get("compliance_frameworks", [])
                actual_framework = classification_result.get("compliance_framework", "")
                
                framework_correct = False
                if classification_result:
                    # Check if expected framework is in the frameworks array
                    if isinstance(actual_frameworks, list):
                        framework_correct = any(expected_framework in fw.lower() for fw in actual_frameworks)
                    # Fallback to check singular field
                    elif isinstance(actual_framework, str):
                        framework_correct = expected_framework in actual_framework.lower()
                    # Handle case where frameworks is a string
                    elif isinstance(actual_frameworks, str):
                        framework_correct = expected_framework in actual_frameworks.lower()
                
                confidence = classification_result.get("confidence", 0) if classification_result else 0
                confidence_appropriate = self._assess_confidence_appropriateness(
                    confidence, expected["expected_confidence_level"]
                )
                
                detail = {
                    "document": doc_name,
                    "format": doc_data["format"],
                    "classification_time_ms": classification_time,
                    "success": is_successful,
                    "expected": expected,
                    "actual": classification_result,
                    "type_correct": type_correct,
                    "framework_correct": framework_correct,
                    "confidence": confidence,
                    "confidence_appropriate": confidence_appropriate,
                    "validation_details": validation_details
                }
                
                if is_successful:
                    results["successful_classifications"] += 1
                    classification_times.append(classification_time)
                    confidence_levels.append(confidence)
                    
                    if type_correct:
                        correct_types += 1
                    if framework_correct:
                        correct_frameworks += 1
                    
                    logger.info(f"    ✅ Classified as {classification_result.get('document_type')} "
                              f"({confidence:.1%} confidence)")
                else:
                    results["failed_classifications"] += 1
                    logger.warning(f"    ❌ Classification failed: {validation_details}")
                
                results["classification_details"].append(detail)
                
            except Exception as e:
                logger.error(f"    ❌ Exception classifying {doc_name}: {str(e)}")
                results["failed_classifications"] += 1
                results["classification_details"].append({
                    "document": doc_name,
                    "success": False,
                    "error": str(e)
                })
        
        # Calculate accuracy rates
        total_docs = results["total_documents"]
        results["type_accuracy"] = correct_types / total_docs if total_docs > 0 else 0
        results["framework_accuracy"] = correct_frameworks / total_docs if total_docs > 0 else 0
        
        # Analyze confidence distribution
        if confidence_levels:
            results["confidence_distribution"] = {
                "avg_confidence": statistics.mean(confidence_levels),
                "min_confidence": min(confidence_levels),
                "max_confidence": max(confidence_levels),
                "std_confidence": statistics.stdev(confidence_levels) if len(confidence_levels) > 1 else 0
            }
        
        return results
    
    async def _test_edge_cases(self) -> Dict[str, Any]:
        """Test classification handling of edge cases."""
        logger.info("🛡️ Testing edge case handling...")
        
        results = {
            "total_edge_cases": len(self.edge_case_tests),
            "handled_gracefully": 0,
            "failed_edge_cases": 0,
            "edge_case_details": []
        }
        
        for case_name, content in self.edge_case_tests.items():
            logger.info(f"  🧪 Testing edge case: {case_name}")
            
            try:
                start_time = time.time()
                classification_result = await self.classifier.classify_document(content)
                classification_time = (time.time() - start_time) * 1000
                
                # Assess how gracefully the edge case was handled
                graceful_handling = self._assess_edge_case_handling(
                    case_name, content, classification_result
                )
                
                detail = {
                    "edge_case": case_name,
                    "content_length": len(content),
                    "classification_time_ms": classification_time,
                    "graceful_handling": graceful_handling,
                    "classification_result": classification_result,
                    "assessment": self._get_edge_case_assessment(case_name, classification_result)
                }
                
                if graceful_handling:
                    results["handled_gracefully"] += 1
                    logger.info(f"    ✅ Handled gracefully")
                else:
                    results["failed_edge_cases"] += 1
                    logger.warning(f"    ⚠️ Poor edge case handling")
                
                results["edge_case_details"].append(detail)
                
            except Exception as e:
                logger.error(f"    ❌ Exception on edge case {case_name}: {str(e)}")
                results["failed_edge_cases"] += 1
                results["edge_case_details"].append({
                    "edge_case": case_name,
                    "graceful_handling": False,
                    "error": str(e)
                })
        
        return results
    
    def _validate_classification_result(self, result: Optional[Dict[str, Any]], expected: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Validate classification result structure and content."""
        validation = {
            "has_result": result is not None,
            "has_document_type": False,
            "has_confidence": False,
            "confidence_reasonable": False,
            "has_framework": False
        }
        
        if not result:
            return False, validation
        
        validation["has_result"] = True
        
        # Check required fields
        validation["has_document_type"] = "document_type" in result and result["document_type"]
        validation["has_confidence"] = "confidence" in result and isinstance(result["confidence"], (int, float))
        validation["has_framework"] = "compliance_framework" in result and result["compliance_framework"]
        
        # Check confidence is reasonable (0-1 range)
        if validation["has_confidence"]:
            confidence = result["confidence"]
            validation["confidence_reasonable"] = 0 <= confidence <= 1
        
        # Overall validation
        is_valid = (
            validation["has_result"] and
            validation["has_document_type"] and
            validation["has_confidence"] and
            validation["confidence_reasonable"]
        )
        
        return is_valid, validation
    
    def _assess_confidence_appropriateness(self, confidence: float, expected_level: str) -> bool:
        """Assess if confidence level is appropriate for document type."""
        threshold_map = {
            "high": self.confidence_thresholds["high_confidence"],
            "medium": self.confidence_thresholds["medium_confidence"],
            "low": self.confidence_thresholds["low_confidence"]
        }
        
        expected_threshold = threshold_map.get(expected_level, self.confidence_thresholds["minimum_acceptable"])
        return confidence >= expected_threshold
    
    def _assess_edge_case_handling(self, case_name: str, content: str, result: Optional[Dict[str, Any]]) -> bool:
        """Assess how gracefully an edge case was handled."""
        if not result:
            # For some edge cases, returning None might be appropriate
            if case_name in ["empty_content", "non_audit_content", "corrupted_text"]:
                return True  # Graceful handling of obviously invalid content
            return False
        
        confidence = result.get("confidence", 0)
        document_type = result.get("document_type", "")
        
        # Assess based on edge case type
        if case_name == "empty_content":
            # Should either return None or very low confidence
            return confidence < 0.3
        
        elif case_name == "minimal_content":
            # Should have low confidence but still classify
            return 0.2 <= confidence <= 0.6
        
        elif case_name == "mixed_content":
            # Should classify with medium confidence
            return 0.4 <= confidence <= 0.8
        
        elif case_name == "non_audit_content":
            # Should either return None or classify as "unknown" with low confidence
            return confidence < 0.4 or "unknown" in document_type.lower()
        
        elif case_name == "technical_jargon":
            # Should have low confidence for non-audit technical content
            return confidence < 0.5
        
        elif case_name == "foreign_language":
            # Might still detect audit terms but with lower confidence
            return confidence < 0.7
        
        elif case_name == "corrupted_text":
            # Should have very low confidence
            return confidence < 0.3
        
        elif case_name == "very_long_content":
            # Should still classify but might have processing issues
            return confidence > 0.3 and document_type  # Just needs to complete
        
        return True  # Default to graceful if we get here
    
    def _get_edge_case_assessment(self, case_name: str, result: Optional[Dict[str, Any]]) -> str:
        """Get human-readable assessment of edge case handling."""
        if not result:
            if case_name in ["empty_content", "non_audit_content", "corrupted_text"]:
                return "Appropriately returned no classification"
            return "Failed to classify when it should have attempted"
        
        confidence = result.get("confidence", 0)
        document_type = result.get("document_type", "unknown")
        
        assessments = {
            "empty_content": f"Confidence {confidence:.1%} - should be very low",
            "minimal_content": f"Classified as {document_type} with {confidence:.1%} confidence",
            "mixed_content": f"Classified as {document_type} with {confidence:.1%} confidence - reasonable for mixed content",
            "non_audit_content": f"Classified as {document_type} with {confidence:.1%} confidence - should recognize non-audit content",
            "technical_jargon": f"Classified as {document_type} with {confidence:.1%} confidence - good for technical content",
            "foreign_language": f"Classified as {document_type} with {confidence:.1%} confidence - language barrier handled",
            "corrupted_text": f"Classified as {document_type} with {confidence:.1%} confidence - corruption detected",
            "very_long_content": f"Classified as {document_type} with {confidence:.1%} confidence - handled large content"
        }
        
        return assessments.get(case_name, f"Classified as {document_type} with {confidence:.1%} confidence")
    
    def _analyze_confidence_patterns(self, document_results: Dict[str, Any], edge_case_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze confidence scoring patterns."""
        analysis = {
            "confidence_calibration": {},
            "confidence_consistency": {},
            "edge_case_confidence": {}
        }
        
        # Analyze document confidence patterns
        doc_details = document_results.get("classification_details", [])
        successful_docs = [d for d in doc_details if d.get("success", False)]
        
        if successful_docs:
            confidences = [d["confidence"] for d in successful_docs]
            appropriate_confidences = [d for d in successful_docs if d.get("confidence_appropriate", False)]
            
            analysis["confidence_calibration"] = {
                "avg_confidence": statistics.mean(confidences),
                "confidence_range": max(confidences) - min(confidences),
                "appropriateness_rate": len(appropriate_confidences) / len(successful_docs),
                "high_confidence_count": len([c for c in confidences if c > 0.8]),
                "low_confidence_count": len([c for c in confidences if c < 0.4])
            }
        
        # Analyze edge case confidence patterns
        edge_details = edge_case_results.get("edge_case_details", [])
        edge_confidences = []
        
        for detail in edge_details:
            result = detail.get("classification_result")
            if result and "confidence" in result:
                edge_confidences.append({
                    "case": detail["edge_case"],
                    "confidence": result["confidence"],
                    "graceful": detail.get("graceful_handling", False)
                })
        
        if edge_confidences:
            analysis["edge_case_confidence"] = {
                "avg_edge_confidence": statistics.mean([ec["confidence"] for ec in edge_confidences]),
                "graceful_handling_rate": len([ec for ec in edge_confidences if ec["graceful"]]) / len(edge_confidences)
            }
        
        return analysis
    
    def _calculate_performance_metrics(self, document_results: Dict[str, Any], edge_case_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        total_tests = document_results["total_documents"] + edge_case_results["total_edge_cases"]
        successful_tests = document_results["successful_classifications"] + edge_case_results["handled_gracefully"]
        
        # Collect all classification times
        all_times = []
        for detail in document_results.get("classification_details", []):
            if detail.get("classification_time_ms"):
                all_times.append(detail["classification_time_ms"])
        
        for detail in edge_case_results.get("edge_case_details", []):
            if detail.get("classification_time_ms"):
                all_times.append(detail["classification_time_ms"])
        
        metrics = {
            "overall_success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "document_type_accuracy": document_results.get("type_accuracy", 0),
            "framework_accuracy": document_results.get("framework_accuracy", 0),
            "edge_case_handling_rate": edge_case_results["handled_gracefully"] / edge_case_results["total_edge_cases"] if edge_case_results["total_edge_cases"] > 0 else 0,
            "avg_classification_time_ms": statistics.mean(all_times) if all_times else 0,
            "max_classification_time_ms": max(all_times) if all_times else 0,
            "min_classification_time_ms": min(all_times) if all_times else 0
        }
        
        return metrics
    
    def _print_results(self, results: Dict[str, Any]) -> None:
        """Print comprehensive enhanced classification test results."""
        print("\n" + "="*100)
        print("📊 ENHANCED CLASSIFICATION TEST RESULTS")
        print("="*100)
        
        # Performance metrics
        metrics = results["performance_metrics"]
        print(f"📊 OVERALL PERFORMANCE:")
        print(f"   ✅ Overall Success Rate: {metrics['overall_success_rate']:.1%}")
        print(f"   🏷️ Document Type Accuracy: {metrics['document_type_accuracy']:.1%}")
        print(f"   📋 Framework Accuracy: {metrics['framework_accuracy']:.1%}")
        print(f"   🛡️ Edge Case Handling: {metrics['edge_case_handling_rate']:.1%}")
        print(f"   ⏱️ Avg Classification Time: {metrics['avg_classification_time_ms']:.1f}ms")
        
        # Document classification results
        doc_results = results["document_classification_tests"]
        print(f"\n📄 DOCUMENT CLASSIFICATION RESULTS:")
        print(f"   📊 Documents Tested: {doc_results['total_documents']}")
        print(f"   ✅ Successful: {doc_results['successful_classifications']}")
        print(f"   ❌ Failed: {doc_results['failed_classifications']}")
        
        # Confidence analysis
        confidence_analysis = results["confidence_analysis"]
        if "confidence_calibration" in confidence_analysis:
            calib = confidence_analysis["confidence_calibration"]
            print(f"\n🎯 CONFIDENCE ANALYSIS:")
            print(f"   📊 Average Confidence: {calib['avg_confidence']:.1%}")
            print(f"   📏 Confidence Range: {calib['confidence_range']:.1%}")
            print(f"   ✅ Appropriateness Rate: {calib['appropriateness_rate']:.1%}")
            print(f"   🔥 High Confidence (>80%): {calib['high_confidence_count']}")
            print(f"   ❄️ Low Confidence (<40%): {calib['low_confidence_count']}")
        
        # Edge case results
        edge_results = results["edge_case_tests"]
        print(f"\n🛡️ EDGE CASE HANDLING:")
        print(f"   🧪 Edge Cases Tested: {edge_results['total_edge_cases']}")
        print(f"   ✅ Handled Gracefully: {edge_results['handled_gracefully']}")
        print(f"   ❌ Poor Handling: {edge_results['failed_edge_cases']}")
        
        # Show edge case details
        print(f"\n📊 EDGE CASE BREAKDOWN:")
        for detail in edge_results["edge_case_details"]:
            case_name = detail["edge_case"]
            graceful = detail.get("graceful_handling", False)
            assessment = detail.get("assessment", "No assessment")
            status = "✅" if graceful else "❌"
            print(f"   {status} {case_name}: {assessment}")
        
        # Detailed document results
        print(f"\n📄 DETAILED DOCUMENT RESULTS:")
        print("-" * 100)
        
        for detail in doc_results["classification_details"]:
            if detail.get("success", False):
                doc_name = detail["document"]
                actual = detail["actual"]
                expected = detail["expected"]
                confidence = detail["confidence"]
                type_correct = "✅" if detail["type_correct"] else "❌"
                framework_correct = "✅" if detail["framework_correct"] else "❌"
                
                print(f"\n📋 {doc_name.upper()}")
                print(f"   🏷️ Type: {actual.get('document_type')} {type_correct} (expected: {expected['document_type']})")
                print(f"   📋 Framework: {actual.get('compliance_framework')} {framework_correct}")
                print(f"   🎯 Confidence: {confidence:.1%}")
                print(f"   ⏱️ Time: {detail.get('classification_time_ms', 0):.1f}ms")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if metrics["overall_success_rate"] > 0.9 and metrics["edge_case_handling_rate"] > 0.8:
            print("   🎉 Excellent classification performance across all test categories!")
        elif metrics["overall_success_rate"] > 0.8:
            print("   ✅ Good classification performance with areas for improvement:")
            if metrics["document_type_accuracy"] < 0.9:
                print("      - Improve document type classification accuracy")
            if metrics["framework_accuracy"] < 0.8:
                print("      - Enhance compliance framework detection")
            if metrics["edge_case_handling_rate"] < 0.7:
                print("      - Strengthen edge case handling robustness")
        else:
            print("   ⚠️ Classification performance needs significant improvement:")
            print("      - Review and enhance classification algorithms")
            print("      - Improve confidence scoring calibration")
            print("      - Add more robust error handling for edge cases")
            print("      - Consider expanding training data diversity")
        
        # Confidence-specific recommendations
        if "confidence_calibration" in confidence_analysis:
            calib = confidence_analysis["confidence_calibration"]
            if calib["appropriateness_rate"] < 0.7:
                print("      - Recalibrate confidence scoring thresholds")
            if calib["confidence_range"] < 0.3:
                print("      - Increase confidence score discrimination")
        
        print("="*100)
        print("✅ ENHANCED CLASSIFICATION TEST COMPLETED")
        print("="*100)


async def main():
    """Run the enhanced classification test."""
    test = EnhancedClassificationTest()
    
    # Run comprehensive test
    results = await test.run_enhanced_classification_test()
    
    # Save detailed results
    output_file = Path(__file__).parent / "classification_enhancement_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📊 Detailed results saved to: {output_file}")
    
    # Return appropriate exit code based on performance
    metrics = results["performance_metrics"]
    overall_success = metrics["overall_success_rate"]
    type_accuracy = metrics["document_type_accuracy"]
    edge_case_handling = metrics["edge_case_handling_rate"]
    
    if overall_success > 0.8 and type_accuracy > 0.8 and edge_case_handling > 0.7:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs improvement


if __name__ == "__main__":
    asyncio.run(main())
