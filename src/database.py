"""
Configuración de base de datos para JumpingKids.

Este módulo maneja la configuración de SQLModel, la creación de sesiones
y la configuración de la base de datos.
"""

import os
from sqlmodel import SQLModel, create_engine, Session, select

# Importar todos los modelos para que SQLModel los reconozca
from src.models import (
    User, Kid, Exercise, Routine, RoutineExercise,
    Assignment, TrainingSession
)

# URL de la base de datos (configurar según el entorno)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jumpingkids.db")

# Crear engine de SQLModel
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith(
        "sqlite") else {},
    echo=True  # Para debug, quitar en producción
)


def get_db():
    """
    Dependency para obtener una sesión de base de datos.

    Yields:
        Session: Sesión de base de datos SQLModel
    """
    with Session(engine) as session:
        yield session


def create_tables():
    """Crear todas las tablas en la base de datos."""
    SQLModel.metadata.create_all(engine)


def init_db():
    """Inicializar la base de datos creando las tablas."""
    create_tables()


def create_test_users():
    """Crear usuarios de prueba en la base de datos."""
    from src.models.user import User, UserType, SubscriptionType, UserCreate
    from src.services.user_service import create_user

    with Session(engine) as session:
        # Verificar si ya existen usuarios de prueba
        existing_test_user = session.exec(
            select(User).where(User.username == "test@example.com")
        ).first()

        if not existing_test_user:
            # Crear usuario de prueba
            test_user = UserCreate(
                name="Usuario Test",
                username="test@example.com",
                password="password123",
                user_type=UserType.TUTOR,  # Cambiar a TUTOR para poder tener niños
                subscription=SubscriptionType.FREE
            )
            create_user(session, test_user)

            # Crear usuario carlos
            carlos_user = UserCreate(
                name="Carlos Mendoza",
                username="carlos",
                password="123456",
                user_type=UserType.TUTOR,  # Cambiar a TUTOR
                subscription=SubscriptionType.PREMIUM
            )
            create_user(session, carlos_user)

            print("Usuarios de prueba creados exitosamente")


def create_test_exercises():
    """Crear ejercicios de prueba en la base de datos."""
    from src.models import Exercise, ExerciseCategory, AgeGroup

    with Session(engine) as session:
        # Verificar si ya existen ejercicios
        existing_exercise = session.exec(
            select(Exercise).where(Exercise.name == "Saltos de Rana")
        ).first()

        if not existing_exercise:
            exercises = [
                Exercise(
                    name="Saltos de Rana",
                    description="Saltar como una rana por 30 segundos",
                    category=ExerciseCategory.CARDIO,
                    difficulty="Principiante",
                    duration_seconds=30,
                    age_group=AgeGroup.CHILD,
                    instructions=["Ponte en cuclillas",
                                  "Salta hacia adelante", "Aterriza suavemente"],
                    benefits=["Fortalece piernas", "Mejora coordinación"],
                    equipment_needed=[],
                    image_url="/images/exercises/frog-jumps.jpg",
                    created_by="system",
                    is_custom=False
                ),
                Exercise(
                    name="Flexiones de Rodillas",
                    description="Flexiones apoyando las rodillas en el suelo",
                    category=ExerciseCategory.FUERZA,
                    difficulty="Principiante",
                    duration_seconds=45,
                    age_group=AgeGroup.CHILD,
                    instructions=["Apoya las rodillas",
                                  "Baja el pecho al suelo", "Empuja hacia arriba"],
                    benefits=["Fortalece brazos",
                              "Desarrolla fuerza del core"],
                    equipment_needed=[],
                    image_url="/images/exercises/knee-pushups.jpg",
                    created_by="system",
                    is_custom=False
                ),
                Exercise(
                    name="Estiramiento de Gato",
                    description="Estiramiento imitando el movimiento de un gato",
                    category=ExerciseCategory.FLEXIBILIDAD,
                    difficulty="Principiante",
                    duration_seconds=60,
                    age_group=AgeGroup.CHILD,
                    instructions=[
                        "Ponte en cuatro patas", "Arquea la espalda hacia arriba", "Relaja hacia abajo"],
                    benefits=["Mejora flexibilidad", "Relaja la espalda"],
                    equipment_needed=["Mat"],
                    image_url="/images/exercises/cat-stretch.jpg",
                    created_by="system",
                    is_custom=False
                ),
                Exercise(
                    name="Equilibrio del Flamenco",
                    description="Mantener equilibrio en una pierna como un flamenco",
                    category=ExerciseCategory.EQUILIBRIO,
                    difficulty="Intermedio",
                    duration_seconds=30,
                    age_group=AgeGroup.CHILD,
                    instructions=["Levanta una pierna",
                                  "Mantén el equilibrio", "Cambia de pierna"],
                    benefits=["Mejora equilibrio", "Fortalece piernas"],
                    equipment_needed=[],
                    image_url="/images/exercises/flamingo-balance.jpg",
                    created_by="system",
                    is_custom=False
                ),
                Exercise(
                    name="Marcha de Soldado",
                    description="Marchar en el lugar levantando las rodillas",
                    category=ExerciseCategory.COORDINACION,
                    difficulty="Principiante",
                    duration_seconds=45,
                    age_group=AgeGroup.CHILD,
                    instructions=[
                        "Marcha en el lugar", "Levanta las rodillas alto", "Balancea los brazos"],
                    benefits=["Mejora coordinación",
                              "Ejercicio cardiovascular"],
                    equipment_needed=[],
                    image_url="/images/exercises/soldier-march.jpg",
                    created_by="system",
                    is_custom=False
                )
            ]

            for exercise in exercises:
                session.add(exercise)

            session.commit()
            print("Ejercicios de prueba creados exitosamente")


