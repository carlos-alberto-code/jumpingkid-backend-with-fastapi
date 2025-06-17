"""
Servicio para la gestión de rutinas (Routines).

Este módulo contiene la lógica de negocio para la gestión de rutinas,
incluyendo CRUD operations y gestión de ejercicios asociados.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, and_, or_

from src.models import (
    Routine, RoutineCreate, RoutineRead, RoutineUpdate,
    RoutineExercise, RoutineExerciseRead,
    Exercise, ExerciseRead
)


class RoutineService:
    """Servicio para gestión de rutinas."""

    def __init__(self, db: Session):
        self.db = db

    def get_routines(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        duration_max: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[int] = None
    ) -> List[RoutineRead]:
        """Obtener rutinas con filtros opcionales."""
        statement = select(Routine).where(Routine.is_active == True)

        # Filtros opcionales
        if category:
            statement = statement.where(Routine.category == category)

        if difficulty:
            statement = statement.where(Routine.difficulty == difficulty)

        if duration_max:
            statement = statement.where(
                Routine.duration_minutes <= duration_max)

        if search:
            search_filter = or_(
                Routine.name.like(f"%{search}%"),
                Routine.description.like(f"%{search}%")
            )
            statement = statement.where(search_filter)

        # Solo mostrar rutinas del sistema y rutinas personalizadas del usuario
        if user_id:
            access_filter = or_(
                Routine.created_by == "system",
                Routine.created_by == str(user_id)
            )
            statement = statement.where(access_filter)
        else:
            statement = statement.where(Routine.created_by == "system")

        # Paginación
        statement = statement.offset(offset).limit(limit)

        routines = self.db.exec(statement).all()

        # Cargar rutinas con sus ejercicios
        routine_reads = []
        for routine in routines:
            routine_read = self._load_routine_with_exercises(routine)
            routine_reads.append(routine_read)

        return routine_reads

    def get_routine_by_id(self, routine_id: UUID, user_id: Optional[int] = None) -> Optional[RoutineRead]:
        """Obtener una rutina por ID con sus ejercicios."""
        statement = select(Routine).where(
            and_(
                Routine.id == routine_id,
                Routine.is_active == True
            )
        )

        # Verificar acceso si se proporciona user_id
        if user_id:
            access_filter = or_(
                Routine.created_by == "system",
                Routine.created_by == str(user_id)
            )
            statement = statement.where(access_filter)

        routine = self.db.exec(statement).first()
        if routine:
            return self._load_routine_with_exercises(routine)
        return None

    def create_routine(self, routine_data: RoutineCreate, user_id: int) -> RoutineRead:
        """Crear una nueva rutina personalizada."""
        # Separar ejercicios de los datos de rutina
        exercises_data = routine_data.exercises
        routine_dict = routine_data.model_dump()
        del routine_dict['exercises']

        # Crear rutina
        routine = Routine(
            **routine_dict,
            created_by=str(user_id),
            is_custom=True
        )
        self.db.add(routine)
        self.db.commit()
        self.db.refresh(routine)

        # Crear ejercicios asociados
        for exercise_data in exercises_data:
            routine_exercise = RoutineExercise(
                **exercise_data.model_dump(),
                routine_id=routine.id
            )
            self.db.add(routine_exercise)

        self.db.commit()

        # Retornar rutina con ejercicios cargados
        return self._load_routine_with_exercises(routine)

    def update_routine(self, routine_id: UUID, routine_data: RoutineUpdate, user_id: int) -> Optional[RoutineRead]:
        """Actualizar una rutina personalizada."""
        statement = select(Routine).where(
            and_(
                Routine.id == routine_id,
                Routine.created_by == str(user_id),
                Routine.is_active == True
            )
        )
        routine = self.db.exec(statement).first()

        if not routine:
            return None

        # Actualizar campos de rutina
        update_data = routine_data.model_dump(
            exclude_unset=True, exclude={'exercises'})
        for field, value in update_data.items():
            setattr(routine, field, value)

        routine.updated_at = datetime.utcnow()

        # Si se proporcionan ejercicios, actualizar la relación
        if routine_data.exercises is not None:
            # Eliminar ejercicios existentes
            existing_exercises = self.db.exec(
                select(RoutineExercise).where(
                    RoutineExercise.routine_id == routine_id)
            ).all()
            for exercise in existing_exercises:
                self.db.delete(exercise)

            # Crear nuevos ejercicios
            for exercise_data in routine_data.exercises:
                routine_exercise = RoutineExercise(
                    **exercise_data.model_dump(),
                    routine_id=routine.id
                )
                self.db.add(routine_exercise)

        self.db.add(routine)
        self.db.commit()
        self.db.refresh(routine)

        return self._load_routine_with_exercises(routine)

    def delete_routine(self, routine_id: UUID, user_id: int) -> bool:
        """Eliminar una rutina personalizada (soft delete)."""
        statement = select(Routine).where(
            and_(
                Routine.id == routine_id,
                Routine.created_by == str(user_id),
                Routine.is_active == True
            )
        )
        routine = self.db.exec(statement).first()

        if not routine:
            return False

        routine.is_active = False
        routine.updated_at = datetime.utcnow()
        self.db.add(routine)
        self.db.commit()
        return True

    def _load_routine_with_exercises(self, routine: Routine) -> RoutineRead:
        """Cargar rutina con sus ejercicios asociados."""
        # Obtener ejercicios de la rutina
        routine_exercises = self.db.exec(
            select(RoutineExercise).where(RoutineExercise.routine_id ==
                                          routine.id).order_by("order")
        ).all()

        exercises_read = []
        for routine_exercise in routine_exercises:
            # Cargar datos del ejercicio
            exercise = self.db.exec(
                select(Exercise).where(Exercise.id ==
                                       routine_exercise.exercise_id)
            ).first()

            if exercise:
                exercise_read = RoutineExerciseRead(
                    exercise_id=routine_exercise.exercise_id,
                    order=routine_exercise.order,
                    duration_seconds=routine_exercise.duration_seconds,
                    repetitions=routine_exercise.repetitions,
                    rest_seconds=routine_exercise.rest_seconds,
                    exercise=ExerciseRead(**exercise.model_dump())
                )
                exercises_read.append(exercise_read)

        return RoutineRead(
            **routine.model_dump(),
            exercises=exercises_read
        )
