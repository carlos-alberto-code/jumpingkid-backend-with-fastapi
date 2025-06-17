"""
Router para endpoints de utilidad.

Este módulo define endpoints de utilidad como health check.
"""

from fastapi import APIRouter
from src.models.responses import HealthResponse

router = APIRouter(tags=["Utility"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check del servicio."""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )
