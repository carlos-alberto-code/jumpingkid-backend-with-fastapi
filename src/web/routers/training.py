"""
Router para la gestión de sesiones de entrenamiento (Training).

Este módulo define los endpoints de la API para sesiones de entrenamiento
en tiempo real.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_db
from src.models import (
    TrainingSessionCreate, TrainingSessionRead,
    ExerciseCompletion, SessionCompletion
)
from src.models.responses import APIResponse
from src.services.training_service import TrainingService
from src.web.dependencies import get_current_user

router = APIRouter(tags=["Training"])


@router.post("/training/sessions", response_model=APIResponse[TrainingSessionRead])
async def create_training_session(
    session_data: TrainingSessionCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Iniciar nueva sesión de entrenamiento."""
    training_service = TrainingService(db)
    session = training_service.create_session(session_data, current_user.id)

    return APIResponse(
        success=True,
        data=session,
        message="Training session started successfully"
    )


@router.get("/training/sessions/{session_id}", response_model=APIResponse[TrainingSessionRead])
async def get_training_session(
    session_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estado actual de sesión de entrenamiento."""
    training_service = TrainingService(db)
    session = training_service.get_session(session_id, current_user.id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )

    return APIResponse(
        success=True,
        data=session,
        message="Training session retrieved successfully"
    )


@router.put("/training/sessions/{session_id}/exercise/complete", response_model=APIResponse[TrainingSessionRead])
async def complete_exercise(
    session_id: UUID,
    completion_data: ExerciseCompletion,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar ejercicio actual como completado y avanzar al siguiente."""
    training_service = TrainingService(db)
    session = training_service.complete_exercise(
        session_id, completion_data, current_user.id
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found or not in progress"
        )

    return APIResponse(
        success=True,
        data=session,
        message="Exercise completed successfully"
    )


@router.put("/training/sessions/{session_id}/complete", response_model=APIResponse[dict])
async def complete_training_session(
    session_id: UUID,
    completion_data: SessionCompletion,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Finalizar sesión de entrenamiento."""
    training_service = TrainingService(db)
    result = training_service.complete_session(
        session_id, completion_data, current_user.id
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )

    return APIResponse(
        success=True,
        data=result,
        message="Training session completed successfully"
    )
