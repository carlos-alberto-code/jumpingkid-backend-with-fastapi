"""
Servicio para la gestión de niños (Kids).

Este módulo contiene la lógica de negocio para la gestión de niños,
incluyendo CRUD operations y cálculo de estadísticas.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, and_

from src.models import Kid, KidCreate, KidRead, KidUpdate, KidStats, KidStatsResponse


class KidService:
    """Servicio para gestión de niños."""

    def __init__(self, db: Session):
        self.db = db

    def get_kids_by_user(self, user_id: int) -> List[KidRead]:
        """Obtener todos los niños de un usuario."""
        statement = select(Kid).where(
            and_(Kid.user_id == user_id, Kid.is_active == True)
        )
        kids = self.db.exec(statement).all()
        return [KidRead.model_validate(kid) for kid in kids]

    def get_kid_by_id(self, kid_id: UUID, user_id: int) -> Optional[KidRead]:
        """Obtener un niño por ID, verificando que pertenezca al usuario."""
        statement = select(Kid).where(
            and_(
                Kid.id == kid_id,
                Kid.user_id == user_id,
                Kid.is_active == True
            )
        )
        kid = self.db.exec(statement).first()
        if kid:
            return KidRead.model_validate(kid)
        return None

    def create_kid(self, kid_data: KidCreate, user_id: int) -> KidRead:
        """Crear un nuevo niño."""
        kid = Kid(**kid_data.model_dump(), user_id=user_id)
        self.db.add(kid)
        self.db.commit()
        self.db.refresh(kid)
        return KidRead.model_validate(kid)

    def update_kid(self, kid_id: UUID, kid_data: KidUpdate, user_id: int) -> Optional[KidRead]:
        """Actualizar un niño existente."""
        statement = select(Kid).where(
            and_(
                Kid.id == kid_id,
                Kid.user_id == user_id,
                Kid.is_active == True
            )
        )
        kid = self.db.exec(statement).first()

        if not kid:
            return None

        # Actualizar campos
        update_data = kid_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(kid, field, value)

        kid.updated_at = datetime.utcnow()
        self.db.add(kid)
        self.db.commit()
        self.db.refresh(kid)
        return KidRead.model_validate(kid)

    def delete_kid(self, kid_id: UUID, user_id: int) -> bool:
        """Eliminar un niño (soft delete)."""
        statement = select(Kid).where(
            and_(
                Kid.id == kid_id,
                Kid.user_id == user_id,
                Kid.is_active == True
            )
        )
        kid = self.db.exec(statement).first()

        if not kid:
            return False

        kid.is_active = False
        kid.updated_at = datetime.utcnow()
        self.db.add(kid)
        self.db.commit()
        return True

    def get_kid_stats(self, kid_id: UUID, user_id: int) -> Optional[KidStatsResponse]:
        """Obtener estadísticas detalladas de un niño."""
        kid = self.get_kid_by_id(kid_id, user_id)
        if not kid:
            return None

        # Generar datos de progreso semanal (simulado por ahora)
        weekly_progress = self._generate_weekly_progress(kid_id)

        stats_response = KidStatsResponse(
            **kid.stats.model_dump(),
            weekly_progress=weekly_progress
        )

        return stats_response

    def update_kid_stats(self, kid_id: UUID, user_id: int, stats_update: dict) -> Optional[KidRead]:
        """Actualizar estadísticas de un niño."""
        statement = select(Kid).where(
            and_(
                Kid.id == kid_id,
                Kid.user_id == user_id,
                Kid.is_active == True
            )
        )
        kid = self.db.exec(statement).first()

        if not kid:
            return None

        # Actualizar stats
        current_stats = kid.stats.model_dump()
        current_stats.update(stats_update)
        kid.stats = KidStats(**current_stats)
        kid.updated_at = datetime.utcnow()

        self.db.add(kid)
        self.db.commit()
        self.db.refresh(kid)
        return KidRead.model_validate(kid)

    def _generate_weekly_progress(self, _kid_id: UUID) -> List[dict]:
        """Generar datos de progreso semanal (implementación básica)."""
        # Por ahora generamos datos de ejemplo
        # En una implementación real, esto consultaría la tabla de assignments
        today = date.today()
        progress = []

        # Generar últimos 7 días
        for i in range(7):
            day = today - timedelta(days=i)
            progress.append({
                "date": day.strftime("%Y-%m-%d"),
                "completed": 1 if i < 3 else 0,  # Simulamos que completó los últimos 3 días
                "assigned": 1
            })

        # Ordenar del más antiguo al más reciente
        return list(reversed(progress))
