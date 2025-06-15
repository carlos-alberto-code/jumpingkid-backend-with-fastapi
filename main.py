"""
Módulo principal de la API JumpingKid Backend.

Este módulo contiene la aplicación FastAPI que proporciona endpoints
para la aplicación JumpingKid, incluyendo endpoints de salud,
información de la API y funcionalidades principales.
"""

from fastapi import FastAPI

# Crear instancia de FastAPI
app = FastAPI(
    title="JumpingKid Backend API",
    description="API backend para la aplicación JumpingKid",
    version="0.1.0"
)

# Endpoint de prueba básico


@app.get("/")
async def root():
    """
    Endpoint raíz de la API.

    Returns:
        dict: Mensaje de bienvenida confirmando que el servidor está funcionando.
    """
    return {"message": "¡Hola! El servidor de JumpingKid está funcionando correctamente"}

# Endpoint de health check


@app.get("/health")
async def health_check():
    """
    Endpoint de verificación de estado de la API.

    Returns:
        dict: Estado del servidor y mensaje de confirmación.
    """
    return {"status": "ok", "message": "Servidor funcionando"}

# Endpoint de información de la API


@app.get("/info")
async def api_info():
    """
    Endpoint de información de la API.

    Returns:
        dict: Información básica de la API incluyendo nombre, versión y descripción.
    """
    return {
        "name": "JumpingKid Backend API",
        "version": "0.1.0",
        "description": "API backend para la aplicación JumpingKid"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
