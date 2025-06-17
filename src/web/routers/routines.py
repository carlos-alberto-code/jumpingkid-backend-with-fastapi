"""
Router para la gestión de rutinas (Routines).

Este módulo define los endpoints de la API para la gestión de rutinas,
incluyendo CRUD operations y filtrado.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from src.database import get_db
from src.models import RoutineCreate, RoutineRead, RoutineUpdate
from src.models.responses import APIResponse
from src.services.routine_service import RoutineService
from src.web.dependencies import get_current_user

router = APIRouter(tags=["Routines"])


@router.get("/routines", response_model=APIResponse[List[RoutineRead]])
async def get_routines(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    duration_max: Optional[int] = Query(None, ge=1),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener catálogo de rutinas con filtros opcionales."""
    routine_service = RoutineService(db)
    routines = routine_service.get_routines(
        category=category,
        difficulty=difficulty,
        duration_max=duration_max,
        search=search,
        limit=limit,
        offset=offset,
        user_id=current_user.id
    )

    return APIResponse(
        success=True,
        data=routines,
        message=f"Retrieved {len(routines)} routines"
    )


@router.post("/routines", response_model=APIResponse[RoutineRead])
async def create_routine(
    routine_data: RoutineCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear rutina personalizada."""
    routine_service = RoutineService(db)
    routine = routine_service.create_routine(routine_data, current_user.id)

    return APIResponse(
        success=True,
        data=routine,
        message="Routine created successfully"
    )


@router.get("/routines/{routine_id}", response_model=APIResponse[RoutineRead])
async def get_routine(
    routine_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener rutina específica con todos sus ejercicios."""
    routine_service = RoutineService(db)
    routine = routine_service.get_routine_by_id(routine_id, current_user.id)

    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found"
        )

    return APIResponse(
        success=True,
        data=routine,
        message="Routine retrieved successfully"
    )


@router.put("/routines/{routine_id}", response_model=APIResponse[RoutineRead])
async def update_routine(
    routine_id: UUID,
    routine_data: RoutineUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar rutina personalizada."""
    routine_service = RoutineService(db)
    routine = routine_service.update_routine(
        routine_id, routine_data, current_user.id)

    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found or not authorized"
        )

    return APIResponse(
        success=True,
        data=routine,
        message="Routine updated successfully"
    )


@router.delete("/routines/{routine_id}", response_model=APIResponse[dict])
async def delete_routine(
    routine_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar rutina personalizada."""
    routine_service = RoutineService(db)
    success = routine_service.delete_routine(routine_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found or not authorized"
        )

    return APIResponse(
        success=True,
        data={"id": str(routine_id)},
        message="Routine deleted successfully"
    )
