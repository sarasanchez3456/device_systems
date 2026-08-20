from fastapi import APIRouter, HTTPException, Query, Path, Response
from typing import List, Optional
from app.schemas.user_schema import UserCreate, UserResponse, RoleEnum

router = APIRouter()

# In-memory database for users
fake_users_db = []
user_id_counter = 1

@router.get("/users", response_model=List[UserResponse])
def get_users(
    response: Response,
    role: Optional[RoleEnum] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

    filtered_users = fake_users_db
    if role is not None:
        filtered_users = [user for user in filtered_users if user["role"] == role]
    if is_active is not None:
        filtered_users = [user for user in filtered_users if user["is_active"] == is_active]
    
    return filtered_users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    response: Response,
    user_id: int = Path(..., description="The ID of the user to retrieve"),
):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

    for user in fake_users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"
    
    global user_id_counter
    # Check for duplicate email
    for existing_user in fake_users_db:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = user.model_dump()
    new_user["id"] = user_id_counter
    user_id_counter += 1
    
    fake_users_db.append(new_user)
    return new_user
