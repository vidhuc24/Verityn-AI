"""
Web Search API endpoints for Verityn AI.

This module provides web search capabilities using Tavily API
to enhance compliance document analysis with real-time information.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from app.services.tavily_service import tavily_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/web-search", tags=["web-search"])


class WebSearchRequest(BaseModel):
    """Request model for web search."""
    query: str
    document_id: str
    document_type: Optional[str] = None
    framework: Optional[str] = None


class WebSearchResponse(BaseModel):
    """Response model for web search results."""
    success: bool
    query: str
    results: List[Dict[str, Any]]
    compliance_insights: List[Dict[str, Any]]
    timestamp: str
    error: Optional[str] = None


@router.post("/", response_model=WebSearchResponse)
async def perform_web_search(request: WebSearchRequest):
    """
    Perform web search for compliance guidance based on document content.
    
    Args:
        request: Web search request containing query and document context
        
    Returns:
        Web search results with compliance insights and source links
    """
    try:
        logger.info(f"Performing web search for document {request.document_id}")
        
        # Perform the web search using Tavily service
        search_results = await tavily_service.search_compliance_guidance(
            query=request.query,
            document_type=request.document_type,
            compliance_framework=request.framework
        )
        
        if not search_results.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=f"Web search failed: {search_results.get('error', 'Unknown error')}"
            )
        
        logger.info(f"Web search completed successfully for document {request.document_id}")
        
        return WebSearchResponse(
            success=True,
            query=search_results["query"],
            results=search_results["results"],
            compliance_insights=search_results["compliance_insights"],
            timestamp=search_results["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Web search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Web search failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for web search service."""
    return {
        "status": "healthy",
        "service": "web-search",
        "tavily_available": tavily_service.client is not None
    }
