from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.security import get_password_hash, pwd_context
from database.models import User
import schemas
from database.session import get_db
from core.security import create_access_token

router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    hashed_password = get_password_hash(user_in.password)

    new_user = User(username=user_in.username, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(User.username == form_data.username).first()
    if not existing_user or not pwd_context.verify(
        form_data.password, existing_user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Wrong username or password")

    access_token = create_access_token(data={"sub": existing_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "logged in",
    }
