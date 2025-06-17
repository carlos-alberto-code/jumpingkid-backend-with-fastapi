"""main.py
Archivo principal para iniciar la aplicación FastAPI de JumpingKids.
Este archivo configura la aplicación, incluye los routers y define los endpoints básicos."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Importar routers
from src.web.routers import auth, kids, exercises, routines, assignments, training, utils

# Importar configuración de base de datos
from src.database import init_db_with_test_data

# Crear aplicación FastAPI
app = FastAPI(
    title="JumpingKids API",
    description="API para la aplicación de ejercicios JumpingKids",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Inicializar base de datos


@app.on_event("startup")
async def startup_event():
    """Inicializar la base de datos al iniciar la aplicación."""
    init_db_with_test_data()

# Configurar CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Incluir routers con prefijo /api
app.include_router(auth.router, prefix="/api")
app.include_router(kids.router, prefix="/api")
app.include_router(exercises.router, prefix="/api")
app.include_router(routines.router, prefix="/api")
app.include_router(assignments.router, prefix="/api")
app.include_router(training.router, prefix="/api")
app.include_router(utils.router, prefix="/api")

# Health check endpoint


@app.get("/api/health")
async def health_check():
    """Endpoint para verificar que el servidor está funcionando."""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "JumpingKids API is running!",
            "version": "1.0.0"
        }
    )

# Root endpoint


@app.get("/")
async def root():
    """Endpoint raíz con información básica."""
    return {
        "message": "JumpingKids API",
        "docs": "/docs",
        "health": "/api/health"
    }

# Ejecutar servidor si se ejecuta directamente
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Recarga automática en desarrollo
        log_level="info"
    )
