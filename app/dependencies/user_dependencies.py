from fastapi import Header, Response
from typing import Optional


def get_api_headers(response: Response) -> None:
    """
    Dependencia reutilizable: inyecta cabeceras personalizadas en la respuesta HTTP.
    Uso: _: None = Depends(get_api_headers)
    """
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "2.0"


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
