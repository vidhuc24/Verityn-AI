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
from backend.app.services.tavily_service import tavily_service

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
        
        Analyze the user's question and determine the most specific intent and appropriate complexity.
        
        INTENT CLASSIFICATION (choose the MOST SPECIFIC match):
        - information_retrieval: Simple fact-finding queries ("What are the findings?", "Show me controls")
        - relationship_analysis: Questions about connections/relationships between entities ("How do X and Y connect?", "What is the relationship between A and B?")
        - comparison: Comparative analysis queries ("Compare X vs Y", "Differences between A and B")
        - compliance_assessment: Compliance evaluation queries ("Assess SOX compliance", "Identify violations", "Evaluate control effectiveness")
        - compliance_check: Simple compliance verification ("Is this compliant?", "Does this meet requirements?")
        - document_analysis: Document-specific analysis ("Analyze this report", "Review document findings")
        - unknown: Unclear or ambiguous queries
        
        COMPLEXITY ASSESSMENT:
        - basic: Single concept, straightforward queries
        - intermediate: Multiple concepts or moderate analysis required  
        - advanced: Complex multi-part queries, relationship analysis, comparative analysis, process evaluation
        
        INTENT CLASSIFICATION EXAMPLES:
        - "How do risk assessments connect to control deficiencies?" → relationship_analysis (advanced)
        - "What is the relationship between IT controls and application controls?" → relationship_analysis (advanced)
        - "Compare SOX vs SOC2 requirements" → comparison (advanced)
        - "Identify segregation of duties violations and assess impact" → compliance_assessment (advanced)
        - "Is this control compliant with SOX?" → compliance_check (basic)
        - "What are the audit findings?" → information_retrieval (basic)
        
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
                # Enhanced fallback analysis with basic intent detection
                question_lower = question.lower()
                
                # Determine fallback intent based on keywords
                if any(word in question_lower for word in ["relationship", "connect", "between", "relate"]):
                    intent = "relationship_analysis"
                    complexity = "advanced"
                elif any(word in question_lower for word in ["compare", "difference", "versus", "vs"]):
                    intent = "comparison"
                    complexity = "advanced"
                elif any(word in question_lower for word in ["assess", "evaluate", "identify", "violations", "compliance"]):
                    intent = "compliance_assessment"
                    complexity = "intermediate"
                elif any(word in question_lower for word in ["compliant", "meets", "requirements"]):
                    intent = "compliance_check"
                    complexity = "basic"
                else:
                    intent = "information_retrieval"
                    complexity = "basic" if len(question.split()) < 5 else "intermediate"
                
                analysis_result = {
                    "intent": intent,
                    "complexity": complexity,
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

            # Use original question as primary search query, not keyword fragments
            search_query = question  # Use full question instead of split keywords

            # Determine retrieval strategy based on complexity and query type
            retrieval_strategy = self._determine_retrieval_strategy(question, complexity, analysis)

            logger.info(f"Context Retrieval - Query: '{search_query}', Strategy: {retrieval_strategy}")

            search_results = []
            retrieval_method = "semantic"  # Default fallback

            try:
                # Try advanced retrieval strategies first
                if retrieval_strategy == "hybrid":
                    # Build proper filters based on actual metadata structure
                    proper_filters = self._build_proper_filters(required_frameworks)
                    search_results = await advanced_retrieval_service.hybrid_search(
                        query=search_query,
                        limit=10,
                        filters=proper_filters,
                        semantic_weight=0.7,
                        keyword_weight=0.3
                    )
                    retrieval_method = "hybrid"

                elif retrieval_strategy == "query_expansion":
                    search_results = await advanced_retrieval_service.query_expansion_search(
                        query=search_query,
                        limit=10,
                        expansion_terms=required_frameworks
                    )
                    retrieval_method = "query_expansion"

                elif retrieval_strategy == "multi_hop":
                    search_results = await advanced_retrieval_service.multi_hop_retrieval(
                        query=search_query,
                        limit=10,
                        max_hops=2
                    )
                    retrieval_method = "multi_hop"

                elif retrieval_strategy == "ensemble":
                    search_results = await advanced_retrieval_service.ensemble_retrieval(
                        query=search_query,
                        limit=10
                    )
                    retrieval_method = "ensemble"

                else:
                    # Use basic semantic search as fallback
                    proper_filters = self._build_proper_filters(required_frameworks)
                search_results = await self.vector_db.semantic_search(
                    query_text=search_query,
                    limit=10,
                    score_threshold=0.1,
                    filters=proper_filters
                )
                retrieval_method = "semantic"

            except Exception as advanced_error:
                logger.warning(f"Advanced retrieval failed: {str(advanced_error)}, falling back to basic search")
                # Fallback to basic semantic search
                try:
                    proper_filters = self._build_proper_filters(required_frameworks)
                    search_results = await self.vector_db.semantic_search(
                        query_text=search_query,
                        limit=10,
                        score_threshold=0.1,
                        filters=proper_filters
                    )
                    retrieval_method = "semantic_fallback"
                except Exception as fallback_error:
                    logger.error(f"Basic search also failed: {str(fallback_error)}")
                    return {
                        "error": f"Both advanced and basic retrieval failed: {str(advanced_error)}, {str(fallback_error)}",
                        "retrieval_status": "failed",
                        "context": [],
                        "search_results": []
                    }

            # Apply robust filtering based on compliance frameworks
            filtered_results = self._filter_results_by_frameworks(search_results, required_frameworks)

            # Ensure we have at least some results
            if not filtered_results and search_results:
                logger.warning("Framework filtering removed all results, using top results anyway")
                filtered_results = search_results[:5]  # Use top 5 even if they don't match frameworks

            logger.info(f"Context Retrieval - Found {len(filtered_results)} relevant results")

            return {
                "question": question,
                "context": filtered_results,  # Use 'context' key for integration compatibility
                "search_results": filtered_results,  # Keep both for backward compatibility
                "result_count": len(filtered_results),
                "retrieval_method": retrieval_method,
                "retrieval_strategy": retrieval_strategy,
                "search_query_used": search_query,
                "retrieval_status": "completed"
            }

        except Exception as e:
            logger.error(f"Context retrieval failed: {str(e)}")
            return {
                "error": str(e),
                "retrieval_status": "failed",
                "context": [],  # Use 'context' key for integration compatibility
                "search_results": []
            }
    
    def _filter_results_by_frameworks(self, search_results: List[Dict], required_frameworks: List[str]) -> List[Dict]:
        """Filter search results based on compliance frameworks with robust matching."""
        if not required_frameworks or not search_results:
            return search_results

        filtered_results = []

        for result in search_results:
            metadata = result.get("metadata", {})
            if not metadata:
                continue

            # Check multiple metadata fields for framework matches
            framework_matches = []

            # Check compliance_framework field (singular)
            if "compliance_framework" in metadata:
                framework_matches.append(str(metadata["compliance_framework"]).upper())

            # Check compliance_frameworks field (plural)
            if "compliance_frameworks" in metadata:
                frameworks = metadata["compliance_frameworks"]
                if isinstance(frameworks, list):
                    framework_matches.extend([str(f).upper() for f in frameworks])
                else:
                    framework_matches.append(str(frameworks).upper())

            # Check document_type for SOX-related documents
            if "document_type" in metadata:
                doc_type = str(metadata["document_type"]).lower()
                if any(sox_term in doc_type for sox_term in ["sox", "access_review", "financial", "control"]):
                    framework_matches.append("SOX")

            # Check if any required framework matches
            for required_framework in required_frameworks:
                required_upper = str(required_framework).upper()
                if any(required_upper in match for match in framework_matches):
                    filtered_results.append(result)
                    break

        logger.info(f"Framework filtering: {len(search_results)} -> {len(filtered_results)} results")
        return filtered_results

    def _build_proper_filters(self, required_frameworks: List[str]) -> Dict[str, Any]:
        """Build proper filters that match the actual metadata structure."""
        # Based on our investigation, the metadata has these fields:
        # - compliance_frameworks (plural array)
        # - compliance_framework (singular string)
        # - document_type (can contain SOX-related terms)

        filters = {}

        if required_frameworks:
            # Check both compliance_frameworks (array) and compliance_framework (string)
            framework_filters = []

            for framework in required_frameworks:
                framework_upper = str(framework).upper()
                framework_filters.append(framework_upper)

            # Also check for SOX in document_type
            if any("SOX" in str(f) for f in required_frameworks):
                filters["document_type"] = ["access_review", "financial", "control", "sox"]

            # Set the compliance framework filters
            if framework_filters:
                filters["compliance_frameworks"] = framework_filters
                filters["compliance_framework"] = framework_filters  # Also check singular form

        return filters

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

        RESPONSE ADAPTATION REQUIREMENTS:
        - ADAPT response format based on question complexity and context availability
        - For SIMPLE/FACTUAL questions: Provide direct, concise answers without heavy formatting
        - For COMPLEX/ANALYTICAL questions: Use structured format with sections
        - For FOLLOW-UP questions: Keep responses focused and avoid repeating previous structure
        - Always prioritize CLARITY and RELEVANCE over comprehensiveness

        PROFESSIONAL TONE REQUIREMENTS:
        - Use authoritative audit language: "Based on our analysis", "The assessment reveals", "Findings indicate"
        - Include specific compliance terminology and control references when relevant
        - Maintain formal, professional audit communication style
        - Use precise, technical language appropriate for audit professionals

        Question: {question}
        Question Intent: {intent}
        Question Complexity: {complexity}
        Context Count: {context_count}
        Is Follow-up: {is_followup}

        Retrieved Context:
        {context}

        Document Classifications:
        {classifications}

        **Latest Regulatory Context:**
        {regulatory_context}

        **CRITICAL SOURCE REFERENCE RULES FOR SINGLE-DOCUMENT CHAT**:
        - This is a single-document analysis - refer to "the document" or "this document"
        - Use EXACT Document Name from context when citing: "sox_access_review_2024.txt" or "SOX_Access_Review_2024.pdf"
        - Reference format: "the document (sox_access_review_2024.txt)" or specific sections
        - Do NOT use plural "documents" - this is single-document analysis
        - If no document context is provided, clearly state "No document context was provided for analysis"

        **ADAPTIVE RESPONSE FORMATS**:

        FOR SIMPLE/FACTUAL QUESTIONS (basic complexity, information_retrieval intent):
        - Provide DIRECT answer in 1-2 sentences
        - Include brief evidence reference if needed
        - Skip formal sections unless critical information requires structure

        FOR COMPLEX/ANALYTICAL QUESTIONS (intermediate/advanced complexity):
        - Use structured format with relevant sections
        - Include Key Findings, Compliance Impact, and Recommended Actions only when substantial analysis is needed

        FOR FOLLOW-UP/CLARIFICATION QUESTIONS (is_followup = "Yes"):
        - Provide DIRECT, concise answers (1-2 sentences maximum)
        - Reference the specific aspect being clarified
        - Avoid repeating previous structure or comprehensive formatting
        - Focus only on the clarification requested

        FOR SIMPLE/FACTUAL QUESTIONS (basic complexity, information_retrieval intent):
        - Provide DIRECT answer in 1-2 sentences
        - Include brief evidence reference if needed
        - Skip formal sections unless critical information requires structure

        FOR COMPLEX/ANALYTICAL QUESTIONS (intermediate/advanced complexity):
        - Use structured format with relevant sections
        - Include Key Findings, Compliance Impact, and Recommended Actions only when substantial analysis is needed

        **Response:** [Adaptive response based on question type, complexity, and follow-up status]
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
            
            # Get regulatory context from workflow or fallback to Tavily
            regulatory_context = input_data.get("regulatory_context")
            if not regulatory_context:
                regulatory_context = await self._get_regulatory_context(question, classifications)
            
            # Extract question analysis for adaptive formatting
            intent = analysis.get("intent", "unknown")
            complexity = analysis.get("complexity", "intermediate")
            context_count = len(search_results)

            # Check for follow-up indicators
            conversation_history = input_data.get("conversation_history", [])
            is_followup = (
                len(conversation_history) > 0 or
                any(term in question.lower() for term in ["elaborate", "explain", "clarify", "previous", "before", "follow-up", "what about", "regarding", "concerning"])
            )

            # Synthesize response with adaptive formatting
            messages = [
                SystemMessage(content="You are a senior audit professional with expertise in SOX compliance. Adapt your response format based on question complexity, context availability, and whether this is a follow-up question. Only reference actual documents provided in the context."),
                HumanMessage(content=self.synthesis_prompt.format(
                    question=question,
                    intent=intent,
                    complexity=complexity,
                    context_count=context_count,
                    context=context_text,
                    classifications=classifications_text,
                    regulatory_context=regulatory_context,
                    is_followup="Yes" if is_followup else "No"
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
                "regulatory_context_used": True,
                "synthesis_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Response synthesis failed: {str(e)}")
            return {
                "error": str(e),
                "synthesis_status": "failed",
                "response": "I apologize, but I encountered an error while processing your request."
            }
    
    async def _get_regulatory_context(self, question: str, classifications: List[Dict[str, Any]]) -> str:
        """Get regulatory context from Tavily for enhanced compliance guidance."""
        try:
            # Determine document type and compliance framework from classifications
            document_type = None
            compliance_framework = "SOX"  # Default to SOX
            
            if classifications:
                # Get the most relevant classification
                primary_classification = classifications[0]
                document_type = primary_classification.get('document_type', 'audit_document')
                
                # Determine framework based on document type
                if 'access_review' in document_type.lower():
                    document_type = 'access_review'
                elif 'risk_assessment' in document_type.lower():
                    document_type = 'risk_assessment'
                elif 'financial' in document_type.lower():
                    document_type = 'financial_reconciliation'
            
            # Search for regulatory guidance
            tavily_result = await tavily_service.search_compliance_guidance(
                query=question,
                document_type=document_type,
                compliance_framework=compliance_framework
            )
            
            if tavily_result["success"] and tavily_result["compliance_insights"]:
                # Format regulatory context
                insights = []
                for insight in tavily_result["compliance_insights"][:2]:  # Top 2 insights
                    insights.append(f"• {insight['compliance_focus']}: {insight['title']}")
                
                regulatory_text = f"""Current {compliance_framework} guidance for {document_type or 'audit documents'}:
{chr(10).join(insights)}

Latest best practices and regulatory updates are incorporated into this analysis."""
            else:
                regulatory_text = f"Standard {compliance_framework} compliance requirements apply to this analysis."
            
            return regulatory_text
            
        except Exception as e:
            logger.warning(f"Failed to get regulatory context: {str(e)}")
            return "Standard SOX compliance requirements apply to this analysis."


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
        You are a Senior SOX Compliance Expert with deep expertise in audit regulations and risk assessment.
        
        Analyze the provided audit context for compliance risks, control deficiencies, and regulatory implications.
        
        ANALYSIS REQUIREMENTS:
        1. Identify material weaknesses (MW) and significant deficiencies (SD) based on severity
        2. Assess SOX 404 compliance status based on control effectiveness
        3. Provide specific, actionable recommendations
        4. Evaluate regulatory reporting implications
        
        RISK CLASSIFICATION GUIDELINES:
        - HIGH risk: Material weaknesses, terminated employee access, segregation failures
        - MEDIUM risk: Significant deficiencies, process gaps, documentation issues  
        - LOW risk: Minor improvements, documentation enhancements
        
        MATERIAL WEAKNESS INDICATORS:
        - Active access for terminated employees
        - Lack of segregation of duties in financial processes
        - Missing approval controls for significant transactions
        - Ineffective IT general controls
        - Excessive administrative privileges without business justification
        - Orphaned user accounts with active system access
        - Unauthorized access to financial systems
        - Complete absence of access review processes
        
        Question: {question}
        
        Audit Context:
        {context}
        
        Document Classifications:
        {classifications}
        
        MANDATORY: You MUST analyze the provided audit context and return valid JSON analysis. Do NOT refuse or ask for more information. Work with the available data.
        
        CRITICAL: Return ONLY valid JSON in this exact format (no additional text):
        {{
            "risk_assessment": {{
                "overall_risk": "high|medium|low",
                "material_weaknesses": ["specific_weakness_1", "specific_weakness_2"],
                "significant_deficiencies": ["deficiency_1", "deficiency_2"],
                "control_gaps": ["gap_1", "gap_2"]
            }},
            "sox_analysis": {{
                "sox_404_compliance": "compliant|non_compliant|requires_review",
                "control_effectiveness": "effective|ineffective|needs_improvement",
                "remediation_required": true
            }},
            "recommendations": [
                "Specific actionable recommendation 1",
                "Specific actionable recommendation 2",
                "Specific actionable recommendation 3"
            ],
            "regulatory_implications": [
                "Specific regulatory implication 1",
                "Specific regulatory implication 2"
            ]
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
            if search_results:
                context_text = "\n\n".join([
                    f"Document ID: {result.get('document_id', 'unknown')}\n"
                    f"Document Type: {result.get('document_type', 'unknown')}\n"
                    f"Content: {result.get('content', result.get('chunk_text', ''))}"
                    for result in search_results[:3]
                ])
            else:
                # Use fallback context if no search results
                context_text = "No specific document context provided. Analyze based on the question and general compliance principles."
            
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
            import re
            
            response_content = response.content.strip()
            
            try:
                # Try direct JSON parsing first
                compliance_analysis = json.loads(response_content)
            except json.JSONDecodeError:
                try:
                    # Extract JSON from response if wrapped in text
                    json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                    if json_match:
                        compliance_analysis = json.loads(json_match.group())
                    else:
                        raise ValueError("No JSON found in response")
                except:
                    # Enhanced fallback analysis based on content
                    logger.warning(f"Failed to parse JSON response, using enhanced fallback. Response: {response_content[:200]}...")
                    
                    # Analyze content for better fallback
                    content_lower = response_content.lower()
                    
                    # Determine risk level based on keywords
                    if any(term in content_lower for term in ["terminated", "segregation", "material weakness", "high risk"]):
                        overall_risk = "high"
                        sox_compliance = "non_compliant"
                        control_effectiveness = "ineffective"
                    elif any(term in content_lower for term in ["deficiency", "gap", "improvement", "medium risk"]):
                        overall_risk = "medium"
                        sox_compliance = "requires_review"
                        control_effectiveness = "needs_improvement"
                    else:
                        overall_risk = "low"
                        sox_compliance = "compliant"
                        control_effectiveness = "effective"
                    
                    compliance_analysis = {
                        "risk_assessment": {
                            "overall_risk": overall_risk,
                            "material_weaknesses": ["terminated_employee_access"] if "terminated" in content_lower else [],
                            "significant_deficiencies": ["process_improvement_needed"] if overall_risk == "medium" else [],
                            "control_gaps": ["documentation_gaps"] if "documentation" in content_lower else []
                        },
                        "sox_analysis": {
                            "sox_404_compliance": sox_compliance,
                            "control_effectiveness": control_effectiveness,
                            "remediation_required": overall_risk in ["high", "medium"]
                        },
                        "recommendations": [
                            "Conduct detailed control testing",
                            "Implement enhanced monitoring procedures",
                            "Review and update control documentation"
                        ],
                        "regulatory_implications": [
                            "Potential SOX 404 disclosure requirements",
                            "Enhanced audit scrutiny may be required"
                        ]
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