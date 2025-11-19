# Gym Training App - Backend API

API REST construida con FastAPI para gestión de planes de entrenamiento con sistema de progresiones automáticas y cronómetros integrados.

## Características Principales

- Sistema de gestión de clientes y planes semanales
- Progresiones automáticas (lineal/ondulante para series/repeticiones)
- Cronómetros integrados para ejercicios y descansos
- Tracking de tiempos reales vs objetivos
- Registro detallado de series completadas
- Estadísticas de progreso
- API RESTful documentada con Swagger

## Estructura del Proyecto

```
gym_javier/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada FastAPI
│   ├── database.py             # Configuración de DB
│   ├── models.py               # Modelos SQLAlchemy
│   ├── schemas.py              # Schemas Pydantic
│   └── routers/
│       ├── __init__.py
│       ├── admin.py            # Endpoints para web admin
│       ├── mobile.py           # Endpoints para app móvil
│       └── progresiones.py     # Lógica de progresiones
├── requirements.txt
├── .env
├── project.md
└── README.md
```

## Estado del Proyecto

✅ **Backend 100% sincronizado con la base de datos PostgreSQL**

La base de datos ya fue inicializada con `init.sql` y contiene:
- 4 ejercicios en el catálogo
- 1 cliente demo (Juan Pérez)
- 2 planes semanales (Semana 1 y 2)
- Ejercicios con diferentes progresiones aplicadas

Ver [SINCRONIZACION.md](./SINCRONIZACION.md) para detalles completos.

## Instalación

### 1. Clonar el repositorio o crear el proyecto

```bash
cd C:\Proyectos\gym_javier
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

El archivo `.env` ya está configurado con la base de datos PostgreSQL de Railway.

### 6. Ejecutar el servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Verificar que funciona

El servidor debería iniciar en: http://localhost:8000

Deberías ver un mensaje de bienvenida al abrir la URL raíz.

## Uso de la API

### Acceder a la documentación interactiva

Una vez el servidor esté corriendo, abre tu navegador en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

#### Admin Web

- `GET /api/admin/clientes` - Listar todos los clientes
- `POST /api/admin/clientes` - Crear un nuevo cliente
- `GET /api/admin/cliente/{cliente_id}/planes` - Ver planes de un cliente
- `POST /api/admin/cliente/{cliente_id}/plan` - Crear plan semanal
- `GET /api/admin/ejercicios-catalogo` - Listar ejercicios disponibles
- `POST /api/admin/ejercicios-catalogo` - Crear nuevo ejercicio

#### App Móvil

- `GET /api/mobile/cliente/{cliente_id}/plan-actual` - Obtener plan activo
- `POST /api/mobile/ejercicio/completar` - Registrar ejercicio completado
- `GET /api/mobile/cliente/{cliente_id}/estadisticas` - Ver estadísticas
- `GET /api/mobile/ejercicio/{ejercicio_plan_id}/cronometro` - Config de cronómetro

#### Progresiones (Endpoint Clave)

- `POST /api/progresiones/crear-plan-con-progresiones` - Crear plan con progresiones automáticas

## Pruebas Rápidas con Datos Existentes

La base de datos ya contiene datos demo. Puedes probar inmediatamente:

### 1. Listar clientes existentes

```bash
curl http://localhost:8000/api/admin/clientes
```

Debería retornar a Juan Pérez (cliente_id: 1)

### 2. Ver plan semanal actual del cliente

```bash
curl http://localhost:8000/api/mobile/cliente/1/plan-actual
```

### 3. Ver todos los planes del cliente

```bash
curl http://localhost:8000/api/admin/cliente/1/planes
```

### 4. Ver estadísticas de entrenamiento

```bash
curl http://localhost:8000/api/mobile/cliente/1/estadisticas
```

### 5. Listar ejercicios del catálogo

```bash
curl http://localhost:8000/api/admin/ejercicios-catalogo
```

## Ejemplos de Creación de Nuevos Datos

### 1. Crear un nuevo cliente

```bash
curl -X POST "http://localhost:8000/api/admin/clientes" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Javier García",
    "email": "javier@example.com",
    "telefono": "+34 666 777 888"
  }'
```

### 2. Crear ejercicios en el catálogo

```bash
curl -X POST "http://localhost:8000/api/admin/ejercicios-catalogo" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Press Banca",
    "descripcion": "Ejercicio para pecho",
    "grupo_muscular": "Pecho"
  }'
