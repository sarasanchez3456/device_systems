# device_systems API

## Descripción de la API

**device_systems** es una API REST construida con **FastAPI** orientada a la gestión completa de usuarios de un sistema de dispositivos. Implementa el **CRUD completo** (GET, POST, PUT, PATCH, DELETE), validación de datos con **Pydantic v2**, separación de responsabilidades en capas, manejo de errores con **HTTPException** y reutilización de lógica con **Dependency Injection** (`Depends()`).

---

## Tecnologías utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.11+ | Lenguaje base |
| FastAPI | Latest | Framework web y API |
| Pydantic v2 | Latest | Validación de datos y esquemas |
| Uvicorn | Latest | Servidor ASGI |
| email-validator | Latest | Validación de correos |

---

## Instalación de dependencias

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual (Windows)
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Ejecución del servidor

```bash
uvicorn app.main:app --reload
```

| Interfaz | URL |
|---|---|
| API | `http://127.0.0.1:8000` |
| Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |

---

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── main.py                        # Instancia FastAPI, metadatos, router
│   ├── data/
│   │   └── users_db.py                # Base de datos en memoria + contador ID
│   ├── schemas/
│   │   └── user_schema.py             # Modelos Pydantic (entrada y salida)
│   ├── services/
│   │   └── user_service.py            # Lógica de negocio CRUD
│   ├── dependencies/
│   │   └── user_dependencies.py       # Funciones reutilizables con Depends()
│   └── routes/
│       └── user_routes.py             # Definición de endpoints
├── requirements.txt
└── README.md
```

---

## Tabla de Endpoints

| Método | Endpoint | Descripción | Código éxito |
|---|---|---|---|
| `GET` | `/users` | Listar todos los usuarios | 200 OK |
| `GET` | `/users?role=admin` | Filtrar por rol | 200 OK |
| `GET` | `/users?is_active=true` | Filtrar por estado | 200 OK |
| `GET` | `/users/{user_id}` | Consultar usuario por ID | 200 OK |
| `POST` | `/users` | Crear nuevo usuario | 201 Created |
| `PUT` | `/users/{user_id}` | Actualizar completamente un usuario | 200 OK |
| `PATCH` | `/users/{user_id}` | Actualizar parcialmente un usuario | 200 OK |
| `DELETE` | `/users/{user_id}` | Eliminar un usuario *(requiere API Key)* | 204 No Content |

---

## Ejemplos de peticiones y respuestas

### POST /users — Crear usuario

**Petición:**
```json
POST http://127.0.0.1:8000/users
Content-Type: application/json

{
  "name": "Ana Silva",
  "email": "ana@correo.com",
  "role": "admin",
  "is_active": true
}
```

**Respuesta exitosa (201 Created):**
```json
{
  "id": 1,
  "name": "Ana Silva",
  "email": "ana@correo.com",
  "role": "admin",
  "is_active": true
}
```

---

### GET /users — Listar usuarios

```
GET http://127.0.0.1:8000/users
```

### GET /users?role=admin — Filtrar por rol

```
GET http://127.0.0.1:8000/users?role=admin
```

### GET /users/{user_id} — Consultar por ID

```
GET http://127.0.0.1:8000/users/1
```

---

### PUT /users/{user_id} — Actualización completa

**Petición (todos los campos requeridos):**
```json
PUT http://127.0.0.1:8000/users/1
Content-Type: application/json

{
  "name": "Ana Silva Actualizada",
  "email": "ana_nueva@correo.com",
  "role": "support",
  "is_active": false
}
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "name": "Ana Silva Actualizada",
  "email": "ana_nueva@correo.com",
  "role": "support",
  "is_active": false
}
```

---

### PATCH /users/{user_id} — Actualización parcial

**Petición (solo los campos a modificar):**
```json
PATCH http://127.0.0.1:8000/users/1
Content-Type: application/json

