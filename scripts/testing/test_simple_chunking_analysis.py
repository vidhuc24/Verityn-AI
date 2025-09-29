#!/usr/bin/env python3
"""
Simplified Chunking and Embedding Analysis Test

This test investigates:
1. Current chunking strategy effectiveness
2. Similarity score distributions
3. Sample document chunks and their quality

Uses real SOX documents and focuses on the core issues.
"""

import asyncio
import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
import sys
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.services.vector_database import vector_db_service
from backend.app.services.document_processor import EnhancedDocumentProcessor
from fastapi import UploadFile
from io import BytesIO
import openai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleChunkingAnalyzer:
    def __init__(self):
        self.document_processor = EnhancedDocumentProcessor()
        
    async def analyze_current_chunking(self):
        """Analyze the current chunking strategy and similarity scores."""
        logger.info("🔍 Analyzing current chunking strategy and similarity scores...")
        
        # Test queries with different complexity levels
        test_queries = [
            "What are the key findings from the access review?",
            "SOX compliance requirements",
            "material weaknesses",
            "internal controls assessment",
            "risk management procedures"
        ]
        
        analysis_results = {
            "chunking_analysis": {},
            "similarity_analysis": {},
            "sample_chunks": {},
            "recommendations": []
        }
        
        # Analyze similarity scores for each query
        for query in test_queries:
            logger.info(f"  🔍 Analyzing query: '{query[:40]}...'")
            
            try:
                # Search with very low threshold to get all results
                results = await vector_db_service.semantic_search(query, limit=20, score_threshold=0.0)
                
                if results:
                    scores = [result.score for result in results]
                    
                    analysis_results["similarity_analysis"][query] = {
                        "total_results": len(results),
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
                        "top_3_scores": sorted(scores, reverse=True)[:3],
                        "sample_results": [
                            {
                                "score": result.score,
                                "content_preview": result.page_content[:100] + "..." if result.page_content else "No content",
                                "metadata": result.metadata
                            }
                            for result in results[:3]
                        ]
                    }
                else:
                    analysis_results["similarity_analysis"][query] = {"error": "No results found"}
                    
            except Exception as e:
                analysis_results["similarity_analysis"][query] = {"error": str(e)}
        
        # Get sample chunks from the database
        analysis_results["sample_chunks"] = await self._get_sample_chunks()
        
        # Generate recommendations
        analysis_results["recommendations"] = self._generate_recommendations(analysis_results)
        
        return analysis_results
    
    async def _get_sample_chunks(self) -> Dict:
        """Get sample chunks from the vector database."""
        try:
            # Get a few sample points to analyze chunk quality
            sample_results = await vector_db_service.semantic_search("sample", limit=10, score_threshold=0.0)
            
            sample_chunks = {}
            for i, result in enumerate(sample_results):
                sample_chunks[f"chunk_{i}"] = {
                    "score": result.score,
                    "content_length": len(result.page_content) if result.page_content else 0,
                    "content_preview": result.page_content[:150] + "..." if result.page_content else "No content",
                    "metadata": result.metadata,
                    "chunk_quality": self._assess_chunk_quality(result.page_content) if result.page_content else "No content"
                }
            
            return {
                "total_chunks_analyzed": len(sample_results),
                "chunks": sample_chunks
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _assess_chunk_quality(self, content: str) -> Dict:
        """Assess the quality of a chunk."""
        if not content:
            return {"quality": "empty", "issues": ["No content"]}
        
        issues = []
        quality_score = 100
        
        # Check chunk size
        if len(content) < 50:
            issues.append("Too short")
            quality_score -= 30
        elif len(content) > 1000:
            issues.append("Too long")
            quality_score -= 20
        
        # Check for audit-specific terms
        audit_terms = ["sox", "compliance", "control", "risk", "audit", "finding", "deficiency", "material"]
        content_lower = content.lower()
        audit_term_count = sum(1 for term in audit_terms if term in content_lower)
        
        if audit_term_count == 0:
            issues.append("No audit-specific terms")
            quality_score -= 25
        elif audit_term_count < 2:
            issues.append("Few audit-specific terms")
            quality_score -= 10
        
        # Check for sentence completeness
        if not content.strip().endswith(('.', '!', '?')):
            issues.append("Incomplete sentence")
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
        
        return {
            "quality": quality_level,
            "score": quality_score,
            "issues": issues,
            "audit_term_count": audit_term_count
        }
    
    def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Analyze similarity scores
        similarity_analysis = analysis_results.get("similarity_analysis", {})
        low_score_queries = []
        
        for query, analysis in similarity_analysis.items():
            if "score_stats" in analysis:
                mean_score = analysis["score_stats"]["mean"]
                if mean_score < 0.2:
                    low_score_queries.append((query, mean_score))
        
        if low_score_queries:
            recommendations.append(f"Low similarity scores detected for {len(low_score_queries)} queries (mean scores < 0.2)")
            recommendations.append("Consider improving document chunking strategy or query formulation")
        
        # Analyze chunk quality
        sample_chunks = analysis_results.get("sample_chunks", {})
        if "chunks" in sample_chunks:
            chunks = sample_chunks["chunks"]
            poor_quality_chunks = [chunk for chunk in chunks.values() 
                                 if chunk.get("chunk_quality", {}).get("quality") in ["poor", "fair"]]
            
            if poor_quality_chunks:
                recommendations.append(f"{len(poor_quality_chunks)} chunks have poor/fair quality")
                recommendations.append("Consider adjusting chunk size, overlap, or chunking method")
        
        # Check score distribution
        for query, analysis in similarity_analysis.items():
            if "score_distribution" in analysis:
                dist = analysis["score_distribution"]
                if dist.get("above_0.3", 0) == 0:
                    recommendations.append(f"No high-confidence matches for query: '{query[:30]}...'")
                    break
        
        return recommendations
    
    async def test_different_chunk_sizes(self):
        """Test different chunk sizes with a single document."""
        logger.info("🧪 Testing different chunk sizes...")
        
        # Load one document for testing
        sox_docs_path = Path("data/sox_test_documents/sox_access_review_2024.txt")
        if not sox_docs_path.exists():
            logger.error("Test document not found")
            return {}
        
        with open(sox_docs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunk_sizes = [200, 500, 1000]
        overlap_ratios = [0.1, 0.2, 0.3]  # 10%, 20%, 30% overlap
        
        results = {}
        
        for chunk_size in chunk_sizes:
            for overlap_ratio in overlap_ratios:
                overlap = int(chunk_size * overlap_ratio)
                strategy_name = f"size_{chunk_size}_overlap_{overlap}"
                
                logger.info(f"  🧪 Testing: {strategy_name}")
                
                try:
                    # Create UploadFile
                    file_obj = UploadFile(
                        file=BytesIO(content.encode('utf-8')),
                        filename="test_document.txt",
                        headers={"content-type": "text/plain"}
                    )
                    
                    # Temporarily modify chunking parameters
                    original_chunk_size = getattr(self.document_processor, 'chunk_size', 500)
                    original_chunk_overlap = getattr(self.document_processor, 'chunk_overlap', 100)
                    
                    self.document_processor.chunk_size = chunk_size
                    self.document_processor.chunk_overlap = overlap
                    
                    # Process document
                    result = await self.document_processor.process_document(
                        file=file_obj,
                        document_id=f"test_{strategy_name}"
                    )
                    
                    if result and result.get("status") in ["success", "processed"]:
                        chunks = result.get("chunks", [])
                        
                        results[strategy_name] = {
                            "chunk_size": chunk_size,
                            "chunk_overlap": overlap,
                            "chunk_count": len(chunks),
                            "avg_chunk_size": np.mean([len(chunk.page_content) for chunk in chunks]) if chunks else 0,
                            "chunk_size_std": np.std([len(chunk.page_content) for chunk in chunks]) if chunks else 0,
                            "sample_chunks": [chunk.page_content[:100] + "..." for chunk in chunks[:2]] if chunks else []
                        }
                    
                    # Restore original settings
                    self.document_processor.chunk_size = original_chunk_size
                    self.document_processor.chunk_overlap = original_chunk_overlap
                    
                except Exception as e:
                    results[strategy_name] = {"error": str(e)}
        
        return results
    
    async def run_analysis(self):
        """Run the complete analysis."""
        logger.info("🚀 Starting Simplified Chunking and Embedding Analysis")
        
        try:
            # Analyze current chunking
            current_analysis = await self.analyze_current_chunking()
            
            # Test different chunk sizes
            chunk_size_tests = await self.test_different_chunk_sizes()
            
            # Compile final results
            final_results = {
                "current_analysis": current_analysis,
                "chunk_size_tests": chunk_size_tests,
                "summary": self._generate_summary(current_analysis, chunk_size_tests)
            }
            
            # Save results
            results_file = Path("scripts/testing/simple_chunking_analysis_results.json")
            with open(results_file, 'w') as f:
                json.dump(final_results, f, indent=2, default=str)
            
            logger.info(f"📊 Results saved to: {results_file}")
            
            # Print summary
            self._print_summary(final_results)
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            raise
    
    def _generate_summary(self, current_analysis: Dict, chunk_size_tests: Dict) -> Dict:
        """Generate analysis summary."""
        summary = {
            "similarity_score_issues": [],
            "chunking_issues": [],
            "recommendations": []
        }
        
        # Analyze similarity scores
        similarity_analysis = current_analysis.get("similarity_analysis", {})
        for query, analysis in similarity_analysis.items():
            if "score_stats" in analysis:
                mean_score = analysis["score_stats"]["mean"]
                if mean_score < 0.2:
                    summary["similarity_score_issues"].append({
                        "query": query,
                        "mean_score": mean_score,
                        "issue": "Low similarity scores"
                    })
        
        # Analyze chunk quality
        sample_chunks = current_analysis.get("sample_chunks", {})
        if "chunks" in sample_chunks:
            chunks = sample_chunks["chunks"]
            poor_chunks = [chunk for chunk in chunks.values() 
                         if chunk.get("chunk_quality", {}).get("quality") in ["poor", "fair"]]
            if poor_chunks:
                summary["chunking_issues"].append(f"{len(poor_chunks)} chunks have quality issues")
        
        # Add recommendations
        summary["recommendations"] = current_analysis.get("recommendations", [])
        
        return summary
    
    def _print_summary(self, results: Dict):
        """Print analysis summary."""
        print("\n" + "="*80)
        print("🔬 SIMPLIFIED CHUNKING AND EMBEDDING ANALYSIS SUMMARY")
        print("="*80)
        
        # Similarity analysis
        print("\n🔍 SIMILARITY SCORE ANALYSIS:")
        current_analysis = results.get("current_analysis", {})
        similarity_analysis = current_analysis.get("similarity_analysis", {})
        
        for query, analysis in similarity_analysis.items():
            if "score_stats" in analysis:
                stats = analysis["score_stats"]
                dist = analysis.get("score_distribution", {})
                print(f"  '{query[:40]}...':")
                print(f"    📊 Mean score: {stats['mean']:.3f}, Max: {stats['max']:.3f}")
                print(f"    📈 Above 0.3: {dist.get('above_0.3', 0)}, Above 0.1: {dist.get('above_0.1', 0)}")
        
        # Chunk quality analysis
        print("\n📄 CHUNK QUALITY ANALYSIS:")
        sample_chunks = current_analysis.get("sample_chunks", {})
        if "chunks" in sample_chunks:
            chunks = sample_chunks["chunks"]
            quality_counts = {}
            for chunk in chunks.values():
                quality = chunk.get("chunk_quality", {}).get("quality", "unknown")
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            for quality, count in quality_counts.items():
                print(f"  {quality.capitalize()}: {count} chunks")
        
        # Recommendations
        recommendations = current_analysis.get("recommendations", [])
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution."""
    analyzer = SimpleChunkingAnalyzer()
    await analyzer.run_analysis()

if __name__ == "__main__":
    asyncio.run(main())
