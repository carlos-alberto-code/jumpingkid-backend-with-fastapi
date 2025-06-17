"""
Router para la gestión de asignaciones (Assignments).

Este módulo define los endpoints de la API para la gestión de asignaciones,
incluyendo CRUD operations y filtrado por estado y fecha.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from src.database import get_db
from src.models import AssignmentCreate, AssignmentRead, AssignmentComplete
from src.models.responses import APIResponse
from src.services.assignment_service import AssignmentService
from src.web.dependencies import get_current_user

router = APIRouter(tags=["Assignments"])


@router.get("/assignments", response_model=APIResponse[List[AssignmentRead]])
async def get_assignments(
    kid_id: Optional[UUID] = Query(None),
    date_filter: Optional[date] = Query(None),
    assignment_status: Optional[str] = Query(
        None, regex="^(pending|in-progress|completed|skipped)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener asignaciones de rutinas con filtros opcionales."""
    assignment_service = AssignmentService(db)
    assignments = assignment_service.get_assignments(
        user_id=current_user.id,
        kid_id=kid_id,
        date_filter=date_filter,
        status_filter=assignment_status,
        limit=limit,
        offset=offset
    )

    return APIResponse(
        success=True,
        data=assignments,
        message=f"Retrieved {len(assignments)} assignments"
    )


@router.post("/assignments", response_model=APIResponse[AssignmentRead])
async def create_assignment(
    assignment_data: AssignmentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva asignación de rutina."""
    assignment_service = AssignmentService(db)
    assignment = assignment_service.create_assignment(
        assignment_data, current_user.id)

    return APIResponse(
        success=True,
        data=assignment,
        message="Assignment created successfully"
    )


@router.get("/assignments/today", response_model=APIResponse[List[AssignmentRead]])
async def get_assignments_today(
    kid_id: Optional[UUID] = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener asignaciones de hoy."""
    assignment_service = AssignmentService(db)
    assignments = assignment_service.get_assignments_today(
        user_id=current_user.id,
        kid_id=kid_id
    )

    return APIResponse(
        success=True,
        data=assignments,
        message=f"Retrieved {len(assignments)} assignments for today"
    )


@router.get("/assignments/kids/{kid_id}/today", response_model=APIResponse[Optional[AssignmentRead]])
async def get_kid_assignment_today(
    kid_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener la asignación de hoy para un niño específico."""
    assignment_service = AssignmentService(db)
    assignment = assignment_service.get_kid_assignment_today(
        kid_id, current_user.id)

    return APIResponse(
        success=True,
        data=assignment,
        message="Today's assignment retrieved successfully" if assignment else "No assignment found for today"
    )


@router.put("/assignments/{assignment_id}/complete", response_model=APIResponse[AssignmentRead])
async def complete_assignment(
    assignment_id: UUID,
    completion_data: AssignmentComplete,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar asignación como completada."""
    assignment_service = AssignmentService(db)
    assignment = assignment_service.complete_assignment(
        assignment_id, completion_data, current_user.id
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    return APIResponse(
        success=True,
        data=assignment,
        message="Assignment completed successfully"
    )
