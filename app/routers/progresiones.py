from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from typing import List

router = APIRouter()

def aplicar_progresion_lineal_series(series_config: List[int], valor: int = 1) -> List[int]:
    """Aumenta el número de series manteniendo las mismas reps"""
    if not series_config:
        return []
    # Añadir N series con las mismas reps que la última serie
    reps_por_serie = series_config[0]  # Asumimos todas iguales en lineal
    return series_config + [reps_por_serie] * valor

def aplicar_progresion_lineal_reps(series_config: List[int], valor: int = 1) -> List[int]:
    """Aumenta las reps de todas las series"""
    return [reps + valor for reps in series_config]

def aplicar_progresion_ondulante_series(series_config: List[int], valor: int = 1) -> List[int]:
    """Añade series con patrón ondulante"""
    if len(series_config) < 2:
        return series_config + [series_config[0]] * valor

    # Calcular patrón ondulante basado en series existentes
    promedio = sum(series_config) // len(series_config)
    nueva_serie = promedio + (valor * 2)  # Pico más alto
    return series_config + [nueva_serie]

def aplicar_progresion_ondulante_reps(series_config: List[int]) -> List[int]:
    """
    Convierte progresión lineal a ondulante
    Ejemplo: [10, 10, 10] -> [10, 14, 12]
    """
    if len(series_config) < 3:
        return series_config

    base = series_config[0]
    return [base, base + 4, base + 2]

@router.post("/crear-plan-con-progresiones")
def crear_plan_con_progresiones(
    data: schemas.CrearPlanDesdeSemanaAnterior,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo plan basado en la semana anterior aplicando progresiones
    ESTE ES EL ENDPOINT CLAVE PARA LA DEMO
    """
    # Buscar plan de semana anterior
    plan_anterior = db.query(models.PlanSemanal).filter(
        models.PlanSemanal.cliente_id == data.cliente_id,
        models.PlanSemanal.numero_semana == data.semana_anterior
    ).first()

    if not plan_anterior:
        raise HTTPException(status_code=404, detail="Plan de semana anterior no encontrado")

    # Crear nuevo plan
    nuevo_plan = models.PlanSemanal(
        cliente_id=data.cliente_id,
        numero_semana=data.semana_anterior + 1,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        notas="Plan generado con progresiones automáticas"
    )

    db.add(nuevo_plan)
    db.flush()

    # Obtener ejercicios de semana anterior
    ejercicios_anteriores = db.query(models.EjercicioPlan).filter(
        models.EjercicioPlan.plan_semanal_id == plan_anterior.id
    ).order_by(models.EjercicioPlan.orden).all()

    # Crear diccionario de progresiones a aplicar
    progresiones_dict = {
        prog.ejercicio_catalogo_id: prog
        for prog in data.progresiones
    }

    # Copiar ejercicios aplicando progresiones
    for ejercicio_anterior in ejercicios_anteriores:
        # Obtener configuración base
        nueva_config = ejercicio_anterior.series_config.copy()
        tipo_progresion = 'ninguna'
        valor_progresion = 0

        # Verificar si hay progresión para este ejercicio
        if ejercicio_anterior.ejercicio_catalogo_id in progresiones_dict:
            progresion = progresiones_dict[ejercicio_anterior.ejercicio_catalogo_id]
            tipo_progresion = progresion.tipo_progresion
            valor_progresion = progresion.valor

            # Aplicar la progresión correspondiente
            if progresion.tipo_progresion == 'lineal_series':
                nueva_config = aplicar_progresion_lineal_series(nueva_config, progresion.valor)
            elif progresion.tipo_progresion == 'lineal_reps':
                nueva_config = aplicar_progresion_lineal_reps(nueva_config, progresion.valor)
            elif progresion.tipo_progresion == 'ondulante_series':
                nueva_config = aplicar_progresion_ondulante_series(nueva_config, progresion.valor)
            elif progresion.tipo_progresion == 'ondulante_reps':
                nueva_config = aplicar_progresion_ondulante_reps(nueva_config)

        # Crear nuevo ejercicio
        nuevo_ejercicio = models.EjercicioPlan(
            plan_semanal_id=nuevo_plan.id,
            ejercicio_catalogo_id=ejercicio_anterior.ejercicio_catalogo_id,
            orden=ejercicio_anterior.orden,
            series_config=nueva_config,
            tiempo_ejercicio_segundos=ejercicio_anterior.tiempo_ejercicio_segundos,
            tiempo_descanso_segundos=ejercicio_anterior.tiempo_descanso_segundos,
            tipo_progresion=tipo_progresion,
            valor_progresion=valor_progresion,
            notas_ejercicio=ejercicio_anterior.notas_ejercicio
        )

        db.add(nuevo_ejercicio)

    db.commit()
    db.refresh(nuevo_plan)

    return {
        "message": "Plan creado con progresiones",
        "plan_id": nuevo_plan.id,
        "numero_semana": nuevo_plan.numero_semana
    }
