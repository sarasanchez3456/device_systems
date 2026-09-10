# device_systems API

## Descripción de la API

**device_systems** es una API REST construida con **FastAPI** orientada a la gestión completa de usuarios. Implementa el **CRUD completo** (GET, POST, PUT, PATCH, DELETE) con persistencia en SQLite mediante **SQLAlchemy**, validación con **Pydantic v2**, separación de responsabilidades y manejo de errores con `HTTPException`.

---

## Tecnologías utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.11+ | Lenguaje base |
| FastAPI | Latest | Framework web y API |
| Pydantic v2 | Latest | Validación de datos y esquemas |
| Uvicorn | Latest | Servidor ASGI |
| SQLAlchemy | Latest | ORM y persistencia en SQLite |
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
│   ├── database/
│   │   └── connection.py              # Engine, sesiones y Base declarativa
│   ├── models/
│   │   └── user_model.py              # Modelo ORM de la tabla users
│   ├── schemas/
│   │   └── user_schema.py             # Modelos Pydantic (entrada y salida)
│   ├── dependencies/
│   │   └── database_dependency.py     # Sesión por solicitud
│   ├── services/
│   │   └── user_service.py            # Lógica de negocio CRUD
│   └── routes/
│       └── user_routes.py             # Definición de endpoints
├── device_systems.db                  # SQLite generado al iniciar la API
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
| `DELETE` | `/users/{user_id}` | Eliminar un usuario | 204 No Content |

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
### `get_db`
Abre y cierra una sesión SQLAlchemy por solicitud.

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

**Petición:**
```
DELETE http://127.0.0.1:8000/users/1
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
| Datos inválidos | Validación Pydantic | 422 Unprocessable Entity |

---

## Manejo de errores

La API controla los siguientes escenarios de error usando `HTTPException`:

| Error | Código | Detalle |
|---|---|---|
| Usuario no encontrado | 404 | `"Usuario no encontrado"` |
| Correo duplicado | 400 | `"El correo ya está registrado"` |
| PATCH sin campos | 400 | `"No se enviaron campos para actualizar"` |
| Rol no permitido | 422 | Validación automática de Pydantic |
| Datos inválidos | 422 | Validación automática de Pydantic |

**Formato de respuesta de error:**
```json
{
  "detail": "Usuario no encontrado"
}
```

---

## Diferencia entre modelo y schema

El modelo SQLAlchemy de `app/models/user_model.py` representa la tabla `users` y define la persistencia, los tipos de columnas y las restricciones de la base de datos. El schema Pydantic de `app/schemas/user_schema.py` representa los datos que recibe o devuelve la API y aplica validaciones como longitud mínima, formato de email y roles permitidos. Separar ambos modelos evita mezclar reglas HTTP con la estructura interna de SQLite.

## Dependency Injection con Depends()

FastAPI permite inyectar lógica reutilizable en los endpoints mediante `Depends()`. En este proyecto se utiliza `get_db` desde `app/dependencies/database_dependency.py` para abrir y cerrar una sesión SQLAlchemy por solicitud.

```python
@router.get("")
def get_users(db: Session = Depends(get_db)):
  return service.get_all_users(db)
```

### `get_api_headers`
Inyecta las cabeceras `X-App-Name` y `X-API-Version` en cada respuesta HTTP sin repetir código.

```python
@router.get("")
def get_users(_: None = Depends(get_api_headers)):
    ...
```

### `get_api_info`
Retorna un diccionario con la configuración general de la API (nombre, versión, descripción).

---

## Capturas de Swagger UI / Evidencias de pruebas

### Colección de Postman
[Descargar colección device_systems.postman_collection.json](Evidencias/device_systems.postman_collection.json)

Importa esta colección en Postman con **Import**, verifica que la API esté ejecutándose en `http://127.0.0.1:8000` y ejecuta la carpeta completa con **Run collection**. La colección guarda automáticamente el `userId` creado y valida los códigos HTTP esperados.

### Evidencias nuevas ejecutadas en Postman

#### Crear usuario — 201 Created
![Crear usuario 201](Evidencias/01_crear_usuario_201.png)

#### Email duplicado — 400 Bad Request
![Email duplicado 400](Evidencias/02_email_duplicado_400.png)

#### Listar usuarios — 200 OK
![Listar usuarios 200](Evidencias/03_listar_usuarios_200.png)

#### Consultar usuario por ID — 200 OK
![Consultar usuario por ID 200](Evidencias/04_consultar_usuario_id_200.png)

#### Usuario inexistente — 404 Not Found
![Usuario inexistente 404](Evidencias/05_usuario_inexistente_404.png)

#### Filtrar por rol — 200 OK
![Filtrar por rol 200](Evidencias/06_filtrar_por_rol_200.png)

#### Filtrar usuarios activos — 200 OK
![Filtrar activos 200](Evidencias/07_filtrar_usuarios_activos_200.png)

#### Actualización completa PUT — 200 OK
![PUT 200](Evidencias/08_actualizar_put_200.png)

#### Actualización parcial PATCH — 200 OK
![PATCH 200](Evidencias/09_actualizar_patch_200.png)

#### Eliminación de usuario inexistente — 404 Not Found
![DELETE usuario inexistente 404](Evidencias/10_eliminar_usuario_inexistente_404.png)

#### Creación adicional — 201 Created
![Creación adicional 201](Evidencias/11_crear_usuario_201_adicional.png)

### Swagger UI — Documentación automática
![Swagger UI](Evidencias/capturas_SwaggerUIV2.png)
![Swagger UI V1](Evidencias/Captura_SwaggerUIV1.png)

### ReDoc — Documentación alternativa
![ReDoc 1](Evidencias/cap_redoc.png)
![ReDoc 2](Evidencias/cap_redoc1.png)

### POST /users — Creación exitosa (201 Created)
![Creación Exitosa](Evidencias/Creación_Exitosa.png)

### GET /users — Listar usuarios
![Listar Usuarios](Evidencias/Listar_Usuarios.png)

### Búsqueda por ID
![Búsqueda por ID](Evidencias/usuario_id.png)

### PUT /users/{user_id} — Actualización completa (200 OK)
![Actualización PUT](Evidencias/actualizar_con_PUT.png)

### PATCH /users/{user_id} — Actualización parcial (200 OK)
![Actualización PATCH](Evidencias/patch.png)

### DELETE /users/{user_id} — Eliminación (204 No Content)
![Eliminación DELETE](Evidencias/delete.png)

### Error — Correo duplicado (400 Bad Request)
![Error Correo Duplicado](Evidencias/correo_duplicado.png)

### Error — Correo con formato inválido (422)
![Error Correo Inválido](Evidencias/Correo_invalido.png)

### Error — Nombre corto y rol inválido (422)
![Error Nombre y Rol](Evidencias/Error_Nombrecorto_Rolinvalido.png)

### Error — PATCH con body vacío (400 Bad Request)
![Error PATCH vacío](Evidencias/Error_PATCH_vacio.png)

---

## Reflexión

La evolución de esta API permitió aplicar buenas prácticas del desarrollo backend moderno: separar responsabilidades en capas (`routes`, `schemas`, `services`, `dependencies`, `database`, `models`), persistir datos con SQLAlchemy y documentar automáticamente todos los endpoints con **Swagger/OpenAPI**. El manejo estructurado de errores con `HTTPException`, las validaciones de Pydantic y los constraints de la base de datos hacen que la API sea predecible y fácil de consumir desde cualquier cliente.
