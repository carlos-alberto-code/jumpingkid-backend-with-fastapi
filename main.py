# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Importar routers
from src.web.routers import auth

# Crear aplicación FastAPI
app = FastAPI(
    title="JumpingKids API",
    description="API para la aplicación de ejercicios JumpingKids",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

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
