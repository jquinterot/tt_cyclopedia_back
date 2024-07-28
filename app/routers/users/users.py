from fastapi import APIRouter, status
from .models import Users
from typing import Optional, List
from app.config.postgres_config import SessionLocal
import shortuuid

from .schemas import User

router = APIRouter(prefix="/users",
                   )


class Config:
    orm_mode = True


db = SessionLocal()


@router.get("", response_model=List[User], status_code=status.HTTP_200_OK)
def get_users():
    users = db.query(Users).all()
    return users


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def post_comment(user: User):
    new_user = Users(
        id=shortuuid.uuid(),
        username=user.username)
    db.add(new_user)
    db.commit()
    return new_user
