"""
Modelo de asignaciones para la aplicación JumpingKids.

Este módulo define el modelo de datos para las asignaciones de rutinas
a niños, incluyendo estados y fechas.
"""

from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .routine import Routine, RoutineRead
    from .kid import Kid
    from .user import User


class AssignmentStatus(str, Enum):
    """Estados de asignación disponibles."""
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class AssignmentBase(SQLModel):
    """Modelo base de asignación con campos comunes."""
    routine_id: UUID = Field(foreign_key="routines.id")
    kid_id: UUID = Field(foreign_key="kids.id")
    assigned_date: date
    status: AssignmentStatus = AssignmentStatus.PENDING


class Assignment(AssignmentBase, table=True):
    """
    Modelo de asignación para la base de datos.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    assigned_by: int = Field(foreign_key="user.id")  # Usuario que asignó
    completed_at: Optional[datetime] = None
    completion_time_minutes: Optional[int] = Field(None, ge=1)
    exercises_completed: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    routine: Optional["Routine"] = Relationship()
    kid: Optional["Kid"] = Relationship()
    assigned_by_user: Optional["User"] = Relationship()


class AssignmentCreate(AssignmentBase):
    """Modelo para crear una nueva asignación."""
    pass


class AssignmentRead(AssignmentBase):
    """Modelo para leer datos de asignación."""
    id: UUID
    assigned_by: int
    completed_at: Optional[datetime] = None
    completion_time_minutes: Optional[int] = None
    exercises_completed: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    routine: Optional["RoutineRead"] = None


class AssignmentUpdate(SQLModel):
    """Modelo para actualizar datos de asignación."""
    status: Optional[AssignmentStatus] = None
    completion_time_minutes: Optional[int] = Field(None, ge=1)
    exercises_completed: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)


class AssignmentComplete(SQLModel):
    """Modelo para completar una asignación."""
    completion_time_minutes: int = Field(ge=1)
    exercises_completed: int = Field(ge=0)
    notes: Optional[str] = Field(None, max_length=500)
