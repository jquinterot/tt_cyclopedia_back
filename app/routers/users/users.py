from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import null
from sqlalchemy.orm import Session
from .models import Users
from typing import Optional, List
from app.config.postgres_config import SessionLocal
import shortuuid
from passlib.context import CryptContext
from app.auth.jwt_handler import jwt_handler
from app.auth.dependencies import get_current_user

from .schemas import User, UserCreate, UserLogin, UserResponse, LoginResponse

router = APIRouter(prefix="/users",
                   )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Config:
    orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)):
    users = db.query(Users).all()
    return users


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.username == user_data.username).first()

    if not user or not verify_password(user_data.password, str(user.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Create access token
    access_token = jwt_handler.create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def post_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_username: Optional[Users] = db.query(Users).filter(Users.username == user.username).first()
    existing_email: Optional[Users] = db.query(Users).filter(Users.email == user.email).first()

    if existing_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    if existing_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    hashed_password = hash_password(user.password)
    
    new_user = Users(
        id=shortuuid.uuid(),
        username=user.username,
        password=hashed_password,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if str(user.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    db.delete(user)
    db.commit()
    return
