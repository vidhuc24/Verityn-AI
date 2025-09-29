#!/usr/bin/env python3
"""
Direct Chunking and Similarity Score Analysis

This test directly examines:
1. Current similarity scores for test queries
2. Sample chunks from the database
3. Chunk quality assessment

Simple and focused approach.
"""

import asyncio
import json
import logging
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.services.vector_database import vector_db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def analyze_similarity_scores():
    """Analyze similarity scores for test queries."""
    logger.info("🔍 Analyzing similarity scores...")
    
    test_queries = [
        "What are the key findings from the access review?",
        "SOX compliance requirements",
        "material weaknesses",
        "internal controls assessment",
        "risk management procedures"
    ]
    
    results = {}
    
    for query in test_queries:
        logger.info(f"  🔍 Query: '{query[:40]}...'")
        
        try:
            # Search with very low threshold to get all results
            search_results = await vector_db_service.semantic_search(query, limit=20, score_threshold=0.0)
            
            if search_results:
                scores = [result.score for result in search_results]
                
                results[query] = {
                    "total_results": len(search_results),
                    "score_stats": {
                        "min": min(scores),
                        "max": max(scores),
                        "mean": np.mean(scores),
                        "median": np.median(scores),
                        "std": np.std(scores)
                    },
                    "score_distribution": {
                        "above_0.5": len([s for s in scores if s > 0.5]),
                        "above_0.3": len([s for s in scores if s > 0.3]),
                        "above_0.1": len([s for s in scores if s > 0.1]),
                        "above_0.05": len([s for s in scores if s > 0.05])
                    },
                    "top_5_scores": sorted(scores, reverse=True)[:5],
                    "sample_results": [
                        {
                            "score": result.score,
                            "content_preview": result.page_content[:100] + "..." if result.page_content else "No content",
                            "metadata": result.metadata
                        }
                        for result in search_results[:3]
                    ]
                }
                
                logger.info(f"    📊 Mean score: {np.mean(scores):.3f}, Max: {max(scores):.3f}")
                logger.info(f"    📈 Above 0.3: {len([s for s in scores if s > 0.3])}, Above 0.1: {len([s for s in scores if s > 0.1])}")
            else:
                results[query] = {"error": "No results found"}
                logger.warning(f"    ⚠️ No results found")
                
        except Exception as e:
            results[query] = {"error": str(e)}
            logger.error(f"    ❌ Error: {str(e)}")
    
    return results

async def analyze_sample_chunks():
    """Analyze sample chunks from the database."""
    logger.info("📄 Analyzing sample chunks...")
    
    try:
        # Get sample chunks
        sample_results = await vector_db_service.semantic_search("sample", limit=15, score_threshold=0.0)
        
        if not sample_results:
            return {"error": "No chunks found in database"}
        
        chunks_analysis = []
        
        for i, result in enumerate(sample_results):
            content = result.page_content if result.page_content else ""
            
            # Analyze chunk quality
            quality_issues = []
            quality_score = 100
            
            # Check chunk size
            if len(content) < 50:
                quality_issues.append("Too short")
                quality_score -= 30
            elif len(content) > 1000:
                quality_issues.append("Too long")
                quality_score -= 20
            
            # Check for audit-specific terms
            audit_terms = ["sox", "compliance", "control", "risk", "audit", "finding", "deficiency", "material"]
            content_lower = content.lower()
            audit_term_count = sum(1 for term in audit_terms if term in content_lower)
            
            if audit_term_count == 0:
                quality_issues.append("No audit-specific terms")
                quality_score -= 25
            elif audit_term_count < 2:
                quality_issues.append("Few audit-specific terms")
                quality_score -= 10
            
            # Check for sentence completeness
            if content and not content.strip().endswith(('.', '!', '?')):
                quality_issues.append("Incomplete sentence")
                quality_score -= 15
            
            # Determine quality level
            if quality_score >= 80:
                quality_level = "excellent"
            elif quality_score >= 60:
                quality_level = "good"
            elif quality_score >= 40:
                quality_level = "fair"
            else:
                quality_level = "poor"
            
            chunks_analysis.append({
                "chunk_id": i,
                "score": result.score,
                "content_length": len(content),
                "content_preview": content[:150] + "..." if content else "No content",
                "quality_level": quality_level,
                "quality_score": quality_score,
                "quality_issues": quality_issues,
                "audit_term_count": audit_term_count,
                "metadata": result.metadata
            })
        
        # Calculate summary statistics
        quality_counts = {}
        for chunk in chunks_analysis:
            quality = chunk["quality_level"]
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        avg_score = np.mean([chunk["score"] for chunk in chunks_analysis])
        avg_length = np.mean([chunk["content_length"] for chunk in chunks_analysis])
        
        return {
            "total_chunks": len(chunks_analysis),
            "avg_similarity_score": avg_score,
            "avg_chunk_length": avg_length,
            "quality_distribution": quality_counts,
            "chunks": chunks_analysis
        }
        
    except Exception as e:
        return {"error": str(e)}

