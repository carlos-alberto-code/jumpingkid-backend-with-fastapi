"""
Modelo de respuestas comunes para la API.

Este módulo define estructuras de respuesta estándar
para mantener consistencia en toda la API.
"""

from datetime import datetime
from typing import Optional, TypeVar, Generic, Any, Dict, List
from pydantic import BaseModel

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Respuesta estándar de la API."""
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    errors: Optional[Dict[str, List[str]]] = None
    timestamp: datetime = datetime.utcnow()


class PaginationMetadata(BaseModel):
    """Metadatos de paginación."""
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada estándar."""
    success: bool = True
    data: List[T]
    pagination: PaginationMetadata
    timestamp: datetime = datetime.utcnow()


class HealthResponse(BaseModel):
    """Respuesta del health check."""
    status: str = "healthy"
    timestamp: datetime = datetime.utcnow()
    version: str = "1.0.0"


class ErrorDetail(BaseModel):
    """Detalle de error."""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Respuesta de error estándar."""
    success: bool = False
    data: Optional[Any] = None
    message: str
    errors: Optional[Dict[str, List[str]]] = None
    timestamp: datetime = datetime.utcnow()


# Respuestas específicas para stats y analytics
class WeeklyProgress(BaseModel):
    """Progreso semanal."""
    date: str  # YYYY-MM-DD
    completed: int
    assigned: int
    minutes: Optional[int] = 0


class ProgressByCategory(BaseModel):
    """Progreso por categoría."""
    sessions: int
    minutes: int


class MostActiveKid(BaseModel):
    """Niño más activo."""
    kid_id: str
    name: str
    sessions_completed: int


class PopularExercise(BaseModel):
    """Ejercicio popular."""
    exercise_id: str
    name: str
    count: int


class CalendarData(BaseModel):
    """Datos del calendario."""
    status: str  # "completed", "assigned", "skipped"
    minutes: int


class AnalyticsOverview(BaseModel):
    """Analytics generales."""
    total_kids: int
    total_sessions_completed: int
    total_minutes_exercised: int
    average_completion_rate: float
    most_active_kid: Optional[MostActiveKid] = None
    popular_exercises: List[PopularExercise] = []


class KidAnalytics(BaseModel):
    """Analytics específicos de un niño."""
    kid_id: str
    name: str
    total_sessions: int
    sessions_completed: int
    completion_rate: float
    total_minutes: int
    current_streak: int
    favorite_category: Optional[str] = None
    weekly_activity: List[WeeklyProgress] = []
    progress_by_category: Dict[str, ProgressByCategory] = {}


# Achievement models
class Achievement(BaseModel):
    """Logro/Achievement."""
    id: str
    name: str
    description: str
    icon: str
    earned_at: datetime


class RecentActivity(BaseModel):
    """Actividad reciente."""
    date: str
    routine_name: str
    minutes: int
    exercises_completed: int
    rating: int


class ProgressData(BaseModel):
    """Datos de progreso del niño."""
    kid_id: str
    current_level: int
    experience_points: int
    next_level_points: int
    achievements: List[Achievement] = []
    recent_activities: List[RecentActivity] = []
    calendar_data: Dict[str, CalendarData] = {}
