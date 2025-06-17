"""
Modelo de sesiones de entrenamiento para la aplicación JumpingKids.

Este módulo define el modelo de datos para las sesiones de entrenamiento
en tiempo real.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .kid import Kid
    from .assignment import Assignment
    from .routine import Routine


class TrainingSessionStatus(str, Enum):
    """Estados de sesión de entrenamiento."""
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class TrainingSessionBase(SQLModel):
    """Modelo base de sesión de entrenamiento."""
    kid_id: UUID = Field(foreign_key="kids.id")
    assignment_id: Optional[UUID] = Field(None, foreign_key="assignments.id")
    routine_id: UUID = Field(foreign_key="routines.id")
    status: TrainingSessionStatus = TrainingSessionStatus.IN_PROGRESS


class TrainingSession(TrainingSessionBase, table=True):
    """
    Modelo de sesión de entrenamiento para la base de datos.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    current_exercise_index: int = Field(default=0, ge=0)
    exercises_completed: int = Field(default=0, ge=0)
    total_exercises: int = Field(ge=1)
    total_time_minutes: Optional[int] = Field(None, ge=1)
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    kid: Optional["Kid"] = Relationship()
    assignment: Optional["Assignment"] = Relationship()
    routine: Optional["Routine"] = Relationship()


class TrainingSessionCreate(TrainingSessionBase):
    """Modelo para crear una nueva sesión de entrenamiento."""
    total_exercises: int = Field(ge=1)


class TrainingSessionRead(TrainingSessionBase):
    """Modelo para leer datos de sesión de entrenamiento."""
    id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_exercise_index: int
    exercises_completed: int
    total_exercises: int
    total_time_minutes: Optional[int] = None
    overall_rating: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class TrainingSessionUpdate(SQLModel):
    """Modelo para actualizar sesión de entrenamiento."""
    status: Optional[TrainingSessionStatus] = None
    current_exercise_index: Optional[int] = Field(None, ge=0)
    exercises_completed: Optional[int] = Field(None, ge=0)
    total_time_minutes: Optional[int] = Field(None, ge=1)
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)


class ExerciseCompletion(SQLModel):
    """Modelo para completar un ejercicio."""
    completion_time_seconds: int = Field(ge=1)
    rating: int = Field(ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=200)


class SessionCompletion(SQLModel):
    """Modelo para completar una sesión."""
    total_time_minutes: int = Field(ge=1)
    exercises_completed: int = Field(ge=0)
    overall_rating: int = Field(ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)
