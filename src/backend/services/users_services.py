import schemas
from core.security import get_password_hash
from database.models import User, UserRole
from sqlalchemy.orm import Session


def get_user_by_username(db: Session, username: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    return user


def create_user(db: Session, user_in: schemas.UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    new_user = User(username=user_in.username, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user_role(db: Session, user: User, new_role: UserRole) -> User:
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    return user


def deactivate_user(db: Session, user: User) -> User:
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
