from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_current_user_optional
from app.config.postgres_config import get_db
from app.middleware.rate_limiter import read_rate_limit, write_rate_limit
from app.routers.users.models import Users

from . import service
from .schemas import ForumCreate, ForumResponse, ForumUpdate

router = APIRouter(prefix="/forums")


@router.get("", response_model=list[ForumResponse], status_code=status.HTTP_200_OK)
def get_all_forums(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_optional),
    _: bool = Depends(read_rate_limit),
):
    return service.get_all_forums(db, current_user)


@router.get("/{forum_id}", response_model=ForumResponse, status_code=status.HTTP_200_OK)
def get_forum_by_id(
    forum_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_optional),
    _: bool = Depends(read_rate_limit),
):
    return service.get_forum_by_id(db, forum_id, current_user)


@router.post("", response_model=ForumResponse, status_code=status.HTTP_201_CREATED)
def create_forum(
    forum: ForumCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.create_forum(db, forum, current_user)


@router.put("/{forum_id}", response_model=ForumResponse, status_code=status.HTTP_200_OK)
def update_forum(
    forum_id: str,
    forum_update: ForumUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.update_forum(db, forum_id, forum_update, current_user)


@router.delete("/{forum_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_forum(
    forum_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
    _: bool = Depends(write_rate_limit),
):
    service.delete_forum(db, forum_id, current_user)
    return


@router.post("/{forum_id}/like", response_model=ForumResponse, status_code=200)
@router.post("/{forum_id}/toggle-like", response_model=ForumResponse, status_code=200)
def toggle_like_forum(
    forum_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.toggle_like_forum(db, forum_id, current_user)
