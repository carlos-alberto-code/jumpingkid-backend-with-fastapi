"""
Router para la gestión de ejercicios (Exercises).

Este módulo define los endpoints de la API para la gestión de ejercicios,
incluyendo CRUD operations y filtrado.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from src.database import get_db
from src.models import ExerciseCreate, ExerciseRead, ExerciseUpdate
from src.models.responses import APIResponse
from src.services.exercise_service import ExerciseService
from src.web.dependencies import get_current_user

router = APIRouter(tags=["Exercises"])


@router.get("/exercises", response_model=APIResponse[List[ExerciseRead]])
async def get_exercises(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener catálogo de ejercicios con filtros opcionales."""
    exercise_service = ExerciseService(db)
    exercises = exercise_service.get_exercises(
        category=category,
        difficulty=difficulty,
        age_group=age_group,
        search=search,
        limit=limit,
        offset=offset,
        user_id=current_user.id
    )

    return APIResponse(
        success=True,
        data=exercises,
        message=f"Retrieved {len(exercises)} exercises"
    )


@router.post("/exercises", response_model=APIResponse[ExerciseRead])
async def create_exercise(
    exercise_data: ExerciseCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear ejercicio personalizado."""
    exercise_service = ExerciseService(db)
    exercise = exercise_service.create_exercise(exercise_data, current_user.id)

    return APIResponse(
        success=True,
        data=exercise,
        message="Exercise created successfully"
    )


@router.get("/exercises/{exercise_id}", response_model=APIResponse[ExerciseRead])
async def get_exercise(
    exercise_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un ejercicio específico."""
    exercise_service = ExerciseService(db)
    exercise = exercise_service.get_exercise_by_id(
        exercise_id, current_user.id)

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    return APIResponse(
        success=True,
        data=exercise,
        message="Exercise retrieved successfully"
    )


@router.put("/exercises/{exercise_id}", response_model=APIResponse[ExerciseRead])
async def update_exercise(
    exercise_id: UUID,
    exercise_data: ExerciseUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar ejercicio personalizado."""
    exercise_service = ExerciseService(db)
    exercise = exercise_service.update_exercise(
        exercise_id, exercise_data, current_user.id)

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found or not authorized"
        )

    return APIResponse(
        success=True,
        data=exercise,
        message="Exercise updated successfully"
    )


@router.delete("/exercises/{exercise_id}", response_model=APIResponse[dict])
async def delete_exercise(
    exercise_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar ejercicio personalizado."""
    exercise_service = ExerciseService(db)
    success = exercise_service.delete_exercise(exercise_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found or not authorized"
        )

    return APIResponse(
        success=True,
        data={"id": str(exercise_id)},
        message="Exercise deleted successfully"
    )


@router.get("/exercises/categories", response_model=APIResponse[List[str]])
async def get_exercise_categories(
    db: Session = Depends(get_db)
):
    """Obtener lista de categorías disponibles."""
    exercise_service = ExerciseService(db)
    categories = exercise_service.get_categories()

    return APIResponse(
        success=True,
        data=categories,
        message="Categories retrieved successfully"
    )
