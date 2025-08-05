"""
Chat routes for Verityn AI backend.

This module handles chat-related API endpoints including message processing,
conversation management, and question suggestions using the RAG Chat Engine.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.models.chat import ChatRequest, ChatResponse, ConversationResponse
from backend.app.services.chat_engine import chat_engine
from backend.app.services.question_suggestions import QuestionSuggestions

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a chat message and get RAG-powered response."""
    try:
        response = await chat_engine.process_message(
            message=request.message,
            document_id=request.document_id,
            conversation_id=request.conversation_id,
            include_web_search=request.include_web_search,
        )
        
        return ChatResponse(
            message=response["message"],
            conversation_id=response["conversation_id"],
            suggested_questions=response.get("suggested_questions"),
            compliance_insights=response.get("compliance_insights"),
            context_metadata=response.get("context_metadata")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """Get conversation history by ID."""
    try:
        conversation = await chat_engine.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationResponse(
            conversation_id=conversation["conversation_id"],
            turns=conversation["turns"],
            total_turns=conversation["total_turns"],
            created_at=conversation["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation by ID."""
    try:
        success = await chat_engine.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")


@router.get("/conversations")
async def list_conversations(
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of conversations to return")
):
    """List all conversations with metadata."""
    try:
        conversations = await chat_engine.list_conversations()
        
        # Sort by last message timestamp (most recent first)
        conversations.sort(key=lambda x: x["last_message"], reverse=True)
        
        # Apply limit
        limited_conversations = conversations[:limit]
        
        return {
            "conversations": limited_conversations,
            "total": len(conversations),
            "returned": len(limited_conversations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")


@router.get("/suggestions")
async def get_question_suggestions(
    document_id: Optional[str] = Query(default=None, description="Document ID for context-specific suggestions"),
    category: Optional[str] = Query(default=None, description="Suggestion category (audit, compliance, risk)")
):
    """Get suggested questions for the chat interface."""
    try:
        suggestions_service = QuestionSuggestions()
        suggestions = await suggestions_service.get_suggestions(
            document_id=document_id,
            category=category
        )
        
        return {
            "suggestions": suggestions,
            "category": category,
            "document_id": document_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@router.post("/feedback")
async def submit_feedback(
    conversation_id: str,
    message_index: int,
    feedback_type: str,  # "helpful", "not_helpful", "inaccurate"
    feedback_text: Optional[str] = None
):
    """Submit feedback for a chat response (future feature for RAGAS evaluation)."""
    try:
        # TODO: Implement feedback storage for RAGAS evaluation
        # This will be used in future RAGAS evaluation implementation
        
        return {
            "message": "Feedback submitted successfully",
            "conversation_id": conversation_id,
            "message_index": message_index,
            "feedback_type": feedback_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}") 