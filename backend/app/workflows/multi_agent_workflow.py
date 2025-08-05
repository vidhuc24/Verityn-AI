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
    SYNTHESIZE_RESPONSE = "synthesize_response"
    COMPLETE = "complete"


class MultiAgentWorkflow:
    """Multi-agent workflow orchestrator for audit document analysis."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the multi-agent workflow."""
        self.verbose = verbose
        
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
        workflow.add_node("synthesize_response", self._synthesize_response)
        workflow.add_node("complete", self._complete_workflow)
        
        # Define edges - simple linear flow
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "analyze_question")
        workflow.add_edge("analyze_question", "retrieve_context")
        workflow.add_edge("retrieve_context", "classify_documents")
        workflow.add_edge("classify_documents", "analyze_compliance")
        workflow.add_edge("analyze_compliance", "synthesize_response")
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
        """Classify retrieved documents."""
        try:
            context_results = state.get("context_retrieval", {})
            search_results = context_results.get("search_results", [])
            
            # Classify each document
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
            
            # Only update document_classifications field
            return {
                **state,
                "document_classifications": classifications,
                "agent_results": {**state.get("agent_results", {}), "classifier": {
                    "classifications": classifications,
                    "count": len(classifications)
                }}
            }
            
        except Exception as e:
            error_msg = f"Document classification failed: {str(e)}"
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "status": "failed"
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
    
    async def _synthesize_response(self, state: WorkflowState) -> WorkflowState:
        """Synthesize the final response."""
        try:
            question = state["question"]
            analysis = state.get("question_analysis", {})
            context_results = state.get("context_retrieval", {})
            classifications = state.get("document_classifications", [])
            
            search_results = context_results.get("search_results", [])
            
            # Execute response synthesis
            result = await self.response_synthesizer.execute({
                "question": question,
                "analysis": analysis.get("analysis", {}),
                "context": search_results,
                "classifications": classifications
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

    async def execute(
        self,
        question: str,
        conversation_id: Optional[str] = None,
        document_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the multi-agent workflow with LangSmith monitoring.
        
        Args:
            question: User question to analyze
            conversation_id: Optional conversation ID for context
            document_id: Optional specific document ID to focus on
            config: Optional configuration overrides
            
        Returns:
            Dictionary containing workflow results and metadata
        """
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
                    "agent_execution_times": self._extract_agent_timings(final_state),
                    "token_usage": self._extract_total_token_usage(final_state),
                    "agents_executed": list(final_state.keys()),
                    "timestamp": datetime.now().isoformat(),
                    "langsmith_trace_id": workflow_run_id,
                    "performance_summary": {
                        "total_duration": execution_time,
                        "agent_count": len([k for k in final_state.keys() if k.endswith("_status")]),
                        "success_rate": self._calculate_success_rate(final_state),
                        "average_agent_time": self._calculate_average_agent_time(final_state)
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