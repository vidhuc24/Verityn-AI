#!/usr/bin/env python3
"""
Vector Database Threshold Optimization Test

Analyzes actual similarity scores from real queries to determine optimal
score thresholds for Phase 3 Response Synthesis Agent.

Usage:
    uv run python scripts/testing/test_threshold_optimization.py
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

from backend.app.agents.specialized_agents import ContextRetrievalAgent
from backend.app.agents.base_agent import AgentContext, AgentType
from backend.app.services.vector_database import vector_db_service
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ThresholdOptimizationTest:
    """Test to find optimal vector similarity thresholds."""
    
    def __init__(self):
        """Initialize the threshold optimization test."""
        self.context_agent = ContextRetrievalAgent(verbose=False)
        
        # Real audit queries to test thresholds with
        self.test_queries = [
            "What are the key findings from the access review?",
            "Are there any SOX 404 material weaknesses?",
            "What controls need improvement?",
            "What are the high-risk findings?",
            "What remediation actions are recommended?",
            "How effective are the current internal controls?",
            "What segregation of duties issues were identified?",
            "Are there any terminated employee access concerns?"
        ]
        
        # Thresholds to test
        self.thresholds_to_test = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
    
    async def run_threshold_optimization(self) -> Dict[str, Any]:
        """Run threshold optimization analysis."""
        logger.info("🎯 Starting Threshold Optimization Test")
        logger.info("📊 Testing different similarity thresholds with real queries")
        
        results = {
            "test_timestamp": time.time(),
            "thresholds_tested": self.thresholds_to_test,
            "queries_tested": self.test_queries,
            "threshold_results": {},
            "score_analysis": {},
            "recommendations": {}
        }
        
        # Initialize vector database
        await vector_db_service.initialize_collection()
        
        # Test each threshold
        for threshold in self.thresholds_to_test:
            logger.info(f"🔍 Testing threshold: {threshold}")
            threshold_result = await self._test_threshold(threshold)
            results["threshold_results"][str(threshold)] = threshold_result
        
        # Analyze score distributions
        results["score_analysis"] = self._analyze_score_distributions(results["threshold_results"])
        
        # Generate recommendations
        results["recommendations"] = self._generate_threshold_recommendations(results)
        
        # Print results
        self._print_threshold_results(results)
        
        return results
    
    async def _test_threshold(self, threshold: float) -> Dict[str, Any]:
        """Test a specific threshold value."""
        threshold_result = {
            "threshold": threshold,
            "query_results": [],
            "total_results": 0,
            "avg_results_per_query": 0,
            "score_stats": {},
            "performance_ms": 0
        }
        
        all_scores = []
        total_results = 0
        total_time = 0
        
        for i, query in enumerate(self.test_queries):
            start_time = time.time()
            
            # Create context for retrieval agent
            context = AgentContext(
                inputs={
                    "question": query,
                    "analysis": {"intent": "information_retrieval", "complexity": "basic"}
                },
                agent_type=AgentType.CONTEXT_RETRIEVER,
                timestamp=datetime.now(),
                conversation_id=f"threshold_test_{threshold}_{i}",
                workflow_id=f"threshold_optimization_{int(time.time())}"
            )
            
            try:
                # Temporarily modify the vector database threshold
                original_threshold = getattr(vector_db_service, '_default_score_threshold', 0.1)
                vector_db_service._default_score_threshold = threshold
                
                # Run context retrieval
                result = await self.context_agent._execute_logic(context)
                
                # Restore original threshold
                vector_db_service._default_score_threshold = original_threshold
                
                execution_time = (time.time() - start_time) * 1000
                total_time += execution_time
                
                # Extract results and scores
                context_results = result.get("context", [])
                result_count = len(context_results)
                total_results += result_count
                
                # Extract similarity scores
                query_scores = []
                for doc in context_results:
                    if "score" in doc:
                        score = doc["score"]
                        query_scores.append(score)
                        all_scores.append(score)
                
                threshold_result["query_results"].append({
                    "query": query[:50] + "..." if len(query) > 50 else query,
                    "result_count": result_count,
                    "scores": query_scores,
                    "avg_score": statistics.mean(query_scores) if query_scores else 0,
                    "min_score": min(query_scores) if query_scores else 0,
                    "max_score": max(query_scores) if query_scores else 0,
                    "execution_time_ms": execution_time
                })
                
            except Exception as e:
                logger.warning(f"Query failed with threshold {threshold}: {str(e)}")
                threshold_result["query_results"].append({
                    "query": query[:50] + "..." if len(query) > 50 else query,
                    "result_count": 0,
                    "scores": [],
                    "error": str(e),
                    "execution_time_ms": (time.time() - start_time) * 1000
                })
        
        # Calculate statistics
        threshold_result["total_results"] = total_results
        threshold_result["avg_results_per_query"] = total_results / len(self.test_queries)
        threshold_result["performance_ms"] = total_time / len(self.test_queries)
        
        if all_scores:
            threshold_result["score_stats"] = {
                "count": len(all_scores),
                "mean": statistics.mean(all_scores),
                "median": statistics.median(all_scores),
                "min": min(all_scores),
                "max": max(all_scores),
                "std_dev": statistics.stdev(all_scores) if len(all_scores) > 1 else 0
            }
        else:
            threshold_result["score_stats"] = {"count": 0, "mean": 0, "median": 0, "min": 0, "max": 0, "std_dev": 0}
        
        logger.info(f"  📊 Threshold {threshold}: {total_results} total results, avg {threshold_result['avg_results_per_query']:.1f} per query")
        
        return threshold_result
    
    def _analyze_score_distributions(self, threshold_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze score distributions across thresholds."""
        analysis = {
            "threshold_comparison": [],
            "optimal_range": {},
            "score_distribution": {}
        }
        
        # Compare thresholds
        for threshold_str, result in threshold_results.items():
            threshold = float(threshold_str)
            analysis["threshold_comparison"].append({
                "threshold": threshold,
                "avg_results": result["avg_results_per_query"],
                "total_results": result["total_results"],
                "avg_score": result["score_stats"]["mean"],
                "score_range": result["score_stats"]["max"] - result["score_stats"]["min"] if result["score_stats"]["max"] > 0 else 0,
                "performance_ms": result["performance_ms"]
            })
        
        # Find optimal range (balance between relevance and recall)
        sorted_thresholds = sorted(analysis["threshold_comparison"], key=lambda x: x["threshold"])
        
        # Look for "sweet spot" - decent number of results with good performance
        target_results_per_query = 3  # Aim for ~3 relevant results per query
        optimal_candidates = []
        
        for item in sorted_thresholds:
            if 1 <= item["avg_results"] <= 8:  # Reasonable result range
                quality_score = item["avg_score"]
                result_balance = abs(item["avg_results"] - target_results_per_query)
                combined_score = quality_score - (result_balance * 0.1)  # Penalize being far from target
                
                optimal_candidates.append({
                    "threshold": item["threshold"],
                    "combined_score": combined_score,
                    **item
                })
        
        if optimal_candidates:
            best_threshold = max(optimal_candidates, key=lambda x: x["combined_score"])
            analysis["optimal_range"] = {
                "recommended_threshold": best_threshold["threshold"],
                "reason": f"Best balance of quality ({best_threshold['avg_score']:.3f}) and results ({best_threshold['avg_results']:.1f})",
                "alternatives": [c for c in optimal_candidates if c["threshold"] != best_threshold["threshold"]][:3]
            }
        
        return analysis
    
    def _generate_threshold_recommendations(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate threshold recommendations."""
        analysis = results["score_analysis"]
        recommendations = {
            "current_assessment": {},
            "suggested_changes": [],
            "considerations": []
        }
        
        if "optimal_range" in analysis and analysis["optimal_range"]:
            optimal = analysis["optimal_range"]
            current_threshold = 0.1  # Current default
            recommended = optimal["recommended_threshold"]
            
            recommendations["current_assessment"] = {
                "current_threshold": current_threshold,
                "recommended_threshold": recommended,
                "improvement_expected": recommended != current_threshold
            }
            
            if recommended > current_threshold:
                recommendations["suggested_changes"].append(
                    f"INCREASE threshold from {current_threshold} to {recommended} for better precision"
                )
                recommendations["considerations"].append("Higher threshold = fewer but more relevant results")
            elif recommended < current_threshold:
                recommendations["suggested_changes"].append(
                    f"DECREASE threshold from {current_threshold} to {recommended} for better recall"
                )
                recommendations["considerations"].append("Lower threshold = more results but potentially less relevant")
            else:
                recommendations["suggested_changes"].append("Current threshold appears optimal")
            
            # Performance considerations
            perf_data = [item for item in analysis["threshold_comparison"] if item["threshold"] == recommended]
            if perf_data:
                perf = perf_data[0]["performance_ms"]
                if perf > 1000:
                    recommendations["considerations"].append(f"Performance impact: {perf:.0f}ms avg per query")
                
        else:
            recommendations["suggested_changes"].append("Unable to determine optimal threshold from current data")
        
        return recommendations
    
    def _print_threshold_results(self, results: Dict[str, Any]) -> None:
        """Print threshold optimization results."""
        print("\n" + "="*100)
        print("🎯 THRESHOLD OPTIMIZATION TEST RESULTS")
        print("="*100)
        
        analysis = results["score_analysis"]
        recommendations = results["recommendations"]
        
        # Print threshold comparison
        print(f"\n📊 THRESHOLD COMPARISON:")
        print(f"{'Threshold':<10} {'Avg Results':<12} {'Avg Score':<12} {'Performance':<12}")
        print("-" * 50)
        
        for item in sorted(analysis["threshold_comparison"], key=lambda x: x["threshold"]):
            print(f"{item['threshold']:<10} {item['avg_results']:<12.1f} {item['avg_score']:<12.3f} {item['performance_ms']:<12.0f}ms")
        
        # Print recommendations
        if "optimal_range" in analysis and analysis["optimal_range"]:
            optimal = analysis["optimal_range"]
            print(f"\n🎯 RECOMMENDED THRESHOLD: {optimal['recommended_threshold']}")
            print(f"📝 Reason: {optimal['reason']}")
            
            if "alternatives" in optimal and optimal["alternatives"]:
                print(f"\n📋 ALTERNATIVE THRESHOLDS:")
                for alt in optimal["alternatives"]:
                    print(f"   {alt['threshold']}: {alt['avg_results']:.1f} results, {alt['avg_score']:.3f} score")
        
        # Print current vs recommended
        if recommendations["current_assessment"]:
            current = recommendations["current_assessment"]
            print(f"\n🔄 THRESHOLD ADJUSTMENT:")
            print(f"   Current: {current['current_threshold']}")
            print(f"   Recommended: {current['recommended_threshold']}")
            
            if recommendations["suggested_changes"]:
                print(f"\n💡 SUGGESTED CHANGES:")
                for change in recommendations["suggested_changes"]:
                    print(f"   • {change}")
            
            if recommendations["considerations"]:
                print(f"\n⚠️ CONSIDERATIONS:")
                for consideration in recommendations["considerations"]:
                    print(f"   • {consideration}")
        
        print("="*100)
        print("✅ THRESHOLD OPTIMIZATION TEST COMPLETED")
        print("="*100)


async def main():
    """Run the threshold optimization test."""
    test = ThresholdOptimizationTest()
    
    # Run optimization
    results = await test.run_threshold_optimization()
    
    # Save results
    output_file = Path(__file__).parent / "threshold_optimization_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📊 Results saved to: {output_file}")
    
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
