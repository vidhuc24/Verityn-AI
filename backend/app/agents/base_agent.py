"""
Base Agent for Verityn AI Multi-Agent System.

This module provides the foundation for all specialized agents in our
multi-agent workflow, following LangGraph best practices.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import time
import logging

from langchain_openai import ChatOpenAI
from backend.app.config import settings
from backend.app.services.langsmith_service import langsmith_service


class AgentType(str, Enum):
    """Types of agents in the system."""
    DOCUMENT_PROCESSOR = "document_processor"
    CLASSIFIER = "classifier"
    QUESTION_ANALYZER = "question_analyzer"
    CONTEXT_RETRIEVER = "context_retriever"
    WEB_RESEARCHER = "web_researcher"
    RESPONSE_SYNTHESIZER = "response_synthesizer"
    COMPLIANCE_ANALYZER = "compliance_analyzer"


@dataclass
class AgentContext:
    """Context object passed to agents during execution."""
    inputs: Dict[str, Any]
    agent_type: AgentType
    timestamp: datetime
    conversation_id: str
    workflow_id: str


class AgentMessage:
    """Standardized message format for agent communication."""
    
    def __init__(
        self,
        sender: AgentType,
        recipient: AgentType,
        content: Dict[str, Any],
        message_type: str = "data",
        priority: int = 1
    ):
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.message_type = message_type
        self.priority = priority
        self.timestamp = datetime.now().isoformat()
        self.message_id = f"{sender.value}_{recipient.value}_{self.timestamp}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender": self.sender.value,
            "recipient": self.recipient.value,
            "content": self.content,
            "message_type": self.message_type,
            "priority": self.priority,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary."""
        return cls(
            sender=AgentType(data["sender"]),
            recipient=AgentType(data["recipient"]),
            content=data["content"],
            message_type=data.get("message_type", "data"),
            priority=data.get("priority", 1)
        )


class BaseAgent:
    """Base class for all agents in the multi-agent system."""
    
    def __init__(
        self,
        agent_type: AgentType,
        llm_model: str = "gpt-3.5-turbo",
        temperature: float = 0.1,
        verbose: bool = False
    ):
        """Initialize the base agent."""
        self.agent_type = agent_type
        self.llm_model = llm_model
        self.temperature = temperature
        self.verbose = verbose
        self.execution_history: List[Dict[str, Any]] = []
        
        # Lazy initialization of LLM
        self._llm = None
        
        # Initialize logger
        self.logger = logging.getLogger(f"{__name__}.{agent_type.value}")
        
        # Initialize agent-specific components
        self._initialize_agent()
    
    @property
    def llm(self):
        """Lazy initialization of LLM."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.llm_model,
                temperature=self.temperature,
                openai_api_key=settings.OPENAI_API_KEY
            )
        return self._llm
    
    def _initialize_agent(self):
        """Initialize agent-specific components. Override in subclasses."""
        pass
    
    @abstractmethod
    async def _execute_logic(self, context: "AgentContext") -> Dict[str, Any]:
        """Execute the core agent logic. Must be implemented by subclasses."""
        pass
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with comprehensive performance tracking."""
        agent_start_time = time.time()
        
        # Create agent context
        context = AgentContext(
            inputs=inputs,
            agent_type=self.agent_type,
            timestamp=datetime.now(),
            conversation_id=inputs.get('conversation_id', 'unknown'),
            workflow_id=inputs.get('workflow_id', 'unknown')
        )
        
        try:
            # Execute the agent logic
            result = await self._execute_logic(context)
            
            # Calculate execution time
            execution_time = time.time() - agent_start_time
            
            # Track token usage if available
            token_usage = self._extract_token_usage(result)
            
            # Add comprehensive execution metadata
            result.update({
                "agent_type": self.agent_type.value,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "token_usage": token_usage,
                "performance_metrics": {
                    "start_time": agent_start_time,
                    "end_time": time.time(),
                    "duration_seconds": execution_time,
                    "tokens_used": token_usage.get("total_tokens", 0) if token_usage else 0,
                    "agent_name": self.agent_type.value
                }
            })
            
            # Log to LangSmith with comprehensive data
            langsmith_service.log_agent_execution(
                agent_name=self.agent_type.value,
                inputs=inputs,
                outputs=result,
                execution_time=execution_time,
                status="completed",
                error=None
            )
            
            self.logger.info(f"Completed {self.agent_type.value} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - agent_start_time
            error_result = {
                "agent_type": self.agent_type.value,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e),
                "token_usage": None,
                "performance_metrics": {
                    "start_time": agent_start_time,
                    "end_time": time.time(),
                    "duration_seconds": execution_time,
                    "tokens_used": 0,
                    "agent_name": self.agent_type.value,
                    "error": str(e)
                }
            }
            
            # Log error to LangSmith
            langsmith_service.log_agent_execution(
                agent_name=self.agent_type.value,
                inputs=inputs,
                outputs=error_result,
                execution_time=execution_time,
                status="failed",
                error=str(e)
            )
            
            self.logger.error(f"Failed {self.agent_type.value} after {execution_time:.2f}s: {str(e)}")
            return error_result
    
    def _extract_token_usage(self, result: Dict[str, Any]) -> Optional[Dict[str, int]]:
        """Extract token usage information from LLM response."""
        try:
            # Look for token usage in various possible locations
            if "llm_output" in result and isinstance(result["llm_output"], dict):
                llm_output = result["llm_output"]
                if "token_usage" in llm_output:
                    return llm_output["token_usage"]
            
            # Check if result has usage information directly
            if "usage" in result:
                usage = result["usage"]
                return {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
            
            # For now, return None if no token usage found
            # In production, we'd integrate with LangChain's token counting
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to extract token usage: {str(e)}")
            return None
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get the agent's execution history."""
        return self.execution_history.copy()
    
    def reset(self):
        """Reset the agent to initial state."""
        self.execution_history.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_type": self.agent_type.value,
            "execution_count": len(self.execution_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None
        } 