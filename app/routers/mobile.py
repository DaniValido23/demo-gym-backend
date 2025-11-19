from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.get("/cliente/{cliente_id}/plan-actual", response_model=schemas.PlanSemanalMovil)
def obtener_plan_actual(cliente_id: int, db: Session = Depends(get_db)):
    """
    Obtiene el plan de entrenamiento actual del cliente
    Incluye configuración de cronómetros para cada ejercicio
    """
    # Buscar plan activo (fecha actual entre fecha_inicio y fecha_fin)
    plan = db.query(models.PlanSemanal).filter(
        models.PlanSemanal.cliente_id == cliente_id,
        models.PlanSemanal.fecha_inicio <= date.today(),
        models.PlanSemanal.fecha_fin >= date.today()
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="No hay plan activo para esta semana")

    # Obtener ejercicios con información completa
    ejercicios = db.query(
        models.EjercicioPlan,
        models.EjercicioCatalogo.nombre
    ).join(
        models.EjercicioCatalogo
    ).filter(
        models.EjercicioPlan.plan_semanal_id == plan.id
    ).order_by(
        models.EjercicioPlan.orden
    ).all()

    # Formatear ejercicios con cronómetros
    ejercicios_formateados = []
    for ejercicio_plan, ejercicio_nombre in ejercicios:
        # Verificar si ya fue completado
        completado = db.query(models.EjercicioCompletado).filter(
            models.EjercicioCompletado.ejercicio_plan_id == ejercicio_plan.id
        ).first()

        ejercicios_formateados.append({
            "id": ejercicio_plan.id,
            "nombre": ejercicio_nombre,
            "orden": ejercicio_plan.orden,
            "series_config": ejercicio_plan.series_config,
            "tiempo_ejercicio_segundos": ejercicio_plan.tiempo_ejercicio_segundos,
            "tiempo_descanso_segundos": ejercicio_plan.tiempo_descanso_segundos,
            "notas": ejercicio_plan.notas_ejercicio,
            "completado": completado is not None,
            "series_completadas": completado.series_completadas if completado else []
        })

    return schemas.PlanSemanalMovil(
        plan_id=plan.id,
        cliente_nombre=plan.cliente.nombre,
        numero_semana=plan.numero_semana,
        fecha_inicio=plan.fecha_inicio,
        fecha_fin=plan.fecha_fin,
        ejercicios=ejercicios_formateados
    )

@router.post("/ejercicio/completar")
def completar_ejercicio(
    data: schemas.EjercicioCompletadoCreate,
    db: Session = Depends(get_db)
):
    """
    Registra la completación de un ejercicio
    Incluye tiempos reales de ejercicio y descanso del cronómetro
    """
    # Verificar que el ejercicio existe
    ejercicio_plan = db.query(models.EjercicioPlan).filter(
        models.EjercicioPlan.id == data.ejercicio_plan_id
    ).first()

    if not ejercicio_plan:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    # Verificar si ya fue completado anteriormente
    completado_existente = db.query(models.EjercicioCompletado).filter(
        models.EjercicioCompletado.ejercicio_plan_id == data.ejercicio_plan_id
    ).first()

    if completado_existente:
        # Actualizar registro existente
        completado_existente.series_completadas = [s.model_dump() for s in data.series_completadas]
        completado_existente.tiempo_ejercicio_real_segundos = data.tiempo_ejercicio_real_segundos
        completado_existente.tiempo_descanso_real_segundos = data.tiempo_descanso_real_segundos
        completado_existente.completado_totalmente = data.completado_totalmente
        completado_existente.notas_cliente = data.notas_cliente
        completado_existente.fecha_completado = func.now()

        db.commit()
        db.refresh(completado_existente)
        return {"message": "Ejercicio actualizado", "id": completado_existente.id}

    # Crear nuevo registro
    nuevo_completado = models.EjercicioCompletado(
        ejercicio_plan_id=data.ejercicio_plan_id,
        series_completadas=[s.model_dump() for s in data.series_completadas],
        tiempo_ejercicio_real_segundos=data.tiempo_ejercicio_real_segundos,
        tiempo_descanso_real_segundos=data.tiempo_descanso_real_segundos,
        completado_totalmente=data.completado_totalmente,
        notas_cliente=data.notas_cliente
    )

    db.add(nuevo_completado)
    db.commit()
    db.refresh(nuevo_completado)

    return {"message": "Ejercicio completado registrado", "id": nuevo_completado.id}

@router.get("/cliente/{cliente_id}/estadisticas", response_model=schemas.EstadisticasEntrenamiento)
def obtener_estadisticas(cliente_id: int, db: Session = Depends(get_db)):
    """
    Obtiene estadísticas del entrenamiento actual del cliente
    """
    # Buscar plan activo
    plan = db.query(models.PlanSemanal).filter(
        models.PlanSemanal.cliente_id == cliente_id,
        models.PlanSemanal.fecha_inicio <= date.today(),
        models.PlanSemanal.fecha_fin >= date.today()
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="No hay plan activo")

    # Contar ejercicios totales
    total_ejercicios = db.query(models.EjercicioPlan).filter(
        models.EjercicioPlan.plan_semanal_id == plan.id
    ).count()

    # Contar ejercicios completados
    ejercicios_completados = db.query(models.EjercicioCompletado).join(
        models.EjercicioPlan
    ).filter(
        models.EjercicioPlan.plan_semanal_id == plan.id
    ).count()

    # Calcular porcentaje
    porcentaje = (ejercicios_completados / total_ejercicios * 100) if total_ejercicios > 0 else 0

    # Calcular tiempo total de entrenamiento
    tiempos = db.query(
        func.sum(models.EjercicioCompletado.tiempo_ejercicio_real_segundos)
    ).join(
        models.EjercicioPlan
    ).filter(
        models.EjercicioPlan.plan_semanal_id == plan.id
    ).scalar()

    tiempo_total = tiempos or 0
    promedio = (tiempo_total / ejercicios_completados) if ejercicios_completados > 0 else 0

    return schemas.EstadisticasEntrenamiento(
        total_ejercicios=total_ejercicios,
        ejercicios_completados=ejercicios_completados,
        porcentaje_completado=round(porcentaje, 2),
        tiempo_total_entrenamiento_segundos=tiempo_total,
        promedio_tiempo_por_ejercicio_segundos=round(promedio, 2)
    )

@router.get("/ejercicio/{ejercicio_plan_id}/cronometro", response_model=schemas.CronometroConfig)
def obtener_config_cronometro(ejercicio_plan_id: int, db: Session = Depends(get_db)):
    """
    Obtiene la configuración del cronómetro para un ejercicio específico
    Útil cuando la app necesita recargar un ejercicio en progreso
    """
    ejercicio = db.query(
        models.EjercicioPlan,
        models.EjercicioCatalogo.nombre
    ).join(
        models.EjercicioCatalogo
    ).filter(
        models.EjercicioPlan.id == ejercicio_plan_id
    ).first()

    if not ejercicio:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    ejercicio_plan, ejercicio_nombre = ejercicio

    return schemas.CronometroConfig(
        ejercicio_plan_id=ejercicio_plan.id,
        ejercicio_nombre=ejercicio_nombre,
        orden=ejercicio_plan.orden,
        series_config=ejercicio_plan.series_config,
        tiempo_ejercicio_segundos=ejercicio_plan.tiempo_ejercicio_segundos,
        tiempo_descanso_segundos=ejercicio_plan.tiempo_descanso_segundos
    )
