from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserPatch


def _check_email_duplicate(db: Session, email: str, exclude_id: int = None) -> None:
    query = db.query(User).filter(User.email == email)
    if exclude_id is not None:
        query = query.filter(User.id != exclude_id)
    if query.first() is not None:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")


# ── Operaciones CRUD ────────────────────────────────────────────────────────────

def get_all_users(db: Session, role=None, is_active=None, order_by="name") -> list:
    """Retorna usuarios aplicando filtros y ordenamiento."""
    query = db.query(User)
    if role is not None:
        query = query.filter(User.role == role.value if hasattr(role, "value") else role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if order_by == "created_at":
        query = query.order_by(User.created_at.desc())
    else:
        query = query.order_by(User.name.asc())
    return query.all()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Crea un nuevo usuario. Lanza 400 si el correo ya está registrado."""
    _check_email_duplicate(db, user.email)
    new_user = User(**user.model_dump())
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    db.refresh(new_user)
    return new_user


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    """Reemplaza completamente un usuario (PUT). Lanza 404 o 400 según el caso."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    _check_email_duplicate(db, data.email, exclude_id=user_id)
    for field, value in data.model_dump().items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def patch_user(db: Session, user_id: int, data: UserPatch) -> User:
    """Actualiza parcialmente un usuario (PATCH). Lanza 400 si el body está vacío."""
    # exclude_unset=True obtiene solo los campos que el cliente envió explícitamente
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    if "email" in changes:
        _check_email_duplicate(db, changes["email"], exclude_id=user_id)

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    """Elimina un usuario por ID. Lanza 404 si no existe."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
