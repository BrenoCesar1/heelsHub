"""Health check endpoints."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns API status and timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AI Content Creator API",
        "version": "1.0.0"
    }


@router.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "service": "AI Content Creator API",
        "version": "1.0.0",
        "description": "REST API for AI-powered video generation and management",
        "docs": "/docs",
        "health": "/health"
    }
