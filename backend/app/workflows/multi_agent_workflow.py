"""
Multi-Agent Workflow Orchestrator for Verityn AI.

This module implements the LangGraph workflow that orchestrates multiple
specialized agents for comprehensive audit document analysis.
"""

from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
import logging
import asyncio
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain.schema import BaseMessage

from backend.app.agents.base_agent import AgentType, AgentContext, AgentMessage
from backend.app.agents.specialized_agents import (
    DocumentProcessingAgent,
    ClassificationAgent,
    QuestionAnalysisAgent,
    ContextRetrievalAgent,
    ResponseSynthesisAgent,
    ComplianceAnalyzerAgent
)
from backend.app.services.langsmith_service import langsmith_service
from backend.app.services.tavily_service import tavily_service

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State definition for the multi-agent workflow."""
    # Input data
    question: str
    conversation_id: Optional[str]
    document_id: Optional[str]
    
    # Agent results
    question_analysis: Optional[Dict[str, Any]]
    context_retrieval: Optional[Dict[str, Any]]
    document_classifications: Optional[List[Dict[str, Any]]]
    compliance_analysis: Optional[Dict[str, Any]]
    regulatory_context: Optional[Dict[str, Any]]
    final_response: Optional[Dict[str, Any]]
    
    # Workflow metadata
    workflow_id: str
    start_time: str
    current_step: str
    agent_results: Dict[str, Any]
    errors: List[str]
    status: str


class WorkflowStep(str, Enum):
    """Workflow execution steps."""
    INITIALIZE = "initialize"
    ANALYZE_QUESTION = "analyze_question"
    RETRIEVE_CONTEXT = "retrieve_context"
    CLASSIFY_DOCUMENTS = "classify_documents"
    ANALYZE_COMPLIANCE = "analyze_compliance"
    REGULATORY_SEARCH = "regulatory_search"
    SYNTHESIZE_RESPONSE = "synthesize_response"
    COMPLETE = "complete"


class MultiAgentWorkflow:
    """Multi-agent workflow orchestrator for audit document analysis."""
    
    def __init__(self, verbose: bool = False, single_document_mode: bool = True):
        """Initialize the multi-agent workflow."""
        self.verbose = verbose
        self.single_document_mode = single_document_mode  # New flag for single document focus
        
        # Initialize agents
        self.question_analyzer = QuestionAnalysisAgent(verbose=verbose)
        self.context_retriever = ContextRetrievalAgent(verbose=verbose)
        self.classifier = ClassificationAgent(verbose=verbose)
        self.compliance_analyzer = ComplianceAnalyzerAgent(verbose=verbose)
        self.response_synthesizer = ResponseSynthesisAgent(verbose=verbose)
        
        # Initialize memory first
        self.memory = MemorySaver()
        
        # Initialize workflow graph
        self.workflow = self._create_workflow_graph()
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_workflow)
        workflow.add_node("analyze_question", self._analyze_question)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("classify_documents", self._classify_documents)
        workflow.add_node("analyze_compliance", self._analyze_compliance)
        workflow.add_node("regulatory_search", self._regulatory_search)
        workflow.add_node("synthesize_response", self._synthesize_response)
        workflow.add_node("complete", self._complete_workflow)
        
        # Define edges - simple linear flow
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "analyze_question")
        workflow.add_edge("analyze_question", "retrieve_context")
        workflow.add_edge("retrieve_context", "classify_documents")
        workflow.add_edge("classify_documents", "analyze_compliance")
        workflow.add_edge("analyze_compliance", "regulatory_search")
        workflow.add_edge("regulatory_search", "synthesize_response")
        workflow.add_edge("synthesize_response", "complete")
        workflow.add_edge("complete", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    async def _initialize_workflow(self, state: WorkflowState) -> WorkflowState:
        """Initialize the workflow state."""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        state.update({
            "workflow_id": workflow_id,
            "start_time": datetime.now().isoformat(),
            "current_step": WorkflowStep.INITIALIZE.value,
            "agent_results": {},
            "errors": [],
            "status": "running"
        })
        
        if self.verbose:
            logger.info(f"Initialized workflow {workflow_id}")
        
        return state
    
    async def _analyze_question(self, state: WorkflowState) -> WorkflowState:
        """Analyze the user question."""
        try:
            question = state["question"]
            conversation_id = state.get("conversation_id")
            
            # Execute question analysis
            result = await self.question_analyzer.execute({
                "question": question,
                "conversation_id": conversation_id
            })
            
            # Only update question_analysis field
            return {
                **state,
                "question_analysis": result,
                "agent_results": {**state.get("agent_results", {}), "question_analyzer": result}
            }
            
        except Exception as e:
            error_msg = f"Question analysis failed: {str(e)}"
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "status": "failed"
            }
    
    async def _retrieve_context(self, state: WorkflowState) -> WorkflowState:
        """Retrieve relevant context from vector database."""
        try:
            question = state["question"]
            analysis = state.get("question_analysis", {})
            
            # Execute context retrieval
            result = await self.context_retriever.execute({
                "question": question,
                "analysis": analysis.get("analysis", {})
            })
            
            # Only update context_retrieval field
            return {
                **state,
                "context_retrieval": result,
                "agent_results": {**state.get("agent_results", {}), "context_retriever": result}
            }
            
        except Exception as e:
            error_msg = f"Context retrieval failed: {str(e)}"
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "status": "failed"
            }
    
    async def _classify_documents(self, state: WorkflowState) -> WorkflowState:
        """Classify documents with single document focus + multi-document fallback."""
        try:
            context_results = state.get("context_retrieval", {})
            search_results = context_results.get("search_results", [])
            
            if not search_results:
                if self.verbose:
                    logger.warning("No search results found for classification")
                return {
                    **state,
                    "document_classifications": [],
                    "primary_document": None,
                    "agent_results": {**state.get("agent_results", {}), "classifier": {
                        "classifications": [],
                        "count": 0,
                        "focus": "no_documents",
                        "mode": "single_document" if self.single_document_mode else "multi_document"
                    }}
                }
            
            # Single document focus (primary path) - optimized for performance
            if self.single_document_mode or len(search_results) == 1:
                if self.verbose:
                    logger.info(f"Processing in single document mode. Found {len(search_results)} results, focusing on primary result.")
                
                # Get the most relevant result (highest similarity score)
                primary_result = search_results[0]  # Already sorted by relevance
                content = primary_result.get("chunk_text", "")
                document_id = primary_result.get("document_id", "")
                
                # Single classification call - much faster than loop
                classification_result = await self.classifier.execute({
                    "content": content,
                    "document_id": document_id
                })
                
                if classification_result.get("classification_status") == "completed":
                    classification = classification_result.get("classification", {})
                    
                    if self.verbose:
                        logger.info(f"Successfully classified primary document {document_id}")
                    
                    # Store as single classification with primary document focus
                    return {
                        **state,
                        "document_classifications": [classification],  # Keep as list for compatibility
                        "primary_document": {
                            "id": document_id,
                            "classification": classification,
                            "content_preview": content[:200] + "..." if len(content) > 200 else content,
                            "processing_mode": "single_document_focus"
                        },
                        "agent_results": {**state.get("agent_results", {}), "classifier": {
                            "classification": classification,
                            "document_count": 1,
                            "focus": "single_document",
                            "mode": "single_document",
                            "performance_optimized": True
                        }}
                    }
                else:
                    # Handle classification failure
                    error_msg = f"Primary document classification failed for {document_id}"
                    if self.verbose:
                        logger.error(error_msg)
                    return {
                        **state,
                        "document_classifications": [],
                        "primary_document": None,
                        "errors": state.get("errors", []) + [error_msg],
                        "agent_results": {**state.get("agent_results", {}), "classifier": {
                            "error": error_msg,
                            "focus": "single_document",
                            "mode": "single_document"
                        }}
                    }
            
            # Multi-document fallback (compatibility path) - for future integration
            else:
                if self.verbose:
                    logger.info(f"Processing in multi-document mode. Found {len(search_results)} results.")
                
                # Fallback to original multi-document logic for compatibility
                classifications = []
                for result in search_results:
                    content = result.get("chunk_text", "")
                    document_id = result.get("document_id", "")
                    
                    classification_result = await self.classifier.execute({
                        "content": content,
                        "document_id": document_id
                    })
                    
                    if classification_result.get("classification_status") == "completed":
                        classifications.append(classification_result.get("classification", {}))
                
                if self.verbose:
                    logger.info(f"Successfully classified {len(classifications)} documents")
                
                # Return multi-document results for compatibility
                return {
                    **state,
                    "document_classifications": classifications,
                    "primary_document": None,  # No primary focus in multi-document mode
                    "agent_results": {**state.get("agent_results", {}), "classifier": {
                        "classifications": classifications,
                        "count": len(classifications),
                        "focus": "multi_document",
                        "mode": "multi_document",
                        "performance_optimized": False
                    }}
                }
            
        except Exception as e:
            error_msg = f"Document classification failed: {str(e)}"
            logger.error(error_msg)
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "status": "failed",
                "agent_results": {**state.get("agent_results", {}), "classifier": {
                    "error": error_msg,
                    "focus": "unknown",
                    "mode": "single_document" if self.single_document_mode else "multi_document"
                }}
            }
    
    async def _analyze_compliance(self, state: WorkflowState) -> WorkflowState:
        """Perform deep compliance analysis."""
        try:
            question = state["question"]
            context_results = state.get("context_retrieval", {})
            classifications = state.get("document_classifications", [])
            
            search_results = context_results.get("search_results", [])
            
            # Execute compliance analysis
            result = await self.compliance_analyzer.execute({
                "question": question,
                "context": search_results,
                "classifications": classifications
            })
            
            # Only update compliance_analysis field
            return {
                **state,
                "compliance_analysis": result,
                "agent_results": {**state.get("agent_results", {}), "compliance_analyzer": result}
            }
            
        except Exception as e:
            error_msg = f"Compliance analysis failed: {str(e)}"
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "status": "failed"
            }
    
    async def _regulatory_search(self, state: WorkflowState) -> WorkflowState:
        """Perform regulatory search using Tavily for enhanced compliance guidance."""
        try:
            question = state["question"]
            classifications = state.get("document_classifications", [])
            
            # Determine document type and compliance framework
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
            
            # Search for regulatory guidance using Tavily
            regulatory_result = await tavily_service.search_compliance_guidance(
                query=question,
                document_type=document_type,
                compliance_framework=compliance_framework
            )
            
            # Update state with regulatory context
            return {
                **state,
                "regulatory_context": regulatory_result,
                "agent_results": {**state.get("agent_results", {}), "regulatory_search": regulatory_result}
            }
            
        except Exception as e:
            error_msg = f"Regulatory search failed: {str(e)}"
            logger.warning(f"Regulatory search failed, continuing with default context: {str(e)}")
            
            # Continue with default regulatory context
            return {
                **state,
                "regulatory_context": {
                    "success": False,
                    "error": str(e),
                    "compliance_insights": [],
                    "fallback_message": "Standard SOX compliance requirements apply to this analysis."
                },
                "agent_results": {**state.get("agent_results", {}), "regulatory_search": {
                    "status": "failed",
                    "error": str(e)
                }}
            }
    
    async def _synthesize_response(self, state: WorkflowState) -> WorkflowState:
        """Synthesize the final response."""
        try:
            question = state["question"]
            analysis = state.get("question_analysis", {})
            context_results = state.get("context_retrieval", {})
            classifications = state.get("document_classifications", [])
            
            search_results = context_results.get("search_results", [])
            
            # Get regulatory context from workflow state
            regulatory_context = state.get("regulatory_context", {})
            
            # Execute response synthesis with regulatory context
            result = await self.response_synthesizer.execute({
                "question": question,
                "analysis": analysis.get("analysis", {}),
                "context": search_results,
                "classifications": classifications,
                "regulatory_context": regulatory_context
            })
            
            # Only update final_response field
            return {
                **state,
                "final_response": result,
                "agent_results": {**state.get("agent_results", {}), "response_synthesizer": result}
            }
            
        except Exception as e:
            error_msg = f"Response synthesis failed: {str(e)}"
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "status": "failed"
            }
    
    async def _complete_workflow(self, state: WorkflowState) -> WorkflowState:
        """Complete the workflow and prepare final result."""
        state["current_step"] = WorkflowStep.COMPLETE.value
        
        # Determine final status
        if state["errors"]:
            state["status"] = "failed"
        else:
            state["status"] = "completed"
        
        # Add completion metadata
        state["end_time"] = datetime.now().isoformat()
        state["total_duration"] = (
            datetime.fromisoformat(state["end_time"]) - 
            datetime.fromisoformat(state["start_time"])
        ).total_seconds()
        
        if self.verbose:
            logger.info(f"Workflow {state['workflow_id']} completed with status: {state['status']}")
        
        return state
    
    def _should_continue(self, state: WorkflowState) -> str:
        """Determine if workflow should continue or handle errors."""
        current_step = state.get("current_step", "")
        
        # Check if current step has errors
        if state.get("errors"):
            return "error"
        
        # Check if current step completed successfully
        agent_results = state.get("agent_results", {})
        
        if current_step == WorkflowStep.ANALYZE_QUESTION.value:
            result = agent_results.get("question_analyzer", {})
            return "continue" if result.get("analysis_status") == "completed" else "error"
        
        elif current_step == WorkflowStep.RETRIEVE_CONTEXT.value:
            result = agent_results.get("context_retriever", {})
            return "continue" if result.get("retrieval_status") == "completed" else "error"
        
        elif current_step == WorkflowStep.CLASSIFY_DOCUMENTS.value:
            result = agent_results.get("classifier", {})
            return "continue" if result.get("count", 0) > 0 else "error"
        
        elif current_step == WorkflowStep.ANALYZE_COMPLIANCE.value:
            result = agent_results.get("compliance_analyzer", {})
            return "continue" if result.get("analysis_status") == "completed" else "error"
        
        elif current_step == WorkflowStep.REGULATORY_SEARCH.value:
            result = agent_results.get("regulatory_search", {})
            return "continue" if result.get("success", False) or result.get("fallback_message") else "error"
        
        elif current_step == WorkflowStep.SYNTHESIZE_RESPONSE.value:
            result = agent_results.get("response_synthesizer", {})
            return "continue" if result.get("synthesis_status") == "completed" else "error"
        
        return "continue"
    
    def _extract_agent_timings(self, final_state: Dict[str, Any]) -> Dict[str, float]:
        """Extract execution times for each agent."""
        timings = {}
        for key, value in final_state.items():
            if isinstance(value, dict) and "execution_time" in value:
                agent_name = value.get("agent_type", key)
                timings[agent_name] = value["execution_time"]
        return timings
    
    def _extract_total_token_usage(self, final_state: Dict[str, Any]) -> Dict[str, int]:
        """Extract and sum token usage across all agents."""
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        for key, value in final_state.items():
            if isinstance(value, dict) and "token_usage" in value and value["token_usage"]:
                usage = value["token_usage"]
                total_tokens["prompt_tokens"] += usage.get("prompt_tokens", 0)
                total_tokens["completion_tokens"] += usage.get("completion_tokens", 0)
                total_tokens["total_tokens"] += usage.get("total_tokens", 0)
        
        return total_tokens if total_tokens["total_tokens"] > 0 else None
    
    def _calculate_success_rate(self, final_state: Dict[str, Any]) -> float:
        """Calculate the success rate of agent executions."""
        total_agents = 0
        successful_agents = 0
        
        for key, value in final_state.items():
            if isinstance(value, dict) and "status" in value:
                total_agents += 1
                if value["status"] == "completed":
                    successful_agents += 1
        
        return successful_agents / total_agents if total_agents > 0 else 0.0
    
    def _calculate_average_agent_time(self, final_state: Dict[str, Any]) -> float:
        """Calculate average execution time across agents."""
        timings = self._extract_agent_timings(final_state)
        return sum(timings.values()) / len(timings) if timings else 0.0

    def set_single_document_mode(self, enabled: bool):
        """Dynamically switch between single and multi-document modes."""
        self.single_document_mode = enabled
        if self.verbose:
            mode = "single document" if enabled else "multi-document"
            logger.info(f"Switched to {mode} mode")
    
    def get_processing_mode(self) -> str:
        """Get the current processing mode."""
        return "single_document" if self.single_document_mode else "multi_document"

    async def execute(
        self,
        question: str,
        conversation_id: Optional[str] = None,
        document_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        single_document_mode: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Execute the multi-agent workflow with LangSmith monitoring.
        
        Args:
            question: User question to analyze
            conversation_id: Optional conversation ID for context
            document_id: Optional specific document ID to focus on
            config: Optional configuration overrides
            single_document_mode: Optional override for single document mode
            
        Returns:
            Dictionary containing workflow results and metadata
        """
        # Apply single document mode override if provided
        if single_document_mode is not None:
            self.single_document_mode = single_document_mode
            if self.verbose:
                mode = "single document" if single_document_mode else "multi-document"
                logger.info(f"Overriding processing mode to {mode} for this execution")
        
        workflow_start_time = datetime.now()
        
        # Initialize state
        initial_state = WorkflowState(
            question=question,
            conversation_id=conversation_id,
            document_id=document_id,
            question_analysis=None,
            context_retrieval=None,
            document_classifications=None,
            compliance_analysis=None,
            final_response=None,
            workflow_id="",
            start_time="",
            current_step="",
            agent_results={},
            errors=[],
            status=""
        )
        
        # Prepare configuration with required checkpointer keys
        workflow_config = config or {}
        workflow_config.update({
            "configurable": {
                "thread_id": conversation_id or f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "checkpoint_ns": "verityn_workflow",
                "checkpoint_id": f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        })
        
        # Add LangSmith callback manager if available
        callback_manager = langsmith_service.get_callback_manager()
        if callback_manager:
            workflow_config["callbacks"] = callback_manager.handlers
        
        # Execute workflow with LangSmith tracing
        try:
            # Create LangSmith run for overall workflow
            workflow_run_id = langsmith_service.create_run(
                name=f"Verityn Multi-Agent Workflow",
                run_type="chain",
                inputs={
                    "question": question,
                    "conversation_id": conversation_id,
                    "document_id": document_id
                },
                tags=["verityn-ai", "multi-agent", "workflow"],
                metadata={
                    "workflow_type": "multi_agent_audit_analysis",
                    "timestamp": workflow_start_time.isoformat()
                }
            )
            
            final_state = await self.workflow.ainvoke(
                initial_state,
                config=workflow_config
            )
            
            # Calculate execution time
            execution_time = (datetime.now() - workflow_start_time).total_seconds()
            
            # Extract final response
            final_response = final_state.get("final_response", {})
            response_content = final_response.get("response", "")
            compliance_insights = final_response.get("compliance_insights", {})
            
            # Prepare final result with comprehensive metadata
            result = {
                "response": response_content,  # Use the extracted response_content instead of wrong field
                "status": final_state.get("status", "unknown"),
                "conversation_id": conversation_id,
                "workflow_id": final_state["workflow_id"],
                "metadata": {
                    "workflow_execution_time": execution_time,
                    "processing_mode": self.get_processing_mode(),
                    "single_document_optimized": self.single_document_mode,
                    "agent_execution_times": self._extract_agent_timings(final_state),
                    "token_usage": self._extract_total_token_usage(final_state),
                    "agents_executed": list(final_state.keys()),
                    "timestamp": datetime.now().isoformat(),
                    "langsmith_trace_id": workflow_run_id,
                    "performance_summary": {
                        "total_duration": execution_time,
                        "agent_count": len([k for k in final_state.keys() if k.endswith("_status")]),
                        "success_rate": self._calculate_success_rate(final_state),
                        "average_agent_time": self._calculate_average_agent_time(final_state),
                        "optimization_mode": "single_document_focus" if self.single_document_mode else "multi_document_compatibility"
                    }
                },
                "langsmith_run_id": workflow_run_id
            }
            
            # Add individual agent results to metadata
            result["metadata"]["agent_results"] = {
                k: v for k, v in final_state.items() 
                if isinstance(v, dict) and "agent_type" in str(v)
            }
            
            # Log complete workflow execution to LangSmith
            langsmith_service.log_workflow_execution(
                workflow_id=final_state["workflow_id"],
                question=question,
                final_response=final_response,
                agent_results=final_state.get("agent_results", {}),
                execution_time=execution_time,
                status=final_state["status"],
                errors=final_state.get("errors", [])
            )
            
            # Update LangSmith run with results
            if workflow_run_id:
                langsmith_service.update_run(
                    run_id=workflow_run_id,
                    outputs=result,
                    error="; ".join(final_state.get("errors", [])) if final_state.get("errors") else None
                )
            
            if self.verbose:
                logger.info(f"Workflow completed successfully in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - workflow_start_time).total_seconds()
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(error_msg)
            
            # Log error to LangSmith
            if workflow_run_id:
                langsmith_service.update_run(
                    run_id=workflow_run_id,
                    outputs={"error": error_msg, "execution_time": execution_time},
                    error=error_msg
                )
            
            return {
                "workflow_id": f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "failed",
                "response": "",
                "compliance_insights": {},
                "agent_results": {},
                "execution_time": execution_time,
                "errors": [error_msg],
                "metadata": {
                    "conversation_id": conversation_id,
                    "document_id": document_id,
                    "langsmith_run_id": workflow_run_id
                }
            }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific workflow."""
        try:
            # This would typically query the memory/checkpointer
            # For now, return basic status
            return {
                "workflow_id": workflow_id,
                "status": "unknown",
                "message": "Workflow status retrieval not implemented"
            }
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            return None
    
    def reset_workflow(self):
        """Reset the workflow state."""
        self.memory.clear()
        if self.verbose:
            logger.info("Workflow memory cleared") 