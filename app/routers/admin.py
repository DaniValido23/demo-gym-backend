from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.get("/clientes", response_model=List[schemas.Cliente])
def listar_clientes(db: Session = Depends(get_db)):
    """Lista todos los clientes activos"""
    return db.query(models.Cliente).filter(models.Cliente.activo == True).all()

@router.post("/clientes", response_model=schemas.Cliente)
def crear_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    """Crea un nuevo cliente"""
    nuevo_cliente = models.Cliente(
        nombre=cliente.nombre,
        email=cliente.email,
        telefono=cliente.telefono
    )
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente

@router.get("/cliente/{cliente_id}/planes", response_model=List[schemas.PlanSemanal])
def listar_planes_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Lista todos los planes de un cliente"""
    planes = db.query(models.PlanSemanal).filter(
        models.PlanSemanal.cliente_id == cliente_id
    ).order_by(
        models.PlanSemanal.numero_semana.desc()
    ).all()

    # Construir respuesta con ejercicios
    resultado = []
    for plan in planes:
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

        ejercicios_lista = []
        for ejercicio_plan, ejercicio_nombre in ejercicios:
            ejercicio_dict = {
                'id': ejercicio_plan.id,
                'plan_semanal_id': ejercicio_plan.plan_semanal_id,
                'ejercicio_catalogo_id': ejercicio_plan.ejercicio_catalogo_id,
                'orden': ejercicio_plan.orden,
                'series_config': ejercicio_plan.series_config,
                'tiempo_ejercicio_segundos': ejercicio_plan.tiempo_ejercicio_segundos,
                'tiempo_descanso_segundos': ejercicio_plan.tiempo_descanso_segundos,
                'notas_ejercicio': ejercicio_plan.notas_ejercicio,
                'tipo_progresion': ejercicio_plan.tipo_progresion,
                'valor_progresion': ejercicio_plan.valor_progresion,
                'ejercicio_nombre': ejercicio_nombre
            }
            ejercicios_lista.append(ejercicio_dict)

        plan_dict = {
            'id': plan.id,
            'cliente_id': plan.cliente_id,
            'numero_semana': plan.numero_semana,
            'fecha_inicio': plan.fecha_inicio,
            'fecha_fin': plan.fecha_fin,
            'notas': plan.notas,
            'ejercicios': ejercicios_lista
        }
        resultado.append(plan_dict)

    return resultado

@router.post("/cliente/{cliente_id}/plan", response_model=schemas.PlanSemanal)
def crear_plan_semanal(
    cliente_id: int,
    plan: schemas.PlanSemanalCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo plan semanal para un cliente
    Usado cuando el cliente no tiene historial (Semana 1)
    """
    # Verificar que el cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Crear plan semanal
    nuevo_plan = models.PlanSemanal(
        cliente_id=cliente_id,
        numero_semana=plan.numero_semana,
        fecha_inicio=plan.fecha_inicio,
        fecha_fin=plan.fecha_fin,
        notas=plan.notas
    )

    db.add(nuevo_plan)
    db.flush()  # Para obtener el ID

    # Agregar ejercicios
    for ejercicio_data in plan.ejercicios:
        nuevo_ejercicio = models.EjercicioPlan(
            plan_semanal_id=nuevo_plan.id,
            ejercicio_catalogo_id=ejercicio_data.ejercicio_catalogo_id,
            orden=ejercicio_data.orden,
            series_config=ejercicio_data.series_config,
            tiempo_ejercicio_segundos=ejercicio_data.tiempo_ejercicio_segundos,
            tiempo_descanso_segundos=ejercicio_data.tiempo_descanso_segundos,
            notas_ejercicio=ejercicio_data.notas_ejercicio,
            tipo_progresion='ninguna',
            valor_progresion=0
        )
        db.add(nuevo_ejercicio)

    db.commit()
    db.refresh(nuevo_plan)

    return nuevo_plan

@router.put("/cliente/{cliente_id}/plan/{plan_id}", response_model=schemas.PlanSemanal)
def actualizar_plan_semanal(
    cliente_id: int,
    plan_id: int,
    plan_update: schemas.PlanSemanalUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un plan semanal completo (fechas, notas y ejercicios)
    Permite editar TODO del plan activo
    """
    # Verificar que el cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Obtener el plan
    plan = db.query(models.PlanSemanal).filter(
        models.PlanSemanal.id == plan_id,
        models.PlanSemanal.cliente_id == cliente_id
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    # Actualizar campos del plan
    plan.fecha_inicio = plan_update.fecha_inicio
    plan.fecha_fin = plan_update.fecha_fin
    plan.notas = plan_update.notas

    # Eliminar todos los ejercicios existentes del plan
    db.query(models.EjercicioPlan).filter(
        models.EjercicioPlan.plan_semanal_id == plan.id
    ).delete()

    # Crear nuevos ejercicios según el payload
    for ejercicio_data in plan_update.ejercicios:
        nuevo_ejercicio = models.EjercicioPlan(
            plan_semanal_id=plan.id,
            ejercicio_catalogo_id=ejercicio_data.ejercicio_catalogo_id,
            orden=ejercicio_data.orden,
            series_config=ejercicio_data.series_config,
            tiempo_ejercicio_segundos=ejercicio_data.tiempo_ejercicio_segundos,
            tiempo_descanso_segundos=ejercicio_data.tiempo_descanso_segundos,
            notas_ejercicio=ejercicio_data.notas_ejercicio
        )
        db.add(nuevo_ejercicio)

    db.commit()
    db.refresh(plan)

    return plan

@router.get("/ejercicios-catalogo", response_model=List[schemas.EjercicioCatalogo])
def listar_ejercicios_catalogo(db: Session = Depends(get_db)):
    """Lista todos los ejercicios disponibles en el catálogo"""
    return db.query(models.EjercicioCatalogo).all()

@router.post("/ejercicios-catalogo", response_model=schemas.EjercicioCatalogo)
def crear_ejercicio_catalogo(
    ejercicio: schemas.EjercicioCatalogoCreate,
    db: Session = Depends(get_db)
):
    """Crea un nuevo ejercicio en el catálogo"""
    nuevo_ejercicio = models.EjercicioCatalogo(
        nombre=ejercicio.nombre,
        descripcion=ejercicio.descripcion,
        grupo_muscular=ejercicio.grupo_muscular
    )
    db.add(nuevo_ejercicio)
    db.commit()
    db.refresh(nuevo_ejercicio)
    return nuevo_ejercicio
