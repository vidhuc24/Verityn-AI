"""
Main FastAPI application for Verityn AI

This module contains the main FastAPI application with all routes,
middleware, and configuration for the Verityn AI backend.
"""

import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.routes import chat, documents, health, workflow


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    environment: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    print("🚀 Starting Verityn AI Backend...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    
    # Initialize services here (Qdrant, LangSmith, etc.)
    # await initialize_services()
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Verityn AI Backend...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Intelligent Document Chat for Audit, Risk & Compliance Professionals",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(documents.router, prefix="/documents", tags=["documents"])
    app.include_router(chat.router, prefix="/chat", tags=["chat"])
    app.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
    
    return app


app = create_app()


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with application information."""
    return {
        "message": "Welcome to Verityn AI",
        "version": settings.APP_VERSION,
        "description": "Intelligent Document Chat for Audit, Risk & Compliance Professionals",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "path": str(request.url),
        },
    )


def main():
    """Main entry point for running the application."""
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main() 