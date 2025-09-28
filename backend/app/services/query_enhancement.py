"""
Query Enhancement Service for Verityn AI.

This module handles "no results" scenarios intelligently by:
1. Analyzing why queries failed
2. Generating helpful query suggestions  
3. Providing fallback search strategies
4. Offering domain-specific guidance
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from backend.app.config import settings
from backend.app.services.vector_database import vector_db_service

logger = logging.getLogger(__name__)


class QueryEnhancementService:
    """Service for handling no-results scenarios and query optimization."""
    
    def __init__(self):
        """Initialize the query enhancement service."""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.1,  # Low temperature for consistent suggestions
        )
        
        # Audit domain vocabulary
        self.audit_synonyms = {
            'controls': ['procedures', 'processes', 'safeguards', 'mechanisms', 'measures'],
            'findings': ['issues', 'observations', 'deficiencies', 'weaknesses', 'results'],
            'risk': ['threat', 'exposure', 'vulnerability', 'concern', 'hazard'],
            'compliance': ['adherence', 'conformity', 'regulatory', 'standards', 'requirements'],
            'assessment': ['evaluation', 'review', 'analysis', 'examination', 'audit'],
            'deficiency': ['weakness', 'gap', 'shortcoming', 'inadequacy', 'failure'],
            'sox': ['sarbanes-oxley', 'section 404', 'financial controls', 'public company'],
            'access': ['permissions', 'privileges', 'rights', 'authorization', 'security']
        }
        
        # Common audit query patterns
        self.query_patterns = {
            'what_are': ['What are the', 'What were the', 'What'],
            'how_many': ['How many', 'Count of', 'Number of'],
            'who_has': ['Who has', 'Which users', 'Who can'],
            'when_was': ['When was', 'When did', 'What date'],
            'why_did': ['Why did', 'What caused', 'Reason for'],
            'where_is': ['Where is', 'In which section', 'Location of']
        }
    
    async def handle_no_results(
        self,
        original_query: str,
        search_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle no results scenario with intelligent suggestions and fallbacks.
        
        Args:
            original_query: The original user query that returned no results
            search_metadata: Metadata from the failed search attempt
            
        Returns:
            Dictionary with suggestions, fallbacks, and helpful messaging
        """
        try:
            # Step 1: Analyze the query to understand why it failed
            query_analysis = await self._analyze_query_failure(original_query)
            
            # Step 2: Generate alternative query suggestions
            suggestions = await self._generate_query_suggestions(original_query, query_analysis)
            
            # Step 3: Try fallback searches with broader terms
            fallback_results = await self._attempt_fallback_searches(original_query)
            
            # Step 4: Provide domain-specific guidance
            domain_guidance = self._get_domain_guidance(original_query)
            
            # Step 5: Create user-friendly response
            response_message = self._create_helpful_message(
                original_query, query_analysis, suggestions, fallback_results
            )
            
            return {
                "has_results": len(fallback_results) > 0,
                "message": response_message,
                "suggestions": {
                    "alternative_queries": suggestions[:4],  # Top 4 suggestions
                    "related_terms": self._extract_related_terms(original_query),
                    "query_tips": self._get_query_tips(query_analysis)
                },
                "fallback_results": fallback_results[:3] if fallback_results else [],
                "domain_guidance": domain_guidance,
                "query_analysis": query_analysis
            }
            
        except Exception as e:
            logger.error(f"Query enhancement failed: {str(e)}")
            return self._create_fallback_response(original_query)
    
    async def _analyze_query_failure(self, query: str) -> Dict[str, Any]:
        """Analyze why a query might have failed to return results."""
        analysis = {
            "query_length": len(query.split()),
            "has_audit_terms": False,
            "is_too_specific": False,
            "is_too_vague": False,
            "potential_issues": []
        }
        
        query_lower = query.lower()
        
        # Check for audit domain terms
        audit_terms_found = []
        for term, synonyms in self.audit_synonyms.items():
            if term in query_lower or any(syn in query_lower for syn in synonyms):
                audit_terms_found.append(term)
        
        analysis["has_audit_terms"] = len(audit_terms_found) > 0
        analysis["audit_terms_found"] = audit_terms_found
        
        # Analyze query characteristics
        if len(query.split()) < 3:
            analysis["is_too_vague"] = True
            analysis["potential_issues"].append("Query may be too brief")
        
        if len(query.split()) > 15:
            analysis["is_too_specific"] = True
            analysis["potential_issues"].append("Query may be too detailed")
        
        # Check for common patterns
        if not any(pattern in query_lower for patterns in self.query_patterns.values() for pattern in patterns):
            analysis["potential_issues"].append("Query may need restructuring")
        
        # Check for typos or unusual terms
        if re.search(r'\b\w{15,}\b', query):  # Very long words might be typos
            analysis["potential_issues"].append("May contain typos or technical jargon")
        
        return analysis
    
    async def _generate_query_suggestions(
        self, 
        original_query: str, 
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate alternative query suggestions using LLM."""
        try:
            suggestion_prompt = ChatPromptTemplate.from_template("""
            You are an expert in audit and compliance document analysis. A user searched for information but got no results.
            
            Original query: "{query}"
            Query analysis: {analysis}
            
            Generate 5 alternative ways to ask the same question that might find relevant audit documents. 
            Focus on:
            1. Using common audit terminology (controls, findings, compliance, risk, assessment)
            2. Simplifying complex queries
            3. Expanding brief queries with context
            4. Using different question patterns (What, How, Where, When)
            
            Return only the alternative queries, one per line, without numbers or explanations.
            """)
            
            response = await self.llm.ainvoke(
                suggestion_prompt.format(query=original_query, analysis=str(analysis))
            )
            
            suggestions = [line.strip() for line in response.content.split('\n') if line.strip()]
            return suggestions[:5]
            
        except Exception as e:
            logger.error(f"LLM suggestion generation failed: {str(e)}")
            return self._generate_rule_based_suggestions(original_query)
    
    def _generate_rule_based_suggestions(self, query: str) -> List[str]:
        """Generate suggestions using rule-based approach as fallback."""
        suggestions = []
        query_lower = query.lower()
        
        # Expand with synonyms
        for term, synonyms in self.audit_synonyms.items():
            if term in query_lower:
                for synonym in synonyms[:2]:  # Top 2 synonyms
                    suggestions.append(query_lower.replace(term, synonym).title())
        
        # Simplify complex queries
        if len(query.split()) > 10:
            # Extract key terms and create simpler query
            key_terms = [word for word in query.split() if word.lower() in self.audit_synonyms]
            if key_terms:
                suggestions.append(f"What are the {' '.join(key_terms[:3]).lower()}?")
        
        # Expand brief queries
        if len(query.split()) < 3:
            suggestions.extend([
                f"What are the {query.lower()} findings?",
                f"How do {query.lower()} work?",
                f"What {query.lower()} were identified?"
            ])
        
        return suggestions[:5]
    
    async def _attempt_fallback_searches(self, query: str) -> List[Dict[str, Any]]:
        """Attempt broader searches as fallbacks."""
        fallback_results = []
        
        # Strategy 1: Extract key terms and search individually
        key_terms = self._extract_key_terms(query)
        for term in key_terms[:3]:  # Try top 3 key terms
            try:
                results = await vector_db_service.hybrid_search(
                    query_text=term,
                    limit=2,
                    semantic_weight=0.5,
                    keyword_weight=0.5
                )
                if results:
                    fallback_results.extend(results[:1])  # Add top result
            except Exception as e:
                logger.warning(f"Fallback search for '{term}' failed: {str(e)}")
        
        # Strategy 2: Search with domain-general terms
        if not fallback_results:
            general_terms = ["findings", "controls", "assessment", "compliance"]
            for term in general_terms:
                try:
                    results = await vector_db_service.hybrid_search(
                        query_text=term,
                        limit=1,
                        semantic_weight=0.3,
                        keyword_weight=0.7
                    )
                    if results:
                        fallback_results.extend(results)
                        break  # Stop after first successful general search
                except Exception as e:
                    logger.warning(f"General fallback search for '{term}' failed: {str(e)}")
        
        return fallback_results
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query for fallback searches."""
        # Remove common stop words
        stop_words = {'what', 'are', 'the', 'how', 'where', 'when', 'why', 'who', 'which', 'is', 'was', 'were', 'have', 'has', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can'}
        
        words = [word.lower().strip('.,!?') for word in query.split()]
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Prioritize audit terms
        audit_terms = []
        other_terms = []
        
        for term in key_terms:
            if any(term in synonyms or term == audit_term for audit_term, synonyms in self.audit_synonyms.items()):
                audit_terms.append(term)
            else:
                other_terms.append(term)
        
        return audit_terms + other_terms
    
    def _extract_related_terms(self, query: str) -> List[str]:
        """Extract related terms that might help the user."""
        related_terms = []
        query_lower = query.lower()
        
        for term, synonyms in self.audit_synonyms.items():
            if term in query_lower:
                related_terms.extend(synonyms[:3])  # Add top 3 synonyms
        
        return list(set(related_terms))[:6]  # Return unique terms, max 6
    
    def _get_domain_guidance(self, query: str) -> Dict[str, Any]:
        """Provide domain-specific guidance based on query content."""
        guidance = {
            "category": "general",
            "tips": [],
            "common_searches": []
        }
        
        query_lower = query.lower()
        
        # Categorize query and provide specific guidance
        if any(term in query_lower for term in ['access', 'user', 'permission', 'privilege']):
            guidance["category"] = "access_controls"
            guidance["tips"] = [
                "Try searching for 'user access review' or 'access control matrix'",
                "Look for specific user roles or system names",
                "Search for 'privileged access' or 'administrative rights'"
            ]
            guidance["common_searches"] = [
                "What users have administrative access?",
                "Access control deficiencies found",
                "User access review results"
            ]
        
        elif any(term in query_lower for term in ['sox', 'sarbanes', 'financial', 'controls']):
            guidance["category"] = "sox_compliance"
            guidance["tips"] = [
                "Try 'SOX 404' or 'internal controls over financial reporting'",
                "Search for 'material weakness' or 'significant deficiency'",
                "Look for specific financial processes like 'revenue recognition'"
            ]
            guidance["common_searches"] = [
                "SOX 404 assessment results",
                "Material weaknesses identified",
                "Financial controls testing"
            ]
        
        elif any(term in query_lower for term in ['risk', 'threat', 'vulnerability']):
            guidance["category"] = "risk_assessment"
            guidance["tips"] = [
                "Try 'risk assessment' or 'risk matrix'",
                "Search for specific risk categories like 'operational risk'",
                "Look for 'risk mitigation' or 'control activities'"
            ]
            guidance["common_searches"] = [
                "High risk areas identified",
                "Risk mitigation strategies",
                "Control effectiveness assessment"
            ]
        
        return guidance
    
    def _get_query_tips(self, analysis: Dict[str, Any]) -> List[str]:
        """Get query improvement tips based on analysis."""
        tips = []
        
        if analysis.get("is_too_vague"):
            tips.append("Try adding more specific terms like document type or process name")
        
        if analysis.get("is_too_specific"):
            tips.append("Try simplifying your question to focus on key concepts")
        
        if not analysis.get("has_audit_terms"):
            tips.append("Include audit terms like 'controls', 'findings', 'compliance', or 'risk'")
        
        if "Query may need restructuring" in analysis.get("potential_issues", []):
            tips.append("Try starting with 'What are...', 'How many...', or 'Where is...'")
        
        if not tips:
            tips = [
                "Use specific audit terminology",
                "Ask clear, focused questions",
                "Try different phrasings of the same concept"
            ]
        
        return tips[:3]  # Return top 3 tips
    
    def _create_helpful_message(
        self,
        query: str,
        analysis: Dict[str, Any],
        suggestions: List[str],
        fallback_results: List[Dict[str, Any]]
    ) -> str:
        """Create a helpful, user-friendly message for no results scenario."""
        if fallback_results:
            return f"""I couldn't find exact matches for "{query}", but I found some related information that might help. Here are some alternative ways to search for what you're looking for."""
        
        if suggestions:
            return f"""I couldn't find results for "{query}". This might be because the documents don't contain that specific information, or the query could be phrased differently. Here are some alternative searches that might help you find what you're looking for."""
        
        return f"""I couldn't find results for "{query}". This could be because:
• The documents may not contain that specific information
• The query might need different phrasing
• Try using more common audit terminology

Let me suggest some alternative approaches to help you find what you need."""
    
    def _create_fallback_response(self, query: str) -> Dict[str, Any]:
        """Create a basic fallback response when enhancement fails."""
        return {
            "has_results": False,
            "message": f"I couldn't find results for \"{query}\". Try rephrasing your question or using different terms.",
            "suggestions": {
                "alternative_queries": [
                    "What are the key findings?",
                    "What controls were tested?",
                    "What compliance issues were identified?",
                    "What risks were assessed?"
                ],
                "related_terms": ["findings", "controls", "compliance", "risk", "assessment"],
                "query_tips": [
                    "Use specific audit terminology",
                    "Try asking 'What', 'How', or 'Where' questions",
                    "Be specific about what you're looking for"
                ]
            },
            "fallback_results": [],
            "domain_guidance": {
                "category": "general",
                "tips": ["Try using common audit terms", "Be specific about the process or area"],
                "common_searches": ["Key audit findings", "Control deficiencies", "Risk assessment results"]
            },
            "query_analysis": {"error": "Enhancement service failed"}
        }


# Global service instance
query_enhancement_service = QueryEnhancementService()
