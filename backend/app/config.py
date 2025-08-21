"""
Configuration settings for Verityn AI backend.

This module contains all configuration settings using Pydantic Settings
for environment variable management and validation.

ENVIRONMENT VARIABLE LOCATION:
- The .env file is located in the PROJECT ROOT directory: /Verityn-AI/.env
- NOT in the backend directory: /Verityn-AI/backend/.env
- The config uses "../.env" to access the root .env file from the backend directory
- DO NOT change this path - it's intentionally set to access the root .env file
"""

import json
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Configuration
    APP_NAME: str = "Verityn AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Server Configuration
    BACKEND_HOST: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    BACKEND_PORT: int = Field(default=8000, env="BACKEND_PORT")
    FRONTEND_PORT: int = Field(default=8501, env="FRONTEND_PORT")
    
    # Security Configuration
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:8501"], env="CORS_ORIGINS")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL")
    
    # Tavily API Configuration
    TAVILY_API_KEY: str = Field(env="TAVILY_API_KEY")
    
    # Cohere API Configuration (for advanced retrieval)
    COHERE_API_KEY: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    
    # LangSmith Configuration (Updated to match bootcamp patterns)
    LANGCHAIN_TRACING_V2: str = Field(default="true", env="LANGCHAIN_TRACING_V2")
    LANGCHAIN_API_KEY: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = Field(default="verityn-ai-dev", env="LANGCHAIN_PROJECT")
    
    # Legacy LangSmith support
    LANGSMITH_API_KEY: Optional[str] = Field(default=None, env="LANGSMITH_API_KEY")
    LANGSMITH_PROJECT: str = Field(default="verityn-ai", env="LANGSMITH_PROJECT")
    LANGSMITH_TRACING_V2: bool = Field(default=True, env="LANGSMITH_TRACING_V2")
    
    # Qdrant Configuration
    QDRANT_HOST: str = Field(default="localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")
    QDRANT_COLLECTION_NAME: str = Field(default="verityn_documents", env="QDRANT_COLLECTION_NAME")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: List[str] = Field(default=["pdf", "docx", "txt", "csv", "xlsx"], env="ALLOWED_FILE_TYPES")
    
    # RAGAS Evaluation Configuration
    RAGAS_EVALUATION_ENABLED: bool = Field(default=True, env="RAGAS_EVALUATION_ENABLED")
    RAGAS_DATASET_PATH: str = Field(default="./data/evaluation_datasets/", env="RAGAS_DATASET_PATH")
    
    # Development Configuration
    ENABLE_MONITORING: bool = Field(default=True, env="ENABLE_MONITORING")
    ENABLE_LOGGING: bool = Field(default=True, env="ENABLE_LOGGING")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_file_types(cls, v):
        """Parse allowed file types from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v.strip() for v in v.split(",")]
        return v
    
    class Config:
        # IMPORTANT: .env file is located in the PROJECT ROOT directory (/Verityn-AI/.env)
        # NOT in the backend directory (/Verityn-AI/backend/.env)
        # This path "../.env" goes up one level from backend/ to find the .env file
        # DO NOT CHANGE THIS PATH - it's intentionally set to access the root .env file
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env file


# Global settings instance
settings = Settings() 