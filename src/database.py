"""
Configuración de base de datos para JumpingKids.

Este módulo maneja la configuración de SQLModel, la creación de sesiones
y la configuración de la base de datos.
"""

import os
from sqlmodel import SQLModel, create_engine, Session, select

# URL de la base de datos (configurar según el entorno)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jumpingkids.db")

# Crear engine de SQLModel
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith(
        "sqlite") else {},
    echo=True  # Para debug, quitar en producción
)


def get_db():
    """
    Dependency para obtener una sesión de base de datos.

    Yields:
        Session: Sesión de base de datos SQLModel
    """
    with Session(engine) as session:
        yield session


def create_tables():
    """Crear todas las tablas en la base de datos."""
    SQLModel.metadata.create_all(engine)


def init_db():
    """Inicializar la base de datos creando las tablas."""
    create_tables()


def create_test_users():
    """Crear usuarios de prueba en la base de datos."""
    from src.models.user import User, UserType, SubscriptionType, UserCreate
    from src.services.user_service import create_user

    with Session(engine) as session:
        # Verificar si ya existen usuarios de prueba
        existing_test_user = session.exec(
            select(User).where(User.username == "test@example.com")
        ).first()

        if not existing_test_user:
            # Crear usuario de prueba
            test_user = UserCreate(
                name="Usuario Test",
                username="test@example.com",
                password="password123",
                user_type=UserType.KID,
                subscription=SubscriptionType.FREE
            )
            create_user(session, test_user)

            # Crear usuario carlos
            carlos_user = UserCreate(
                name="Carlos Mendoza",
                username="carlos",
                password="123456",
                user_type=UserType.KID,
                subscription=SubscriptionType.PREMIUM
            )
            create_user(session, carlos_user)

            print("Usuarios de prueba creados exitosamente")


def init_db_with_test_data():
    """Inicializar la base de datos con datos de prueba."""
    init_db()
    create_test_users()
