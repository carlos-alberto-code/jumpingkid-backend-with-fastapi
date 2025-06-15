"""
Módulo de router de autenticación para el backend de JumpingKid.

Este módulo contiene los endpoints de autenticación incluyendo registro, inicio de sesión,
y manejo de tokens JWT para la aplicación FastAPI de JumpingKid.
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import jwt

# Importar schemas
from src.web.schemas.auth_schemas import (
    UserSignupRequest,
    UserSigninRequest,
    UserResponse,
    AuthResponse,
    CheckEmailResponse,
)

# Configuración temporal (después moveremos a config)
SECRET_KEY = "temp-secret-key-for-development"
ALGORITHM = "HS256"

# Crear router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Base de datos mock temporal
mock_users_db: dict[str, dict[str, Any]] = {}


def create_access_token(user_data: dict) -> str:
    """Crear token JWT."""
    payload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Endpoint para registrar nuevos usuarios en la plataforma",
)
async def signup(request: UserSignupRequest):
    """
    Registrar nuevo usuario.
    
    Crea una nueva cuenta de usuario con los datos proporcionados.
    """
    # Verificar si el email ya existe
    if request.email in mock_users_db:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "message": "El email ya está registrado",
                "data": None,
                "access_token": None,
                "token_type": None
            },
        )

    # Crear usuario mock
    user_id = len(mock_users_db) + 1
    user_data = {
        "id": user_id,
        "email": request.email,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "password_hash": f"hashed_{request.password}",  # Mock hash
    }

    # Guardar en "base de datos" mock
    mock_users_db[request.email] = user_data

    # Crear token
    access_token = create_access_token(user_data)

    # Crear respuesta
    user_response = UserResponse(
        id=user_data["id"],
        email=user_data["email"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"]
    )

    return AuthResponse(
        success=True,
        message="Usuario registrado exitosamente",
        data=user_response,
        access_token=access_token,
        token_type="bearer"
    )


@router.post(
    "/signin",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Endpoint para autenticar usuarios existentes",
)
async def signin(request: UserSigninRequest):
    """
    Iniciar sesión.
    
    Autentica al usuario con email y contraseña.
    """
    # Buscar usuario en "base de datos" mock
    user_data = mock_users_db.get(request.email)

    if not user_data:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "message": "Credenciales inválidas",
                "data": None,
                "access_token": None,
                "token_type": None
            },
        )

    # Verificar contraseña (mock)
    if user_data["password_hash"] != f"hashed_{request.password}":
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "message": "Credenciales inválidas",
                "data": None,
                "access_token": None,
                "token_type": None
            },
        )

    # Crear token
    access_token = create_access_token(user_data)

    # Crear respuesta
    user_response = UserResponse(
        id=user_data["id"],
        email=user_data["email"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"]
    )

    return AuthResponse(
        success=True,
        message="Inicio de sesión exitoso",
        data=user_response,
        access_token=access_token,
        token_type="bearer"
    )


@router.post(
    "/signout",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión",
    description="Endpoint para cerrar sesión del usuario",
)
async def signout():
    """
    Cerrar sesión.
    
    En una implementación real, aquí invalidaríamos el token.
    """
    return {
        "success": True,
        "message": "Sesión cerrada exitosamente",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get(
    "/check-email",
    response_model=CheckEmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar disponibilidad de email",
    description="Endpoint para verificar si un email ya está registrado",
)
async def check_email(email: str):
    """
    Verificar disponibilidad de email.
    
    Verifica si un email específico ya está registrado en el sistema.
    """
    exists = email in mock_users_db

    return CheckEmailResponse(
        success=True,
        exists=exists,
        message=f"Email {'ya registrado' if exists else 'disponible'}"
    )


@router.get(
    "/me",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario actual",
    description="Endpoint para obtener información del usuario autenticado",
)
async def get_current_user():
    """
    Obtener información del usuario actual.
    
    Este endpoint requiere autenticación (mock por ahora).
    """
    # Mock user data
    mock_user = UserResponse(
        id=1,
        email="mock@ejemplo.com",
        first_name="Usuario",
        last_name="Mock",
        created_at=datetime.utcnow(),
        updated_at=None
    )

    return AuthResponse(
        success=True,
        message="Usuario obtenido exitosamente",
        data=mock_user,
        access_token=None,
        token_type=None
    )
