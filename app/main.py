from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import admin, mobile, progresiones

# Crear tablas (en producción usar Alembic)
# NOTA: Las tablas ya existen en la DB (creadas con init.sql), comentado para evitar conflictos
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gym Training App API",
    description="API para gestión de planes de entrenamiento con cronómetros",
    version="1.0.0"
)

# CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: ["http://localhost:3000", "http://tudominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Web"])
app.include_router(mobile.router, prefix="/api/mobile", tags=["Mobile App"])
app.include_router(progresiones.router, prefix="/api/progresiones", tags=["Progresiones"])

@app.get("/")
def read_root():
    return {
        "message": "Gym Training App API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
