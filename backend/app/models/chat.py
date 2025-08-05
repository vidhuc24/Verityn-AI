"""
Chat models for Verityn AI.

This module defines Pydantic models for chat-related API requests and responses,
including message handling, conversation management, and compliance insights.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Response confidence score")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Source documents used")
    timestamp: Optional[str] = Field(None, description="Message timestamp")


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    document_id: Optional[str] = Field(None, description="Specific document to search")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    include_web_search: bool = Field(default=True, description="Include web search results")
    search_filters: Optional[Dict[str, Any]] = Field(None, description="Additional search filters")


class ComplianceInsights(BaseModel):
    """Compliance insights model."""
    frameworks: List[str] = Field(default_factory=list, description="Compliance frameworks identified")
    sox_controls: List[str] = Field(default_factory=list, description="SOX control IDs referenced")
    companies: List[str] = Field(default_factory=list, description="Companies mentioned")
    risk_level: str = Field(default="Unknown", description="Overall risk level assessment")
    quality_levels: List[str] = Field(default_factory=list, description="Document quality levels")
    key_findings: List[str] = Field(default_factory=list, description="Key audit findings")


class ContextMetadata(BaseModel):
    """Context retrieval metadata."""
    documents_searched: int = Field(default=0, description="Number of unique documents searched")
    chunks_retrieved: int = Field(default=0, description="Number of text chunks retrieved")
    avg_relevance_score: float = Field(default=0.0, description="Average relevance score of retrieved chunks")


class ChatResponse(BaseModel):
    """Chat response model."""
    message: ChatMessage = Field(..., description="Assistant response message")
    conversation_id: str = Field(..., description="Conversation identifier")
    suggested_questions: Optional[List[str]] = Field(None, description="Follow-up question suggestions")
    compliance_insights: Optional[ComplianceInsights] = Field(None, description="Compliance analysis insights")
    context_metadata: Optional[ContextMetadata] = Field(None, description="Context retrieval metadata")


class ConversationTurn(BaseModel):
    """Single conversation turn model."""
    timestamp: str = Field(..., description="Turn timestamp")
    user_message: str = Field(..., description="User message")
    assistant_response: str = Field(..., description="Assistant response")
    context_chunks: int = Field(default=0, description="Number of context chunks used")
    documents_referenced: List[str] = Field(default_factory=list, description="Document IDs referenced")


class ConversationResponse(BaseModel):
    """Conversation history response model."""
    conversation_id: str = Field(..., description="Conversation identifier")
    turns: List[ConversationTurn] = Field(..., description="Conversation turns")
    total_turns: int = Field(..., description="Total number of turns")
    created_at: Optional[str] = Field(None, description="Conversation creation timestamp")


class QuestionSuggestionRequest(BaseModel):
    """Question suggestion request model."""
    document_id: Optional[str] = Field(None, description="Document ID for context")
    document_type: Optional[str] = Field(None, description="Document type filter")
    compliance_framework: Optional[str] = Field(None, description="Compliance framework filter")
    category: Optional[str] = Field(None, description="Question category")


class QuestionSuggestionResponse(BaseModel):
    """Question suggestion response model."""
    suggestions: List[str] = Field(..., description="Suggested questions")
    category: Optional[str] = Field(None, description="Question category")
    document_id: Optional[str] = Field(None, description="Associated document ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class FeedbackRequest(BaseModel):
    """Feedback submission model."""
    conversation_id: str = Field(..., description="Conversation identifier")
    message_index: int = Field(..., ge=0, description="Message index in conversation")
    feedback_type: str = Field(..., description="Feedback type: helpful, not_helpful, inaccurate")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Additional feedback text")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1-5")


class FeedbackResponse(BaseModel):
    """Feedback submission response."""
    message: str = Field(..., description="Confirmation message")
    conversation_id: str = Field(..., description="Conversation identifier")
    message_index: int = Field(..., description="Message index")
    feedback_type: str = Field(..., description="Submitted feedback type") 