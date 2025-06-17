"""
Servicio para la gestión de sesiones de entrenamiento (Training).

Este módulo contiene la lógica de negocio para la gestión de sesiones
de entrenamiento en tiempo real.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select, and_
from fastapi import HTTPException, status

from src.models import (
    TrainingSession, TrainingSessionCreate, TrainingSessionRead,
    SessionCompletion,
    TrainingSessionStatus, Kid, Assignment, Routine, RoutineExercise,
    AssignmentStatus
)


class TrainingService:
    """Servicio para gestión de sesiones de entrenamiento."""

    def __init__(self, db: Session):
        self.db = db

    def create_session(self, session_data: TrainingSessionCreate, user_id: int) -> TrainingSessionRead:
        """Iniciar nueva sesión de entrenamiento."""
        # Verificar que el niño pertenezca al usuario
        kid_statement = select(Kid).where(
            and_(
                Kid.id == session_data.kid_id,
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
            and_(Routine.id == session_data.routine_id, Routine.is_active == True)
        )
        routine = self.db.exec(routine_statement).first()

        if not routine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Routine not found"
            )

        # Contar ejercicios en la rutina
        exercise_count = self.db.exec(
            select(RoutineExercise).where(
                RoutineExercise.routine_id == session_data.routine_id)
        ).all()

        total_exercises = len(exercise_count)

        # Verificar asignación si se proporciona
        if session_data.assignment_id:
            assignment_statement = select(Assignment).join(Kid).where(
                and_(
                    Assignment.id == session_data.assignment_id,
                    Kid.user_id == user_id,
                    Assignment.kid_id == session_data.kid_id
                )
            )
            assignment = self.db.exec(assignment_statement).first()

            if not assignment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignment not found"
                )

        # Crear sesión
        session = TrainingSession(
            **session_data.model_dump(),
            total_exercises=total_exercises
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return TrainingSessionRead.model_validate(session)

    def get_session(self, session_id: UUID, user_id: int) -> Optional[TrainingSessionRead]:
        """Obtener estado actual de sesión de entrenamiento."""
        statement = select(TrainingSession).join(Kid).where(
            and_(
                TrainingSession.id == session_id,
                Kid.user_id == user_id
            )
        )
        session = self.db.exec(statement).first()

        if session:
            return TrainingSessionRead.model_validate(session)
        return None

    def complete_exercise(
        self,
        session_id: UUID,
        user_id: int
    ) -> Optional[TrainingSessionRead]:
        """Marcar ejercicio actual como completado y avanzar al siguiente."""
        # Obtener sesión
        statement = select(TrainingSession).join(Kid).where(
            and_(
                TrainingSession.id == session_id,
                Kid.user_id == user_id,
                TrainingSession.status == TrainingSessionStatus.IN_PROGRESS
            )
        )
        session = self.db.exec(statement).first()

        if not session:
            return None

        # Actualizar progreso
        session.exercises_completed += 1
        session.current_exercise_index += 1
        session.updated_at = datetime.utcnow()

        # Si completó todos los ejercicios, marcar sesión como completada
        if session.exercises_completed >= session.total_exercises:
            session.status = TrainingSessionStatus.COMPLETED
            session.completed_at = datetime.utcnow()

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return TrainingSessionRead.model_validate(session)

    def complete_session(
        self,
        session_id: UUID,
        completion_data: SessionCompletion,
        user_id: int
    ) -> Optional[dict]:
        """Finalizar sesión de entrenamiento."""
        # Obtener sesión
        statement = select(TrainingSession).join(Kid).where(
            and_(
                TrainingSession.id == session_id,
                Kid.user_id == user_id
            )
        )
        session = self.db.exec(statement).first()

        if not session:
            return None

        # Actualizar sesión
        session.status = TrainingSessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        session.total_time_minutes = completion_data.total_time_minutes
        session.exercises_completed = completion_data.exercises_completed
        session.overall_rating = completion_data.overall_rating
        session.notes = completion_data.notes
        session.updated_at = datetime.utcnow()

        self.db.add(session)

        # Si hay una asignación asociada, marcarla como completada
        if session.assignment_id:
            assignment_statement = select(Assignment).where(
                Assignment.id == session.assignment_id
            )
            assignment = self.db.exec(assignment_statement).first()
            if assignment:
                assignment.status = AssignmentStatus.COMPLETED
                assignment.completed_at = datetime.utcnow()
                assignment.completed_at = datetime.utcnow()
                assignment.completion_time_minutes = completion_data.total_time_minutes
                assignment.exercises_completed = completion_data.exercises_completed
                assignment.updated_at = datetime.utcnow()
                self.db.add(assignment)

        # Actualizar estadísticas del niño
        kid_statement = select(Kid).where(Kid.id == session.kid_id)
        kid = self.db.exec(kid_statement).first()

        if kid:
            # Actualizar estadísticas básicas
            current_stats = kid.stats.model_dump()
            current_stats['total_routines'] += 1
            current_stats['this_week_completed'] += 1
            current_stats['current_streak'] += 1
            current_stats['total_minutes'] += completion_data.total_time_minutes
            current_stats['last_activity'] = datetime.utcnow()

            # Actualizar longest_streak si es necesario
            if current_stats['current_streak'] > current_stats['longest_streak']:
                current_stats['longest_streak'] = current_stats['current_streak']

            from src.models.kid import KidStats
            kid.stats = KidStats(**current_stats)
            kid.updated_at = datetime.utcnow()
            self.db.add(kid)

        self.db.commit()
        self.db.refresh(session)

        # Preparar respuesta con estadísticas actualizadas
        stats_updated = {
            "new_streak": current_stats['current_streak'] if kid else 0,
            "total_minutes": current_stats['total_minutes'] if kid else 0,
            "level_up": False  # TODO: Implementar lógica de level up
        }

        return {
            "session": TrainingSessionRead.model_validate(session),
            "stats_updated": stats_updated
        }
