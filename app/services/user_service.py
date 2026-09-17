from sqlalchemy.orm import Session

from app.models.user_model import User


def find_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def email_in_use(db: Session, email: str, user_id: int | None = None) -> bool:
    query = db.query(User).filter(User.email == email)
    if user_id is not None:
        query = query.filter(User.id != user_id)
    return query.first() is not None