```

### 3. Crear plan semanal inicial

```bash
curl -X POST "http://localhost:8000/api/admin/cliente/1/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "numero_semana": 1,
    "fecha_inicio": "2025-11-18",
    "fecha_fin": "2025-11-24",
    "notas": "Primera semana de entrenamiento",
    "ejercicios": [
      {
        "ejercicio_catalogo_id": 1,
        "orden": 1,
        "series_config": [10, 10, 10],
        "tiempo_ejercicio_segundos": 60,
        "tiempo_descanso_segundos": 90
      }
    ]
  }'
```

### 4. Crear plan Semana 3 con progresiones automáticas (ENDPOINT CLAVE - DEMO)

Este es el endpoint más importante. Crea la Semana 3 basándose en la Semana 2 con progresiones aplicadas:

```bash
curl -X POST "http://localhost:8000/api/progresiones/crear-plan-con-progresiones" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "semana_anterior": 2,
    "fecha_inicio": "2025-12-02",
    "fecha_fin": "2025-12-08",
    "progresiones": [
      {
        "cliente_id": 1,
        "semana_anterior": 2,
        "tipo_progresion": "lineal_reps",
        "ejercicio_catalogo_id": 1,
        "valor": 2
      },
      {
        "cliente_id": 1,
        "semana_anterior": 2,
        "tipo_progresion": "lineal_series",
        "ejercicio_catalogo_id": 2,
        "valor": 1
      },
      {
        "cliente_id": 1,
        "semana_anterior": 2,
        "tipo_progresion": "ondulante_reps",
        "ejercicio_catalogo_id": 3,
        "valor": 0
      }
    ]
  }'
```

**Explicación de las progresiones aplicadas:**
- **Búlgaras** (ejercicio_id: 1): +2 reps en todas las series (lineal_reps)
- **Curl Mancuerna** (ejercicio_id: 2): +1 serie manteniendo reps (lineal_series)
- **Press Banca** (ejercicio_id: 3): Convertir a patrón ondulante [8, 12, 10] (ondulante_reps)
- **Sentadilla** (ejercicio_id: 4): Sin cambios (no se especifica progresión)

**Resultado esperado:**
```json
{
  "message": "Plan creado con progresiones",
  "plan_id": 3,
  "numero_semana": 3
}
```

Luego puedes verificar el nuevo plan:
```bash
curl http://localhost:8000/api/admin/cliente/1/planes
```

## Tipos de Progresiones

1. **lineal_series**: Añade series manteniendo repeticiones
   - Ejemplo: [10, 10, 10] → [10, 10, 10, 10]

2. **lineal_reps**: Aumenta repeticiones en todas las series
   - Ejemplo: [10, 10, 10] → [12, 12, 12]

3. **ondulante_series**: Añade series con patrón variable
   - Ejemplo: [10, 10, 10] → [10, 10, 10, 12]

4. **ondulante_reps**: Convierte a patrón ondulante
   - Ejemplo: [10, 10, 10] → [10, 14, 12]

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para interacción con base de datos
- **PostgreSQL**: Base de datos relacional
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI

## Estado del Proyecto

- [x] Backend completo con FastAPI
- [x] Sistema de progresiones automáticas
- [x] Cronómetros integrados
- [x] API documentada
- [x] Panel web admin (React) - LISTO PARA DEMO
- [ ] App móvil (Flutter)

## Panel Web Administrativo

El panel web está ubicado en `C:\Proyectos\web-admin\` y está 100% funcional para la demo.

### Ejecutar el Panel Web

```bash
cd C:\Proyectos\web-admin
npm install
npm run dev
```

Abre http://localhost:5173 para ver el panel.

### Funcionalidades Implementadas

- Dashboard con lista de clientes
- Vista detallada de planes semanales por cliente
- **Interfaz de progresiones** (funcionalidad clave para demo):
  - Botones para seleccionar tipo de progresión por ejercicio
  - Progresión Lineal en Series/Repeticiones
  - Progresión Ondulante en Series/Repeticiones
  - Creación automática de nueva semana con progresiones aplicadas

Ver el README en `C:\Proyectos\web-admin\README.md` para más detalles.

## Próximos Pasos

1. Desarrollar app móvil con Flutter
2. Agregar autenticación al panel web
3. Implementar creación de nuevos clientes desde la web
4. Añadir más tipos de progresiones

## Licencia

Este proyecto es privado y está en desarrollo.
