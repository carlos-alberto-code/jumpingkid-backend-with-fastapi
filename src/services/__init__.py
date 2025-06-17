"""
Servicios de negocio para la aplicación JumpingKids.

Este módulo contiene todos los servicios que implementan
la lógica de negocio de la aplicación.
"""

from . import user_service
from .kid_service import KidService
from .exercise_service import ExerciseService
from .routine_service import RoutineService
from .assignment_service import AssignmentService
from .training_service import TrainingService

__all__ = [
    "user_service",
    "KidService",
    "ExerciseService",
    "RoutineService",
    "AssignmentService",
    "TrainingService",
]
