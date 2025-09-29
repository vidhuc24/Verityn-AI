#!/usr/bin/env python3
"""
Chunking Strategy and Embedding Quality Analysis Test

This test investigates:
1. Different chunking strategies (size, overlap, method)
2. Embedding quality and similarity score distributions
3. A/B testing of chunking approaches
4. Sample embedding analysis

Uses real SOX documents and dynamic scenarios.
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

from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.services.vector_database import vector_db_service
from backend.app.services.classification_engine import ClassificationEngine
from fastapi import UploadFile
from io import BytesIO
import openai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChunkingEmbeddingAnalyzer:
    def __init__(self):
        self.document_processor = EnhancedDocumentProcessor()
        self.classification_engine = ClassificationEngine()
        self.test_documents = []
        self.chunking_strategies = {
            "small_chunks": {"chunk_size": 200, "chunk_overlap": 50},
            "medium_chunks": {"chunk_size": 500, "chunk_overlap": 100}, 
            "large_chunks": {"chunk_size": 1000, "chunk_overlap": 200},
            "no_overlap": {"chunk_size": 500, "chunk_overlap": 0},
            "high_overlap": {"chunk_size": 500, "chunk_overlap": 250}
        }
        
    async def load_test_documents(self):
        """Load real SOX documents for testing."""
        logger.info("📄 Loading real SOX test documents...")
        
        sox_docs_path = Path("data/sox_test_documents")
        if not sox_docs_path.exists():
            raise FileNotFoundError("SOX test documents directory not found")
        
        # Load TXT documents
        txt_files = [
            "sox_access_review_2024.txt",
            "sox_risk_assessment_2024.txt", 
            "sox_financial_controls_2024.txt",
            "sox_internal_controls_2024.txt"
        ]
        
        for filename in txt_files:
            file_path = sox_docs_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.test_documents.append({
                    "filename": filename,
                    "content": content,
                    "file_path": str(file_path)
                })
                logger.info(f"  ✅ Loaded {filename} ({len(content)} chars)")
        
        logger.info(f"📊 Loaded {len(self.test_documents)} documents for analysis")
        
    async def test_chunking_strategies(self):
        """Test different chunking strategies and analyze results."""
        logger.info("🔬 Testing different chunking strategies...")
        
        results = {}
        
        for strategy_name, strategy_config in self.chunking_strategies.items():
            logger.info(f"  🧪 Testing strategy: {strategy_name}")
            logger.info(f"    📏 Chunk size: {strategy_config['chunk_size']}, Overlap: {strategy_config['chunk_overlap']}")
            
            strategy_results = await self._test_single_chunking_strategy(strategy_name, strategy_config)
            results[strategy_name] = strategy_results
            
        return results
    
    async def _test_single_chunking_strategy(self, strategy_name: str, strategy_config: Dict) -> Dict:
        """Test a single chunking strategy."""
        # Temporarily modify document processor settings
        original_chunk_size = getattr(self.document_processor, 'chunk_size', 500)
        original_chunk_overlap = getattr(self.document_processor, 'chunk_overlap', 100)
        
        try:
            # Set new chunking parameters
            self.document_processor.chunk_size = strategy_config['chunk_size']
            self.document_processor.chunk_overlap = strategy_config['chunk_overlap']
            
            strategy_results = {
                "config": strategy_config,
                "documents": {},
                "summary": {}
            }
            
            # Test with each document
            for doc in self.test_documents:
                doc_results = await self._process_document_with_strategy(doc, strategy_name)
                strategy_results["documents"][doc["filename"]] = doc_results
            
            # Calculate summary statistics
            strategy_results["summary"] = self._calculate_strategy_summary(strategy_results["documents"])
            
            return strategy_results
            
        finally:
            # Restore original settings
            self.document_processor.chunk_size = original_chunk_size
            self.document_processor.chunk_overlap = original_chunk_overlap
    
    async def _process_document_with_strategy(self, document: Dict, strategy_name: str) -> Dict:
        """Process a single document with the given strategy."""
        filename = document["filename"]
        content = document["content"]
        
        # Create UploadFile object
        file_obj = UploadFile(
            file=BytesIO(content.encode('utf-8')),
            filename=filename,
            headers={"content-type": "text/plain"}
        )
        
        try:
            # Process document
            result = await self.document_processor.process_document(
                file=file_obj,
                document_id=f"{strategy_name}_{filename.replace('.txt', '')}"
            )
            
            if result and result.get("status") in ["success", "processed"]:
                # Get chunk information
                chunks = result.get("chunks", [])
                
                return {
                    "status": "success",
                    "chunk_count": len(chunks),
                    "chunk_sizes": [len(chunk.page_content) for chunk in chunks],
                    "avg_chunk_size": np.mean([len(chunk.page_content) for chunk in chunks]) if chunks else 0,
                    "chunk_size_std": np.std([len(chunk.page_content) for chunk in chunks]) if chunks else 0,
                    "sample_chunks": [chunk.page_content[:100] + "..." for chunk in chunks[:3]] if chunks else []
                }
            else:
                return {
                    "status": "failed",
                    "error": result.get("error", "Unknown error") if result else "No result"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_strategy_summary(self, documents: Dict) -> Dict:
        """Calculate summary statistics for a chunking strategy."""
        successful_docs = [doc for doc in documents.values() if doc["status"] == "success"]
        
        if not successful_docs:
            return {"status": "no_successful_documents"}
        
        all_chunk_counts = [doc["chunk_count"] for doc in successful_docs]
        all_avg_sizes = [doc["avg_chunk_size"] for doc in successful_docs]
        
        return {
            "successful_documents": len(successful_docs),
            "total_documents": len(documents),
            "avg_chunk_count": np.mean(all_chunk_counts),
            "avg_chunk_size": np.mean(all_avg_sizes),
            "chunk_count_std": np.std(all_chunk_counts),
            "chunk_size_std": np.std(all_avg_sizes)
        }
    
    async def analyze_embedding_quality(self):
        """Analyze embedding quality and similarity score distributions."""
        logger.info("🔍 Analyzing embedding quality and similarity scores...")
        
        # Test queries with different complexity levels
        test_queries = [
            "What are the key findings from the access review?",
            "SOX compliance requirements",
            "material weaknesses",
            "internal controls assessment",
            "risk management procedures",
            "financial reporting controls",
            "audit findings and recommendations",
            "control deficiencies identified"
        ]
        
        embedding_analysis = {
            "queries": {},
            "score_distribution": {},
            "sample_embeddings": {}
        }
        
        for query in test_queries:
            logger.info(f"  🔍 Analyzing query: '{query[:50]}...'")
            
            # Get embeddings for query
            query_embedding = await self._get_query_embedding(query)
            
            # Search with different thresholds to see score distribution
            score_analysis = await self._analyze_score_distribution(query)
            
            embedding_analysis["queries"][query] = {
                "query_embedding_shape": query_embedding.shape if query_embedding is not None else None,
                "score_analysis": score_analysis
            }
        
        # Get sample document embeddings
        embedding_analysis["sample_embeddings"] = await self._get_sample_document_embeddings()
        
        return embedding_analysis
    
    async def _get_query_embedding(self, query: str):
        """Get embedding for a query."""
        try:
            response = await openai.Embedding.acreate(
                input=query,
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            logger.error(f"Failed to get query embedding: {str(e)}")
            return None
    
    async def _analyze_score_distribution(self, query: str) -> Dict:
        """Analyze similarity score distribution for a query."""
        try:
            # Search with very low threshold to get all results
            results = await vector_db_service.semantic_search(query, limit=50, score_threshold=0.0)
            
            if not results:
                return {"error": "No results found"}
            
            scores = [result.score for result in results]
            
            return {
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
                "sample_scores": scores[:10]  # First 10 scores
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_sample_document_embeddings(self) -> Dict:
        """Get sample document embeddings for analysis."""
        try:
            # Get collection info
            collection_info = await vector_db_service.get_collection_info()
            total_points = collection_info.get("vectors_count", 0)
            
            if total_points == 0:
                return {"error": "No documents in vector database"}
            
            # Get a few sample points
            sample_results = await vector_db_service.semantic_search("sample", limit=5, score_threshold=0.0)
            
            sample_embeddings = {}
            for i, result in enumerate(sample_results):
                sample_embeddings[f"sample_{i}"] = {
                    "score": result.score,
                    "metadata": result.metadata,
                    "content_preview": result.page_content[:100] + "..." if result.page_content else "No content"
                }
            
            return {
                "total_documents": total_points,
                "sample_count": len(sample_results),
                "samples": sample_embeddings
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def run_comprehensive_analysis(self):
        """Run comprehensive chunking and embedding analysis."""
        logger.info("🚀 Starting Comprehensive Chunking and Embedding Analysis")
        
        try:
            # Load test documents
            await self.load_test_documents()
            
            # Test chunking strategies
            chunking_results = await self.test_chunking_strategies()
            
            # Analyze embedding quality
            embedding_results = await self.analyze_embedding_quality()
            
            # Compile final results
            final_results = {
                "chunking_analysis": chunking_results,
                "embedding_analysis": embedding_results,
                "recommendations": self._generate_recommendations(chunking_results, embedding_results)
            }
            
            # Save results
            results_file = Path("scripts/testing/chunking_embedding_analysis_results.json")
            with open(results_file, 'w') as f:
                json.dump(final_results, f, indent=2, default=str)
            
            logger.info(f"📊 Results saved to: {results_file}")
            
            # Print summary
            self._print_analysis_summary(final_results)
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            raise
    
    def _generate_recommendations(self, chunking_results: Dict, embedding_results: Dict) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Analyze chunking results
        successful_strategies = [name for name, result in chunking_results.items() 
                               if result.get("summary", {}).get("successful_documents", 0) > 0]
        
        if successful_strategies:
            # Find strategy with best chunk size consistency
            best_strategy = None
            best_score = float('inf')
            
            for strategy in successful_strategies:
                summary = chunking_results[strategy]["summary"]
                chunk_size_std = summary.get("chunk_size_std", float('inf'))
                if chunk_size_std < best_score:
                    best_score = chunk_size_std
                    best_strategy = strategy
            
            if best_strategy:
                recommendations.append(f"Recommended chunking strategy: {best_strategy} (most consistent chunk sizes)")
        
        # Analyze embedding results
        for query, analysis in embedding_results.get("queries", {}).items():
            score_analysis = analysis.get("score_analysis", {})
            if "score_stats" in score_analysis:
                mean_score = score_analysis["score_stats"]["mean"]
                if mean_score < 0.2:
                    recommendations.append(f"Low similarity scores detected (mean: {mean_score:.3f}) - consider improving document content or query formulation")
                    break
        
        return recommendations
    
    def _print_analysis_summary(self, results: Dict):
        """Print analysis summary."""
        print("\n" + "="*80)
        print("🔬 CHUNKING AND EMBEDDING ANALYSIS SUMMARY")
        print("="*80)
        
        # Chunking analysis summary
        print("\n📏 CHUNKING STRATEGY ANALYSIS:")
        chunking_results = results.get("chunking_analysis", {})
        for strategy, data in chunking_results.items():
            summary = data.get("summary", {})
            if summary.get("status") != "no_successful_documents":
                print(f"  {strategy}:")
                print(f"    ✅ Successful docs: {summary.get('successful_documents', 0)}/{summary.get('total_documents', 0)}")
                print(f"    📊 Avg chunk count: {summary.get('avg_chunk_count', 0):.1f}")
                print(f"    📏 Avg chunk size: {summary.get('avg_chunk_size', 0):.1f} chars")
                print(f"    📈 Chunk size std: {summary.get('chunk_size_std', 0):.1f}")
        
        # Embedding analysis summary
        print("\n🔍 EMBEDDING QUALITY ANALYSIS:")
        embedding_results = results.get("embedding_analysis", {})
        queries = embedding_results.get("queries", {})
        
        if queries:
            print("  Query Similarity Score Statistics:")
            for query, analysis in list(queries.items())[:3]:  # Show first 3 queries
                score_analysis = analysis.get("score_analysis", {})
                if "score_stats" in score_analysis:
                    stats = score_analysis["score_stats"]
                    print(f"    '{query[:30]}...': mean={stats['mean']:.3f}, max={stats['max']:.3f}")
        
        # Recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution."""
    analyzer = ChunkingEmbeddingAnalyzer()
    await analyzer.run_comprehensive_analysis()

if __name__ == "__main__":
    asyncio.run(main())
