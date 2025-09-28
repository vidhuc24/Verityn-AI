#!/usr/bin/env python3
"""
No Results Handling Test for Verityn AI

This test validates the intelligent "no results" scenario handling by:
1. Testing queries that should return no results
2. Validating query suggestions and fallback mechanisms
3. Ensuring user-friendly messaging and guidance
4. Testing domain-specific enhancement features
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.query_enhancement import query_enhancement_service
from backend.app.services.chat_engine import RAGChatEngine
from backend.app.services.vector_database import vector_db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NoResultsHandlingTest:
    """Test suite for no results scenario handling."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.chat_engine = RAGChatEngine()
        self.test_queries = {
            # Queries that should return no results (non-existent topics)
            "non_existent": [
                "What is the company's marketing budget?",
                "How many employees work in HR?",
                "What are the quarterly sales figures?",
                "Tell me about the company's social media strategy",
                "What is the office location address?"
            ],
            
            # Vague queries that might need enhancement
            "too_vague": [
                "controls",
                "findings",
                "what happened",
                "show me results",
                "audit"
            ],
            
            # Overly specific queries
            "too_specific": [
                "What were the exact timestamps of user login attempts by John Smith on December 15th at 3:47 PM for the SAP financial reporting module?",
                "Show me the detailed reconciliation differences for account 123456789 in the general ledger subsystem for Q3 2024",
                "What is the precise control ID for the automated three-way match validation in the procurement system?"
            ],
            
            # Queries with potential typos
            "with_typos": [
                "What are the complience issues?",
                "Show me controll deficiensies",
                "What risks were identifed?",
                "What are the audet findings?"
            ]
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive no-results handling tests."""
        logger.info("🚀 Starting No Results Handling Test")
        
        results = {
            "test_categories": {},
            "overall_stats": {
                "total_queries": 0,
                "queries_with_suggestions": 0,
                "queries_with_fallbacks": 0,
                "enhancement_success_rate": 0.0
            },
            "detailed_results": []
        }
        
        # Test each category
        for category, queries in self.test_queries.items():
            logger.info(f"\n📋 Testing category: {category}")
            category_results = await self._test_query_category(category, queries)
            results["test_categories"][category] = category_results
            
            # Update overall stats
            results["overall_stats"]["total_queries"] += len(queries)
            results["overall_stats"]["queries_with_suggestions"] += category_results["queries_with_suggestions"]
            results["overall_stats"]["queries_with_fallbacks"] += category_results["queries_with_fallbacks"]
        
        # Calculate enhancement success rate
        total_queries = results["overall_stats"]["total_queries"]
        successful_enhancements = results["overall_stats"]["queries_with_suggestions"]
        results["overall_stats"]["enhancement_success_rate"] = (
            successful_enhancements / total_queries if total_queries > 0 else 0.0
        )
        
        # Print comprehensive results
        self._print_results(results)
        
        return results
    
    async def _test_query_category(self, category: str, queries: List[str]) -> Dict[str, Any]:
        """Test a specific category of queries."""
        category_results = {
            "category": category,
            "total_queries": len(queries),
            "queries_with_suggestions": 0,
            "queries_with_fallbacks": 0,
            "query_details": []
        }
        
        for i, query in enumerate(queries, 1):
            logger.info(f"  🔍 Testing query {i}/{len(queries)}: '{query[:50]}...'")
            
            # Test with query enhancement service directly
            enhancement_result = await query_enhancement_service.handle_no_results(query)
            
            # Test with full chat engine
            chat_result = await self.chat_engine.process_message(query)
            
            query_detail = {
                "query": query,
                "enhancement": {
                    "has_suggestions": len(enhancement_result.get("suggestions", {}).get("alternative_queries", [])) > 0,
                    "has_fallbacks": enhancement_result.get("has_results", False),
                    "suggestions_count": len(enhancement_result.get("suggestions", {}).get("alternative_queries", [])),
                    "fallback_count": len(enhancement_result.get("fallback_results", [])),
                    "domain_category": enhancement_result.get("domain_guidance", {}).get("category", "unknown"),
                    "message_quality": self._assess_message_quality(enhancement_result.get("message", ""))
                },
                "chat_integration": {
                    "has_no_results_data": "no_results_enhancement" in chat_result,
                    "response_helpful": self._assess_response_helpfulness(chat_result),
                    "suggestions_provided": len(chat_result.get("no_results_enhancement", {}).get("alternative_queries", []))
                }
            }
            
            # Update category stats
            if query_detail["enhancement"]["has_suggestions"]:
                category_results["queries_with_suggestions"] += 1
            
            if query_detail["enhancement"]["has_fallbacks"]:
                category_results["queries_with_fallbacks"] += 1
            
            category_results["query_details"].append(query_detail)
            
            # Log key insights
            logger.info(f"    ✅ Suggestions: {query_detail['enhancement']['suggestions_count']}")
            logger.info(f"    ✅ Fallbacks: {query_detail['enhancement']['fallback_count']}")
            logger.info(f"    ✅ Domain: {query_detail['enhancement']['domain_category']}")
        
        return category_results
    
    def _assess_message_quality(self, message: str) -> Dict[str, Any]:
        """Assess the quality of the enhancement message."""
        quality = {
            "length_appropriate": 50 <= len(message) <= 300,
            "mentions_alternatives": "alternative" in message.lower() or "try" in message.lower(),
            "user_friendly": not any(tech_term in message.lower() for tech_term in ["error", "failed", "exception"]),
            "provides_guidance": "help" in message.lower() or "suggest" in message.lower()
        }
        
        quality["overall_score"] = sum(quality.values()) / len(quality)
        return quality
    
    def _assess_response_helpfulness(self, chat_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how helpful the chat response is for no-results scenarios."""
        helpfulness = {
            "has_suggestions": len(chat_result.get("no_results_enhancement", {}).get("alternative_queries", [])) > 0,
            "has_guidance": bool(chat_result.get("no_results_enhancement", {}).get("domain_guidance", {})),
            "message_informative": len(chat_result.get("message", {}).get("content", "")) > 100,
            "provides_tips": len(chat_result.get("no_results_enhancement", {}).get("query_tips", [])) > 0
        }
        
        helpfulness["overall_score"] = sum(helpfulness.values()) / len(helpfulness)
        return helpfulness
    
    def _print_results(self, results: Dict[str, Any]) -> None:
        """Print comprehensive test results."""
        print("\n" + "="*100)
        print("📊 NO RESULTS HANDLING TEST RESULTS")
        print("="*100)
        
        # Overall statistics
        stats = results["overall_stats"]
        print(f"📋 Overall Status: {'✅ EXCELLENT' if stats['enhancement_success_rate'] > 0.8 else '🟡 GOOD' if stats['enhancement_success_rate'] > 0.6 else '❌ NEEDS IMPROVEMENT'}")
        print(f"📄 Total Queries Tested: {stats['total_queries']}")
        print(f"⏱️ Enhancement Success Rate: {stats['enhancement_success_rate']:.1%}")
        
        print(f"\n🎯 SUCCESS RATES:")
        print(f"   ✅ Queries with Suggestions: {stats['queries_with_suggestions']}/{stats['total_queries']} ({stats['queries_with_suggestions']/stats['total_queries']:.1%})")
        print(f"   ✅ Queries with Fallbacks: {stats['queries_with_fallbacks']}/{stats['total_queries']} ({stats['queries_with_fallbacks']/stats['total_queries']:.1%})")
        
        # Category breakdown
        print(f"\n📊 CATEGORY BREAKDOWN:")
        print("-" * 100)
        
        for category, data in results["test_categories"].items():
            success_rate = data["queries_with_suggestions"] / data["total_queries"] if data["total_queries"] > 0 else 0
            status = "✅" if success_rate > 0.8 else "🟡" if success_rate > 0.6 else "❌"
            
            print(f"\n{status} {category.upper().replace('_', ' ')}")
            print(f"   📄 Queries: {data['total_queries']}")
            print(f"   💡 With Suggestions: {data['queries_with_suggestions']} ({success_rate:.1%})")
            print(f"   🔄 With Fallbacks: {data['queries_with_fallbacks']}")
            
            # Show sample suggestions for first query in each category
            if data["query_details"]:
                sample = data["query_details"][0]
                print(f"   📝 Sample Query: \"{sample['query'][:60]}...\"")
                print(f"   🎯 Domain Category: {sample['enhancement']['domain_category']}")
                print(f"   📊 Message Quality: {sample['enhancement']['message_quality']['overall_score']:.1%}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if stats['enhancement_success_rate'] > 0.9:
            print("   🎉 Excellent no-results handling! System provides helpful guidance consistently.")
        elif stats['enhancement_success_rate'] > 0.7:
            print("   ✅ Good no-results handling. Consider improving suggestion quality for edge cases.")
        else:
            print("   ⚠️  No-results handling needs improvement. Focus on:")
            print("      - Better query analysis and suggestion generation")
            print("      - More comprehensive fallback search strategies")
            print("      - Enhanced domain-specific guidance")
        
        print("="*100)
        print("✅ NO RESULTS HANDLING TEST COMPLETED")
        print("="*100)


async def main():
    """Run the no results handling test."""
    test = NoResultsHandlingTest()
    
    # Initialize vector database (needed for fallback searches)
    try:
        await vector_db_service.initialize_collection()
        logger.info("Vector database initialized successfully")
    except Exception as e:
        logger.warning(f"Vector database initialization failed: {str(e)} - Continuing with limited testing")
    
    # Run comprehensive test
    results = await test.run_comprehensive_test()
    
    # Save detailed results
    output_file = Path(__file__).parent / "no_results_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Detailed results saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
