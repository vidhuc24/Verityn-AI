"""
Document processing routes for Verityn AI backend.

This module provides endpoints for document upload, processing,
classification, and management.
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.services.classification_engine import ClassificationEngine

router = APIRouter()


class DocumentResponse(BaseModel):
    """Document processing response model."""
    document_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    classification: Optional[dict] = None
    metadata: Optional[dict] = None


class DocumentListResponse(BaseModel):
    """Document list response model."""
    documents: List[DocumentResponse]
    total: int


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
):
    """Upload and process a document."""
    # Validate file type
    file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
    if file_extension not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_extension}' not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}",
        )
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size {file.size} bytes exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes",
        )
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    try:
        # Process document
        processor = EnhancedDocumentProcessor()
        result = await processor.process_document(file, document_id, description)
        
        # Verify processing was successful
        if result.get("status") != "processed" or result.get("vector_storage") != "success":
            raise HTTPException(
                status_code=500, 
                detail=f"Document processing failed. Status: {result.get('status')}, Storage: {result.get('vector_storage')}"
            )
        
        # Classify document
        classifier = ClassificationEngine()
        classification = await classifier.classify_document(result["content"])
        
        return DocumentResponse(
            document_id=document_id,
            filename=file.filename,
            file_type=file_extension,
            file_size=file.size or 0,
            status="processed",
            classification=classification,
            metadata=result.get("metadata"),
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
):
    """List all processed documents."""
    # TODO: Implement document listing from database
    return DocumentListResponse(
        documents=[],
        total=0,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document details by ID."""
    # TODO: Implement document retrieval from database
    raise HTTPException(status_code=404, detail="Document not found")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document by ID."""
    # TODO: Implement document deletion
    return {"message": "Document deleted successfully"} 