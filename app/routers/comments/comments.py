from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from app.middleware.rate_limiter import read_rate_limit, write_rate_limit
from app.auth.dependencies import get_current_user, get_current_user_optional
from app.routers.users.models import Users
from app.config.postgres_config import get_db
from .schemas import Comment, CommentCreate, CommentUpdate
from . import service

router = APIRouter(prefix="/comments")


class MessageResponse(BaseModel):
    detail: str


@router.get("", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_comments(
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_comments(db)


@router.get("/{item_id}", response_model=Comment, status_code=200)
def get_comment(
    item_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_comment_by_id(db, item_id)


@router.post("", response_model=Comment, status_code=status.HTTP_201_CREATED)
def post_comment(
    comment: CommentCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.create_comment(db, comment, current_user)


@router.put("/{item_id}", response_model=Comment, status_code=status.HTTP_200_OK)
def update_comment(
    item_id: str,
    updated_comment: CommentUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.update_comment(db, item_id, updated_comment, current_user)


@router.delete("/{item_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def delete_comment_with_replies(
    item_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    detail = service.delete_comment(db, item_id, current_user)
    return {"detail": detail}


@router.get("/post/{post_id}", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_comments_by_post_id(
    post_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_comments_by_post(db, post_id)


@router.get(
    "/post/{post_id}/replies/{comment_id}",
    response_model=List[Comment],
    status_code=status.HTTP_200_OK,
)
def get_comments_replied_to(
    comment_id: str,
    post_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_replies(db, comment_id, post_id)


@router.get(
    "/post/{post_id}/main", response_model=List[Comment], status_code=status.HTTP_200_OK
)
def get_main_comments_by_post_id(
    post_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_main_comments(db, post_id)


@router.post("/{comment_id}/like", response_model=Comment, status_code=200)
@router.post("/{comment_id}/toggle-like", response_model=Comment, status_code=200)
def toggle_like_comment(
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.toggle_like_comment(db, comment_id, current_user)


# Forum Comment Endpoints (using the same Comments table)
@router.get(
    "/forum/{forum_id}", response_model=List[Comment], status_code=status.HTTP_200_OK
)
def get_forum_comments(
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_forum_comments(db, forum_id)


@router.get(
    "/forum/{forum_id}/main", response_model=List[Comment], status_code=status.HTTP_200_OK
)
def get_main_forum_comments(
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_main_forum_comments(db, forum_id)


@router.get(
    "/forum/{forum_id}/replies/{comment_id}",
    response_model=List[Comment],
    status_code=status.HTTP_200_OK,
)
def get_forum_comments_replied_to(
    comment_id: str,
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_forum_replies(db, comment_id, forum_id)


@router.post("/forum/{forum_id}", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_forum_comment(
    forum_id: str,
    comment: CommentCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.create_forum_comment(db, forum_id, comment, current_user)
