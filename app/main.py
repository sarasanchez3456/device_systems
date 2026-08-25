from fastapi import FastAPI
from app.routes import user_routes

# Metadatos para organizar los endpoints en Swagger UI por categorías (tags)
tags_metadata = [
    {
        "name": "Users",
        "description": "Operaciones CRUD sobre el recurso **usuarios**. "
                       "Permite crear, consultar, filtrar, actualizar y eliminar usuarios del sistema.",
    },
    {
        "name": "Health",
        "description": "Endpoint de verificación del estado de la API.",
    },
]

# Instancia principal de la aplicación con metadatos completos para Swagger/OpenAPI
app = FastAPI(
    title="device_systems API",
    description="""
API REST para la **gestión de usuarios** del sistema device_systems.

## Funcionalidades
- 📋 Listar y filtrar usuarios por rol y estado
- 👤 Consultar usuario por ID
- ➕ Crear nuevos usuarios con validación de datos
- ✏️ Actualizar completamente un usuario — **PUT**
- 🔧 Actualizar parcialmente un usuario — **PATCH**
- 🗑️ Eliminar usuarios — **DELETE** *(requiere API Key)*
- 🔒 Autenticación básica mediante cabecera `X-Api-Key`

## Documentación interactiva
- **Swagger UI** → `/docs`
- **ReDoc** → `/redoc`

## Autenticación (DELETE)
Para eliminar usuarios se requiere la cabecera:
```
X-Api-Key: device-secret-2026
```
    """,
    version="2.0.0",
    contact={
        "name": "device_systems",
        "email": "soporte@devicesystems.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
)

# Registra todas las rutas del recurso usuarios
app.include_router(user_routes.router)


# Endpoint raíz de verificación (health check)
@app.get("/", tags=["Health"], summary="Verificar estado de la API")
def read_root():
    return {
        "mensaje": "Bienvenido a la API device_systems v2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }
