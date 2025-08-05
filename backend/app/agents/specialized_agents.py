"""
Specialized Agents for Verityn AI Multi-Agent System.

This module implements specialized agents for audit document analysis,
each handling specific aspects of the workflow.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from backend.app.agents.base_agent import BaseAgent, AgentType, AgentMessage
from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.services.vector_database import vector_db_service
from backend.app.config import settings
from backend.app.services.advanced_retrieval import advanced_retrieval_service

logger = logging.getLogger(__name__)


class DocumentProcessingAgent(BaseAgent):
    """Agent responsible for processing and chunking documents."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            agent_type=AgentType.DOCUMENT_PROCESSOR,
            llm_model="gpt-4",
            temperature=0.1,
            verbose=verbose
        )
        self.document_processor = EnhancedDocumentProcessor()
    
    def _initialize_agent(self):
        """Initialize document processing components."""
        self.system_prompt = """You are a Document Processing Agent specializing in audit and compliance documents.

Your responsibilities:
1. Extract and validate document content
2. Identify document type and compliance frameworks
3. Extract key metadata (company, date, document type)
4. Prepare documents for vector storage
5. Ensure proper chunking for audit document analysis

Focus on SOX compliance documents, access reviews, financial reconciliations, and risk assessments."""

    async def _execute_logic(self, context) -> Dict[str, Any]:
        """Execute document processing logic."""
        input_data = context.inputs
        try:
            file_content = input_data.get("file_content", "")
            filename = input_data.get("filename", "unknown")
            document_id = input_data.get("document_id", "")
            
            # Create mock file for processing
            from backend.app.services.document_processor import MockUploadFile
            mock_file = MockUploadFile(
                filename=filename,
                content=file_content,
                content_type="text/plain"
            )
            
            # Process document
            result = await self.document_processor.process_document(
                file=mock_file,
                document_id=document_id,
                description=input_data.get("description", ""),
                document_metadata=input_data.get("metadata", {})
            )
            
            # Extract key information using LLM
            extraction_prompt = ChatPromptTemplate.from_template("""
            Analyze this audit document and extract key information:
            
            Document Content:
            {content}
            
            Extract the following information in JSON format:
            - document_type: (access_review, financial_reconciliation, risk_assessment, etc.)
            - company: (company name)
            - compliance_frameworks: (SOX, SOC2, etc.)
            - key_findings: (list of main findings)
            - risk_level: (high, medium, low)
            - sox_controls: (list of SOX control IDs mentioned)
            - quality_level: (high, medium, low, fail based on findings)
            
            Return only valid JSON.
            """)
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=extraction_prompt.format(content=file_content[:2000]))
            ]
            
            llm_response = await self.llm.ainvoke(messages)
            
            return {
                "document_id": document_id,
                "filename": filename,
                "chunks": result.get("chunks", []),
                "processing_status": "completed",
                "extracted_info": llm_response.content,
                "chunk_count": len(result.get("chunks", [])),
                "metadata": result.get("document_metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            return {
                "processing_status": "failed",
                "error": str(e),
                "document_id": input_data.get("document_id", ""),
                "filename": input_data.get("filename", "")
            }


class ClassificationAgent(BaseAgent):
    """Agent responsible for classifying documents and extracting compliance information."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            agent_type=AgentType.CLASSIFIER,
            llm_model="gpt-4",
            temperature=0.2,
            verbose=verbose
        )
    
    def _initialize_agent(self):
        """Initialize classification components."""
        self.classification_prompt = ChatPromptTemplate.from_template("""
        You are a Compliance Classification Agent specializing in SOX and audit documents.
        
        Analyze the document content and classify it according to:
        1. Document Type: access_review, financial_reconciliation, risk_assessment, control_testing, etc.
        2. Compliance Framework: SOX, SOC2, ISO27001, etc.
        3. Risk Level: high, medium, low based on findings
        4. SOX Controls: specific control IDs (404.1, 404.2, 302.1, etc.)
        5. Material Weaknesses: identify if any material weaknesses are present
        
        Document Content:
        {content}
        
        Return your analysis in JSON format:
        {{
            "document_type": "string",
            "compliance_frameworks": ["string"],
            "risk_level": "string",
            "sox_controls": ["string"],
            "material_weaknesses": ["string"],
            "confidence": 0.95
        }}
        """)
    
    async def _execute_logic(self, context) -> Dict[str, Any]:
        """Execute document classification logic."""
        input_data = context.inputs
        try:
            content = input_data.get("content", "")
            document_id = input_data.get("document_id", "")
            
            # Use LLM for classification
            messages = [
                SystemMessage(content="You are an expert in SOX compliance and audit document classification."),
                HumanMessage(content=self.classification_prompt.format(content=content[:3000]))
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse response (in production, you'd want more robust JSON parsing)
            import json
            try:
                classification_result = json.loads(response.content)
            except:
                # Fallback parsing
                classification_result = {
                    "document_type": "unknown",
                    "compliance_frameworks": ["SOX"],
                    "risk_level": "medium",
                    "sox_controls": [],
                    "material_weaknesses": [],
                    "confidence": 0.5
                }
            
            return {
                "document_id": document_id,
                "classification": classification_result,
                "classification_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return {
                "error": str(e),
                "classification_status": "failed"
            }


class QuestionAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing user questions and determining intent."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            agent_type=AgentType.QUESTION_ANALYZER,
            llm_model="gpt-4",
            temperature=0.3,
            verbose=verbose
        )
    
    def _initialize_agent(self):
        """Initialize question analysis components."""
        self.analysis_prompt = ChatPromptTemplate.from_template("""
        You are a Question Analysis Agent for audit and compliance questions.
        
        Analyze the user's question and determine:
        1. Query Intent: information_retrieval, compliance_check, document_analysis, comparison, etc.
        2. Complexity Level: basic, intermediate, advanced
        3. Required Document Types: access_review, financial_reconciliation, etc.
        4. Compliance Frameworks: SOX, SOC2, ISO27001, etc.
        5. Key Entities: company names, control IDs, dates, etc.
        
        Question: {question}
        
        Return analysis in JSON format:
        {{
            "intent": "string",
            "complexity": "string", 
            "required_documents": ["string"],
            "compliance_frameworks": ["string"],
            "entities": ["string"],
            "search_keywords": ["string"]
        }}
        """)
    
    async def _execute_logic(self, context) -> Dict[str, Any]:
        """Execute question analysis logic."""
        input_data = context.inputs
        try:
            question = input_data.get("question", "")
            conversation_id = input_data.get("conversation_id")
            
            # Analyze question with LLM
            messages = [
                SystemMessage(content="You are an expert in audit and compliance question analysis."),
                HumanMessage(content=self.analysis_prompt.format(question=question))
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse analysis result
            import json
            try:
                analysis_result = json.loads(response.content)
            except:
                # Fallback analysis
                analysis_result = {
                    "intent": "information_retrieval",
                    "complexity": "intermediate",
                    "required_documents": ["access_review"],
                    "compliance_frameworks": ["SOX"],
                    "entities": [],
                    "search_keywords": question.split()[:5]
                }
            
            return {
                "question": question,
                "conversation_id": conversation_id,
                "analysis": analysis_result,
                "analysis_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Question analysis failed: {str(e)}")
            return {
                "error": str(e),
                "analysis_status": "failed"
            }


class ContextRetrievalAgent(BaseAgent):
    """Agent responsible for retrieving relevant context using advanced techniques."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            agent_type=AgentType.CONTEXT_RETRIEVER,
            llm_model="gpt-3.5-turbo",
            temperature=0.1,
            verbose=verbose
        )
        self.vector_db = vector_db_service
    
    def _initialize_agent(self):
        """Initialize context retrieval components."""
        pass
    
    async def _execute_logic(self, context) -> Dict[str, Any]:
        """Execute advanced context retrieval logic."""
        input_data = context.inputs
        try:
            question = input_data.get("question", "")
            analysis = input_data.get("analysis", {})
            
            # Extract search parameters from analysis
            search_keywords = analysis.get("search_keywords", [question])
            required_frameworks = analysis.get("compliance_frameworks", ["SOX"])
            complexity = analysis.get("complexity", "intermediate")
            
            # Determine retrieval strategy based on complexity and query type
            retrieval_strategy = self._determine_retrieval_strategy(question, complexity, analysis)
            
            # Perform advanced retrieval
            if retrieval_strategy == "hybrid":
                search_results = await advanced_retrieval_service.hybrid_search(
                    query=" ".join(search_keywords),
                    limit=10,
                    filters={"compliance_framework": required_frameworks},
                    semantic_weight=0.7,
                    keyword_weight=0.3
                )
                retrieval_method = "hybrid"
                
            elif retrieval_strategy == "query_expansion":
                search_results = await advanced_retrieval_service.query_expansion_search(
                    query=" ".join(search_keywords),
                    limit=10,
                    expansion_terms=required_frameworks
                )
                retrieval_method = "query_expansion"
                
            elif retrieval_strategy == "multi_hop":
                search_results = await advanced_retrieval_service.multi_hop_retrieval(
                    query=" ".join(search_keywords),
                    limit=10,
                    max_hops=2
                )
                retrieval_method = "multi_hop"
                
            elif retrieval_strategy == "ensemble":
                search_results = await advanced_retrieval_service.ensemble_retrieval(
                    query=" ".join(search_keywords),
                    limit=10
                )
                retrieval_method = "ensemble"
                
            else:
                # Fallback to basic semantic search
                search_results = await self.vector_db.semantic_search(
                    query_text=" ".join(search_keywords),
                    limit=10,
                    score_threshold=0.7
                )
                retrieval_method = "semantic"
            
            # Filter results based on compliance frameworks if needed
            filtered_results = []
            for result in search_results:
                metadata = result.get("metadata", {})
                if any(framework in str(metadata) for framework in required_frameworks):
                    filtered_results.append(result)
            
            # Use top results if filtering yields too few results
            if len(filtered_results) < 3 and len(search_results) >= 3:
                filtered_results = search_results[:5]
            
            return {
                "question": question,
                "search_results": filtered_results,
                "result_count": len(filtered_results),
                "retrieval_method": retrieval_method,
                "retrieval_strategy": retrieval_strategy,
                "retrieval_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Advanced context retrieval failed: {str(e)}")
            return {
                "error": str(e),
                "retrieval_status": "failed",
                "search_results": []
            }
    
    def _determine_retrieval_strategy(self, question: str, complexity: str, analysis: Dict) -> str:
        """Determine the best retrieval strategy based on question characteristics."""
        question_lower = question.lower()
        
        # Multi-hop for complex questions requiring multiple document references
        if complexity == "advanced" and any(term in question_lower for term in ["compare", "relationship", "connection", "across"]):
            return "multi_hop"
        
        # Query expansion for compliance-specific questions
        if any(term in question_lower for term in ["SOX", "compliance", "material weakness", "controls"]):
            return "query_expansion"
        
        # Hybrid for questions with specific terminology
        if any(term in question_lower for term in ["access review", "financial reconciliation", "risk assessment"]):
            return "hybrid"
        
        # Ensemble for general questions
        if complexity == "intermediate":
            return "ensemble"
        
        # Default to semantic search
        return "semantic"


class ResponseSynthesisAgent(BaseAgent):
    """Agent responsible for synthesizing final responses from retrieved context."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            agent_type=AgentType.RESPONSE_SYNTHESIZER,
            llm_model="gpt-4",
            temperature=0.4,
            verbose=verbose
        )
    
    def _initialize_agent(self):
        """Initialize response synthesis components."""
        self.synthesis_prompt = ChatPromptTemplate.from_template("""
        You are a Senior Audit Professional providing expert analysis on compliance and audit matters.
        
        Based on the retrieved context, provide a comprehensive response to the user's question.
        Your response should be:
        1. Professional and authoritative
        2. Backed by specific evidence from the documents
        3. Include relevant compliance insights
        4. Formatted as a formal audit communication
        
        Question: {question}
        
        Retrieved Context:
        {context}
        
        Document Classifications:
        {classifications}
        
        **CRITICAL SOURCE REFERENCE RULES**:
        - Only reference documents that are actually provided in the context above
        - Use the exact Document Name, Document Type, and Company information from the context
        - Do NOT invent or fabricate document names
        - If the context shows "Document Name: audit_report.pdf, Document Type: access_review", reference it as "audit_report.pdf (access_review)"
        - If no documents are provided in context, state "No specific documents referenced" in the Source Documents section
        
        Please provide your analysis in this format:
        
        **Subject:** [Clear subject line]
        
        **Response:** [Detailed professional response]
        
        **Compliance Insights:** [Key compliance considerations]
        
        **Source Documents:** [Reference to specific documents used - ONLY use actual document information from context]
        """)
    
    async def _execute_logic(self, context) -> Dict[str, Any]:
        """Execute response synthesis logic."""
        input_data = context.inputs
        try:
            question = input_data.get("question", "")
            analysis = input_data.get("analysis", {})
            search_results = input_data.get("context", [])
            classifications = input_data.get("classifications", [])
            
            # Prepare context from search results with actual document information
            context_parts = []
            for i, result in enumerate(search_results[:5]):
                doc_id = result.get('document_id', f'unknown_{i+1}')
                doc_type = result.get('document_type', 'Unknown')
                company = result.get('company', 'Unknown')
                display_name = result.get('display_name', result.get('filename', f'Document {i+1}'))
                chunk_text = result.get('chunk_text', '')[:500]
                
                context_part = f"""Document {i+1}:
