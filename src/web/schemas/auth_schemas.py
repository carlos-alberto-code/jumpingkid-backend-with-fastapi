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

    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "password": "contraseña123"
            }
        }


class UserResponse(BaseModel):
    """Esquema para la respuesta de datos del usuario."""

    id: int
    email: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "usuario@ejemplo.com",
                "first_name": "Juan",
                "last_name": "Pérez",
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-02T12:00:00Z"
            }
        }


class AuthResponse(BaseModel):
    """Esquema para la respuesta de autenticación."""

    success: bool
    message: str
    data: Optional[UserResponse] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Usuario autenticado exitosamente",
                "data": {
                    "id": 1,
                    "email": "usuario@ejemplo.com",
                    "first_name": "Juan",
                    "last_name": "Pérez",
                    "created_at": "2023-01-01T12:00:00Z"
                },
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer"
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
