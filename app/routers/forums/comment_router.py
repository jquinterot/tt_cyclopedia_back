from fastapi import APIRouter, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from app.auth.dependencies import get_current_user
from app.routers.users.models import Users
from app.config.postgres_config import get_db
from app.middleware.rate_limiter import read_rate_limit, write_rate_limit
from .schemas import ForumComment, ForumCommentCreate, ForumCommentCreateNested, ForumCommentUpdate
from . import service

router = APIRouter(prefix="/forums")


class MessageResponse(BaseModel):
    detail: str


@router.get(
    "/{forum_id}/comments", response_model=List[ForumComment], status_code=status.HTTP_200_OK
)
def get_forum_comments(
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_forum_comments(db, forum_id)


@router.get(
    "/{forum_id}/comments/main",
    response_model=List[ForumComment],
    status_code=status.HTTP_200_OK,
)
def get_main_forum_comments(
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_main_forum_comments(db, forum_id)


@router.get(
    "/{forum_id}/comments/replies/{comment_id}",
    response_model=List[ForumComment],
    status_code=status.HTTP_200_OK,
)
def get_forum_comments_replied_to(
    comment_id: str,
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_forum_comment_replies(db, comment_id, forum_id)


@router.post(
    "/{forum_id}/comments", response_model=ForumComment, status_code=status.HTTP_201_CREATED
)
def post_forum_comment(
    forum_id: str,
    comment: ForumCommentCreateNested,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.create_forum_comment(db, forum_id, comment, current_user)


@router.put(
    "/{forum_id}/comments/{comment_id}",
    response_model=ForumComment,
    status_code=status.HTTP_200_OK,
)
def update_forum_comment(
    forum_id: str,
    comment_id: str,
    updated_comment: ForumCommentUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.update_forum_comment(db, comment_id, updated_comment, current_user)


@router.delete(
    "/{forum_id}/comments/{comment_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def delete_forum_comment_with_replies(
    forum_id: str,
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    detail = service.delete_forum_comment(db, comment_id, current_user)
    return {"detail": detail}


@router.post(
    "/{forum_id}/comments/{comment_id}/like",
    response_model=ForumComment,
    status_code=200,
)
@router.post(
    "/{forum_id}/comments/{comment_id}/toggle-like",
    response_model=ForumComment,
    status_code=200,
)
def toggle_like_forum_comment(
    forum_id: str,
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.toggle_like_forum_comment(db, comment_id, current_user)


# General forum comment endpoints (mimicking post comments behavior)
@router.get("/comments", response_model=List[ForumComment], status_code=status.HTTP_200_OK)
def get_all_forum_comments(
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_all_forum_comments(db)


@router.get("/comments/{comment_id}", response_model=ForumComment, status_code=200)
def get_forum_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_forum_comment(db, comment_id)


@router.post("/comments", response_model=ForumComment, status_code=status.HTTP_201_CREATED)
def create_forum_comment(
    comment: ForumCommentCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.create_general_forum_comment(db, comment, current_user)


@router.put(
    "/comments/{comment_id}", response_model=ForumComment, status_code=status.HTTP_200_OK
)
def update_forum_comment_general(
    comment_id: str,
    updated_comment: ForumCommentUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.update_general_forum_comment(db, comment_id, updated_comment, current_user)


@router.delete(
    "/comments/{comment_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def delete_forum_comment_general(
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    detail = service.delete_general_forum_comment(db, comment_id, current_user)
    return {"detail": detail}


@router.post(
    "/comments/{comment_id}/like", response_model=ForumComment, status_code=200
)
@router.post(
    "/comments/{comment_id}/toggle-like", response_model=ForumComment, status_code=200
)
def toggle_like_forum_comment_general(
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.toggle_like_general_forum_comment(db, comment_id, current_user)


# Forum-specific comment endpoints (mimicking post comments behavior)
@router.get(
    "/forum/{forum_id}/comments",
    response_model=List[ForumComment],
    status_code=status.HTTP_200_OK,
)
def get_forum_comments_by_forum_id(
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_forum_comments_by_forum_id(db, forum_id)


@router.get(
    "/forum/{forum_id}/comments/main",
    response_model=List[ForumComment],
    status_code=status.HTTP_200_OK,
)
def get_main_forum_comments_by_forum_id(
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_main_forum_comments_by_forum_id(db, forum_id)


@router.get(
    "/forum/{forum_id}/comments/replies/{comment_id}",
    response_model=List[ForumComment],
    status_code=status.HTTP_200_OK,
)
def get_forum_comments_replied_to_by_forum_id(
    comment_id: str,
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_forum_comment_replies_by_forum_id(db, comment_id, forum_id)
