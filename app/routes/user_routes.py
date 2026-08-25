from fastapi import APIRouter, Query, Path, Depends, Response
from typing import List, Optional

from app.schemas.user_schema import (
    UserCreate, UserUpdate, UserPatch, UserResponse, RoleEnum
)
from app.dependencies.user_dependencies import (
    get_user_or_404, get_api_headers, verify_api_key
)
import app.services.user_service as service

# Router con prefijo y tag globales: todos los endpoints quedan bajo /users → tag "Users"
router = APIRouter(prefix="/users", tags=["Users"])


# ── GET /users ──────────────────────────────────────────────────────────────────
@router.get(
    "",
    response_model=List[UserResponse],
    summary="Listar usuarios",
    description="Retorna la lista completa de usuarios registrados. "
                "Permite filtrar por **rol** y/o **estado activo** mediante query params.",
    response_description="Lista de usuarios que coinciden con los filtros aplicados.",
)
def get_users(
    role: Optional[RoleEnum] = Query(None, description="Filtrar por rol: admin, support o user"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo: true o false"),
    _: None = Depends(get_api_headers),  # Inyecta cabeceras X-App-Name y X-API-Version
):
    return service.get_all_users(role=role, is_active=is_active)


# ── GET /users/{user_id} ────────────────────────────────────────────────────────
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
    description="Retorna un único usuario identificado por su **ID**. "
                "Si el usuario no existe, responde con **404 Not Found**.",
    response_description="Datos completos del usuario encontrado.",
)
def get_user(
    user: dict = Depends(get_user_or_404),  # Dependency valida existencia y retorna el usuario
    _: None = Depends(get_api_headers),
):
    return user


# ── POST /users ─────────────────────────────────────────────────────────────────
@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="Crear usuario",
    description="Registra un nuevo usuario en el sistema. "
                "El correo electrónico debe ser único. "
                "Responde con **201 Created** si el registro es exitoso.",
    response_description="Datos del usuario recién creado, incluyendo el ID asignado.",
)
def create_user(
    user: UserCreate,
    _: None = Depends(get_api_headers),
):
    return service.create_user(user)


# ── PUT /users/{user_id} ────────────────────────────────────────────────────────
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario (completo)",
    description="Reemplaza **completamente** la información de un usuario existente. "
                "Se deben enviar **todos los campos**: name, email, role e is_active. "
                "Responde con **200 OK**, **404** si no existe o **400** si el correo está duplicado.",
    response_description="Datos actualizados del usuario.",
)
def update_user(
    data: UserUpdate,
    user_id: int = Path(..., description="ID del usuario a actualizar"),
    _: None = Depends(get_api_headers),
):
    return service.update_user(user_id, data)


# ── PATCH /users/{user_id} ──────────────────────────────────────────────────────
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario (parcial)",
    description="Modifica **solo los campos enviados** de un usuario existente. "
                "Si no se envía ningún campo, responde con **400 Bad Request**. "
                "Responde con **200 OK**, **404** si no existe o **400** si el correo está duplicado.",
    response_description="Datos del usuario con los campos actualizados.",
)
def patch_user(
    data: UserPatch,
    user_id: int = Path(..., description="ID del usuario a actualizar parcialmente"),
    _: None = Depends(get_api_headers),
):
    return service.patch_user(user_id, data)


# ── DELETE /users/{user_id} ─────────────────────────────────────────────────────
@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Eliminar usuario",
    description="Elimina permanentemente un usuario del sistema. "
                "Responde con **204 No Content** si la eliminación es exitosa. "
                "Responde con **404** si el usuario no existe. "
                "⚠️ Requiere cabecera de autenticación: `X-Api-Key: device-secret-2024`.",
    response_description="Sin contenido. La eliminación fue exitosa.",
)
def delete_user(
    user_id: int = Path(..., description="ID del usuario a eliminar"),
    _headers: None = Depends(get_api_headers),
    _auth: None = Depends(verify_api_key),  # Endpoint protegido: requiere API Key
):
    service.delete_user(user_id)
    # No retornamos nada → FastAPI envía 204 No Content automáticamente
