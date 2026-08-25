from fastapi import HTTPException
from app.schemas.user_schema import UserCreate, UserUpdate, UserPatch
import app.data.users_db as db  # Importamos el módulo para poder modificar sus variables globales


# ── Función auxiliar privada ────────────────────────────────────────────────────

def _check_email_duplicate(email: str, exclude_id: int = None) -> None:
    """Verifica que el correo no esté registrado. Lanza 400 si ya existe."""
    for user in db.fake_users_db:
        if user["email"] == email and user["id"] != exclude_id:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")


# ── Operaciones CRUD ────────────────────────────────────────────────────────────

def get_all_users(role=None, is_active=None) -> list:
    """Retorna todos los usuarios, con filtros opcionales por rol y estado."""
    result = db.fake_users_db
    if role is not None:
        result = [u for u in result if u["role"] == role]
    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]
    return result


def get_user_by_id(user_id: int) -> dict | None:
    """Busca un usuario por ID. Retorna el dict o None si no existe."""
    for user in db.fake_users_db:
        if user["id"] == user_id:
            return user
    return None


def create_user(user: UserCreate) -> dict:
    """Crea un nuevo usuario. Lanza 400 si el correo ya está registrado."""
    _check_email_duplicate(user.email)

    new_user = user.model_dump()
    new_user["id"] = db.user_id_counter
    db.user_id_counter += 1

    db.fake_users_db.append(new_user)
    return new_user


def update_user(user_id: int, data: UserUpdate) -> dict:
    """Reemplaza completamente un usuario (PUT). Lanza 404 o 400 según el caso."""
    _check_email_duplicate(data.email, exclude_id=user_id)

    for i, user in enumerate(db.fake_users_db):
        if user["id"] == user_id:
            updated = data.model_dump()
            updated["id"] = user_id  # Conservamos el ID original
            db.fake_users_db[i] = updated
            return updated

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


def patch_user(user_id: int, data: UserPatch) -> dict:
    """Actualiza parcialmente un usuario (PATCH). Lanza 400 si el body está vacío."""
    # exclude_unset=True obtiene solo los campos que el cliente envió explícitamente
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    if "email" in changes:
        _check_email_duplicate(changes["email"], exclude_id=user_id)

    for i, user in enumerate(db.fake_users_db):
        if user["id"] == user_id:
            db.fake_users_db[i].update(changes)
            return db.fake_users_db[i]

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


def delete_user(user_id: int) -> None:
    """Elimina un usuario por ID. Lanza 404 si no existe."""
    for i, user in enumerate(db.fake_users_db):
        if user["id"] == user_id:
            db.fake_users_db.pop(i)
            return

    raise HTTPException(status_code=404, detail="Usuario no encontrado")
