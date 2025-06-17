"""
Modelo de rutinas para la aplicación JumpingKids.

Este módulo define el modelo de datos para las rutinas de ejercicios,
incluyendo la relación con ejercicios y configuraciones.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .exercise import Exercise, ExerciseRead


class RoutineExerciseBase(SQLModel):
    """Modelo base para ejercicios dentro de una rutina."""
    exercise_id: UUID = Field(foreign_key="exercises.id")
    order: int = Field(ge=1)
    duration_seconds: Optional[int] = Field(None, ge=10)
    repetitions: Optional[int] = Field(None, ge=1)
    rest_seconds: int = Field(default=10, ge=0, le=300)


class RoutineExercise(RoutineExerciseBase, table=True):
    """
    Modelo de ejercicio dentro de una rutina para la base de datos.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    routine_id: UUID = Field(foreign_key="routines.id")

    # Relationships
    routine: Optional["Routine"] = Relationship(back_populates="exercises")
    exercise: Optional["Exercise"] = Relationship()


class RoutineExerciseRead(RoutineExerciseBase):
    """Modelo para leer ejercicio de rutina con datos del ejercicio."""
    exercise: Optional["ExerciseRead"] = None


class RoutineBase(SQLModel):
    """Modelo base de rutina con campos comunes."""
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=1000)
    category: str  # ExerciseCategory from exercise.py
    difficulty: str = Field(default="Principiante")
    duration_minutes: int = Field(ge=5, le=120)  # 5 minutos a 2 horas
    age_group: str  # AgeGroup from exercise.py


class Routine(RoutineBase, table=True):
    """
    Modelo de rutina para la base de datos.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_by: str = Field(default="system")  # "system" or user_id
    is_custom: bool = Field(default=False)
    is_active: bool = Field(default=True)
    popularity_score: float = Field(default=0.0, ge=0.0, le=5.0)
    total_assignments: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    exercises: List[RoutineExercise] = Relationship(back_populates="routine")


class RoutineCreate(RoutineBase):
    """Modelo para crear una nueva rutina."""
    exercises: List[RoutineExerciseBase] = Field(default_factory=list)


class RoutineRead(RoutineBase):
    """Modelo para leer datos de rutina."""
    id: UUID
    created_by: str
    is_custom: bool
    is_active: bool
    popularity_score: float
    total_assignments: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    exercises: List[RoutineExerciseRead] = Field(default_factory=list)


class RoutineUpdate(SQLModel):
    """Modelo para actualizar datos de rutina."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = None
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=120)
    age_group: Optional[str] = None
    exercises: Optional[List[RoutineExerciseBase]] = None
