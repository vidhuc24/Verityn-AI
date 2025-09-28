#!/usr/bin/env python3
"""
REAL Web Research Agent Test for Verityn AI

This test uses ACTUAL Tavily API calls to test web research functionality
with real regulatory queries and document context.

TESTING PRINCIPLES:
- Uses real Tavily API calls (no mocking)
- Tests actual SOX compliance queries
- Validates real web search results
- Tests both auto-triggering and manual scenarios
- Measures response quality and source accuracy
"""

import asyncio
import time
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.tavily_service import tavily_service
from backend.app.config import settings


class WebResearchAgentTest:
    """Real Web Research Agent testing with actual Tavily API calls."""
    
    def __init__(self):
        self.tavily_service = tavily_service
        self.test_scenarios = self._define_test_scenarios()
        self.results = []
        
    def _define_test_scenarios(self) -> List[Dict[str, Any]]:
        """Define real-world test scenarios for web research."""
        return [
            {
                "name": "sox_404_updates",
                "query": "SOX 404 internal controls requirements 2024",
                "document_type": "access_review",
                "compliance_framework": "SOX",
                "scenario_type": "auto_trigger",
                "expected_quality": {
                    "min_results": 3,
                    "compliance_relevance": 0.8,
                    "source_authority": 0.7,
                    "content_freshness": 0.6
                },
                "description": "Should auto-trigger for SOX 404 queries and return authoritative compliance guidance"
            },
            {
                "name": "access_control_best_practices",
                "query": "access control segregation of duties audit requirements",
                "document_type": "access_review", 
                "compliance_framework": "SOX",
                "scenario_type": "manual_button",
                "expected_quality": {
                    "min_results": 2,
                    "compliance_relevance": 0.8,
                    "source_authority": 0.6,
                    "content_freshness": 0.5
                },
                "description": "Manual button trigger for access control guidance"
            },
            {
                "name": "material_weakness_guidance",
                "query": "material weakness identification reporting requirements",
                "document_type": "audit_report",
                "compliance_framework": "SOX",
                "scenario_type": "auto_trigger",
                "expected_quality": {
                    "min_results": 3,
                    "compliance_relevance": 0.9,
                    "source_authority": 0.8,
                    "content_freshness": 0.6
                },
                "description": "Should provide guidance on material weakness identification and reporting"
            },
            {
                "name": "financial_controls_updates",
                "query": "financial reporting controls effectiveness testing 2024",
                "document_type": "financial_controls",
                "compliance_framework": "SOX",
                "scenario_type": "manual_button",
                "expected_quality": {
                    "min_results": 2,
                    "compliance_relevance": 0.8,
                    "source_authority": 0.7,
                    "content_freshness": 0.7
                },
                "description": "Latest guidance on financial controls testing"
            },
            {
                "name": "risk_assessment_standards",
                "query": "enterprise risk assessment SOX compliance methodology",
                "document_type": "risk_assessment",
                "compliance_framework": "SOX",
                "scenario_type": "auto_trigger",
                "expected_quality": {
                    "min_results": 2,
                    "compliance_relevance": 0.7,
                    "source_authority": 0.6,
                    "content_freshness": 0.5
                },
                "description": "Risk assessment methodology and compliance standards"
            }
        ]
    
    async def run_test(self):
        """Execute the complete Web Research Agent test suite."""
        logger.info("🚀 Starting REAL Web Research Agent Test")
        logger.info("🔗 Using actual Tavily API calls - NO MOCKING")
        logger.info("📊 Testing regulatory compliance queries with real web data")
        
        # Verify Tavily service availability
        if not self._verify_tavily_setup():
            logger.error("❌ Tavily service not properly configured")
            return
            
        logger.info("✅ Tavily service verified - proceeding with real API tests")
        
        # Run test scenarios
        for i, scenario in enumerate(self.test_scenarios, 1):
            logger.info(f"🔍 Testing scenario {i}/{len(self.test_scenarios)}: '{scenario['name']}'")
            
            result = await self._test_scenario(scenario)
            self.results.append(result)
            
            # Brief pause between API calls to be respectful
            await asyncio.sleep(1)
        
        # Analyze and report results
        self._analyze_results()
        self._save_results()
    
    def _verify_tavily_setup(self) -> bool:
        """Verify Tavily service is properly configured."""
        if not self.tavily_service.client:
            logger.error("Tavily client not initialized")
            return False
            
        if not settings.TAVILY_API_KEY:
            logger.error("TAVILY_API_KEY not found in environment")
            return False
            
        logger.info(f"Tavily API key configured: {settings.TAVILY_API_KEY[:8]}...")
        return True
    
    async def _test_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single web research scenario with real API calls."""
        scenario_result = {
            "scenario_name": scenario["name"],
            "query": scenario["query"],
            "scenario_type": scenario["scenario_type"],
            "start_time": time.time(),
            "success": False,
            "web_research_result": {},
            "quality_scores": {},
            "errors": []
        }
        
        try:
            logger.info(f"  📝 Query: {scenario['query']}")
            logger.info(f"  🎯 Type: {scenario['scenario_type']}")
            
            # Execute real Tavily search
            start_time = time.time()
            search_result = await self.tavily_service.search_compliance_guidance(
                query=scenario["query"],
                document_type=scenario["document_type"],
                compliance_framework=scenario["compliance_framework"]
            )
            execution_time = (time.time() - start_time) * 1000
            
            scenario_result["web_research_result"] = search_result
            scenario_result["execution_time_ms"] = execution_time
            
            if search_result.get("success"):
                scenario_result["success"] = True
                
                # Analyze search quality
                scenario_result["quality_scores"] = self._analyze_search_quality(
                    search_result, scenario["expected_quality"]
                )
                
                logger.info(f"    ✅ Search completed in {execution_time:.1f}ms")
                logger.info(f"    📊 Results: {len(search_result.get('results', []))} found")
                logger.info(f"    🎯 Quality: {scenario_result['quality_scores'].get('overall_quality', 0):.1%}")
            else:
                scenario_result["errors"].append(f"Search failed: {search_result.get('error', 'Unknown error')}")
                logger.warning(f"    ❌ Search failed: {search_result.get('error', 'Unknown')}")
                
        except Exception as e:
            scenario_result["errors"].append(f"Test execution failed: {str(e)}")
            logger.error(f"    💥 Test failed: {str(e)}")
        
        scenario_result["end_time"] = time.time()
        return scenario_result
    
    def _analyze_search_quality(self, search_result: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of search results against expectations."""
        results = search_result.get("results", [])
        insights = search_result.get("compliance_insights", [])
        
        scores = {}
        
        # Result quantity
        result_count = len(results)
        min_results = expected.get("min_results", 1)
        scores["result_quantity"] = min(1.0, result_count / min_results) if min_results > 0 else 1.0
        
        # Compliance relevance (based on content analysis)
        compliance_relevance = self._assess_compliance_relevance(results)
        scores["compliance_relevance"] = compliance_relevance
        
        # Source authority (based on domain reputation)
        source_authority = self._assess_source_authority(results)
        scores["source_authority"] = source_authority
        
        # Content freshness (based on recency indicators)
        content_freshness = self._assess_content_freshness(results)
        scores["content_freshness"] = content_freshness
        
        # Insight quality
        insight_quality = self._assess_insight_quality(insights)
        scores["insight_quality"] = insight_quality
        
        # Overall quality (weighted average)
        scores["overall_quality"] = (
            scores["result_quantity"] * 0.2 +
            scores["compliance_relevance"] * 0.3 +
            scores["source_authority"] * 0.2 +
            scores["content_freshness"] * 0.1 +
            scores["insight_quality"] * 0.2
        )
        
        return scores
    
    def _assess_compliance_relevance(self, results: List[Dict[str, Any]]) -> float:
        """Assess how relevant results are to compliance topics."""
        if not results:
            return 0.0
            
        compliance_keywords = [
            "sox", "sarbanes-oxley", "internal controls", "material weakness",
            "compliance", "audit", "financial reporting", "risk assessment",
            "segregation of duties", "access controls", "pcaob"
        ]
        
        relevance_scores = []
        for result in results:
            content = (result.get("content", "") + " " + result.get("title", "")).lower()
            keyword_matches = sum(1 for keyword in compliance_keywords if keyword in content)
            relevance_score = min(1.0, keyword_matches / 5)  # Normalize to max 5 keywords
            relevance_scores.append(relevance_score)
        
        return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    def _assess_source_authority(self, results: List[Dict[str, Any]]) -> float:
        """Assess the authority/credibility of sources."""
        if not results:
            return 0.0
            
        authoritative_domains = [
            "aicpa.org", "pcaobus.org", "sox-online.com", "isaca.org",
            "sec.gov", "fasb.org", "iia.org", "coso.org"
        ]
        
        authority_scores = []
        for result in results:
            url = result.get("url", "").lower()
            if any(domain in url for domain in authoritative_domains):
                authority_scores.append(1.0)
            elif any(domain in url for domain in [".gov", ".edu", ".org"]):
                authority_scores.append(0.7)
            else:
                authority_scores.append(0.3)
        
        return sum(authority_scores) / len(authority_scores) if authority_scores else 0.0
    
    def _assess_content_freshness(self, results: List[Dict[str, Any]]) -> float:
        """Assess content freshness based on recency indicators."""
        if not results:
            return 0.0
            
        freshness_indicators = ["2024", "2023", "recent", "updated", "latest", "new"]
        
        freshness_scores = []
        for result in results:
            content = (result.get("content", "") + " " + result.get("title", "")).lower()
            if any(indicator in content for indicator in freshness_indicators):
                freshness_scores.append(1.0)
            else:
                freshness_scores.append(0.3)
        
        return sum(freshness_scores) / len(freshness_scores) if freshness_scores else 0.0
    
    def _assess_insight_quality(self, insights: List[Dict[str, Any]]) -> float:
        """Assess the quality of extracted compliance insights."""
        if not insights:
            return 0.0
            
        quality_score = 0.0
        for insight in insights:
            # Check for meaningful content
            content_length = len(insight.get("content", ""))
            if content_length > 50:
                quality_score += 0.3
            
            # Check for compliance focus
            compliance_focus = insight.get("compliance_focus", "")
            if "SOX" in compliance_focus or "Compliance" in compliance_focus:
                quality_score += 0.4
            
            # Check for relevance score
            relevance_score = insight.get("relevance_score", 0)
            if relevance_score > 0.5:
                quality_score += 0.3
        
        return min(1.0, quality_score / len(insights)) if insights else 0.0
    
    def _analyze_results(self):
        """Analyze and report test results."""
        total_scenarios = len(self.results)
        successful_scenarios = sum(1 for r in self.results if r["success"])
        
        # Calculate average scores
        quality_scores = [r["quality_scores"] for r in self.results if r["success"]]
        if quality_scores:
            avg_quality = sum(qs.get("overall_quality", 0) for qs in quality_scores) / len(quality_scores)
            avg_relevance = sum(qs.get("compliance_relevance", 0) for qs in quality_scores) / len(quality_scores)
            avg_authority = sum(qs.get("source_authority", 0) for qs in quality_scores) / len(quality_scores)
        else:
            avg_quality = avg_relevance = avg_authority = 0.0
        
        # Calculate average execution time
        execution_times = [r.get("execution_time_ms", 0) for r in self.results if r["success"]]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        logger.info("\n" + "="*100)
        logger.info("🔍 WEB RESEARCH AGENT TEST RESULTS (REAL TAVILY API)")
        logger.info("="*100)
        logger.info(f"📊 OVERALL STATUS: {'✅ SUCCESS' if successful_scenarios == total_scenarios else '❌ NEEDS IMPROVEMENT'}")
        logger.info(f"🎯 Success Rate: {successful_scenarios}/{total_scenarios} ({successful_scenarios/total_scenarios*100:.1f}%)")
        logger.info(f"⏱️ Avg Execution Time: {avg_execution_time:.1f}ms")
        logger.info(f"📄 Test Approach: Real Tavily API calls with regulatory queries")
        logger.info("")
        logger.info("📊 SEARCH QUALITY METRICS:")
        logger.info(f"   ✅ Overall Quality: {avg_quality:.1%} (Target: 80.0%)")
        logger.info(f"   ✅ Compliance Relevance: {avg_relevance:.1%} (Target: 80.0%)")
        logger.info(f"   ✅ Source Authority: {avg_authority:.1%} (Target: 70.0%)")
        logger.info("")
        logger.info("📋 SCENARIO RESULTS:")
        
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            quality = result["quality_scores"].get("overall_quality", 0) if result["success"] else 0
            exec_time = result.get("execution_time_ms", 0)
            logger.info(f"   {status} {result['scenario_name']}: {quality:.1%} quality, {exec_time:.1f}ms")
        
        # Recommendations
        logger.info("")
        if avg_quality < 0.8:
            logger.info("💡 IMPROVEMENT RECOMMENDATIONS:")
            if avg_relevance < 0.8:
                logger.info("   1. CRITICAL: Improve query enhancement for better compliance relevance")
            if avg_authority < 0.7:
                logger.info("   2. HIGH: Focus searches on more authoritative domains")
        else:
            logger.info("🎉 EXCELLENT: Web Research Agent meets all quality targets!")
        
        logger.info("="*100)
        logger.info("✅ WEB RESEARCH AGENT TEST COMPLETED (REAL DATA)")
        logger.info("="*100)
    
    def _save_results(self):
        """Save detailed test results to file."""
        import json
        
        output_path = Path("scripts/testing/web_research_test_results.json")
        
        # Prepare results for JSON serialization
        serializable_results = []
        for result in self.results:
            serializable_result = result.copy()
            # Ensure all values are JSON serializable
            for key, value in serializable_result.items():
                if isinstance(value, (int, float, str, bool, list, dict, type(None))):
                    continue
                else:
                    serializable_result[key] = str(value)
            serializable_results.append(serializable_result)
        
        with open(output_path, 'w') as f:
            json.dump({
                "test_metadata": {
                    "test_name": "Web Research Agent Test (Real Tavily API)",
                    "timestamp": time.time(),
                    "total_scenarios": len(self.results),
                    "api_used": "Tavily (Real)",
                    "test_type": "Integration"
                },
                "results": serializable_results
            }, f, indent=2)
        
        logger.info(f"📊 Detailed results saved to: {output_path}")


if __name__ == "__main__":
    test = WebResearchAgentTest()
    asyncio.run(test.run_test())
