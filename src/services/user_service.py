"""
Servicios para la gestión de usuarios.

Este módulo contiene la lógica de negocio para el manejo de usuarios,
incluyendo creación, autenticación y validación.
"""

from datetime import datetime
from typing import Optional
import hashlib

from sqlmodel import Session, select
from src.models.user import User, UserCreate, UserType, SubscriptionType


def hash_password(password: str) -> str:
    """
    Hashear una contraseña de forma simple (solo para desarrollo).
    En producción usar bcrypt o argon2.
    """
    return f"hashed_{password}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verificar una contraseña contra su hash.
    """
    return hashed_password == f"hashed_{password}"


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Obtener un usuario por su username.
    """
    statement = select(User).where(User.username == username)
    return db.exec(statement).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Obtener un usuario por su ID.
    """
    statement = select(User).where(User.id == user_id)
    return db.exec(statement).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Crear un nuevo usuario en la base de datos.
    """
    # Hashear la contraseña
    hashed_password = hash_password(user_data.password)

    # Crear el usuario
    db_user = User(
        name=user_data.name,
        username=user_data.username,
        password_hash=hashed_password,
        user_type=user_data.user_type,
        subscription=user_data.subscription,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Guardar en la base de datos
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def username_exists(db: Session, username: str) -> bool:
    """
    Verificar si un username ya existe en la base de datos.
    """
    user = get_user_by_username(db, username)
    return user is not None


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Autenticar un usuario con username y contraseña.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
