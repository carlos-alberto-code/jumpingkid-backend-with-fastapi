"""
Módulo de router de autenticación para el backend de JumpingKid.

Este módulo contiene los endpoints de autenticación incluyendo registro, inicio de sesión,
y manejo de tokens JWT para la aplicación FastAPI de JumpingKid.
"""

from datetime import datetime, timedelta
from typing import Any
import re

from fastapi import APIRouter, status, Query, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session
import jwt

# Importar database y modelos
from src.database import get_db
from src.services.user_service import username_exists

# Importar schemas
from src.web.schemas.auth_schemas import (
    UserSignupRequest,
    UserSigninRequest,
    UserResponse,
    AuthResponse,
    SignInResponse,
    AuthTokens,
    CheckEmailResponse,
)

# Configuración temporal (después moveremos a config)
SECRET_KEY = "temp-secret-key-for-development"
ALGORITHM = "HS256"

# Palabras reservadas para usernames
RESERVED_USERNAMES = {
    "admin", "root", "user", "test", "api", "www", "ftp", "mail",
    "email", "help", "support", "info", "contact", "about", "news",
    "blog", "forum", "chat", "dev", "demo", "null", "undefined",
    "system", "config", "settings", "jumpingkids", "tutor", "kid"
}

# Crear router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Base de datos mock temporal
mock_users_db: dict[str, dict[str, Any]] = {}

# Agregar usuarios de prueba
test_user = {
    "id": 1,
    "username": "test@example.com",
    "email": "test@example.com",
    "name": "Usuario Test",
    "user_type": "kid",
    "subscription": "free",
    "created_at": datetime.utcnow(),
    "updated_at": None,
    "password_hash": "hashed_password123",  # Mock hash for "password123"
}
mock_users_db["test@example.com"] = test_user

# Agregar usuario carlos para testing
carlos_user = {
    "id": 2,
    "username": "carlos",
    "email": "carlos@jumpingkids.com",
    "name": "Carlos Mendoza",
    "user_type": "kid",
    "subscription": "premium",
    "created_at": datetime.utcnow(),
    "updated_at": None,
    "password_hash": "hashed_123456",  # Mock hash for "123456"
}
mock_users_db["carlos@jumpingkids.com"] = carlos_user


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
        "username": request.email,  # Use email as username for signup
        "email": request.email,
        "name": f"{request.first_name} {request.last_name}",
        "first_name": request.first_name,
        "last_name": request.last_name,
        "user_type": "kid",  # Default user type
        "subscription": "free",  # Default subscription
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "password_hash": f"hashed_{request.password}",  # Mock hash
    }

    # Guardar en "base de datos" mock
    mock_users_db[request.email] = user_data

    # Crear token
    access_token = create_access_token(user_data)

    # Crear tokens en formato esperado
    tokens = AuthTokens(
        accessToken=access_token,
        refreshToken="mock_refresh_token",  # Temporal
        expiresIn=3600,  # 1 hora en segundos
        tokenType="Bearer"
    )

    # Crear respuesta de usuario
    user_response = UserResponse(
        id=str(user_data["id"]),  # Como string
        name=user_data["name"],
        email=user_data["email"],
        userType=user_data["user_type"],
        subscription=user_data["subscription"],
        createdAt=user_data["created_at"],
        updatedAt=user_data["updated_at"]
    )

    # Crear respuesta final
    signin_response = SignInResponse(
        user=user_response,
        tokens=tokens,
        lastLogin=datetime.utcnow().isoformat()
    )

    return AuthResponse(
        success=True,
        message="Usuario registrado exitosamente",
        data=signin_response
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

    Autentica al usuario con username y contraseña.
    """
    # Buscar usuario por username en "base de datos" mock
    user_data = None
    print(f"Buscando usuario: {request.username}")
    for _, user in mock_users_db.items():
        if user.get("username") == request.username:  # Buscar por username
            user_data = user
            break
    print(f"Usuario encontrado: {user_data}")
    if not user_data:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "message": "Credenciales inválidas",
                "data": None
            },
        )

    # Verificar contraseña (mock)
    if user_data["password_hash"] != f"hashed_{request.password}":
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "message": "Credenciales inválidas",
                "data": None
            },
        )

    # Crear token
    access_token = create_access_token(user_data)

    # Crear tokens en formato esperado
    tokens = AuthTokens(
        accessToken=access_token,
        refreshToken="mock_refresh_token",  # Temporal
        expiresIn=3600,  # 1 hora en segundos
        tokenType="Bearer"
    )

    # Crear respuesta de usuario
    user_response = UserResponse(
        id=str(user_data["id"]),  # Como string
        name=user_data.get("name"),
        email=user_data["email"],
        userType=user_data.get("user_type"),
        subscription=user_data.get("subscription"),
        createdAt=user_data["created_at"],
        updatedAt=user_data.get("updated_at")
    )

    # Crear respuesta final
    signin_response = SignInResponse(
        user=user_response,
        tokens=tokens,
        lastLogin=datetime.utcnow().isoformat()
    )

    return AuthResponse(
        success=True,
        message="Inicio de sesión exitoso",
        data=signin_response
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
    "/check-username",
    status_code=status.HTTP_200_OK,
    summary="Verificar disponibilidad de username en tiempo real",
    description="Endpoint para verificar si un username está disponible",
)
async def check_username_availability(
    username: str = Query(..., min_length=4, max_length=15),
    db: Session = Depends(get_db)
):
    """
    Verificar disponibilidad de username en tiempo real
    """
    try:
        # Normalizar username
        username = username.lower().strip()

        # Validar formato (solo alfanuméricos, guiones y guiones bajos)
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return {"available": False}

        # Verificar palabras reservadas
        if username in RESERVED_USERNAMES:
            return {"available": False}

        # Verificar si ya existe en la base de datos
        user_exists = username_exists(db, username)

        return {"available": not user_exists}

    except (ValueError, TypeError):
        # En caso de error, reportar como no disponible por seguridad
        return {"available": False}


@router.get(
    "/me",
    response_model=dict,
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
        id="1",
        name="Usuario Mock",
        email="mock@ejemplo.com",
        userType="kid",
        subscription="free",
        createdAt=datetime.utcnow(),
        updatedAt=None
    )

    return {
        "success": True,
        "message": "Usuario obtenido exitosamente",
        "data": mock_user
    }
