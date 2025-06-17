"""
Dependencies para la aplicación FastAPI.

Este módulo contiene las dependencias compartidas,
incluyendo autenticación y autorización.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from src.database import get_db
from src.models import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtener el usuario actual a partir del token JWT.

    Por ahora es una implementación simplificada.
    En una implementación real, aquí se validaría el JWT token.
    """
    # Implementación simplificada - en producción validar JWT
    # Por ahora retornamos un usuario de prueba
    # TODO: Implementar validación real del token JWT

    # Buscar usuario por username (simulando validación de token)
    statement = select(User).where(User.username == "test@example.com")
    user = db.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Obtener el usuario actual de forma opcional.
    Retorna None si no hay token o es inválido.
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
