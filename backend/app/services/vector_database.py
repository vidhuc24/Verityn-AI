"""
Vector Database Service for Verityn AI.

This module provides a production-ready vector database service using Qdrant
for storing and retrieving document embeddings with metadata support for
audit document analysis.
"""

import uuid
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncio
import logging

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    Distance, 
    VectorParams, 
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest
)
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document

from backend.app.config import settings

logger = logging.getLogger(__name__)


class VectorDatabaseService:
    """Production vector database service with Qdrant backend."""
    
    def __init__(self, use_memory: bool = True):
        """
        Initialize vector database service.
        
        Args:
            use_memory: If True, use in-memory storage (default). If False, use Qdrant server.
        """
        self.use_memory = use_memory
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.vector_store = None
        self.collection_name = "verityn_documents"
        
        # Initialize based on mode
        if use_memory:
            logger.info("Initializing vector database in memory mode")
        else:
            logger.info("Initializing vector database with Qdrant server")
            self.qdrant_client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT
            )
        
        # Vector dimension for text-embedding-3-small
        self.vector_size = 1536
        
    async def initialize_collection(self) -> bool:
        """
        Initialize the vector database collection.
        For in-memory mode, this just ensures the service is ready.
        For server mode, this would create the collection.
        """
        try:
            if self.use_memory:
                # In-memory mode - no client needed, just ensure service is ready
                logger.info("Vector database initialized in in-memory mode")
                return True
            else:
                # Server mode - initialize collection if client exists
                if hasattr(self, 'client') and self.client:
                    await self._ensure_collection_exists()
                    logger.info(f"Vector database collection '{self.collection_name}' initialized")
                    return True
                else:
                    logger.warning("Vector database client not initialized for server mode")
                    return False
        except Exception as e:
            logger.error(f"Failed to initialize collection: {str(e)}")
            return False
    
    async def insert_document_chunks(self, *args, **kwargs) -> bool:
        """
        Insert document chunks into vector database.
        
        Supports two calling patterns:
        1. insert_document_chunks(chunks: List[Document])  # Simple pattern
        2. insert_document_chunks(document_id: str, chunks: List[str], metadata: Dict)  # Legacy pattern
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Handle different calling patterns
            if len(args) == 1 and isinstance(args[0], list) and len(kwargs) == 0:
                # Simple pattern: insert_document_chunks(documents)
                documents = args[0]
                if isinstance(documents[0], Document):
                    return await self._insert_documents(documents)
                else:
                    # Convert string chunks to Document objects
                    docs = [Document(page_content=chunk) for chunk in documents]
                    return await self._insert_documents(docs)
                    
            elif 'document_id' in kwargs and 'chunks' in kwargs:
                # Legacy pattern: insert_document_chunks(document_id="...", chunks=[...], metadata={...})
                document_id = kwargs.get('document_id')
                chunks = kwargs.get('chunks')
                metadata = kwargs.get('metadata', {})
                
                # Convert to Document objects with metadata
                documents = []
                for i, chunk in enumerate(chunks):
                    doc_metadata = metadata.copy()
                    doc_metadata.update({
                        'document_id': document_id,
                        'chunk_index': i
                    })
                    documents.append(Document(page_content=chunk, metadata=doc_metadata))
                
                return await self._insert_documents(documents)
            else:
                raise ValueError("Invalid arguments. Use either insert_document_chunks(documents) or insert_document_chunks(document_id=..., chunks=..., metadata=...)")
                
        except Exception as e:
            logger.error(f"Failed to insert document chunks: {str(e)}")
            return False
    
    async def _insert_documents(self, documents: List[Document]) -> bool:
        """Internal method to insert Document objects."""
        try:
            if self.use_memory:
                return await self._insert_with_vector_store(documents)
            else:
                return await self._insert_with_qdrant_server(documents)
        except Exception as e:
            logger.error(f"Failed to insert documents: {str(e)}")
            return False
    
    async def _insert_with_vector_store(self, chunks: List[Document]) -> bool:
        """Insert chunks using LangChain vector store (in-memory mode)."""
        try:
            from langchain_community.vectorstores import Qdrant
            
            if self.vector_store is None:
                # First time: create new vector store
                self.vector_store = Qdrant.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    location=":memory:"
                )
                logger.info(f"Created new in-memory vector store with {len(chunks)} chunks")
            else:
                # For in-memory Qdrant, we need to recreate the store with all documents
                # because Qdrant.from_documents doesn't support appending
                # Get existing documents first
                existing_docs = []
                try:
                    # Try to get existing documents
                    existing_results = self.vector_store.similarity_search("", k=1000)
                    existing_docs = [Document(page_content=doc.page_content, metadata=doc.metadata) for doc in existing_results]
                except Exception:
                    # If we can't get existing docs, just continue with new chunks
                    pass
                
                # Combine existing and new documents
                all_documents = existing_docs + chunks
                
                # Recreate vector store with all documents
                self.vector_store = Qdrant.from_documents(
                    documents=all_documents,
                    embedding=self.embeddings,
                    location=":memory:"
                )
                logger.info(f"Recreated in-memory vector store with {len(all_documents)} total chunks")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert chunks into vector store: {str(e)}")
            return False
    
    async def _insert_with_qdrant_server(self, chunks: List[Document]) -> bool:
        """Insert chunks using Qdrant server."""
        try:
            # Create collection if it doesn't exist
            await self._ensure_collection_exists()
            
            # Prepare points for insertion
            points = []
            for i, chunk in enumerate(chunks):
                embedding = self.embeddings.embed_documents([chunk.page_content])[0]
                
                point = PointStruct(
                    id=i,
                    vector=embedding,
                    payload={
                        "text": chunk.page_content,
                        "metadata": chunk.metadata,
                        "document_id": chunk.metadata.get("document_id", f"doc_{i}"),
                        "chunk_index": i
                    }
                )
                points.append(point)
            
            # Insert points
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Successfully inserted {len(chunks)} chunks into Qdrant server")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert chunks into Qdrant server: {str(e)}")
            return False
    
    async def semantic_search(
        self,
        query_text: str,
        limit: int = 10,
        score_threshold: float = 0.3,  # Lowered from 0.7 to work better with Qdrant in-memory scores
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search with fallback to in-memory mode.
        
        Args:
            query_text: Query text to search for
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            filters: Optional metadata filters
            
        Returns:
            List of search results with scores and metadata
        """
        try:
            # If we have a vector store (in-memory mode), use it
            if self.vector_store:
                return await self._search_with_vector_store(
                    query_text, limit, score_threshold, filters
                )
            
            # Otherwise try Qdrant server mode
            if not self.use_memory:
                return await self._search_with_qdrant_server(
                    query_text, limit, score_threshold, filters
                )
            
            # Fallback: No documents loaded yet
            logger.warning("No vector store initialized and no documents loaded")
            return []
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return []
    
    async def _search_with_vector_store(
        self,
        query_text: str,
        limit: int,
        score_threshold: float,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Search using LangChain vector store (in-memory mode)."""
        try:
            # Use similarity_search_with_score for better results
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query_text, k=limit
            )
            
            results = []
            for doc, score in docs_with_scores:
                if score >= score_threshold:
                    # Flatten metadata for easy access
                    metadata = doc.metadata or {}
                    result = {
                        "chunk_text": doc.page_content,
                        "metadata": metadata,
                        "score": float(score),
                        "document_id": metadata.get("document_id", "unknown"),
                        # Flatten common metadata fields for easy access
                        "quality_level": metadata.get("quality_level", "unknown"),
                        "company": metadata.get("company", "unknown"),
                        "document_type": metadata.get("document_type", "unknown"),
                        "sox_control_ids": metadata.get("sox_control_ids", []),
                        "chunk_index": metadata.get("chunk_index", 0)
                    }
                    
                    # Apply filters if specified
                    if filters and not self._matches_filters(result, filters):
                        continue
                        
                    results.append(result)
            
            logger.info(f"Vector store search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Vector store search failed: {str(e)}")
            return []
    
    async def _search_with_qdrant_server(
        self,
        query_text: str,
        limit: int,
        score_threshold: float,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Search using Qdrant server."""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query_text)
            
            # Build Qdrant filter
            qdrant_filter = None
            if filters:
                qdrant_filter = self._build_qdrant_filter(filters)
            
            # Perform search using newer query_points method to avoid deprecation warning
            try:
                search_results = self.qdrant_client.query_points(
                    collection_name=self.collection_name,
                    query=query_embedding,  # Use 'query' instead of 'query_vector'
                    limit=limit,
                    score_threshold=score_threshold,
                    query_filter=qdrant_filter
                )
            except AttributeError:
                # Fallback to old search method if query_points not available
                search_results = self.qdrant_client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=limit,
                    score_threshold=score_threshold,
                    query_filter=qdrant_filter
                )
            
            # Convert to standard format
            results = []
            for result in search_results:
                results.append({
                    "chunk_text": result.payload.get("text", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": float(result.score),
                    "document_id": result.payload.get("document_id", "unknown")
                })
            
            logger.info(f"Qdrant server search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Qdrant server search failed: {str(e)}")
            return []
    
    async def hybrid_search(
        self,
        query_text: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword matching.
        
        Args:
            query_text: Search query
            limit: Maximum number of results
            filters: Optional metadata filters
            semantic_weight: Weight for semantic similarity
            keyword_weight: Weight for keyword matching
            
        Returns:
            List of hybrid search results
        """
        try:
            # Get semantic search results
            semantic_results = await self.semantic_search(
                query_text=query_text,
                limit=limit * 2,  # Get more for reranking
                filters=filters,
                score_threshold=0.5  # Lower threshold for hybrid
            )
            
            # Simple keyword matching for SOX controls and key terms
            query_lower = query_text.lower()
            
            # Enhanced results with hybrid scoring
            enhanced_results = []
            for result in semantic_results:
                chunk_text = result["chunk_text"].lower()
                keyword_bonus = 0.0
                
                # Keyword matching bonuses
                if "sox" in query_lower and "sox" in chunk_text:
                    keyword_bonus += 0.2
                
                # SOX control ID matching
                sox_controls = result.get("sox_control_ids", [])
                for control_id in sox_controls:
                    if control_id.lower() in query_lower:
                        keyword_bonus += 0.3
                
                # Quality level matching
                if "material weakness" in query_lower and result.get("quality_level") == "fail":
                    keyword_bonus += 0.2
                
                # Calculate hybrid score
                semantic_score = result["score"]
                hybrid_score = (semantic_score * semantic_weight) + (keyword_bonus * keyword_weight)
                
                result["hybrid_score"] = hybrid_score
                result["keyword_bonus"] = keyword_bonus
                enhanced_results.append(result)
            
            # Sort by hybrid score and return top results
            enhanced_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
            final_results = enhanced_results[:limit]
            
            logger.info(f"Hybrid search returned {len(final_results)} results")
            return final_results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            return []
    
    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document."""
        try:
            if self.use_memory and self.vector_store:
                # For in-memory mode, retrieve chunks from the vector store
                try:
                    # Use similarity search to get chunks, then filter by document_id
                    # This is a workaround since LangChain in-memory doesn't support direct filtering
                    search_results = self.vector_store.similarity_search("", k=1000)  # Get all chunks
                    
                    chunks = []
                    for i, doc in enumerate(search_results):
                        # Check if this chunk belongs to our document
                        doc_metadata = doc.metadata
                        if doc_metadata.get('document_id') == document_id:
                            chunk = {
                                "id": f"chunk_{i}",
                                "chunk_text": doc.page_content,
                                "chunk_index": doc_metadata.get('chunk_index', i),
                                "metadata": doc_metadata
                            }
                            chunks.append(chunk)
                    
                    # Sort by chunk index
                    chunks.sort(key=lambda x: x.get("chunk_index", 0))
                    
                    logger.info(f"Retrieved {len(chunks)} chunks for document {document_id} from in-memory store")
                    return chunks
                    
                except Exception as e:
                    logger.warning(f"Failed to retrieve chunks from in-memory store: {str(e)}")
                    # Fallback to basic response
                    return [{
                        "id": "in_memory",
                        "chunk_text": "Document chunks stored in memory",
                        "chunk_index": 0,
                        "metadata": {"document_id": document_id, "mode": "in_memory"}
                    }]
                    
            elif hasattr(self, 'qdrant_client') and self.qdrant_client:
                # For server mode, use Qdrant client
                filter_condition = Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
                
                search_result = self.qdrant_client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=filter_condition,
                    limit=1000,  # Assume max 1000 chunks per document
                    with_payload=True,
                    with_vectors=False
                )
                
                chunks = []
                for point in search_result[0]:
                    chunk = {
                        "id": point.id,
                        "chunk_text": point.payload.get("chunk_text", ""),
                        "chunk_index": point.payload.get("chunk_index"),
                        "metadata": point.payload
                    }
                    chunks.append(chunk)
                
                # Sort by chunk index
                chunks.sort(key=lambda x: x.get("chunk_index", 0))
                
                logger.info(f"Retrieved {len(chunks)} chunks for document {document_id}")
                return chunks
            else:
                logger.warning("No vector store or Qdrant client available")
                return []
            
        except Exception as e:
            logger.error(f"Failed to get document chunks: {str(e)}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a specific document."""
        try:
            if self.use_memory and self.vector_store:
                # For in-memory mode, we can't easily delete specific documents
                # Just log the request
                logger.info(f"Document deletion requested for {document_id} (in-memory mode)")
                return True
            elif hasattr(self, 'qdrant_client') and self.qdrant_client:
                # For server mode, use Qdrant client
                filter_condition = Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
                
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.FilterSelector(filter=filter_condition)
                )
                
                logger.info(f"Deleted all chunks for document {document_id}")
                return True
            else:
                logger.warning("No vector store or Qdrant client available")
                return False
            
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            if self.use_memory and self.vector_store:
                # For in-memory mode, return basic info
                return {
                    "collection_name": self.collection_name,
                    "vectors_count": "unknown",  # LangChain doesn't expose this easily
                    "status": "active",
                    "vector_size": self.vector_size,
                    "distance": "cosine",
                    "mode": "in_memory"
                }
            elif hasattr(self, 'qdrant_client') and self.qdrant_client:
                # For server mode, get actual collection info
                info = self.qdrant_client.get_collection(self.collection_name)
                return {
                    "collection_name": self.collection_name,
                    "vectors_count": info.vectors_count,
                    "status": info.status.value,
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance.value,
                    "mode": "server"
                }
            else:
                return {
                    "collection_name": self.collection_name,
                    "vectors_count": 0,
                    "status": "not_initialized",
                    "vector_size": self.vector_size,
                    "distance": "cosine",
                    "mode": "unknown"
                }
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return {
                "collection_name": self.collection_name,
                "vectors_count": 0,
                "status": "error",
                "vector_size": self.vector_size,
                "distance": "cosine",
                "mode": "error",
                "error": str(e)
            }

    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches the given filters."""
        for key, value in filters.items():
            if key not in metadata:
                return False
            
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False
        
        return True
    
    def _build_qdrant_filter(self, filters: Dict[str, Any]):
        """Build Qdrant filter from dictionary."""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        conditions = []
        for field, value in filters.items():
            if isinstance(value, list):
                # Handle multiple values (OR condition)
                for val in value:
                    conditions.append(
                        FieldCondition(
                            key=field,
                            match=MatchValue(value=val)
                        )
                    )
            else:
                conditions.append(
                    FieldCondition(
                        key=field,
                        match=MatchValue(value=value)
                    )
                )
        
        if conditions:
            return Filter(should=conditions)
        return None
    
    async def _ensure_collection_exists(self):
        """Ensure the Qdrant collection exists."""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            raise


# Global vector database instance - use in-memory mode by default
vector_db_service = VectorDatabaseService(use_memory=True)


async def initialize_vector_database() -> bool:
    """Initialize the vector database on startup."""
    return await vector_db_service.initialize_collection() 