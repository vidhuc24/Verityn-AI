"""
Enhanced RAG Chat Engine for Verityn AI.

This module implements a complete RAG (Retrieval-Augmented Generation) pipeline
for document analysis and compliance insights, integrating with our vector database
and following bootcamp best practices.
"""

import uuid
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncio
import logging

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

from backend.app.config import settings
from backend.app.services.vector_database import vector_db_service
from backend.app.services.query_enhancement import query_enhancement_service
from backend.app.services.performance_tracker import performance_tracker

logger = logging.getLogger(__name__)


class RAGChatEngine:
    """Enhanced RAG-powered chat engine for audit document analysis."""
    
    def __init__(self):
        """Initialize the RAG chat engine."""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.3,  # Lower temperature for factual compliance responses
        )
        
        # Conversation storage (in-memory for now)
        self.conversations: Dict[str, List[Dict]] = {}
        
        # RAG prompt templates
        self.system_prompt = self._create_system_prompt()
        self.rag_prompt = self._create_rag_prompt()
        
    def _create_system_prompt(self) -> str:
        """Create the system prompt for audit document analysis."""
        return """You are Verityn AI, an expert assistant specializing in audit, risk, and compliance analysis. 

Your expertise includes:
- SOX (Sarbanes-Oxley) compliance requirements
- Internal controls and risk assessment
- Financial reporting and audit procedures
- Access controls and segregation of duties
- Material weakness identification and remediation

**RESPONSE FORMATTING REQUIREMENTS:**
Always structure your responses using the following markdown format:

## 📋 Executive Summary
Brief overview of the key findings and implications.

## 🔍 Key Findings
- **Finding 1**: [Specific finding with context]
- **Finding 2**: [Specific finding with context]
- **Finding 3**: [Specific finding with context]

## ⚠️ Risk Assessment
**Risk Level**: [High/Medium/Low]
**Rationale**: [Explanation of risk level determination]

## 📊 Compliance Framework
- **Framework**: [SOX, PCI-DSS, etc.]
- **Control IDs**: [Specific control references]
- **Requirements**: [Key compliance requirements identified]

## 🎯 Recommendations
1. **Immediate Actions**: [Priority 1 recommendations]
2. **Short-term**: [30-90 day recommendations]
3. **Long-term**: [Strategic recommendations]

Guidelines for responses:
1. Always base your answers on the provided document context
2. Clearly distinguish between facts from documents and your analysis
3. Use markdown formatting for better readability
4. Highlight risk levels and material weaknesses prominently
5. Provide actionable, prioritized recommendations
6. If information is insufficient, clearly state limitations
7. Use professional audit terminology appropriately
8. Prioritize findings and recommendations by urgency and impact

Remember: Accuracy and compliance are critical in audit contexts. Structure your responses to be immediately actionable for audit professionals."""

    def _create_rag_prompt(self) -> ChatPromptTemplate:
        """Create the RAG prompt template for context-aware responses."""
        template = """Based on the following document context and conversation history, provide a comprehensive response to the user's question.

DOCUMENT CONTEXT:
{context}

CONVERSATION HISTORY:
{chat_history}

USER QUESTION: {question}

**IMPORTANT**: Structure your response using the markdown format specified in the system prompt. Include all relevant sections (Executive Summary, Key Findings, Risk Assessment, Compliance Framework, Recommendations) even if some sections are brief.

Instructions:
- Use the document context as your primary source of information
- Reference specific sections, findings, or data points from the documents
- Identify any compliance frameworks, control IDs, or risk levels mentioned
- If the context doesn't contain sufficient information, clearly state this in the relevant section
- Provide actionable insights relevant to audit and compliance professionals
- Use markdown formatting for headers, bullet points, and emphasis
- Prioritize findings and recommendations by urgency and impact

RESPONSE:"""
        
        return ChatPromptTemplate.from_template(template)
    
    async def process_message(
        self,
        message: str,
        document_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        include_web_search: bool = True,
        search_filters: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """
        Process a chat message using RAG pipeline with comprehensive performance tracking.

        Args:
            message: The user's message/question
            document_id: Specific document to search (optional)
            conversation_id: Conversation ID for context
            include_web_search: Whether to include web search (future feature)
            search_filters: Additional filters for document retrieval

        Returns:
            Dictionary containing the response and metadata
        """
        # Start performance tracking for this query
        query_id = performance_tracker.start_query(query_text=message)
        conversation_id = conversation_id or f"conv_{str(uuid.uuid4())[:8]}"

        try:
            # Step 1: Retrieve relevant context from vector database
            retrieval_start = time.time()
            context_results, no_results_enhancement = await self._retrieve_context(
                query=message,
                document_id=document_id,
                filters=search_filters
            )
            retrieval_time = (time.time() - retrieval_start) * 1000  # Convert to milliseconds

            # Step 2: Format context for the LLM
            formatted_context = self._format_context(context_results)
            
            # Step 3: Get conversation history
            chat_history = self._get_conversation_history(conversation_id)
            
            # Step 4: Generate response using RAG pipeline
            generation_start = time.time()
            response = await self._generate_response(
                question=message,
                context=formatted_context,
                chat_history=chat_history
            )
            generation_time = (time.time() - generation_start) * 1000  # Convert to milliseconds

            # Step 5: Extract compliance insights
            compliance_insights = self._extract_compliance_insights(context_results, response)

            # Step 6: Generate suggested questions
            suggested_questions = self._generate_suggested_questions(context_results, message)

            # Step 7: Store conversation
            self._store_conversation_turn(
                conversation_id=conversation_id,
                user_message=message,
                assistant_response=response,
                context_used=context_results
            )

            # Prepare response with enhanced no-results handling and performance data
            response_data = {
                "message": {
                    "role": "assistant",
                    "content": response,
                    "confidence": self._calculate_confidence(context_results),
                    "sources": self._format_sources(context_results)
                },
                "conversation_id": conversation_id,
                "suggested_questions": suggested_questions,
                "compliance_insights": compliance_insights,
                "context_metadata": {
                    "documents_searched": len(set(r["document_id"] for r in context_results)),
                    "chunks_retrieved": len(context_results),
                    "avg_relevance_score": sum(r["score"] for r in context_results) / len(context_results) if context_results else 0
                }
            }

            # Add no-results enhancement data if applicable
            if no_results_enhancement:
                response_data["no_results_enhancement"] = {
                    "has_suggestions": True,
                    "alternative_queries": no_results_enhancement["suggestions"]["alternative_queries"],
                    "query_tips": no_results_enhancement["suggestions"]["query_tips"],
                    "related_terms": no_results_enhancement["suggestions"]["related_terms"],
                    "domain_guidance": no_results_enhancement["domain_guidance"],
                    "enhancement_message": no_results_enhancement["message"]
                }

                # If we used fallback results, indicate this in the message
                if no_results_enhancement.get("has_results"):
                    response_data["message"]["content"] = (
                        f"{no_results_enhancement['message']}\n\n{response}"
                    )
                    response_data["message"]["is_fallback_result"] = True

            # Manually record step timings
            with performance_tracker.lock:
                if query_id in performance_tracker.active_queries:
                    performance_tracker.active_queries[query_id]['steps']['document_retrieval'] = {
                        'step_name': 'document_retrieval',
                        'duration_ms': retrieval_time,
                        'success': True,
                        'metadata': {'chunks_retrieved': len(context_results)}
                    }
                    performance_tracker.active_queries[query_id]['steps']['llm_generation'] = {
                        'step_name': 'llm_generation',
                        'duration_ms': generation_time,
                        'success': True,
                        'metadata': {'response_length': len(response)}
                    }

            # Add performance tracking data
            query_performance = performance_tracker.end_query(query_id)
            if query_performance:
                response_data["performance"] = {
                    "query_id": query_id,
                    "total_time_ms": query_performance["total_duration_ms"],
                    "step_breakdown": query_performance["steps"],
                    "memory_usage_mb": query_performance.get("total_memory_delta_mb", 0)
                }

            return response_data
            
        except Exception as e:
            logger.error(f"Chat processing failed: {str(e)}")
            return {
                "message": {
                    "role": "assistant", 
                    "content": "I apologize, but I encountered an error while processing your question. Please try again or rephrase your question.",
                    "confidence": 0.0,
                    "sources": []
                },
                "conversation_id": conversation_id or f"conv_{str(uuid.uuid4())[:8]}",
                "suggested_questions": [
                    "What documents are available for analysis?",
                    "Can you help me understand the compliance framework?",
                    "What are the key audit findings?"
                ],
                "compliance_insights": {},
                "error": str(e)
            }
    
    async def _retrieve_context(
        self,
        query: str,
        document_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Retrieve relevant context from vector database with intelligent no-results handling.
        
        Returns:
            Tuple of (results, no_results_enhancement) where no_results_enhancement 
            is present if no results were found and contains suggestions/fallbacks.
        """
        try:
            # Build search filters
            search_filters = filters or {}
            if document_id:
                search_filters["document_id"] = document_id
            
                # Use hybrid search for better results (optimized for speed)
                results = await vector_db_service.hybrid_search(
                    query_text=query,
                    limit=3,  # Reduced from 5 to 3 for faster LLM processing
                    filters=search_filters if search_filters else None,
                    semantic_weight=0.7,
                    keyword_weight=0.3
                )
            
            logger.info(f"Retrieved {len(results)} context chunks for query: {query[:50]}...")

            # Apply intelligent chunk selection for better performance
            results = self._select_optimal_chunks(results)

            # If no results found, use query enhancement service
            if not results:
                logger.info(f"No results found for query: {query[:50]}... - Using query enhancement")
                enhancement = await query_enhancement_service.handle_no_results(
                    original_query=query,
                    search_metadata={
                        "filters": search_filters,
                        "document_id": document_id
                    }
                )
                
                # If enhancement found fallback results, use them
                if enhancement.get("fallback_results"):
                    logger.info(f"Query enhancement found {len(enhancement['fallback_results'])} fallback results")
                    return enhancement["fallback_results"], enhancement
                else:
                    # No results even with fallbacks
                    return [], enhancement
            
            # Normal results found
            return results, None
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {str(e)}")
            return [], None
    
    def _format_context(self, context_results: List[Dict[str, Any]]) -> str:
        """Format retrieved context for LLM consumption (optimized for speed)."""
        if not context_results:
            return "No relevant document context found."

        # Sort by relevance score for better context ordering
        sorted_results = sorted(context_results, key=lambda x: x['score'], reverse=True)

        formatted_chunks = []
        for i, result in enumerate(sorted_results, 1):
            # Optimized formatting - reduced metadata to essential info only
            doc_info = f"[{result['document_id']} - Score: {result['score']:.3f}]"
            content = result['chunk_text'].strip()

            # Limit content length to prevent excessive token usage
            if len(content) > 800:  # Truncate very long chunks
                content = content[:800] + "..."

            formatted_chunks.append(f"{doc_info}\n{content}")

        return "\n\n".join(formatted_chunks)

    def _select_optimal_chunks(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Intelligently select optimal chunks for LLM processing based on relevance and content quality.

        Args:
            results: Raw search results from vector database

        Returns:
            Filtered and optimized list of chunks
        """
        if not results:
            return results

        if len(results) <= 3:  # Already optimal
            return results

        # Sort by relevance score (highest first)
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)

        # Apply relevance threshold - only keep chunks above 0.4 score
        threshold_results = [r for r in sorted_results if r['score'] >= 0.4]

        # If we have enough high-quality results, use them
        if len(threshold_results) >= 2:
            return threshold_results[:3]  # Top 3 high-quality chunks

        # Otherwise, supplement with lower-scoring chunks
        remaining_slots = 3 - len(threshold_results)
        additional_chunks = sorted_results[len(threshold_results):len(threshold_results) + remaining_slots]

        return threshold_results + additional_chunks

    def _get_conversation_history(self, conversation_id: str) -> str:
        """Get formatted conversation history."""
        if conversation_id not in self.conversations:
            return "No previous conversation history."
        
        history = self.conversations[conversation_id]
        formatted_history = []
        
        for turn in history[-3:]:  # Last 3 turns for context
            formatted_history.append(f"User: {turn['user_message']}")
            formatted_history.append(f"Assistant: {turn['assistant_response'][:200]}...")
        
        return "\n".join(formatted_history) if formatted_history else "No previous conversation history."
    
    async def _generate_response(
        self,
        question: str,
        context: str,
        chat_history: str
    ) -> str:
        """Generate response using the RAG pipeline."""
        try:
            # Create the prompt
            prompt = self.rag_prompt.format(
                context=context,
                chat_history=chat_history,
                question=question
            )
            
            # Generate response
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return "I apologize, but I'm unable to generate a response at this time. Please try again."
    
    def _extract_compliance_insights(
        self, 
        context_results: List[Dict[str, Any]], 
        response: str
    ) -> Dict[str, Any]:
        """Extract compliance insights from context and response."""
        if not context_results:
            return {}
        
        # Aggregate compliance information
        frameworks = set()
        sox_controls = set()
        companies = set()
        quality_levels = set()
        
        for result in context_results:
            if result.get('compliance_framework'):
                frameworks.add(result['compliance_framework'])
            if result.get('sox_control_ids'):
                sox_controls.update(result['sox_control_ids'])
            if result.get('company'):
                companies.add(result['company'])
            if result.get('quality_level'):
                quality_levels.add(result['quality_level'])
        
        # Determine risk level based on quality levels and response content
        risk_level = "Low"
        if "fail" in quality_levels or "material weakness" in response.lower():
            risk_level = "High"
        elif "deficient" in response.lower() or "medium" in quality_levels:
            risk_level = "Medium"
        
        return {
            "frameworks": list(frameworks),
            "sox_controls": list(sox_controls),
            "companies": list(companies),
            "risk_level": risk_level,
            "quality_levels": list(quality_levels),
            "key_findings": self._extract_key_findings(response)
        }
    
    def _extract_key_findings(self, response: str) -> List[str]:
        """Extract key findings from the response."""
        findings = []
        response_lower = response.lower()
        
        # Look for common audit findings patterns
        if "material weakness" in response_lower:
            findings.append("Material weakness identified")
        if "segregation of duties" in response_lower:
            findings.append("Segregation of duties issues")
        if "access control" in response_lower:
            findings.append("Access control findings")
        if "remediation" in response_lower:
            findings.append("Remediation required")
        
        return findings[:3]  # Limit to top 3 findings
    
    def _generate_suggested_questions(
        self, 
        context_results: List[Dict[str, Any]], 
        current_question: str
    ) -> List[str]:
        """Generate contextually relevant follow-up questions."""
        if not context_results:
            return [
                "What documents are available for analysis?",
                "Can you explain the compliance framework?",
                "What are the main audit findings?"
            ]
        
        suggestions = []
        
        # Based on document types present
        doc_types = set(r.get('document_type') for r in context_results if r.get('document_type'))
        if 'access_review' in doc_types:
            suggestions.append("What are the key access control findings?")
        if 'financial_reconciliation' in doc_types:
            suggestions.append("Are there any reconciliation discrepancies?")
        if 'risk_assessment' in doc_types:
            suggestions.append("What is the overall risk assessment?")
        
        # Based on quality levels
        quality_levels = set(r.get('quality_level') for r in context_results if r.get('quality_level'))
        if 'fail' in quality_levels:
            suggestions.append("What remediation steps are recommended?")
        
        # Based on SOX controls
        sox_controls = set()
        for r in context_results:
            if r.get('sox_control_ids'):
                sox_controls.update(r['sox_control_ids'])
        
        if sox_controls:
            suggestions.append("Which SOX controls are affected?")
        
        # Default suggestions if none generated
        if not suggestions:
            suggestions = [
                "Can you provide more details about this finding?",
                "What are the compliance implications?",
                "Are there any related control deficiencies?"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _calculate_confidence(self, context_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on context quality."""
        if not context_results:
            return 0.1
        
        # Base confidence on average relevance score
        avg_score = sum(r["score"] for r in context_results) / len(context_results)
        
        # Boost confidence if we have multiple relevant chunks
        chunk_bonus = min(len(context_results) * 0.1, 0.3)
        
        # Cap at 0.95 to indicate some uncertainty
        return min(avg_score + chunk_bonus, 0.95)
    
    def _format_sources(self, context_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for the response."""
        sources = []
        for result in context_results:
            source = {
                "document_id": result["document_id"],
                "title": result.get("metadata", {}).get("filename", "Unknown Document"),
                "content": result["chunk_text"][:200] + "..." if len(result["chunk_text"]) > 200 else result["chunk_text"],
                "relevance_score": result["score"],
                "document_type": result.get("document_type", "Unknown"),
                "company": result.get("company", "Unknown")
            }
            sources.append(source)
        
        return sources
    
    def _store_conversation_turn(
        self,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        context_used: List[Dict[str, Any]]
    ):
        """Store a conversation turn."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "assistant_response": assistant_response,
            "context_chunks": len(context_used),
            "documents_referenced": list(set(r["document_id"] for r in context_used))
        }
        
        self.conversations[conversation_id].append(turn)
        
        # Keep only last 10 turns per conversation
        if len(self.conversations[conversation_id]) > 10:
            self.conversations[conversation_id] = self.conversations[conversation_id][-10:]
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation history by ID."""
        if conversation_id not in self.conversations:
            return None
        
        return {
            "conversation_id": conversation_id,
            "turns": self.conversations[conversation_id],
            "total_turns": len(self.conversations[conversation_id]),
            "created_at": self.conversations[conversation_id][0]["timestamp"] if self.conversations[conversation_id] else None
        }
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation by ID."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
    
    async def list_conversations(self) -> List[Dict[str, Any]]:
        """List all conversations with metadata."""
        conversations = []
        for conv_id, turns in self.conversations.items():
            if turns:
                conversations.append({
                    "conversation_id": conv_id,
                    "turn_count": len(turns),
                    "created_at": turns[0]["timestamp"],
                    "last_message": turns[-1]["timestamp"],
                    "preview": turns[-1]["user_message"][:100] + "..." if len(turns[-1]["user_message"]) > 100 else turns[-1]["user_message"]
                })
        
        return conversations


# Global chat engine instance
chat_engine = RAGChatEngine()

# Alias for backwards compatibility
ChatEngine = RAGChatEngine 