"""
Router para la gestión de niños (Kids).

Este módulo define los endpoints de la API para la gestión de niños,
incluyendo CRUD operations y estadísticas.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from src.database import get_db
from src.models import KidCreate, KidRead, KidUpdate, KidStatsResponse
from src.models.responses import APIResponse
from src.services.kid_service import KidService
from src.web.dependencies import get_current_user

router = APIRouter(tags=["Kids Management"])


@router.get("/user/kids", response_model=APIResponse[List[KidRead]])
async def get_user_kids(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los niños del usuario autenticado."""
    kid_service = KidService(db)
    kids = kid_service.get_kids_by_user(current_user.id)

    return APIResponse(
        success=True,
        data=kids,
        message=f"Retrieved {len(kids)} kids"
    )


@router.post("/user/kids", response_model=APIResponse[KidRead])
async def create_kid(
    kid_data: KidCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo niño."""
    kid_service = KidService(db)
    kid = kid_service.create_kid(kid_data, current_user.id)

    return APIResponse(
        success=True,
        data=kid,
        message="Kid created successfully"
    )


@router.get("/user/kids/{kid_id}", response_model=APIResponse[KidRead])
async def get_kid(
    kid_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un niño específico."""
    kid_service = KidService(db)
    kid = kid_service.get_kid_by_id(kid_id, current_user.id)

    if not kid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kid not found"
        )

    return APIResponse(
        success=True,
        data=kid,
        message="Kid retrieved successfully"
    )


@router.put("/user/kids/{kid_id}", response_model=APIResponse[KidRead])
async def update_kid(
    kid_id: UUID,
    kid_data: KidUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar datos de un niño."""
    kid_service = KidService(db)
    kid = kid_service.update_kid(kid_id, kid_data, current_user.id)

    if not kid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kid not found"
        )

    return APIResponse(
        success=True,
        data=kid,
        message="Kid updated successfully"
    )


@router.delete("/user/kids/{kid_id}", response_model=APIResponse[dict])
async def delete_kid(
    kid_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un niño."""
    kid_service = KidService(db)
    success = kid_service.delete_kid(kid_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kid not found"
        )

    return APIResponse(
        success=True,
        data={"id": str(kid_id)},
        message="Kid deleted successfully"
    )


@router.get("/user/kids/{kid_id}/stats", response_model=APIResponse[KidStatsResponse])
async def get_kid_stats(
    kid_id: UUID,
    period: Optional[str] = Query(None, regex="^(week|month|year)$"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas detalladas de un niño."""
    kid_service = KidService(db)
    stats = kid_service.get_kid_stats(kid_id, current_user.id, period)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kid not found"
        )

    return APIResponse(
        success=True,
        data=stats,
        message="Kid stats retrieved successfully"
    )
