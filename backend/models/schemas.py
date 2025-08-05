"""
Pydantic schemas for Verityn AI API.

This module contains all the data models used for API requests
and responses.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document model."""
    filename: str
    file_type: str
    file_size: int
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Document creation model."""
    pass


class DocumentResponse(DocumentBase):
    """Document response model."""
    document_id: str
    status: str
    classification: Optional[Dict] = None
    metadata: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None
    sources: Optional[List[Dict]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User's message")
    document_id: Optional[str] = None
    conversation_id: Optional[str] = None
    include_web_search: bool = True


class ChatResponse(BaseModel):
    """Chat response model."""
    message: ChatMessage
    conversation_id: str
    suggested_questions: Optional[List[str]] = None
    compliance_insights: Optional[Dict] = None


class QuestionSuggestionRequest(BaseModel):
    """Question suggestion request model."""
    document_id: str
    document_type: Optional[str] = None
    compliance_framework: Optional[str] = None


class QuestionSuggestionResponse(BaseModel):
    """Question suggestion response model."""
    questions: List[str]
    categories: List[str]
    compliance_frameworks: List[str]


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    environment: str
    services: Dict[str, str]


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    status_code: int
    path: str 