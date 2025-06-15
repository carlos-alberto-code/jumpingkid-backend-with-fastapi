"""
Esquemas de autenticación para la API.

Este módulo contiene los modelos Pydantic utilizados para validar
los datos de entrada y salida de los endpoints de autenticación.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserSignupRequest(BaseModel):
    """Esquema para la solicitud de registro de usuario."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "password": "contraseña123",
                "first_name": "Juan",
                "last_name": "Pérez"
            }
        }


class UserSigninRequest(BaseModel):
    """Esquema para la solicitud de inicio de sesión."""

    username: str  # Cambiar de email a username
    password: str
    remember_me: bool | None = False

    class Config:
        json_schema_extra = {
            "example": {
                "username": "usuario@ejemplo.com",
                "password": "contraseña123",
                "remember_me": False
            }
        }


class AuthTokens(BaseModel):
    """Esquema para los tokens de autenticación."""

    accessToken: str      # camelCase como espera frontend
    refreshToken: str
    expiresIn: int        # en segundos
    tokenType: str = "Bearer"


class UserResponse(BaseModel):
    """Esquema para la respuesta de datos del usuario."""

    id: str               # Como string, no int
    name: Optional[str] = None
    email: str
    userType: Optional[str] = None
    subscription: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "name": "Juan Pérez",
                "email": "usuario@ejemplo.com",
                "userType": "kid",
                "subscription": "free",
                "createdAt": "2023-01-01T12:00:00Z",
                "updatedAt": "2023-01-02T12:00:00Z"
            }
        }


class SignInResponse(BaseModel):
    """Esquema para la respuesta de inicio de sesión."""

    user: UserResponse
    tokens: AuthTokens
    lastLogin: Optional[str] = None


class AuthResponse(BaseModel):
    """Esquema para la respuesta de autenticación."""

    success: bool
    message: str
    data: Optional[SignInResponse] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Inicio de sesión exitoso",
                "data": {
                    "user": {
                        "id": "1",
                        "name": "Juan Pérez",
                        "email": "usuario@ejemplo.com",
                        "userType": "kid",
                        "subscription": "free"
                    },
                    "tokens": {
                        "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refreshToken": "refresh_token_here",
                        "expiresIn": 3600,
                        "tokenType": "Bearer"
                    },
                    "lastLogin": "2023-01-01T12:00:00Z"
                }
            }
        }


class CheckEmailResponse(BaseModel):
    """Esquema para la respuesta de verificación de email."""

    success: bool
    exists: bool
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "exists": False,
                "message": "Email disponible"
            }
        }
