from fastapi import APIRouter, status, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from .models import Users
from typing import Optional, List
from passlib.context import CryptContext
from app.auth.jwt_handler import jwt_handler
from app.auth.dependencies import get_current_user
from app.auth.account_security import (
    check_account_lockout,
    record_failed_login,
    record_successful_login,
    get_remaining_lockout_time
)
from .schemas import UserCreate, UserLogin, UserResponse, LoginResponse
from app.config.postgres_config import get_db
import shortuuid
from app.middleware.rate_limiter import auth_rate_limit, read_rate_limit

router = APIRouter(prefix="/users")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(auth_rate_limit),
):
    # Check if account is locked
    is_locked, lockout_until = check_account_lockout(user_data.username)
    if is_locked:
        remaining = get_remaining_lockout_time(user_data.username)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account temporarily locked. Try again in {remaining} seconds.",
            headers={"X-Error-Code": "AUTH_003"},
        )

    user = db.query(Users).filter(Users.username == user_data.username).first()
    if not user or not verify_password(user_data.password, str(user.password)):
        # Record failed attempt
        lockout_info = record_failed_login(user_data.username)
        if lockout_info["is_locked"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Account locked for 15 minutes.",
                headers={"X-Error-Code": "AUTH_003"},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "AUTH_002"},
        )

    # Record successful login - clear failed attempts
    record_successful_login(user_data.username)

    access_token = jwt_handler.create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def post_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(auth_rate_limit),
):
    existing_username: Optional[Users] = db.query(Users).filter(
        Users.username == user.username
    ).first()
    existing_email: Optional[Users] = db.query(Users).filter(
        Users.email == user.email
    ).first()
    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
            headers={"X-Error-Code": "USER_002"},
        )
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
            headers={"X-Error-Code": "USER_003"},
        )
    hashed_password = hash_password(user.password)
    new_user = Users(
        id=shortuuid.uuid(),
        username=user.username,
        password=hashed_password,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_users(
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    users = db.query(Users).all()
    return users


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"X-Error-Code": "USER_001"},
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"X-Error-Code": "USER_001"},
        )
    if str(user.id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
            headers={"X-Error-Code": "USER_004"},
        )
    db.delete(user)
    db.commit()
    return
