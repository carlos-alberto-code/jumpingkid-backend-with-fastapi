"""
Servicio para la gestión de asignaciones (Assignments).

Este módulo contiene la lógica de negocio para la gestión de asignaciones,
incluyendo CRUD operations y filtrado por estado y fecha.
"""

from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, and_, desc, col
from fastapi import HTTPException, status

from src.models import (
    Assignment, AssignmentCreate, AssignmentRead, AssignmentComplete, AssignmentStatus, Routine, Kid
)


class AssignmentService:
    """Servicio para gestión de asignaciones."""

    def __init__(self, db: Session):
        self.db = db

    def get_assignments(
        self,
        user_id: int,
        kid_id: Optional[UUID] = None,
        date_filter: Optional[date] = None,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AssignmentRead]:
        """Obtener asignaciones con filtros opcionales."""
        # Primero verificar que el usuario tenga acceso a los niños
        kid_statement = select(Kid.id).where(
            and_(Kid.user_id == user_id, Kid.is_active == True)
        )
        accessible_kid_ids = self.db.exec(kid_statement).all()

        if not accessible_kid_ids:
            return []

        # Construir query de asignaciones
        statement = select(Assignment).where(
            col(Assignment.kid_id).in_(accessible_kid_ids)
        )

        # Filtros opcionales
        if kid_id:
            if kid_id not in accessible_kid_ids:
                return []  # El usuario no tiene acceso a este niño
            statement = statement.where(Assignment.kid_id == kid_id)

        if date_filter:
            statement = statement.where(
                Assignment.assigned_date == date_filter)

        if status_filter:
            statement = statement.where(Assignment.status == status_filter)

        # Ordenar por fecha de asignación
        statement = statement.order_by(desc(Assignment.assigned_date))

        # Paginación
        statement = statement.offset(offset).limit(limit)

        assignments = self.db.exec(statement).all()

        # Cargar asignaciones con rutinas
        assignment_reads = []
        for assignment in assignments:
            assignment_read = self._load_assignment_with_routine(assignment)
            assignment_reads.append(assignment_read)

        return assignment_reads

    def get_assignments_today(
        self,
        user_id: int,
        kid_id: Optional[UUID] = None
    ) -> List[AssignmentRead]:
        """Obtener asignaciones de hoy."""
        today = date.today()
        return self.get_assignments(
            user_id=user_id,
            kid_id=kid_id,
            date_filter=today
        )

    def get_kid_assignment_today(
        self,
        kid_id: UUID,
        user_id: int
    ) -> Optional[AssignmentRead]:
        """Obtener la asignación de hoy para un niño específico."""
        # Verificar que el niño pertenezca al usuario
        kid_statement = select(Kid).where(
            and_(Kid.id == kid_id, Kid.user_id ==
                 user_id, Kid.is_active == True)
        )
        kid = self.db.exec(kid_statement).first()

        if not kid:
            return None

        today = date.today()
        statement = select(Assignment).where(
            and_(
                Assignment.kid_id == kid_id,
                Assignment.assigned_date == today
            )
        )

        assignment = self.db.exec(statement).first()
        if assignment:
            return self._load_assignment_with_routine(assignment)
        return None

    def create_assignment(self, assignment_data: AssignmentCreate, user_id: int) -> AssignmentRead:
        """Crear nueva asignación de rutina."""
        # Verificar que el niño pertenezca al usuario
        kid_statement = select(Kid).where(
            and_(
                Kid.id == assignment_data.kid_id,
                Kid.user_id == user_id,
                Kid.is_active == True
            )
        )
        kid = self.db.exec(kid_statement).first()

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kid not found"
            )

        # Verificar que la rutina existe
        routine_statement = select(Routine).where(
            and_(Routine.id == assignment_data.routine_id,
                 Routine.is_active == True)
        )
        routine = self.db.exec(routine_statement).first()

        if not routine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Routine not found"
            )

        # Crear asignación
        assignment = Assignment(
            **assignment_data.model_dump(),
            assigned_by=user_id
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        return self._load_assignment_with_routine(assignment)

    def complete_assignment(
        self,
        assignment_id: UUID,
        completion_data: AssignmentComplete,
        user_id: int
    ) -> Optional[AssignmentRead]:
        """Marcar asignación como completada."""
        # Verificar que la asignación pertenezca a un niño del usuario
        statement = select(Assignment).join(Kid).where(
            and_(
                Assignment.id == assignment_id,
                Kid.user_id == user_id,
                Kid.is_active == True
            )
        )
        assignment = self.db.exec(statement).first()

        if not assignment:
            return None

        # Actualizar asignación
        assignment.status = AssignmentStatus.COMPLETED
        assignment.completed_at = datetime.utcnow()
        assignment.completion_time_minutes = completion_data.completion_time_minutes
        assignment.exercises_completed = completion_data.exercises_completed
        assignment.notes = completion_data.notes
        assignment.updated_at = datetime.utcnow()

        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        return self._load_assignment_with_routine(assignment)

    def _load_assignment_with_routine(self, assignment: Assignment) -> AssignmentRead:
        """Cargar asignación con datos de la rutina."""
        # Cargar rutina asociada
        routine = self.db.exec(
            select(Routine).where(Routine.id == assignment.routine_id)
        ).first()

        assignment_dict = assignment.model_dump()
        if routine:
            assignment_dict['routine'] = routine.model_dump()

        return AssignmentRead(**assignment_dict)
