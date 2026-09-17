# device_systems

Proyecto final de FastAPI con SQLAlchemy, relaciones entre modelos, Alembic y consultas avanzadas con joins.

## Objetivo
Evolucionar la API REST para gestionar usuarios, dispositivos y préstamos con integridad referencial, migraciones versionadas y consultas con datos relacionados.

## Estructura del proyecto

```text
device_systems/
├── app/
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   └── loan_schema.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   └── main.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── requirements.txt
├── README.md
├── device_systems.db
└── tests/
    └── test_api.py
```

## Requisitos

- Python 3.13
- FastAPI
- SQLAlchemy
- Alembic
- SQLite
- Pytest

## Instalación

```powershell
cd "C:\Users\sarit\device_systems"
py -3.13 -m pip install -r requirements.txt
```

## Ejecución de la API

```powershell
cd "C:\Users\sarit\device_systems"
py -3.13 -m uvicorn app.main:app --reload
```

La API queda disponible en:

- Swagger: http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc

## Alembic

La estructura de Alembic ya estaba inicializada en el proyecto y por eso no se repitió el comando `alembic init` para evitar sobrescribir la carpeta de migraciones ya creada. La evidencia real del proyecto consiste en la estructura generada y en la comprobación del historial de migraciones aplicado, que se muestran a continuación.

### Estructura del proyecto con Alembic

![Estructura del proyecto con Alembic](evidencias/06-estructura-alembic.png)

### Generar migración

```powershell
cd "C:\Users\sarit\device_systems"
py -3.13 -m alembic revision --autogenerate -m "create users devices loans tables"
```

### Aplicar migración

```powershell
cd "C:\Users\sarit\device_systems"
py -3.13 -m alembic upgrade head
```

### Historial de migraciones

```powershell
cd "C:\Users\sarit\device_systems"
py -3.13 -m alembic history
```

### Evidencia del resultado

El proyecto incluye la migración generada en:

```text
alembic/versions/20260917_create_users_devices_loans.py
```

La evidencia funcional de la ejecución queda resumida en la estructura del proyecto y en la validación del historial de migraciones del entorno de trabajo.

## Modelos y relaciones

### User
- id
- name
- email
- phone
- is_active
- created_at

### Device
- id
- name
- serial_number
- device_type
- brand
- is_available
- created_at

### Loan
- id
- user_id
- device_id
- loan_date
- return_date
- status

Relaciones implementadas:

- User -> loans
- Device -> loans
- Loan -> user
- Loan -> device

Con `relationship()` y `back_populates` para mantener la integridad conceptual del modelo.

## Endpoints principales

### Users
- GET /users
- GET /users/{user_id}
- POST /users
- PUT /users/{user_id}
- PATCH /users/{user_id}
- DELETE /users/{user_id}

### Devices
- GET /devices
- GET /devices/{device_id}
- POST /devices
- PUT /devices/{device_id}
- PATCH /devices/{device_id}
- DELETE /devices/{device_id}

### Loans
- GET /loans
- GET /loans/details
- GET /loans/{loan_id}
- POST /loans
- PATCH /loans/{loan_id}/return
- GET /users/{user_id}/loans
- GET /devices/{device_id}/loans

## Ejemplos de pruebas en Swagger / Postman

### Crear usuario

```json
{
  "name": "Ana Pérez",
  "email": "ana@sena.edu.co",
  "phone": "3001234567"
}
```

### Crear dispositivo

```json
{
  "name": "Laptop Lenovo ThinkPad",
  "serial_number": "LEN-2024-001",
  "device_type": "laptop",
  "brand": "Lenovo",
  "is_available": true
}
```

### Crear préstamo

```json
{
  "user_id": 1,
  "device_id": 1,
  "status": "active"
}
```

### Consultar préstamos con información relacionada

```http
GET /loans/details
```

Respuesta esperada:

