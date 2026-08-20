# device_systems API

API REST enfocada en la gestión del recurso usuarios, construida con FastAPI.
Desarrollada para el reto integrador de la guía de fundamentos de FastAPI.

## Instalación de dependencias

Asegúrate de tener Python instalado. Luego, crea un entorno virtual e instala las dependencias:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución del servidor

Para ejecutar el servidor de desarrollo, utiliza Uvicorn:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.
La documentación interactiva (Swagger UI) estará en `http://127.0.0.1:8000/docs`.

## Tabla de Endpoints

| Método | Endpoint         | Descripción                                     |
|--------|------------------|-------------------------------------------------|
| GET    | `/users`         | Listar todos los usuarios. Permite filtros.     |
| GET    | `/users/{id}`    | Consultar un usuario por ID.                    |
| POST   | `/users`         | Registrar un nuevo usuario.                     |

## Ejemplos de Peticiones

### POST /users

Crear un usuario:

```json
POST /users
{
  "name": "Juan Perez",
  "email": "juan.perez@example.com",
  "role": "admin",
  "is_active": true
}
```

### GET /users

Listar todos los usuarios activos:

```
GET /users?is_active=true
```

### GET /users/{id}

Obtener el usuario con ID 1:

```
GET /users/1
```

## Capturas de Swagger UI / Evidencias de pruebas

*(Agrega aquí las capturas de pantalla de Swagger UI probando los endpoints)*
- Captura de GET /users
- Captura de GET /users/{user_id}
- Captura de POST /users
- Captura de validaciones y errores (ej. correo duplicado, formato inválido)

## Reflexión

El uso de FastAPI facilita enormemente la creación de APIs REST gracias a su integración con Pydantic para la validación de datos y la auto-generación de documentación con Swagger UI. Además, el uso de tipado estático ayuda a prevenir errores y mejorar la experiencia de desarrollo.
