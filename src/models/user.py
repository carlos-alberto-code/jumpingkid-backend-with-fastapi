"""
Modelo de usuario para la aplicación JumpingKids.

Este módulo define el modelo de datos para los usuarios de la aplicación,
incluyendo tipos de usuario y tipos de suscripción.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .kid import Kid


class UserType(str, Enum):
    """Tipos de usuario disponibles en la aplicación."""
    KID = "kid"
    TUTOR = "tutor"


class SubscriptionType(str, Enum):
    """Tipos de suscripción disponibles."""
    FREE = "free"
    PREMIUM = "premium"


class UserBase(SQLModel):
    """Modelo base de usuario con campos comunes."""
    name: str
    username: str = Field(unique=True, index=True)
    user_type: UserType
    subscription: SubscriptionType = SubscriptionType.FREE


class User(UserBase, table=True):
    """
    Modelo de usuario para la base de datos.

    Representa a los usuarios de la aplicación JumpingKids,
    tanto niños como tutores.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    # Relationships
    kids: List["Kid"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """Modelo para crear un nuevo usuario."""
    password: str


class UserRead(UserBase):
    """Modelo para leer datos de usuario (sin password_hash)."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserUpdate(SQLModel):
    """Modelo para actualizar datos de usuario."""
    name: Optional[str] = None
    username: Optional[str] = None
    user_type: Optional[UserType] = None
    subscription: Optional[SubscriptionType] = None
