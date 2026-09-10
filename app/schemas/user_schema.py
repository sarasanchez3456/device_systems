from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum

# Roles permitidos en el sistema
class RoleEnum(str, Enum):
    admin = "admin"
    support = "support"
    user = "user"

# Campos base compartidos por todos los esquemas de usuario
class UserBase(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre completo del usuario")
    email: EmailStr
    role: RoleEnum
    is_active: bool = True

# Esquema para POST: creación de un nuevo usuario (todos los campos requeridos)
class UserCreate(UserBase):
    pass

# Esquema para PUT: reemplaza completamente la información de un usuario existente
class UserUpdate(UserBase):
    pass

# Esquema para PATCH: actualización parcial (todos los campos son opcionales)
class UserPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=3, description="Nombre completo del usuario")
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None

# Esquema de respuesta: incluye el ID asignado por el sistema
class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
