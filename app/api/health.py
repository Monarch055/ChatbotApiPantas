from fastapi import APIRouter, status
from app.models import HealthResponse
from app.core.config import settings
from datetime import datetime

# Create router
router = APIRouter(tags=["Health"])

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Check if the API is running and healthy"
)
async def health_check():
    """
    Health check endpoint
    
    Returns the current status of the API, timestamp, and version information.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.API_VERSION
    )

@router.get(
    "/",
    summary="API information",
    description="Get basic information about the Chatbot API"
)
async def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the Chatbot API",
        "version": settings.API_VERSION,
        "documentation": "/docs",
        "health_check": "/health"
    }