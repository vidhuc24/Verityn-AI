"""
Enhanced Document processing service for Verityn AI.

This module handles document upload, text extraction, optimized chunking,
and vector database integration for audit document analysis.
"""

import os
import tempfile
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from backend.app.config import settings
from backend.app.services.vector_database import vector_db_service


class EnhancedDocumentProcessor:
    """Enhanced service for processing uploaded documents with vector database integration."""
    
    def __init__(self):
        """Initialize the enhanced document processor."""
        # Optimized chunking strategy: balanced size with high coverage
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,  # Increased from 300 for better coverage
            chunk_overlap=150,  # Maximum overlap to ensure no content loss
            length_function=len,
            separators=[
                "\n\n",          # Paragraphs (highest priority)
                "\n• ",          # Bullet points
                "\n- ",          # Dash lists  
                "\n",            # Line breaks
                ". ",            # Sentences
                "! ", "? ",      # Other sentence endings
                ": ",            # Colons (common in audit docs)
                "; ",            # Semicolons
                " ",             # Words
                ""               # Characters (fallback)
            ],
        )
        
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )
    
    async def process_document(
        self,
        file: UploadFile,
        document_id: str,
        description: Optional[str] = None,
        document_metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Process an uploaded document with enhanced vector database integration.
        
        Args:
            file: The uploaded file
            document_id: Unique identifier for the document
            description: Optional description of the document
            document_metadata: Optional metadata (quality_level, company, document_type, etc.)
            
        Returns:
            Dictionary containing processed document data
        """
        try:
            # Extract text from document
            content = await self._extract_text(file)
            
            # Split content into optimized chunks
            chunks = self._split_text_optimized(content)
            
            # Extract enhanced metadata
            metadata = self._extract_enhanced_metadata(file, description, document_metadata)
            
            # Classify document to get accurate document type
            from backend.app.services.classification_engine import ClassificationEngine
            classifier = ClassificationEngine()
            classification = await classifier.classify_document(content)
            
            # Update metadata with classification results
            metadata.update({
                "document_type": classification.get("document_type", "unknown"),
                "compliance_frameworks": classification.get("compliance_frameworks", ["SOX"]),
                "risk_level": classification.get("risk_level", "medium"),
                "key_topics": classification.get("key_topics", []),
                "classification_confidence": classification.get("confidence", 0.5),
                "classification_metadata": classification.get("metadata", {})
            })
            
            # Store in vector database
            success = await self._store_in_vector_database(document_id, chunks, metadata)
            
            if not success:
                raise Exception("Failed to store document in vector database")
            
            # Verify storage was successful by checking if chunks can be retrieved
            stored_chunks = await vector_db_service.get_document_chunks(document_id)
            if not stored_chunks:
                raise Exception("Document was stored but cannot be retrieved - storage verification failed")
            
            return {
                "document_id": document_id,
                "content": content,
                "chunks": chunks,  # Include chunks in response
                "chunk_count": len(chunks),
                "metadata": metadata,
                "classification": classification,
                "status": "processed",
                "vector_storage": "success",
            }
        
        except Exception as e:
            raise Exception(f"Enhanced document processing failed: {str(e)}")
    
    async def _extract_text(self, file: UploadFile) -> str:
        """Extract text content from uploaded file."""
        file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
        
        if file_extension == "pdf":
            return await self._extract_pdf_text(file)
        elif file_extension == "docx":
            return await self._extract_docx_text(file)
        elif file_extension == "txt":
            return await self._extract_txt_text(file)
        elif file_extension in ["csv", "xlsx"]:
            return await self._extract_spreadsheet_text(file)
        elif file_extension == "json":
            return await self._extract_json_text(file)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    async def _extract_pdf_text(self, file: UploadFile) -> str:
        """Extract text from PDF file."""
        try:
            from pypdf import PdfReader
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Extract text
            reader = PdfReader(temp_file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Clean up
            os.unlink(temp_file_path)
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"PDF text extraction failed: {str(e)}")
    
    async def _extract_docx_text(self, file: UploadFile) -> str:
        """Extract text from DOCX file."""
        try:
            from docx import Document
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Extract text
            doc = Document(temp_file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Clean up
            os.unlink(temp_file_path)
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"DOCX text extraction failed: {str(e)}")
    
    async def _extract_txt_text(self, file: UploadFile) -> str:
        """Extract text from TXT file."""
        try:
            content = await file.read()
            return content.decode("utf-8").strip()
        
        except Exception as e:
            raise Exception(f"TXT text extraction failed: {str(e)}")
    
    async def _extract_spreadsheet_text(self, file: UploadFile) -> str:
        """Extract text from spreadsheet files (CSV, XLSX)."""
        try:
            import pandas as pd
            
            # Save file temporarily
            file_extension = file.filename.split(".")[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Read spreadsheet
            if file_extension == "csv":
                df = pd.read_csv(temp_file_path)
            else:
                df = pd.read_excel(temp_file_path)
            
            # Convert to text with better formatting for audit documents
            text = f"Document contains {len(df)} rows and {len(df.columns)} columns.\n\n"
            text += f"Column headers: {', '.join(df.columns)}\n\n"
            text += df.to_string(index=False)
            
            # Clean up
            os.unlink(temp_file_path)
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Spreadsheet text extraction failed: {str(e)}")
    
    async def _extract_json_text(self, file: UploadFile) -> str:
        """Extract text from JSON audit documents."""
        try:
            import json
            
            content = await file.read()
            json_data = json.loads(content.decode("utf-8"))
            
            # Extract text from structured audit JSON
            text_parts = []
            
            # Add metadata section
            if "metadata" in json_data:
                text_parts.append("DOCUMENT METADATA:")
                metadata = json_data["metadata"]
                for key, value in metadata.items():
                    text_parts.append(f"{key.replace('_', ' ').title()}: {value}")
                text_parts.append("")
            
            # Add content sections
            if "content" in json_data:
                content = json_data["content"]
                
                # Executive summary
                if "executive_summary" in content:
                    text_parts.append("EXECUTIVE SUMMARY:")
                    text_parts.append(content["executive_summary"])
                    text_parts.append("")
                
                # Scope
                if "scope" in content:
                    text_parts.append("SCOPE:")
                    text_parts.append(content["scope"])
                    text_parts.append("")
                
                # Key findings
                if "key_findings" in content:
                    text_parts.append("KEY FINDINGS:")
                    for finding in content["key_findings"]:
                        text_parts.append(f"• {finding}")
                    text_parts.append("")
                
                # Risk assessment
                if "risk_assessment" in content:
                    text_parts.append("RISK ASSESSMENT:")
                    text_parts.append(content["risk_assessment"])
                    text_parts.append("")
                
                # Recommendations
                if "recommendations" in content:
                    text_parts.append("RECOMMENDATIONS:")
                    for rec in content["recommendations"]:
                        text_parts.append(f"• {rec}")
                    text_parts.append("")
                
                # Controls tested
                if "controls_tested" in content:
                    text_parts.append("CONTROLS TESTED:")
                    for control in content["controls_tested"]:
                        if isinstance(control, dict):
                            text_parts.append(f"Control ID: {control.get('control_id', 'N/A')}")
                            text_parts.append(f"Description: {control.get('description', 'N/A')}")
                            text_parts.append(f"Status: {control.get('status', 'N/A')}")
                            text_parts.append("")
                        else:
                            text_parts.append(f"• {control}")
                
                # Handle other content fields dynamically
                for key, value in content.items():
                    if key not in ["executive_summary", "scope", "key_findings", "risk_assessment", "recommendations", "controls_tested"]:
                        text_parts.append(f"{key.replace('_', ' ').upper()}:")
                        if isinstance(value, list):
                            for item in value:
                                text_parts.append(f"• {item}")
                        else:
                            text_parts.append(str(value))
                        text_parts.append("")
            
            return "\n".join(text_parts).strip()
        
        except Exception as e:
            raise Exception(f"JSON text extraction failed: {str(e)}")

    def _split_text_optimized(self, text: str) -> List[str]:
        """Split text into optimized chunks for audit documents."""
        # Use improved chunking strategy
        chunks = self.text_splitter.split_text(text)
        
        # Post-process chunks for better semantic boundaries
        optimized_chunks = []
        for chunk in chunks:
            # Ensure chunks end at natural boundaries when possible
            if len(chunk) > 50 and not chunk.endswith(('.', '!', '?', '\n')):
                # Try to find a better break point
                last_sentence = max(
                    chunk.rfind('. '),
                    chunk.rfind('! '),
                    chunk.rfind('? '),
                    chunk.rfind('\n'),
                    chunk.rfind(': '),  # Preserve header-content relationships
                    chunk.rfind(' - '),  # Preserve list items
                    chunk.rfind(', ')    # Preserve comma-separated items
                )
                if last_sentence > len(chunk) * 0.6:  # More flexible boundary finding
                    chunk = chunk[:last_sentence + 1]
            
            # Preserve all chunks to maximize coverage (was filtering out small chunks)
            if len(chunk.strip()) >= 20:  # Reduced minimum size to preserve more content
                optimized_chunks.append(chunk.strip())
            elif chunk.strip():  # Even preserve very small chunks if they have content
                # Merge with previous chunk if possible to avoid losing content
                if optimized_chunks:
                    optimized_chunks[-1] += " " + chunk.strip()
                else:
                    optimized_chunks.append(chunk.strip())
        
        return optimized_chunks
    
    def _extract_enhanced_metadata(
        self, 
        file: UploadFile, 
        description: Optional[str], 
        document_metadata: Optional[Dict]
    ) -> Dict:
        """Extract enhanced metadata for audit documents."""
        base_metadata = {
            "filename": file.filename,
            "display_name": file.filename,  # Use filename as display name
            "file_size": file.size,
            "content_type": file.content_type,
            "description": description,
            "upload_timestamp": datetime.now().isoformat(),
            "file_extension": file.filename.split(".")[-1].lower() if file.filename else "",
        }
        
        # Add document-specific metadata if provided
        if document_metadata:
            base_metadata.update(document_metadata)
        
        # Set defaults for audit document metadata if not provided
        audit_defaults = {
            "document_type": base_metadata.get("document_type", "unknown"),
            "quality_level": base_metadata.get("quality_level", "medium"),
            "company": base_metadata.get("company", "unknown"),
            "sox_control_ids": base_metadata.get("sox_control_ids", []),
            "compliance_framework": base_metadata.get("compliance_framework", "SOX"),
            "created_by": base_metadata.get("created_by", "system"),
        }
        
        base_metadata.update(audit_defaults)
        return base_metadata
    
    async def _store_in_vector_database(
        self,
        document_id: str,
        chunks: List[str],
        metadata: Dict,
    ) -> bool:
        """Store document chunks in vector database with metadata."""
        try:
            # Ensure vector database is initialized
            await vector_db_service.initialize_collection()
            
            # Store chunks with embeddings and metadata
            success = await vector_db_service.insert_document_chunks(
                document_id=document_id,
                chunks=chunks,
                metadata=metadata
            )
            
            return success
        
        except Exception as e:
            raise Exception(f"Vector database storage failed: {str(e)}")
    
    async def get_document_info(self, document_id: str) -> Dict:
        """Get information about a processed document."""
        try:
            chunks = await vector_db_service.get_document_chunks(document_id)
            
            if not chunks:
                return {"error": "Document not found"}
            
            # Extract metadata from first chunk
            metadata = chunks[0].get("metadata", {})
            
            return {
                "document_id": document_id,
                "chunk_count": len(chunks),
                "metadata": {
                    "filename": metadata.get("filename"),
                    "document_type": metadata.get("document_type"),
                    "quality_level": metadata.get("quality_level"),
                    "company": metadata.get("company"),
                    "sox_control_ids": metadata.get("sox_control_ids", []),
                    "upload_timestamp": metadata.get("upload_timestamp"),
                    "file_size": metadata.get("file_size"),
                },
                "status": "stored"
            }
        
        except Exception as e:
            return {"error": f"Failed to get document info: {str(e)}"}
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the vector database."""
        try:
            return await vector_db_service.delete_document(document_id)
        except Exception as e:
            raise Exception(f"Document deletion failed: {str(e)}")


# Create global instance for backwards compatibility
document_processor = EnhancedDocumentProcessor()

# Alias for the original class name
DocumentProcessor = EnhancedDocumentProcessor 