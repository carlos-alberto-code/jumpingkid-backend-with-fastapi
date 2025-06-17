"""
Modelos de datos para la aplicación JumpingKids.

Este módulo contiene todos los modelos de SQLModel utilizados
en la aplicación.
"""

from .user import User, UserCreate, UserRead, UserUpdate, UserType, SubscriptionType
from .kid import Kid, KidCreate, KidRead, KidUpdate, KidPreferences, KidStats, KidStatsResponse, DifficultyLevel, PreferredTime
from .exercise import Exercise, ExerciseCreate, ExerciseRead, ExerciseUpdate, ExerciseCategory, AgeGroup
from .routine import Routine, RoutineCreate, RoutineRead, RoutineUpdate, RoutineExercise, RoutineExerciseBase, RoutineExerciseRead
from .assignment import Assignment, AssignmentCreate, AssignmentRead, AssignmentUpdate, AssignmentComplete, AssignmentStatus
from .training import TrainingSession, TrainingSessionCreate, TrainingSessionRead, TrainingSessionUpdate, ExerciseCompletion, SessionCompletion, TrainingSessionStatus
from .responses import APIResponse, PaginatedResponse, HealthResponse, ErrorResponse, AnalyticsOverview, KidAnalytics, ProgressData

__all__ = [
    # User models
    "User", "UserCreate", "UserRead", "UserUpdate", "UserType", "SubscriptionType",
    # Kid models
    "Kid", "KidCreate", "KidRead", "KidUpdate", "KidPreferences", "KidStats", "KidStatsResponse", "DifficultyLevel", "PreferredTime",
    # Exercise models
    "Exercise", "ExerciseCreate", "ExerciseRead", "ExerciseUpdate", "ExerciseCategory", "AgeGroup",
    # Routine models
    "Routine", "RoutineCreate", "RoutineRead", "RoutineUpdate", "RoutineExercise", "RoutineExerciseBase", "RoutineExerciseRead",
    # Assignment models
    "Assignment", "AssignmentCreate", "AssignmentRead", "AssignmentUpdate", "AssignmentComplete", "AssignmentStatus",
    # Training models
    "TrainingSession", "TrainingSessionCreate", "TrainingSessionRead", "TrainingSessionUpdate", "ExerciseCompletion", "SessionCompletion", "TrainingSessionStatus",
    # Response models
    "APIResponse", "PaginatedResponse", "HealthResponse", "ErrorResponse", "AnalyticsOverview", "KidAnalytics", "ProgressData",
]
