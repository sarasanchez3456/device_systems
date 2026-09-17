from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserReplace, UserResponse, UserUpdate
from app.services.user_service import email_in_use

router = APIRouter()
ERROR_RESPONSES = {
    400: {"description": "The request conflicts with existing user data."},
    404: {"description": "User not found."},
    422: {"description": "Validation error."},
}


@router.get("", response_model=list[UserResponse], summary="List users", description="List all users with optional search filters.", response_description="Users matching the filters.", responses={422: ERROR_RESPONSES[422]})
def list_users(
    search: str | None = Query(default=None, description="Search by name or email."),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(User.name.ilike(search_term), User.email.ilike(search_term)))
    return query.order_by(User.id).all()


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID", response_description="The requested user.", responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422]})
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create user", response_description="The created user.", responses=ERROR_RESPONSES)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if email_in_use(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The email is already registered")
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/{user_id}", response_model=UserResponse, summary="Replace user", description="Replace all editable fields of an existing user.", response_description="The user was replaced successfully.", responses=ERROR_RESPONSES)
def update_user(user_id: int, user: UserReplace, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = user.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"]:
        if email_in_use(db, update_data["email"], user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The email is already registered")
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.patch("/{user_id}", response_model=UserResponse, summary="Partial update user", response_description="The updated user.", responses=ERROR_RESPONSES)
def patch_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return update_user(user_id, user, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user", response_description="The user was deleted.", responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422]})
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return None
