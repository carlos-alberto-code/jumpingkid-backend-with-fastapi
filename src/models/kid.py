"""
Modelo de niños para la aplicación JumpingKids.

Este módulo define el modelo de datos para los niños,
incluyendo sus preferencias, estadísticas y configuraciones.
"""

from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User


class DifficultyLevel(str, Enum):
    """Niveles de dificultad disponibles."""
    PRINCIPIANTE = "Principiante"
    INTERMEDIO = "Intermedio"
    AVANZADO = "Avanzado"


class PreferredTime(str, Enum):
    """Momentos preferidos del día para ejercitarse."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class KidPreferences(SQLModel):
    """Preferencias del niño para ejercicios."""
    favorite_exercises: List[str] = Field(
        default_factory=list, sa_column_kwargs={"type_": "JSON"})
    preferred_time: PreferredTime = PreferredTime.MORNING
    max_daily_exercises: int = Field(default=5, ge=1, le=20)
    difficulty: DifficultyLevel = DifficultyLevel.PRINCIPIANTE


class KidStats(SQLModel):
    """Estadísticas del progreso del niño."""
    total_routines: int = Field(default=0, ge=0)
    this_week_completed: int = Field(default=0, ge=0)
    this_week_assigned: int = Field(default=0, ge=0)
    current_streak: int = Field(default=0, ge=0)
    longest_streak: int = Field(default=0, ge=0)
    favorite_category: Optional[str] = None
    total_minutes: int = Field(default=0, ge=0)
    last_activity: Optional[datetime] = None


class KidBase(SQLModel):
    """Modelo base de niño con campos comunes."""
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=3, le=18)
    avatar: str = Field(default="boy-smile")
    birth_date: date
    preferences: KidPreferences = Field(
        default_factory=KidPreferences, sa_column_kwargs={"type_": "JSON"})
    stats: KidStats = Field(default_factory=KidStats,
                            sa_column_kwargs={"type_": "JSON"})


class Kid(KidBase, table=True):
    """
    Modelo de niño para la base de datos.

    Representa a los niños asociados a un usuario tutor.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="kids")


class KidCreate(KidBase):
    """Modelo para crear un nuevo niño."""
    pass


class KidRead(KidBase):
    """Modelo para leer datos de niño."""
    id: UUID
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class KidUpdate(SQLModel):
    """Modelo para actualizar datos de niño."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=3, le=18)
    avatar: Optional[str] = None
    birth_date: Optional[date] = None
    preferences: Optional[KidPreferences] = None


class KidStatsResponse(SQLModel):
    """Respuesta con estadísticas detalladas del niño."""
    total_routines: int
    this_week_completed: int
    this_week_assigned: int
    current_streak: int
    longest_streak: int
    favorite_category: Optional[str]
    total_minutes: int
    last_activity: Optional[datetime]
    weekly_progress: List[dict] = Field(default_factory=list)
