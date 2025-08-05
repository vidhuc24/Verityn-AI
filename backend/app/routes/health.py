"""
Health check routes for Verityn AI backend.

This module provides health check endpoints for monitoring
the application status and external service connectivity.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    environment: str
    services: dict


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services={
            "openai": "configured" if settings.OPENAI_API_KEY else "not_configured",
            "tavily": "configured" if settings.TAVILY_API_KEY else "not_configured",
            "qdrant": "configured",
            "langsmith": "configured" if settings.LANGSMITH_API_KEY else "not_configured",
        },
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes and load balancers."""
    # Add more comprehensive checks here
    # - Database connectivity
    # - External API connectivity
    # - Required services status
    
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes health probes."""
    return {"status": "alive"} 