async def main():
    """Main analysis function."""
    logger.info("🚀 Starting Direct Chunking and Similarity Score Analysis")
    
    try:
        # Analyze similarity scores
        similarity_results = await analyze_similarity_scores()
        
        # Analyze sample chunks
        chunks_results = await analyze_sample_chunks()
        
        # Compile results
        final_results = {
            "similarity_analysis": similarity_results,
            "chunks_analysis": chunks_results,
            "summary": {
                "low_score_queries": [],
                "chunking_issues": [],
                "recommendations": []
            }
        }
        
        # Generate summary
        for query, analysis in similarity_results.items():
            if "score_stats" in analysis:
                mean_score = analysis["score_stats"]["mean"]
                if mean_score < 0.2:
                    final_results["summary"]["low_score_queries"].append({
                        "query": query,
                        "mean_score": mean_score
                    })
        
        if "quality_distribution" in chunks_results:
            quality_dist = chunks_results["quality_distribution"]
            poor_fair_count = quality_dist.get("poor", 0) + quality_dist.get("fair", 0)
            if poor_fair_count > 0:
                final_results["summary"]["chunking_issues"].append(f"{poor_fair_count} chunks have poor/fair quality")
        
        # Generate recommendations
        recommendations = []
        if final_results["summary"]["low_score_queries"]:
            recommendations.append("Low similarity scores detected - consider improving chunking strategy or query formulation")
        if final_results["summary"]["chunking_issues"]:
            recommendations.append("Chunk quality issues detected - consider adjusting chunk size, overlap, or chunking method")
        
        final_results["summary"]["recommendations"] = recommendations
        
        # Save results
        results_file = Path("scripts/testing/direct_chunking_analysis_results.json")
        with open(results_file, 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        
        logger.info(f"📊 Results saved to: {results_file}")
        
        # Print summary
        print("\n" + "="*80)
        print("🔬 DIRECT CHUNKING AND SIMILARITY SCORE ANALYSIS SUMMARY")
        print("="*80)
        
        print("\n🔍 SIMILARITY SCORE ANALYSIS:")
        for query, analysis in similarity_results.items():
            if "score_stats" in analysis:
                stats = analysis["score_stats"]
                dist = analysis.get("score_distribution", {})
                print(f"  '{query[:40]}...':")
                print(f"    📊 Mean: {stats['mean']:.3f}, Max: {stats['max']:.3f}, Min: {stats['min']:.3f}")
                print(f"    📈 Above 0.3: {dist.get('above_0.3', 0)}, Above 0.1: {dist.get('above_0.1', 0)}")
        
        print("\n📄 CHUNK QUALITY ANALYSIS:")
        if "quality_distribution" in chunks_results:
            quality_dist = chunks_results["quality_distribution"]
            print(f"  Total chunks analyzed: {chunks_results.get('total_chunks', 0)}")
            print(f"  Average similarity score: {chunks_results.get('avg_similarity_score', 0):.3f}")
            print(f"  Average chunk length: {chunks_results.get('avg_chunk_length', 0):.1f} chars")
            print("  Quality distribution:")
            for quality, count in quality_dist.items():
                print(f"    {quality.capitalize()}: {count} chunks")
        
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*80)
        
        return final_results
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
