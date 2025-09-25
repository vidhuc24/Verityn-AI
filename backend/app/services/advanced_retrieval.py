"""
Advanced Retrieval Service for Verityn AI.

This module implements multiple advanced retrieval techniques following
bootcamp Session 9 patterns for enhanced RAG performance.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import time
from collections import OrderedDict
import hashlib
import json

from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.ensemble import EnsembleRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

logger = logging.getLogger(__name__)

# Optional Cohere import
try:
    from langchain_cohere import CohereRerank
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    logger.warning("Cohere not available - will use LLM-based compression")

from backend.app.services.vector_database import vector_db_service
from backend.app.config import settings


class InMemoryCache:
    """In-memory cache with TTL and LRU eviction for Session 9 optimization."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize the in-memory cache.
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds (5 minutes)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
    
    def _generate_cache_key(self, query: str, limit: int, filters: Optional[Dict] = None) -> str:
        """Generate a unique cache key for the search parameters."""
        # Create a hash of the search parameters
        key_data = {
            "query": query.lower().strip(),
            "limit": limit,
            "filters": filters or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, query: str, limit: int, filters: Optional[Dict] = None) -> Optional[Any]:
        """Get a value from cache if it exists and hasn't expired."""
        cache_key = self._generate_cache_key(query, limit, filters)
        self.stats["total_requests"] += 1
        
        if cache_key in self.cache:
            # Check if entry has expired
            if time.time() - self.timestamps[cache_key] < self.default_ttl:
                # Move to end (LRU)
                self.cache.move_to_end(cache_key)
                self.stats["hits"] += 1
                logger.debug(f"Cache HIT for query: {query[:50]}...")
                return self.cache[cache_key]
            else:
                # Entry expired, remove it
                del self.cache[cache_key]
                del self.timestamps[cache_key]
                logger.debug(f"Cache entry expired for query: {query[:50]}...")
        
        self.stats["misses"] += 1
        logger.debug(f"Cache MISS for query: {query[:50]}...")
        return None
    
    def set(self, query: str, limit: int, filters: Optional[Dict], value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache with optional TTL override."""
        cache_key = self._generate_cache_key(query, limit, filters)
        ttl_seconds = ttl or self.default_ttl
        
        # Evict oldest entries if cache is full
        while len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
            self.stats["evictions"] += 1
            logger.debug(f"Cache eviction due to size limit")
        
        # Add new entry
        self.cache[cache_key] = value
        self.timestamps[cache_key] = time.time()
        
        # Move to end (LRU)
        self.cache.move_to_end(cache_key)
        logger.debug(f"Cache SET for query: {query[:50]}... (TTL: {ttl_seconds}s)")
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern (e.g., document type)."""
        invalidated = 0
        keys_to_remove = []
        
        for key in list(self.cache.keys()):
            # Check if any cached result contains the pattern
            cached_value = self.cache[key]
            if isinstance(cached_value, list):
                for result in cached_value:
                    if isinstance(result, dict):
                        metadata = result.get("metadata", {})
                        if pattern.lower() in str(metadata).lower():
                            keys_to_remove.append(key)
                            break
        
        # Remove invalidated entries
        for key in keys_to_remove:
            del self.cache[key]
            del self.timestamps[key]
            invalidated += 1
        
        logger.info(f"Cache invalidation: {invalidated} entries removed for pattern '{pattern}'")
        return invalidated
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.timestamps.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        hit_rate = (self.stats["hits"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
        
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": f"{hit_rate:.1f}%",
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "total_requests": self.stats["total_requests"],
            "memory_usage_mb": len(self.cache) * 0.001  # Rough estimate
        }
    
    def set_ttl(self, ttl_seconds: int) -> None:
        """Set a new default TTL for cache entries."""
        self.default_ttl = ttl_seconds
        logger.info(f"Cache TTL updated to {ttl_seconds} seconds")


class AdvancedRetrievalService:
    """Advanced retrieval service with multiple techniques and in-memory caching."""
    
    def __init__(self, use_memory: bool = True, cache_size: int = 1000, cache_ttl: int = 300):
        """
        Initialize the advanced retrieval service.
        
        Args:
            use_memory: Enable in-memory caching (default: True for Session 9 optimization)
            cache_size: Maximum cache entries
            cache_ttl: Cache TTL in seconds
        """
        self.vector_db = vector_db_service
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )
        
        # Initialize in-memory cache for Session 9 optimization
        self.cache_enabled = use_memory
        if self.cache_enabled:
            self.cache = InMemoryCache(max_size=cache_size, default_ttl=cache_ttl)
            logger.info(f"Session 9 in-memory cache initialized (size: {cache_size}, TTL: {cache_ttl}s)")
        else:
            self.cache = None
            logger.info("In-memory caching disabled")
        
        # Initialize different retrievers
        self.bm25_retriever = None
        self.compression_retriever = None
        self.multi_query_retriever = None
        self.ensemble_retriever = None
        
        # Audit-specific query expansion terms
        self.audit_query_expansions = {
            "sox": ["SOX 404", "Sarbanes-Oxley", "internal controls", "financial reporting"],
            "access_review": ["user access", "permissions", "authorization", "access controls"],
            "material_weakness": ["material weakness", "significant deficiency", "control deficiency"],
            "compliance": ["compliance", "regulatory", "audit", "governance"],
            "risk": ["risk assessment", "risk management", "risk mitigation"],
            "financial": ["financial", "accounting", "reconciliation", "month-end close"]
        }
    
    async def initialize_retrievers(self, documents: Optional[List[Document]] = None):
        """Initialize all retrieval techniques with documents."""
        try:
            # If no documents provided, try to get from vector database
            if documents is None:
                # For in-memory testing, we'll initialize with empty documents
                # The actual retrieval will happen through the vector database
                documents = []
            
            # Initialize BM25 retriever only if we have documents
            if documents:
                self.bm25_retriever = BM25Retriever.from_documents(documents)
            else:
                # For in-memory mode, we'll skip BM25 initialization
                # and rely on vector database for retrieval
                self.bm25_retriever = None
                logger.info("BM25 retriever skipped - using vector database only")
            
            # Initialize compression retriever with reranking
            if COHERE_AVAILABLE and settings.COHERE_API_KEY:
                try:
                    # Initialize Cohere client with API key
                    compressor = CohereRerank(
                        model="rerank-v3.5",
                        cohere_api_key=settings.COHERE_API_KEY
                    )
                    if self.bm25_retriever:
                        self.compression_retriever = ContextualCompressionRetriever(
                            base_compressor=compressor,
                            base_retriever=self.bm25_retriever
                        )
                        logger.info("Cohere reranker initialized for compression retrieval")
                    else:
                        self.compression_retriever = None
                        logger.info("Compression retriever skipped - no BM25 retriever available")
                except Exception as e:
                    logger.warning(f"Cohere initialization failed: {str(e)} - falling back to LLM-based compression")
                    self.compression_retriever = None
            else:
                # Fallback to LLM-based compression
                if self.bm25_retriever:
                    from langchain.retrievers.document_compressors import LLMChainExtractor
                    compressor = LLMChainExtractor.from_llm(
                        llm=self._get_llm()
                    )
                    self.compression_retriever = ContextualCompressionRetriever(
                        base_compressor=compressor,
                        base_retriever=self.bm25_retriever
                    )
                    logger.info("LLM-based compression retriever initialized")
                else:
                    self.compression_retriever = None
                    logger.info("Compression retriever skipped - no BM25 retriever available")
            
            # Initialize multi-query retriever
            if self.bm25_retriever:
                try:
                    # Use newer initialization method if available
                    self.multi_query_retriever = MultiQueryRetriever.from_llm(
                        retriever=self.bm25_retriever,
                        llm=self._get_llm()
                    )
                except Exception as e:
                    logger.warning(f"Multi-query retriever initialization failed: {str(e)}")
                    self.multi_query_retriever = None
            else:
                self.multi_query_retriever = None
                logger.info("Multi-query retriever skipped - no BM25 retriever available")
            
            # Initialize ensemble retriever (simplified for in-memory testing)
            # Only use BM25 for now to avoid Runnable type validation errors
            if self.bm25_retriever:
                self.ensemble_retriever = EnsembleRetriever(
                    retrievers=[self.bm25_retriever],
                    weights=[1.0]  # Single retriever with full weight
                )
            else:
                self.ensemble_retriever = None
                logger.info("Ensemble retriever skipped - no BM25 retriever available")
            
            logger.info("Advanced retrievers initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize advanced retrievers: {str(e)}")
            return False
    
    def _get_llm(self):
        """Get LLM instance for retrieval operations."""
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def _get_vector_retriever(self):
        """Get vector-based retriever."""
        # This would be our existing vector database retriever
        # For now, we'll use a simple implementation
        return self.vector_db
    
    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword approaches with caching.
        
        Args:
            query: Search query
            limit: Maximum number of results
            filters: Optional metadata filters
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            use_cache: Enable caching for this search (default: True)
            
        Returns:
            List of search results with scores and cache metadata
        """
        start_time = time.time()
        
        # Check cache first if enabled
        if use_cache and self.cache_enabled:
            cached_results = self.cache.get(query, limit, filters)
            if cached_results:
                execution_time = time.time() - start_time
                logger.info(f"Cache HIT for query: '{query[:50]}...' - returned in {execution_time:.3f}s")
                
                # Add cache metadata to results
                for result in cached_results:
                    result["cache_metadata"] = {
                        "source": "cache",
                        "cache_hit": True,
                        "execution_time": execution_time,
                        "cache_timestamp": datetime.now().isoformat()
                    }
                
                return cached_results
        
        # Cache miss or disabled - perform actual search
        try:
            logger.info(f"Cache MISS for query: '{query[:50]}...' - performing hybrid search")
            
            # Perform semantic search
            semantic_results = await self.vector_db.semantic_search(
                query_text=query,
                limit=limit * 2,  # Get more results for reranking
                filters=filters
            )
            
            # Perform keyword search (BM25)
            if self.bm25_retriever:
                try:
                    # Use the newer invoke method instead of deprecated get_relevant_documents
                    keyword_docs = await self.bm25_retriever.ainvoke(query)
                except AttributeError:
                    # Fallback to old method if invoke not available
                    keyword_docs = self.bm25_retriever.get_relevant_documents(query)
                
                keyword_results = [
                    {
                        "chunk_text": doc.page_content,
                        "metadata": doc.metadata,
                        "score": 1.0 - (i * 0.1)  # Simple scoring
                    }
                    for i, doc in enumerate(keyword_docs[:limit * 2])
                ]
            else:
                keyword_results = []
            
            # Combine and rerank results
            combined_results = self._combine_search_results(
                semantic_results, keyword_results, semantic_weight, keyword_weight
            )
            
            # Apply filters if specified
            if filters:
                combined_results = self._apply_filters(combined_results, filters)
            
            final_results = combined_results[:limit]
            
            # Add performance metadata
            execution_time = time.time() - start_time
            for result in final_results:
                result["search_metadata"] = {
                    "source": "hybrid_search",
                    "cache_hit": False,
                    "execution_time": execution_time,
                    "search_timestamp": datetime.now().isoformat(),
                    "semantic_weight": semantic_weight,
                    "keyword_weight": keyword_weight,
                    "total_results_processed": len(combined_results)
                }
            
            # Cache the results if enabled
            if use_cache and self.cache_enabled:
                self.cache.set(query, limit, filters, final_results)
                logger.info(f"Cached hybrid search results for query: '{query[:50]}...' (TTL: {self.cache.default_ttl}s)")
            
            logger.info(f"Hybrid search completed in {execution_time:.3f}s for query: '{query[:50]}...'")
            return final_results
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Hybrid search failed in {execution_time:.3f}s for query '{query[:50]}...': {str(e)}")
            return []
    
    # Cache Management Methods for Session 9 Optimization
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        if not self.cache_enabled or not self.cache:
            return {"status": "cache_disabled"}
        return self.cache.get_stats()
    
    def clear_cache(self) -> None:
        """Clear all cached search results."""
        if self.cache_enabled and self.cache:
            self.cache.clear()
            logger.info("Advanced retrieval cache cleared")
    
    def invalidate_cache_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern (e.g., document type)."""
        if not self.cache_enabled or not self.cache:
            return 0
        return self.cache.invalidate_pattern(pattern)
    
    def set_cache_ttl(self, ttl_seconds: int) -> None:
        """Set a new default TTL for cache entries."""
        if self.cache_enabled and self.cache:
            self.cache.set_ttl(ttl_seconds)
    
    def enable_cache(self, cache_size: int = 1000, cache_ttl: int = 300) -> None:
        """Enable in-memory caching with specified parameters."""
        if not self.cache_enabled:
            self.cache = InMemoryCache(max_size=cache_size, default_ttl=cache_ttl)
            self.cache_enabled = True
            logger.info(f"Session 9 in-memory cache enabled (size: {cache_size}, TTL: {cache_ttl}s)")
    
    def disable_cache(self) -> None:
        """Disable in-memory caching."""
        if self.cache_enabled:
            self.cache = None
            self.cache_enabled = False
            logger.info("In-memory caching disabled")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get current cache configuration and status."""
        return {
            "cache_enabled": self.cache_enabled,
            "cache_size": self.cache.max_size if self.cache else 0,
            "cache_ttl": self.cache.default_ttl if self.cache else 0,
            "stats": self.get_cache_stats() if self.cache_enabled else {"status": "cache_disabled"}
        }
    
    def _combine_search_results(
        self,
        semantic_results: List[Dict],
        keyword_results: List[Dict],
        semantic_weight: float,
        keyword_weight: float
    ) -> List[Dict]:
        """Combine and rerank search results."""
        # Create a mapping of document IDs to scores
        doc_scores = {}
        
        # Add semantic search scores
        for result in semantic_results:
            doc_id = result.get("document_id", result.get("chunk_text", "")[:50])
            doc_scores[doc_id] = {
                "result": result,
                "semantic_score": result.get("score", 0.0),
                "keyword_score": 0.0
            }
        
        # Add keyword search scores
        for result in keyword_results:
            doc_id = result.get("document_id", result.get("chunk_text", "")[:50])
            if doc_id in doc_scores:
                doc_scores[doc_id]["keyword_score"] = result.get("score", 0.0)
            else:
                doc_scores[doc_id] = {
                    "result": result,
                    "semantic_score": 0.0,
                    "keyword_score": result.get("score", 0.0)
                }
        
        # Calculate combined scores
        combined_results = []
        for doc_id, scores in doc_scores.items():
            combined_score = (
                scores["semantic_score"] * semantic_weight +
                scores["keyword_score"] * keyword_weight
            )
            result = scores["result"].copy()
            result["combined_score"] = combined_score
            result["semantic_score"] = scores["semantic_score"]
            result["keyword_score"] = scores["keyword_score"]
            combined_results.append(result)
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x["combined_score"], reverse=True)
        return combined_results
    
    async def query_expansion_search(
        self,
        query: str,
        limit: int = 10,
        expansion_terms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform search with query expansion for audit terminology.
        
        Args:
            query: Original search query
            limit: Maximum number of results
            expansion_terms: Additional terms to expand query
            
        Returns:
            List of search results
        """
        try:
            # Generate expanded queries
            expanded_queries = self._expand_query(query, expansion_terms)
            
            # Perform search with each expanded query
            all_results = []
            for expanded_query in expanded_queries:
                results = await self.vector_db.semantic_search(
                    query_text=expanded_query,
                    limit=limit // len(expanded_queries)
                )
                all_results.extend(results)
            
            # Deduplicate and rerank
            unique_results = self._deduplicate_results(all_results)
            unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return unique_results[:limit]
            
        except Exception as e:
            logger.error(f"Query expansion search failed: {str(e)}")
            return []
    
    def _expand_query(self, query: str, expansion_terms: Optional[List[str]] = None) -> List[str]:
        """Expand query with audit-specific terminology."""
        expanded_queries = [query]
        
        # Add audit-specific expansions
        query_lower = query.lower()
        for category, terms in self.audit_query_expansions.items():
            if any(term in query_lower for term in [category, *terms[:2]]):
                for term in terms:
                    expanded_queries.append(f"{query} {term}")
        
        # Add custom expansion terms
        if expansion_terms:
            for term in expansion_terms:
                expanded_queries.append(f"{query} {term}")
        
        # Limit to reasonable number of expansions
        return expanded_queries[:5]
    
    async def multi_hop_retrieval(
        self,
        query: str,
        limit: int = 10,
        max_hops: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Perform multi-hop retrieval to find related documents.
        
        Args:
            query: Initial search query
            limit: Maximum number of results
            max_hops: Maximum number of retrieval hops
            
        Returns:
            List of search results from multiple hops
        """
        try:
            all_results = []
            current_query = query
            
            for hop in range(max_hops):
                # Perform search for current query
                hop_results = await self.vector_db.semantic_search(
                    query_text=current_query,
                    limit=limit // max_hops
                )
                
                all_results.extend(hop_results)
                
                # Generate next query based on found documents
                if hop < max_hops - 1 and hop_results:
                    current_query = self._generate_follow_up_query(query, hop_results)
            
            # Deduplicate and rerank
            unique_results = self._deduplicate_results(all_results)
            unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return unique_results[:limit]
            
        except Exception as e:
            logger.error(f"Multi-hop retrieval failed: {str(e)}")
            return []
    
    def _generate_follow_up_query(self, original_query: str, results: List[Dict]) -> str:
        """Generate follow-up query based on retrieved results."""
        # Extract key terms from results
        key_terms = []
        for result in results[:3]:  # Use top 3 results
            content = result.get("chunk_text", "")
            # Simple keyword extraction (in production, use more sophisticated NLP)
            words = content.split()
            key_terms.extend([w for w in words if len(w) > 5 and w.isalpha()][:3])
        
        # Combine original query with key terms
        if key_terms:
            return f"{original_query} {' '.join(key_terms[:3])}"
        return original_query
    
    async def ensemble_retrieval(
        self,
        query: str,
        limit: int = 10,
        weights: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform ensemble retrieval using multiple techniques.
        
        Args:
            query: Search query
            limit: Maximum number of results
            weights: Weights for different retrievers
            
        Returns:
            List of ensemble search results
        """
        try:
            if not self.ensemble_retriever:
                logger.warning("Ensemble retriever not initialized, falling back to semantic search")
                return await self.vector_db.semantic_search(query_text=query, limit=limit)
            
            # Use ensemble retriever with newer invoke method
            try:
                docs = await self.ensemble_retriever.ainvoke(query)
            except AttributeError:
                # Fallback to old method if invoke not available
                docs = self.ensemble_retriever.get_relevant_documents(query)
            
            # Convert to our result format
            results = []
            for i, doc in enumerate(docs):
                results.append({
                    "chunk_text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 1.0 - (i * 0.1),
                    "retrieval_method": "ensemble"
                })
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Ensemble retrieval failed: {str(e)}")
            return []
    
    async def contextual_compression_retrieval(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform retrieval with contextual compression/reranking.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of compressed/reranked results
        """
        try:
            if not self.compression_retriever:
                logger.warning("Compression retriever not initialized, falling back to semantic search")
                return await self.vector_db.semantic_search(query_text=query, limit=limit)
            
            # Use compression retriever with newer invoke method
            try:
                docs = await self.compression_retriever.ainvoke(query)
            except AttributeError:
                # Fallback to old method if invoke not available
                docs = self.compression_retriever.get_relevant_documents(query)
            
            # Convert to our result format
            results = []
            for i, doc in enumerate(docs):
                results.append({
                    "chunk_text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 1.0 - (i * 0.1),
                    "retrieval_method": "compression"
                })
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Contextual compression retrieval failed: {str(e)}")
            return []
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on content similarity."""
        seen_content = set()
        unique_results = []
        
        for result in results:
            content_hash = hash(result.get("chunk_text", "")[:100])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
        
        return unique_results
    
    def _apply_filters(self, results: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply metadata filters to search results."""
        filtered_results = []
        
        for result in results:
            metadata = result.get("metadata", {})
            matches_filter = True
            
            for key, value in filters.items():
                if key in metadata:
                    if isinstance(value, list):
                        if metadata[key] not in value:
                            matches_filter = False
                            break
                    else:
                        if metadata[key] != value:
                            matches_filter = False
                            break
                else:
                    matches_filter = False
                    break
            
            if matches_filter:
                filtered_results.append(result)
        
        return filtered_results
    
    async def compare_retrieval_techniques(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Compare different retrieval techniques for the same query.
        
        Args:
            query: Search query to test
            limit: Maximum number of results per technique
            
        Returns:
            Dictionary with results from each technique
        """
        try:
            comparison = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "techniques": {}
            }
            
            # Test different techniques
            techniques = [
                ("semantic", lambda: self.vector_db.semantic_search(query_text=query, limit=limit)),
                ("hybrid", lambda: self.hybrid_search(query=query, limit=limit)),
                ("query_expansion", lambda: self.query_expansion_search(query=query, limit=limit)),
                ("multi_hop", lambda: self.multi_hop_retrieval(query=query, limit=limit)),
                ("ensemble", lambda: self.ensemble_retrieval(query=query, limit=limit)),
                ("compression", lambda: self.contextual_compression_retrieval(query=query, limit=limit))
            ]
            
            for technique_name, technique_func in techniques:
                try:
                    results = await technique_func()
                    comparison["techniques"][technique_name] = {
                        "result_count": len(results),
                        "avg_score": sum(r.get("score", 0) for r in results) / len(results) if results else 0,
                        "results": results[:3]  # Show top 3 results
                    }
                except Exception as e:
                    logger.error(f"Technique {technique_name} failed: {str(e)}")
                    comparison["techniques"][technique_name] = {
                        "error": str(e),
                        "result_count": 0,
                        "avg_score": 0
                    }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Retrieval comparison failed: {str(e)}")
            return {"error": str(e)}


# Global advanced retrieval service instance
advanced_retrieval_service = AdvancedRetrievalService() 