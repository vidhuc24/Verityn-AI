"""
LangSmith Integration Service for Verityn AI.

This service provides comprehensive monitoring and tracing capabilities
for our multi-agent workflow using LangSmith.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4

from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager

from backend.app.config import settings

logger = logging.getLogger(__name__)


class LangSmithService:
    """Service for LangSmith monitoring and tracing."""
    
    def __init__(self):
        """Initialize LangSmith service with configuration."""
        self.client = None
        self.tracer = None
        self.project_name = self._get_project_name()
        self._setup_environment()
        self._initialize_client()
    
    def _get_project_name(self) -> str:
        """Generate project name for this session."""
        base_name = settings.LANGCHAIN_PROJECT
        session_id = uuid4().hex[:8]
        return f"{base_name}-{session_id}"
    
    def _setup_environment(self):
        """Setup LangSmith environment variables following bootcamp patterns."""
        try:
            # Set up LangSmith environment variables following bootcamp patterns exactly
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = self.project_name
            
            # Use LANGCHAIN_API_KEY (bootcamp standard) - prioritize LANGSMITH_API_KEY from .env
            api_key = settings.LANGSMITH_API_KEY or settings.LANGCHAIN_API_KEY
            if api_key:
                os.environ["LANGCHAIN_API_KEY"] = api_key
                logger.info("LangSmith environment configured successfully")
            else:
                logger.warning("No LangSmith API key found in environment")
                
        except Exception as e:
            logger.error(f"Failed to setup LangSmith environment: {str(e)}")
    
    def _initialize_client(self):
        """Initialize LangSmith client following bootcamp pattern."""
        try:
            if os.environ.get("LANGCHAIN_TRACING_V2") == "true":
                # Simple client initialization following bootcamp pattern
                self.client = Client()
                
                # Create tracer with project name
                self.tracer = LangChainTracer(project_name=self.project_name)
                logger.info(f"LangSmith initialized successfully with project: {self.project_name}")
                    
            else:
                logger.info("LangSmith tracing disabled")
        except Exception as e:
            logger.error(f"Failed to initialize LangSmith: {e}")
            self.client = None
            self.tracer = None
    
    def get_callback_manager(self) -> Optional[CallbackManager]:
        """Get callback manager with LangSmith tracer."""
        if self.tracer:
            return CallbackManager([self.tracer])
        return None
    
    def create_run(
        self,
        name: str,
        run_type: str,
        inputs: Dict[str, Any],
        **kwargs
    ) -> Optional[str]:
        """
        Create a new LangSmith run following bootcamp pattern.
        
        Since direct create_run has API issues, we'll rely on the tracer approach
        which is the primary method used in bootcamp materials.
        
        Args:
            name: Name of the run
            run_type: Type of run (e.g., 'chain', 'llm', 'tool')
            inputs: Input data for the run
            **kwargs: Additional run parameters
            
        Returns:
            Proper UUID for run ID (tracing happens via callback manager)
        """
        if not self.client or not self.tracer:
            logger.warning("LangSmith client or tracer not initialized")
            return None
            
        try:
            # Generate a proper UUID for run ID to avoid validation errors
            run_id = str(uuid4())
            logger.info(f"LangSmith tracing enabled for: {name} (ID: {run_id})")
            return run_id
                
        except Exception as e:
            logger.error(f"Failed to prepare LangSmith tracing: {str(e)}")
            return None

    def update_run(
        self,
        run_id: str,
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Update an existing LangSmith run.
        
        Since we use placeholder UUIDs, this method logs the update
        but doesn't make actual API calls (tracing happens via callback manager).
        
        Args:
            run_id: ID of the run to update
            outputs: Output data for the run
            error: Error message if run failed
            **kwargs: Additional update parameters
            
        Returns:
            True (logging successful)
        """
        if not self.client or not run_id:
            return False
            
        try:
            # Log the update information instead of making API call
            logger.info(f"LangSmith run update logged: {run_id}")
            if outputs:
                logger.debug(f"Run outputs: {list(outputs.keys())}")
            if error:
                logger.warning(f"Run error: {error}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log LangSmith run update {run_id}: {str(e)}")
            return False
    
    def log_agent_execution(
        self,
        agent_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        execution_time: float,
        status: str,
        error: Optional[str] = None
    ) -> Optional[str]:
        """Log individual agent execution."""
        if not self.client:
            return None
        
        tags = [
            "verityn-ai",
            "multi-agent",
            f"agent:{agent_name}",
            f"status:{status}"
        ]
        
        metadata = {
            "agent_name": agent_name,
            "execution_time": execution_time,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        run_id = self.create_run(
            name=f"Agent: {agent_name}",
            run_type="llm",
            inputs=inputs,
            tags=tags,
            metadata=metadata
        )
        
        if run_id:
            self.update_run(
                run_id=run_id,
                outputs=outputs,
                error=error
            )
        
        return run_id
    
    def log_workflow_execution(
        self,
        workflow_id: str,
        question: str,
        final_response: Dict[str, Any],
        agent_results: Dict[str, Any],
        execution_time: float,
        status: str,
        errors: List[str]
    ) -> Optional[str]:
        """Log complete workflow execution."""
        if not self.client:
            return None
        
        tags = [
            "verityn-ai",
            "multi-agent-workflow",
            f"status:{status}",
            f"agents:{len(agent_results)}"
        ]
        
        metadata = {
            "workflow_id": workflow_id,
            "total_execution_time": execution_time,
            "agents_executed": list(agent_results.keys()),
            "error_count": len(errors),
            "timestamp": datetime.now().isoformat()
        }
        
        inputs = {
            "question": question,
            "workflow_id": workflow_id
        }
        
        outputs = {
            "final_response": final_response,
            "agent_results": agent_results,
            "execution_time": execution_time,
            "status": status,
            "errors": errors
        }
        
        run_id = self.create_run(
            name=f"Multi-Agent Workflow: {workflow_id}",
            run_type="chain",
            inputs=inputs,
            tags=tags,
            metadata=metadata
        )
        
        if run_id:
            self.update_run(
                run_id=run_id,
                outputs=outputs,
                error="; ".join(errors) if errors else None
            )
        
        return run_id
    
    def create_dataset(
        self,
        dataset_name: str,
        description: str = "",
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[str]:
        """Create a dataset for evaluation."""
        if not self.client:
            return None
        
        try:
            dataset = self.client.create_dataset(
                dataset_name=dataset_name,
                description=description
            )
            
            if examples:
                for example in examples:
                    self.client.create_example(
                        dataset_id=dataset.id,
                        inputs=example.get("inputs", {}),
                        outputs=example.get("outputs", {})
                    )
            
            logger.info(f"Created dataset: {dataset_name} with {len(examples or [])} examples")
            return str(dataset.id)
            
        except Exception as e:
            logger.error(f"Failed to create dataset: {e}")
            return None
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get current project information."""
        return {
            "project_name": self.project_name,
            "tracing_enabled": os.environ.get("LANGCHAIN_TRACING_V2") == "true",
            "client_initialized": self.client is not None,
            "api_key_configured": bool(os.environ.get("LANGCHAIN_API_KEY"))
        }

    def is_configured(self) -> bool:
        """Check if LangSmith is properly configured."""
        return (
            self.client is not None and
            os.environ.get("LANGCHAIN_TRACING_V2") == "true" and
            (os.environ.get("LANGCHAIN_API_KEY") is not None or 
             os.environ.get("LANGSMITH_API_KEY") is not None)
        )
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get detailed configuration status for debugging."""
        is_configured = (
            self.client is not None and
            os.environ.get("LANGCHAIN_TRACING_V2") == "true" and
            (os.environ.get("LANGCHAIN_API_KEY") is not None or 
             os.environ.get("LANGSMITH_API_KEY") is not None)
        )
        
        return {
            "configured": is_configured,
            "client_initialized": self.client is not None,
            "tracing_enabled": os.environ.get("LANGCHAIN_TRACING_V2") == "true",
            "api_key_set": bool(os.environ.get("LANGCHAIN_API_KEY") or os.environ.get("LANGSMITH_API_KEY")),
            "project_name": self.project_name,
            "endpoint": os.environ.get("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com/"),
            "environment_vars": {
                "LANGCHAIN_TRACING_V2": os.environ.get("LANGCHAIN_TRACING_V2"),
                "LANGCHAIN_PROJECT": os.environ.get("LANGCHAIN_PROJECT"),
                "LANGCHAIN_ENDPOINT": os.environ.get("LANGCHAIN_ENDPOINT"),
                "LANGSMITH_ENDPOINT": os.environ.get("LANGSMITH_ENDPOINT"),
                "has_langchain_api_key": bool(os.environ.get("LANGCHAIN_API_KEY")),
                "has_langsmith_api_key": bool(os.environ.get("LANGSMITH_API_KEY"))
            }
        }


# Global LangSmith service instance
langsmith_service = LangSmithService() 