- Document ID: {doc_id}
- Document Name: {display_name}
- Document Type: {doc_type}
- Company: {company}
- Content: {chunk_text}..."""
                context_parts.append(context_part)
            
            context_text = "\n\n".join(context_parts) if context_parts else "No relevant document context found."
            
            # Prepare classifications summary
            classifications_text = "\n".join([
                f"- {cls.get('document_type', 'Unknown')}: {cls.get('risk_level', 'Unknown')} risk"
                for cls in classifications[:3]
            ])
            
            # Synthesize response
            messages = [
                SystemMessage(content="You are a senior audit professional with expertise in SOX compliance. Only reference actual documents provided in the context."),
                HumanMessage(content=self.synthesis_prompt.format(
                    question=question,
                    context=context_text,
                    classifications=classifications_text
                ))
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Extract compliance insights (simple parsing)
            response_content = response.content
            
            # Simple extraction of compliance insights
            compliance_insights = {}
            if "material weakness" in response_content.lower():
                compliance_insights["material_weaknesses_identified"] = True
            if "sox 404" in response_content.lower():
                compliance_insights["sox_404_related"] = True
            if "high risk" in response_content.lower():
                compliance_insights["high_risk_identified"] = True
            
            return {
                "question": question,
                "response": response_content,
                "compliance_insights": compliance_insights,
                "sources_used": len(search_results),
                "synthesis_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Response synthesis failed: {str(e)}")
            return {
                "error": str(e),
                "synthesis_status": "failed",
                "response": "I apologize, but I encountered an error while processing your request."
            }


class ComplianceAnalyzerAgent(BaseAgent):
    """Agent responsible for deep compliance analysis and risk assessment."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            agent_type=AgentType.COMPLIANCE_ANALYZER,
            llm_model="gpt-4",
            temperature=0.2,
            verbose=verbose
        )
    
    def _initialize_agent(self):
        """Initialize compliance analysis components."""
        self.compliance_prompt = ChatPromptTemplate.from_template("""
        You are a Compliance Risk Assessment Expert specializing in SOX and audit regulations.
        
        Analyze the provided context for compliance risks, control deficiencies, and regulatory implications.
        
        Focus on:
        1. SOX 404 control effectiveness
        2. Material weaknesses and significant deficiencies  
        3. Risk assessment and mitigation strategies
        4. Regulatory reporting implications
        5. Management recommendations
        
        Question: {question}
        Context: {context}
        Classifications: {classifications}
        
        Provide detailed compliance analysis in JSON format:
        {{
            "risk_assessment": {{
                "overall_risk": "high|medium|low",
                "material_weaknesses": ["list"],
                "significant_deficiencies": ["list"],
                "control_gaps": ["list"]
            }},
            "sox_analysis": {{
                "sox_404_compliance": "compliant|non_compliant|requires_review",
                "control_effectiveness": "effective|ineffective|needs_improvement",
                "remediation_required": true/false
            }},
            "recommendations": ["list of recommendations"],
            "regulatory_implications": ["list of implications"]
        }}
        """)
    
    async def _execute_logic(self, context) -> Dict[str, Any]:
        """Execute compliance analysis logic."""
        input_data = context.inputs
        try:
            question = input_data.get("question", "")
            search_results = input_data.get("context", [])
            classifications = input_data.get("classifications", [])
            
            # Prepare analysis context
            context_text = "\n\n".join([
                f"Document: {result.get('chunk_text', '')[:400]}..."
                for result in search_results[:3]
            ])
            
            classifications_text = "\n".join([
                f"- Type: {cls.get('document_type', 'Unknown')}, Risk: {cls.get('risk_level', 'Unknown')}"
                for cls in classifications[:3]
            ])
            
            # Perform compliance analysis
            messages = [
                SystemMessage(content="You are an expert compliance analyst with deep SOX and audit expertise."),
                HumanMessage(content=self.compliance_prompt.format(
                    question=question,
                    context=context_text,
                    classifications=classifications_text
                ))
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse compliance analysis
            import json
            try:
                compliance_analysis = json.loads(response.content)
            except:
                # Fallback analysis
                compliance_analysis = {
                    "risk_assessment": {
                        "overall_risk": "medium",
                        "material_weaknesses": [],
                        "significant_deficiencies": [],
                        "control_gaps": []
                    },
                    "sox_analysis": {
                        "sox_404_compliance": "requires_review",
                        "control_effectiveness": "needs_improvement",
                        "remediation_required": True
                    },
                    "recommendations": ["Conduct detailed control testing"],
                    "regulatory_implications": ["Potential SOX 404 disclosure requirements"]
                }
            
            return {
                "question": question,
                "compliance_analysis": compliance_analysis,
                "analysis_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Compliance analysis failed: {str(e)}")
            return {
                "error": str(e),
                "analysis_status": "failed"
            } 