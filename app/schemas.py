from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import date, datetime

# ============================================
# SCHEMAS PARA EJERCICIOS
# ============================================

class EjercicioCatalogoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    grupo_muscular: Optional[str] = None

class EjercicioCatalogoCreate(EjercicioCatalogoBase):
    pass

class EjercicioCatalogo(EjercicioCatalogoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# ============================================
# SCHEMAS PARA CLIENTES
# ============================================

class ClienteBase(BaseModel):
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id: int
    fecha_registro: date
    activo: bool

    model_config = ConfigDict(from_attributes=True)

# ============================================
# SCHEMAS PARA EJERCICIOS DEL PLAN
# ============================================

class EjercicioPlanBase(BaseModel):
    ejercicio_catalogo_id: int
    orden: int
    series_config: List[int]  # [10, 10, 10] o [10, 14, 12]
    tiempo_ejercicio_segundos: int = Field(default=60, description="Tiempo objetivo para completar el ejercicio")
    tiempo_descanso_segundos: int = Field(default=90, description="Tiempo de descanso después del ejercicio")
    notas_ejercicio: Optional[str] = None

class EjercicioPlanCreate(EjercicioPlanBase):
    pass

class EjercicioPlan(EjercicioPlanBase):
    id: int
    plan_semanal_id: int
    tipo_progresion: Optional[str] = None
    valor_progresion: Optional[int] = None
    ejercicio_nombre: Optional[str] = None  # Se llena desde el join

    model_config = ConfigDict(from_attributes=True)

# ============================================
# SCHEMAS PARA CRONÓMETROS (APP MÓVIL)
# ============================================

class CronometroConfig(BaseModel):
    """Configuración del cronómetro para un ejercicio"""
    ejercicio_plan_id: int
    ejercicio_nombre: str
    orden: int
    series_config: List[int]
    tiempo_ejercicio_segundos: int
    tiempo_descanso_segundos: int

class IniciarCronometro(BaseModel):
    """Request para iniciar cronómetro"""
    ejercicio_plan_id: int
    tipo: str = Field(..., description="'ejercicio' o 'descanso'")

class RegistrarTiempo(BaseModel):
    """Request para registrar tiempo transcurrido"""
    ejercicio_plan_id: int
    tipo: str = Field(..., description="'ejercicio' o 'descanso'")
    segundos_transcurridos: int

# ============================================
# SCHEMAS PARA SERIES COMPLETADAS
# ============================================

class SerieCompletada(BaseModel):
    serie: int
    reps_objetivo: int
    reps_realizadas: int
    completada: bool

class EjercicioCompletadoCreate(BaseModel):
    ejercicio_plan_id: int
    series_completadas: List[SerieCompletada]
    tiempo_ejercicio_real_segundos: Optional[int] = None
    tiempo_descanso_real_segundos: Optional[int] = None
    completado_totalmente: bool = False
    notas_cliente: Optional[str] = None

class EjercicioCompletado(BaseModel):
    id: int
    ejercicio_plan_id: int
    fecha_completado: datetime
    series_completadas: List[dict]
    tiempo_ejercicio_real_segundos: Optional[int] = None
    tiempo_descanso_real_segundos: Optional[int] = None
    completado_totalmente: bool
    notas_cliente: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# ============================================
# SCHEMAS PARA PLANES SEMANALES
# ============================================

class PlanSemanalBase(BaseModel):
    numero_semana: int
    fecha_inicio: date
    fecha_fin: date
    notas: Optional[str] = None

class PlanSemanalCreate(BaseModel):
    cliente_id: int
    numero_semana: int
    fecha_inicio: date
    fecha_fin: date
    ejercicios: List[EjercicioPlanCreate]
    notas: Optional[str] = None

class PlanSemanal(PlanSemanalBase):
    id: int
    cliente_id: int
    ejercicios: List[EjercicioPlan] = []

    model_config = ConfigDict(from_attributes=True)

# ============================================
# SCHEMAS PARA PROGRESIONES (WEB ADMIN)
# ============================================

class AplicarProgresion(BaseModel):
    cliente_id: int
    semana_anterior: int
    ejercicio_catalogo_id: int
    # Soporta múltiples progresiones por ejercicio
    tipos_progresion: List[str] = Field(
        default=[],
        description="Lista de tipos: 'lineal_series', 'lineal_reps', 'ondulante_series', 'ondulante_reps'"
    )
    valores: dict = Field(
        default={},
        description="Valores por tipo, ej: {'lineal_reps': 2, 'lineal_series': 1}"
    )

class CrearPlanDesdeSemanaAnterior(BaseModel):
    cliente_id: int
    semana_anterior: int
    fecha_inicio: date
    fecha_fin: date
    progresiones: List[AplicarProgresion] = []  # Lista de progresiones a aplicar

# ============================================
# SCHEMAS PARA APP MÓVIL
# ============================================

class PlanSemanalMovil(BaseModel):
    """Plan semanal optimizado para app móvil con cronómetros"""
    plan_id: int
    cliente_nombre: str
    numero_semana: int
    fecha_inicio: date
    fecha_fin: date
    ejercicios: List[dict]  # Lista de ejercicios con toda la info necesaria

    model_config = ConfigDict(from_attributes=True)

class EstadisticasEntrenamiento(BaseModel):
    """Estadísticas del entrenamiento para el cliente"""
    total_ejercicios: int
    ejercicios_completados: int
    porcentaje_completado: float
    tiempo_total_entrenamiento_segundos: int
    promedio_tiempo_por_ejercicio_segundos: float

# ============================================
# SCHEMAS PARA ACTUALIZACIÓN DE PLANES
# ============================================

class EjercicioPlanUpdate(BaseModel):
    """Schema para actualizar ejercicios dentro de un plan"""
    ejercicio_catalogo_id: int
    orden: int
    series_config: List[int]
    tiempo_ejercicio_segundos: int
    tiempo_descanso_segundos: int
    notas_ejercicio: Optional[str] = None

class PlanSemanalUpdate(BaseModel):
    """Schema para actualizar un plan semanal completo"""
    fecha_inicio: date
    fecha_fin: date
    notas: Optional[str] = None
    ejercicios: List[EjercicioPlanUpdate]
