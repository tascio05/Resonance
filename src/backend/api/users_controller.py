import schemas
from core.security import create_access_token, get_current_user, pwd_context
from database.models import User, UserRole
from database.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from services.users_services import create_user, get_user_by_username, update_user_role
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse,
)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    return create_user(db, user_in=user_in)


@router.post("/login", response_model=schemas.TokenResponse)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    existing_user = get_user_by_username(db, username=form_data.username)
    if not existing_user or not pwd_context.verify(
        form_data.password, existing_user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Wrong username or password")

    if not existing_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    access_token = create_access_token(data={"sub": existing_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.patch("/me/role", response_model=schemas.UserResponse)
def role_user(
    new_role: schemas.UserRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if new_role.role == UserRole.Admin:
        raise HTTPException(status_code=403, detail="Cannot self assign Admin role")

    return update_user_role(db, current_user, new_role.role)