def create_test_routines():
    """Crear rutinas de prueba en la base de datos."""
    from src.models import Routine, RoutineExercise, Exercise, ExerciseCategory, AgeGroup

    with Session(engine) as session:
        # Verificar si ya existen rutinas
        existing_routine = session.exec(
            select(Routine).where(Routine.name ==
                                  "Rutina Matutina Energizante")
        ).first()

        if not existing_routine:
            # Obtener ejercicios existentes
            exercises = session.exec(select(Exercise)).all()
            if len(exercises) >= 3:
                routine = Routine(
                    name="Rutina Matutina Energizante",
                    description="Perfecta para empezar el día con energía",
                    category=ExerciseCategory.CARDIO.value,
                    difficulty="Principiante",
                    duration_minutes=15,
                    age_group=AgeGroup.CHILD.value,
                    created_by="system",
                    is_custom=False,
                    popularity_score=4.8,
                    total_assignments=0
                )
                session.add(routine)
                session.commit()
                session.refresh(routine)

                # Agregar ejercicios a la rutina
                routine_exercises = [
                    RoutineExercise(
                        routine_id=routine.id,
                        exercise_id=exercises[0].id,
                        order=1,
                        duration_seconds=30,
                        repetitions=None,
                        rest_seconds=10
                    ),
                    RoutineExercise(
                        routine_id=routine.id,
                        exercise_id=exercises[1].id,
                        order=2,
                        duration_seconds=45,
                        repetitions=None,
                        rest_seconds=15
                    ),
                    RoutineExercise(
                        routine_id=routine.id,
                        exercise_id=exercises[2].id,
                        order=3,
                        duration_seconds=60,
                        repetitions=None,
                        rest_seconds=10
                    )
                ]

                for routine_exercise in routine_exercises:
                    session.add(routine_exercise)

                session.commit()
                print("Rutinas de prueba creadas exitosamente")


def init_db_with_test_data():
    """Inicializar la base de datos con datos de prueba."""
    init_db()
    create_test_users()
    create_test_exercises()
    create_test_routines()
    create_test_exercises()
    create_test_routines()
