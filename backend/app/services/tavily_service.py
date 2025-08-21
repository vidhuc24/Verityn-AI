"""
Tavily API Service for Verityn AI.

This module provides web search capabilities for real-time regulatory guidance
and compliance information to enhance audit document analysis.
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logging.warning("Tavily not available - install with: pip install tavily-python")

from backend.app.config import settings

logger = logging.getLogger(__name__)


class TavilyService:
    """Service for Tavily web search and compliance queries."""
    
    def __init__(self):
        """Initialize the Tavily service."""
        self.client = None
        self.api_key = settings.TAVILY_API_KEY
        
        if TAVILY_AVAILABLE and self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("Tavily service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {str(e)}")
                self.client = None
        else:
            logger.warning("Tavily not available - API key missing or package not installed")
    
    async def search_compliance_guidance(
        self, 
        query: str, 
        document_type: Optional[str] = None,
        compliance_framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for compliance guidance related to the query.
        
        Args:
            query: The search query
            document_type: Type of document being analyzed
            compliance_framework: Specific compliance framework (SOX, SOC2, etc.)
            
        Returns:
            Dictionary containing search results and compliance insights
        """
        if not self.client:
            return {
                "success": False,
                "error": "Tavily service not available",
                "results": [],
                "compliance_insights": []
            }
        
        try:
            # Enhance query with compliance context
            enhanced_query = self._enhance_compliance_query(
                query, document_type, compliance_framework
            )
            
            # Perform search
            search_response = await self._perform_search(enhanced_query)
            
            # Extract compliance insights
            compliance_insights = self._extract_compliance_insights(search_response)
            
            return {
                "success": True,
                "query": enhanced_query,
                "results": search_response.get("results", []),
                "compliance_insights": compliance_insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Tavily search failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "compliance_insights": []
            }
    
    def _enhance_compliance_query(
        self, 
        query: str, 
        document_type: Optional[str] = None,
        compliance_framework: Optional[str] = None
    ) -> str:
        """Enhance the query with compliance context."""
        enhanced_parts = [query]
        
        if compliance_framework:
            enhanced_parts.append(f"{compliance_framework} compliance requirements")
        
        if document_type:
            enhanced_parts.append(f"{document_type} best practices")
        
        enhanced_parts.append("audit compliance guidance 2024")
        
        return " ".join(enhanced_parts)
    
    async def _perform_search(self, query: str) -> Dict[str, Any]:
        """Perform the actual web search using Tavily."""
        try:
            # Use Tavily's search API
            response = self.client.search(
                query=query,
                search_depth="advanced",
                include_domains=["sox-online.com", "aicpa.org", "isaca.org", "pcaobus.org"],
                max_results=5
            )
            return response
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
            raise
    
    def _extract_compliance_insights(self, search_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relevant compliance insights from search results."""
        insights = []
        
        for result in search_response.get("results", []):
            insight = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:300] + "..." if result.get("content") else "",
                "relevance_score": result.get("score", 0),
                "compliance_focus": self._identify_compliance_focus(result.get("content", ""))
            }
            insights.append(insight)
        
        # Sort by relevance
        insights.sort(key=lambda x: x["relevance_score"], reverse=True)
        return insights[:3]  # Return top 3 insights
    
    def _identify_compliance_focus(self, content: str) -> str:
        """Identify the main compliance focus of the content."""
        content_lower = content.lower()
        
        if any(term in content_lower for term in ["sox", "sarbanes-oxley"]):
            return "SOX Compliance"
        elif any(term in content_lower for term in ["soc2", "soc 2", "trust services criteria"]):
            return "SOC2 Compliance"
        elif any(term in content_lower for term in ["iso27001", "information security"]):
            return "ISO27001 Compliance"
        elif any(term in content_lower for term in ["internal controls", "financial reporting"]):
            return "Internal Controls"
        elif any(term in content_lower for term in ["risk assessment", "risk management"]):
            return "Risk Management"
        else:
            return "General Compliance"
    
    async def get_compliance_update(
        self, 
        framework: str, 
        document_type: str
    ) -> Dict[str, Any]:
        """
        Get latest compliance updates for a specific framework and document type.
        
        Args:
            framework: Compliance framework (SOX, SOC2, ISO27001)
            document_type: Type of document (access_review, risk_assessment, etc.)
            
        Returns:
            Dictionary containing compliance updates and guidance
        """
        query = f"latest {framework} {document_type} compliance requirements 2024"
        return await self.search_compliance_guidance(query, document_type, framework)


# Global instance
tavily_service = TavilyService()
