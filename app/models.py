from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey, ARRAY, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class EjercicioCatalogo(Base):
    __tablename__ = "ejercicios_catalogo"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)
    grupo_muscular = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    ejercicios_plan = relationship("EjercicioPlan", back_populates="ejercicio_catalogo")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))
    fecha_registro = Column(Date, server_default=func.current_date())
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    planes_semanales = relationship("PlanSemanal", back_populates="cliente", cascade="all, delete-orphan")

class PlanSemanal(Base):
    __tablename__ = "planes_semanales"
    __table_args__ = (
        UniqueConstraint('cliente_id', 'numero_semana', name='uq_cliente_semana'),
    )

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    numero_semana = Column(Integer, nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    notas = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    cliente = relationship("Cliente", back_populates="planes_semanales")
    ejercicios = relationship("EjercicioPlan", back_populates="plan_semanal", cascade="all, delete-orphan")

class EjercicioPlan(Base):
    __tablename__ = "ejercicios_plan"
    __table_args__ = (
        UniqueConstraint('plan_semanal_id', 'orden', name='uq_plan_orden'),
    )

    id = Column(Integer, primary_key=True, index=True)
    plan_semanal_id = Column(Integer, ForeignKey("planes_semanales.id", ondelete="CASCADE"), nullable=False)
    ejercicio_catalogo_id = Column(Integer, ForeignKey("ejercicios_catalogo.id"), nullable=False)
    orden = Column(Integer, nullable=False)

    # Configuración de series (JSON array de repeticiones)
    series_config = Column(JSON, nullable=False)  # Ej: [10, 10, 10] o [10, 14, 12]

    # CRONÓMETROS
    tiempo_ejercicio_segundos = Column(Integer, default=60)
    tiempo_descanso_segundos = Column(Integer, default=90)

    # Progresión aplicada
    tipo_progresion = Column(String(50))  # 'lineal_series', 'lineal_reps', 'ondulante_series', 'ondulante_reps', 'ninguna'
    valor_progresion = Column(Integer, default=0)

    notas_ejercicio = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    plan_semanal = relationship("PlanSemanal", back_populates="ejercicios")
    ejercicio_catalogo = relationship("EjercicioCatalogo", back_populates="ejercicios_plan")
    completados = relationship("EjercicioCompletado", back_populates="ejercicio_plan", cascade="all, delete-orphan")

class EjercicioCompletado(Base):
    __tablename__ = "ejercicios_completados"

    id = Column(Integer, primary_key=True, index=True)
    ejercicio_plan_id = Column(Integer, ForeignKey("ejercicios_plan.id", ondelete="CASCADE"), nullable=False)
    fecha_completado = Column(DateTime(timezone=True), server_default=func.now())

    # Registro detallado de series
    series_completadas = Column(JSON, nullable=False)
    # Ejemplo: [
    #   {"serie": 1, "reps_objetivo": 10, "reps_realizadas": 10, "completada": true},
    #   {"serie": 2, "reps_objetivo": 10, "reps_realizadas": 8, "completada": false}
    # ]

    # TRACKING DE TIEMPOS
    tiempo_ejercicio_real_segundos = Column(Integer)
    tiempo_descanso_real_segundos = Column(Integer)

    completado_totalmente = Column(Boolean, default=False)
    notas_cliente = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    ejercicio_plan = relationship("EjercicioPlan", back_populates="completados")
