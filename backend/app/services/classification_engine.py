"""
Document classification engine for Verityn AI.

This module handles automatic classification of audit documents
and extraction of relevant metadata.
"""

from typing import Dict, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate

from backend.app.config import settings

logger = logging.getLogger(__name__)


class ClassificationEngine:
    """Service for classifying audit documents."""
    
    def __init__(self):
        """Initialize the classification engine."""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.1,
        )
        
        self.classification_prompt = ChatPromptTemplate.from_template("""
        You are an expert in audit and compliance document classification.
        
        Analyze the following document content and classify it according to:
        1. Document Type: Choose from: access_review, financial_reconciliation, risk_assessment, control_testing, audit_report, compliance_assessment, policy_document, incident_report, vendor_assessment, or other
        2. Compliance Framework: SOX, SOC2, ISO27001, PCI-DSS, HIPAA, or other
        3. Risk Level: high, medium, low based on findings and content
        4. Key Topics: List main topics covered in the document
        
        Document Content (first 2000 characters):
        {content}
        
        Return your analysis in this exact JSON format:
        {{
            "document_type": "string",
            "compliance_frameworks": ["string"],
            "risk_level": "string",
            "key_topics": ["string"],
            "confidence": 0.95
        }}
        
        Only return valid JSON, no additional text.
        """)
    
    async def classify_document(self, content: str) -> Dict:
        """
        Classify a document based on its content.
        
        Args:
            content: The document text content
            
        Returns:
            Dictionary containing classification results
        """
        try:
            # Truncate content for analysis
            analysis_content = content[:2000] if len(content) > 2000 else content
            
            # Use LLM for classification
            messages = [
                SystemMessage(content="You are an expert in audit and compliance document classification."),
                HumanMessage(content=self.classification_prompt.format(content=analysis_content))
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            try:
                classification_result = json.loads(response.content)
                return {
                    "document_type": classification_result.get("document_type", "unknown"),
                    "confidence": classification_result.get("confidence", 0.5),
                    "compliance_frameworks": classification_result.get("compliance_frameworks", ["SOX"]),
                    "risk_level": classification_result.get("risk_level", "medium"),
                    "key_topics": classification_result.get("key_topics", []),
                    "metadata": {
                        "analysis_timestamp": "2024-01-15",
                        "content_length": len(content)
                    }
                }
            except json.JSONDecodeError:
                logger.warning("Failed to parse classification JSON, using fallback")
                return self._fallback_classification(content)
                
        except Exception as e:
            logger.error(f"Document classification failed: {str(e)}")
            return self._fallback_classification(content)
    
    def _fallback_classification(self, content: str) -> Dict:
        """Fallback classification based on content keywords."""
        content_lower = content.lower()
        
        # Simple keyword-based classification
        if any(term in content_lower for term in ["access", "user access", "permissions", "privileges"]):
            doc_type = "access_review"
        elif any(term in content_lower for term in ["financial", "reconciliation", "balance", "accounting"]):
            doc_type = "financial_reconciliation"
        elif any(term in content_lower for term in ["risk", "assessment", "threat", "vulnerability"]):
            doc_type = "risk_assessment"
        elif any(term in content_lower for term in ["control", "testing", "effectiveness"]):
            doc_type = "control_testing"
        elif any(term in content_lower for term in ["audit", "finding", "deficiency"]):
            doc_type = "audit_report"
        else:
            doc_type = "unknown"
        
        # Determine risk level
        if any(term in content_lower for term in ["material weakness", "critical", "high risk", "severe"]):
            risk_level = "high"
        elif any(term in content_lower for term in ["deficiency", "medium", "moderate"]):
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "document_type": doc_type,
            "confidence": 0.6,
            "compliance_frameworks": ["SOX"],
            "risk_level": risk_level,
            "key_topics": [],
            "metadata": {
                "analysis_timestamp": "2024-01-15",
                "content_length": len(content),
                "method": "fallback_keyword"
            }
        } 