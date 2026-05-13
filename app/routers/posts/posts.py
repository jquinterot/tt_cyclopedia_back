from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin, get_current_user, get_current_user_optional
from app.config.cloudinary_config import (
    ALLOWED_TYPES,
    DEFAULT_IMAGE_URL,
    MAX_FILE_SIZE,
    upload_image,
)
from app.config.postgres_config import get_db
from app.middleware.rate_limiter import read_rate_limit, write_rate_limit
from app.routers.users.models import Users

from . import service
from .schemas import PostLikeResponse, PostResponse

router = APIRouter(prefix="/posts")


@router.get("", response_model=list[PostResponse], status_code=status.HTTP_200_OK)
def get_posts(
    search: str | None = Query(
        None, description="Search posts by title or content", min_length=1, max_length=100
    ),
    equipment_id: str | None = Query(None, description="Filter by equipment ID"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_optional),
    _: bool = Depends(read_rate_limit),
):
    return service.get_posts(db, search, equipment_id, current_user)


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
def get_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_optional),
    _: bool = Depends(read_rate_limit),
):
    return service.get_post_by_id(db, post_id, current_user)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    title: str = Form(..., min_length=1, max_length=200),
    content: str = Form(..., min_length=1, max_length=50000),
    stats: str = Form(None, max_length=10000),
    equipment_id: str = Form(None, max_length=50),
    image: UploadFile = File(None),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    image_url = DEFAULT_IMAGE_URL

    if image and image.filename:
        if image.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Only JPEG, PNG, and WEBP are allowed.",
                headers={"X-Error-Code": "POST_005"},
            )
        file_size = 0
        for chunk in image.file:
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size exceeds 5MB limit",
                    headers={"X-Error-Code": "POST_006"},
                )
        image.file.seek(0)
        try:
            image_url = upload_image(image)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image. Please try again.",
                headers={"X-Error-Code": "POST_007"},
            )

    return service.create_post(db, title, content, image_url, stats, equipment_id, current_user)


@router.delete("/all", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_all_posts(
    current_user: Users = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    service.delete_all_posts(db, current_user)
    return


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
    _: bool = Depends(write_rate_limit),
):
    service.delete_post(db, post_id, current_user)
    return


@router.post("/{post_id}/like", response_model=PostResponse, status_code=200)
@router.post("/{post_id}/toggle-like", response_model=PostResponse, status_code=200)
def toggle_like_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
    _: bool = Depends(write_rate_limit),
):
    return service.toggle_like_post(db, post_id, current_user)


@router.get("/{post_id}/likes", response_model=list[PostLikeResponse], status_code=200)
def get_post_likes(
    post_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_post_likes(db, post_id)