{
  "role": "support"
}
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "name": "Ana Silva",
  "email": "ana@correo.com",
  "role": "support",
  "is_active": true
}
```

---

### DELETE /users/{user_id} — Eliminar usuario

**Petición (requiere cabecera X-Api-Key):**
```
DELETE http://127.0.0.1:8000/users/1
X-Api-Key: device-secret-2024
```

**Respuesta (204 No Content):** sin cuerpo de respuesta.

---

## Códigos de estado HTTP

| Operación | Método | Código |
|---|---|---|
| Listar usuarios | `GET /users` | 200 OK |
| Consultar usuario | `GET /users/{id}` | 200 OK |
| Crear usuario | `POST /users` | 201 Created |
| Actualizar completo | `PUT /users/{id}` | 200 OK |
| Actualizar parcial | `PATCH /users/{id}` | 200 OK |
| Eliminar usuario | `DELETE /users/{id}` | 204 No Content |
| Usuario no encontrado | Cualquier método por ID | 404 Not Found |
| Correo duplicado | `POST` o `PUT` | 400 Bad Request |
| Body vacío en PATCH | `PATCH` | 400 Bad Request |
| API Key inválida | `DELETE` | 401 Unauthorized |
| Datos inválidos | Validación Pydantic | 422 Unprocessable Entity |

---

## Manejo de errores

La API controla los siguientes escenarios de error usando `HTTPException`:

| Error | Código | Detalle |
|---|---|---|
| Usuario no encontrado | 404 | `"Usuario no encontrado"` |
| Correo duplicado | 400 | `"El correo ya está registrado"` |
| PATCH sin campos | 400 | `"No se enviaron campos para actualizar"` |
| API Key inválida o ausente | 401 | `"API Key inválida o ausente"` |
| Rol no permitido | 422 | Validación automática de Pydantic |
| Datos inválidos | 422 | Validación automática de Pydantic |

**Formato de respuesta de error:**
```json
{
  "detail": "Usuario no encontrado"
}
```

---

## Dependency Injection con Depends()

FastAPI permite inyectar lógica reutilizable en los endpoints mediante `Depends()`. En este proyecto se implementaron 4 dependencias en `app/dependencies/user_dependencies.py`:

### `get_user_or_404`
Busca un usuario por ID. Si no existe, lanza automáticamente `404 Not Found`. Evita repetir el mismo `for` en cada endpoint.

```python
@router.get("/{user_id}")
def get_user(user: dict = Depends(get_user_or_404)):
    return user
```

### `get_api_headers`
Inyecta las cabeceras `X-App-Name` y `X-API-Version` en cada respuesta HTTP sin repetir código.

```python
@router.get("")
def get_users(_: None = Depends(get_api_headers)):
    ...
```

### `verify_api_key`
Valida la cabecera `X-Api-Key`. Si está ausente o es incorrecta, lanza `401 Unauthorized`. Aplicada en `DELETE`.

```python
@router.delete("/{user_id}")
def delete_user(_auth: None = Depends(verify_api_key)):
    ...
```

### `get_api_info`
Retorna un diccionario con la configuración general de la API (nombre, versión, descripción).

---

## Capturas de Swagger UI / Evidencias de pruebas

### Swagger UI — Documentación automática
![Swagger UI](Evidencias/Captura_SwaggerUI.png)

### POST /users — Creación exitosa (201 Created)
![Creación Exitosa](Evidencias/Creación_Exitosa.png)

### GET /users — Listar usuarios
![Listar Usuarios](Evidencias/Listar_Usuarios.png)

### GET /users/{user_id} — Búsqueda por ID
![Búsqueda por ID](Evidencias/Busqueda_ID.png)

### PUT /users/{user_id} — Actualización completa (200 OK)
![Actualización PUT](Evidencias/PUT_update.png)

### PATCH /users/{user_id} — Actualización parcial (200 OK)
![Actualización PATCH](Evidencias/PATCH_update.png)

### DELETE /users/{user_id} — Eliminación (204 No Content)
![Eliminación DELETE](Evidencias/DELETE_user.png)

### Headers HTTP personalizados (X-App-Name / X-API-Version)
![Headers HTTP](Evidencias/Headers.png)

### Error — Correo duplicado (400 Bad Request)
![Error Correo Duplicado](Evidencias/Error_correo.png)

### Error — Correo con formato inválido (422)
![Error Correo Inválido](Evidencias/Correo_invalido.png)

### Error — Nombre corto y rol inválido (422)
![Error Nombre y Rol](Evidencias/Error_Nombrecorto_Rolinvalido.png)

### Error — PATCH con body vacío (400 Bad Request)
![Error PATCH vacío](Evidencias/Error_PATCH_vacio.png)

### Error — DELETE sin API Key (401 Unauthorized)
![Error sin API Key](Evidencias/Error_apikey.png)

---

## Reflexión

La evolución de esta API permitió aplicar buenas prácticas del desarrollo backend moderno: separar responsabilidades en capas (`routes`, `schemas`, `services`, `dependencies`, `data`), reutilizar lógica con **Dependency Injection** y documentar automáticamente todos los endpoints con **Swagger/OpenAPI**. El manejo estructurado de errores con `HTTPException` y los códigos HTTP correctos hacen que la API sea predecible y fácil de consumir desde cualquier cliente. Esta arquitectura escala de forma natural hacia una implementación con base de datos real usando SQLAlchemy o cualquier otro ORM.
