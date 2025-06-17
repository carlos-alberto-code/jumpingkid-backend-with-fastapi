"""
Servicio para la gestión de ejercicios (Exercises).

Este módulo contiene la lógica de negocio para la gestión de ejercicios,
incluyendo CRUD operations y filtrado por categorías.
"""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status

from src.models import Exercise, ExerciseCreate, ExerciseRead, ExerciseUpdate, ExerciseCategory, AgeGroup


class ExerciseService:
    """Servicio para gestión de ejercicios."""

    def __init__(self, db: Session):
        self.db = db

    def get_exercises(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        age_group: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[int] = None
    ) -> List[ExerciseRead]:
        """Obtener ejercicios con filtros opcionales."""
        statement = select(Exercise).where(Exercise.is_active == True)

        # Filtros opcionales
        if category:
            statement = statement.where(Exercise.category == category)

        if difficulty:
            statement = statement.where(Exercise.difficulty == difficulty)

        if age_group:
            statement = statement.where(Exercise.age_group == age_group)

        if search:
            search_filter = or_(
                Exercise.name.like(f"%{search}%"),
                Exercise.description.like(f"%{search}%")
            )
            statement = statement.where(search_filter)

        # Solo mostrar ejercicios del sistema y ejercicios personalizados del usuario
        if user_id:
            access_filter = or_(
                Exercise.created_by == "system",
                Exercise.created_by == str(user_id)
            )
            statement = statement.where(access_filter)
        else:
            statement = statement.where(Exercise.created_by == "system")

        # Paginación
        statement = statement.offset(offset).limit(limit)

        exercises = self.db.exec(statement).all()
        return [ExerciseRead.model_validate(exercise) for exercise in exercises]

    def get_exercise_by_id(self, exercise_id: UUID, user_id: Optional[int] = None) -> Optional[ExerciseRead]:
        """Obtener un ejercicio por ID."""
        statement = select(Exercise).where(
            and_(
                Exercise.id == exercise_id,
                Exercise.is_active == True
            )
        )

        # Verificar acceso si se proporciona user_id
        if user_id:
            access_filter = or_(
                Exercise.created_by == "system",
                Exercise.created_by == str(user_id)
            )
            statement = statement.where(access_filter)

        exercise = self.db.exec(statement).first()
        if exercise:
            return ExerciseRead.model_validate(exercise)
        return None

    def create_exercise(self, exercise_data: ExerciseCreate, user_id: int) -> ExerciseRead:
        """Crear un nuevo ejercicio personalizado."""
        exercise = Exercise(
            **exercise_data.model_dump(),
            created_by=str(user_id),
            is_custom=True
        )
        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        return ExerciseRead.model_validate(exercise)

    def update_exercise(self, exercise_id: UUID, exercise_data: ExerciseUpdate, user_id: int) -> Optional[ExerciseRead]:
        """Actualizar un ejercicio personalizado."""
        statement = select(Exercise).where(
            and_(
                Exercise.id == exercise_id,
                Exercise.created_by == str(user_id),
                Exercise.is_active == True
            )
        )
        exercise = self.db.exec(statement).first()

        if not exercise:
            return None

        # Actualizar campos
        update_data = exercise_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(exercise, field, value)

        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        return ExerciseRead.model_validate(exercise)

    def delete_exercise(self, exercise_id: UUID, user_id: int) -> bool:
        """Eliminar un ejercicio personalizado (soft delete)."""
        statement = select(Exercise).where(
            and_(
                Exercise.id == exercise_id,
                Exercise.created_by == str(user_id),
                Exercise.is_active == True
            )
        )
        exercise = self.db.exec(statement).first()

        if not exercise:
            return False

        exercise.is_active = False
        self.db.add(exercise)
        self.db.commit()
        return True

    def get_categories(self) -> List[str]:
        """Obtener lista de categorías disponibles."""
        return [category.value for category in ExerciseCategory]

    def get_age_groups(self) -> List[str]:
        """Obtener lista de grupos de edad disponibles."""
        return [age_group.value for age_group in AgeGroup]
