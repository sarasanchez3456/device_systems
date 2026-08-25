from fastapi import HTTPException, Header, Path, Response
from typing import Optional
from app.data.users_db import fake_users_db

# Clave de API válida para simular autenticación básica
API_KEY_VALIDA = "device-secret-2026"


def get_user_or_404(user_id: int = Path(..., description="ID del usuario")) -> dict:
    """
    Dependencia reutilizable: busca un usuario por ID.
    Si no existe, lanza automáticamente un error 404.
    Uso: user: dict = Depends(get_user_or_404)
    """
    for user in fake_users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


def get_api_headers(response: Response) -> None:
    """
    Dependencia reutilizable: inyecta cabeceras personalizadas en la respuesta HTTP.
    Uso: _: None = Depends(get_api_headers)
    """
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "2.0"


def verify_api_key(x_api_key: Optional[str] = Header(None, description="Clave de acceso a la API")) -> None:
    """
    Dependencia reutilizable: valida la cabecera X-Api-Key.
    Si está ausente o es incorrecta, lanza un error 401.
    Uso: _: None = Depends(verify_api_key)
    Cabecera requerida: X-Api-Key: device-secret-2024
    """
    if x_api_key != API_KEY_VALIDA:
        raise HTTPException(status_code=401, detail="API Key inválida o ausente")


def get_api_info() -> dict:
    """
    Dependencia reutilizable: retorna la configuración general de la API.
    Uso: info: dict = Depends(get_api_info)
    """
    return {
        "app_name": "device_systems",
        "version": "2.0.0",
        "description": "API REST para gestión de usuarios",
    }
