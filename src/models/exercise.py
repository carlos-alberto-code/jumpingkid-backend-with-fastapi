"""
Modelo de ejercicios para la aplicación JumpingKids.

Este módulo define el modelo de datos para los ejercicios,
incluyendo categorías, dificultades y configuraciones.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum

from sqlmodel import SQLModel, Field


class ExerciseCategory(str, Enum):
    """Categorías de ejercicios disponibles."""
    CARDIO = "Cardio"
    FUERZA = "Fuerza"
    FLEXIBILIDAD = "Flexibilidad"
    EQUILIBRIO = "Equilibrio"
    COORDINACION = "Coordinación"


class AgeGroup(str, Enum):
    """Grupos de edad para ejercicios."""
    TODDLER = "3-5"
    CHILD = "6-8"
    PRETEEN = "9-12"


class ExerciseBase(SQLModel):
    """Modelo base de ejercicio con campos comunes."""
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=1000)
    category: ExerciseCategory
    # DifficultyLevel from kid.py
    difficulty: str = Field(default="Principiante")
    duration_seconds: int = Field(ge=10, le=600)  # 10 segundos a 10 minutos
    age_group: AgeGroup
    instructions: List[str] = Field(
        default_factory=list, sa_column_kwargs={"type_": "JSON"})
    benefits: List[str] = Field(
        default_factory=list, sa_column_kwargs={"type_": "JSON"})
    equipment_needed: List[str] = Field(
        default_factory=list, sa_column_kwargs={"type_": "JSON"})
    video_url: Optional[str] = None
    image_url: Optional[str] = None


class Exercise(ExerciseBase, table=True):
    """
    Modelo de ejercicio para la base de datos.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_by: str = Field(default="system")  # "system" or user_id
    is_custom: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class ExerciseCreate(ExerciseBase):
    """Modelo para crear un nuevo ejercicio."""
    pass


class ExerciseRead(ExerciseBase):
    """Modelo para leer datos de ejercicio."""
    id: UUID
    created_by: str
    is_custom: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class ExerciseUpdate(SQLModel):
    """Modelo para actualizar datos de ejercicio."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[ExerciseCategory] = None
    difficulty: Optional[str] = None
    duration_seconds: Optional[int] = Field(None, ge=10, le=600)
    age_group: Optional[AgeGroup] = None
    instructions: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    equipment_needed: Optional[List[str]] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