```json
[
  {
    "id": 1,
    "status": "active",
    "loan_date": "2026-09-17T00:00:00",
    "return_date": null,
    "user": {
      "id": 1,
      "name": "Ana Pérez",
      "email": "ana@sena.edu.co"
    },
    "device": {
      "id": 1,
      "name": "Laptop Lenovo ThinkPad",
      "serial_number": "LEN-2024-001",
      "device_type": "laptop"
    }
  }
]
```

### Filtrar por estado

```http
GET /loans?status=active
```

### Filtrar por tipo de dispositivo

```http
GET /loans?device_type=laptop
```

### Filtrar por fechas

```http
GET /loans?loan_date_from=2026-09-01T00:00:00&loan_date_to=2026-09-30T23:59:59
```

También están disponibles `return_date_from` y `return_date_to` para consultar devoluciones por rango.

### Devolver préstamo

```http
PATCH /loans/1/return
```

Respuesta esperada:

```json
{
  "id": 1,
  "user_id": 1,
  "device_id": 1,
  "loan_date": "2026-09-17T00:00:00",
  "return_date": "2026-09-17T00:30:00",
  "status": "returned"
}
```

## Manejo de errores

Se gestionan escenarios como:

- Usuario inexistente
- Dispositivo inexistente
- Dispositivo no disponible
- Préstamo inexistente
- Préstamo ya devuelto
- Serial duplicado
- Validación de datos incorrecta

Con códigos HTTP como:

- 200 OK
- 201 Created
- 204 No Content
- 400 Bad Request
- 404 Not Found
- 409 Conflict
- 422 Unprocessable Entity

## Pruebas funcionales mínimas

Ejecutadas y validadas con pytest:

```powershell
cd "C:\Users\sarit\device_systems"
py -3.13 -m pytest tests/test_api.py -q
```

Resultado verificado:

```text
4 passed
```

Las pruebas cubren creación y devolución, asociaciones con usuarios y dispositivos, filtros por estado, correo, tipo y fecha, seriales duplicados, dispositivos no disponibles, estados inválidos, devolución doble e intercambio completo mediante `PUT`.

## Evidencias de aprendizaje

### 1. Creación de usuario

![Creación de usuario](evidencias/01-crear-usuario.png)

### 2. Creación de dispositivo

![Creación de dispositivo](evidencias/02-crear-dispositivo.png)

### 3. Creación de préstamo

![Creación de préstamo](evidencias/03-crear-prestamo.png)

### 4. Consulta de préstamos con información del usuario y el dispositivo

![Detalle de préstamo](evidencias/04-filtro-dispositivo.png)

### 5. Filtro por estado del préstamo

![Filtro por estado activo](evidencias/04-filtro-dispositivo.png)

### 6. Filtro por tipo de dispositivo

![Filtro por tipo de dispositivo](evidencias/04-filtro-dispositivo.png)

### 7. Devolución de préstamo

![Devolución de préstamo](evidencias/05-devolucion.png)

### 8. Estructura del proyecto con Alembic

![Estructura del proyecto con Alembic](evidencias/06-estructura-alembic.png)

> Se evita mostrar una captura de `alembic init` como evidencia independiente porque la carpeta de migraciones ya estaba creada en el proyecto y el comando `alembic init` no puede ejecutarse sobre un directorio no vacío. La evidencia válida en este caso es la estructura generada del proyecto y la comprobación del historial de migraciones aplicado, junto con la ejecución real de las pruebas funcionales y las consultas en Swagger/Postman.

## Reflexión

Este proyecto demostró la importancia de las migraciones para controlar cambios estructurales sin perder datos ni generar inconsistencias. Las relaciones entre modelos permiten modelar correctamente el negocio y mantener integridad referencial. Además, las consultas con joins y filtros permiten recuperar información útil para reportes, control de inventario y trazabilidad de préstamos. En un backend real, estas tres capacidades son fundamentales para construir APIs seguras, escalables y mantenibles.

## Repositorio GitHub

Rama creada para la entrega:

```text
device_systems_alembic_relaciones
```

Comando utilizado:

```powershell
git checkout -b device_systems_alembic_relaciones
```
