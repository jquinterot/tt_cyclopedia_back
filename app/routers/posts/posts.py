from datetime import datetime

from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, func
from .models import Posts, PostLike
from .schemas import PostResponse, PostLikeResponse
from app.routers.equipment.models import Equipment
from typing import List, Optional
from app.auth.dependencies import get_current_user, get_current_user_optional, get_current_admin
from app.routers.users.models import Users
from app.config.postgres_config import get_db
from app.config.cloudinary_config import upload_image, delete_image_from_cloudinary, ALLOWED_TYPES, MAX_FILE_SIZE, DEFAULT_IMAGE_URL
from app.middleware.rate_limiter import read_rate_limit, write_rate_limit

router = APIRouter(prefix="/posts")


def build_post_response(post: Posts, db: Session, liked: bool) -> PostResponse:
    """Helper to build a PostResponse with equipment info"""
    equipment = None
    if post.equipment:
        equipment = {
            "id": str(post.equipment.id),
            "name": str(post.equipment.name),
            "brand": str(post.equipment.brand),
            "category": str(post.equipment.category),
        }
    return PostResponse(
        id=str(post.id),
        title=str(post.title),
        content=str(post.content),
        image_url=str(post.image_url),
        likes=db.query(PostLike).filter_by(post_id=post.id).count(),
        author=str(post.author),
        timestamp=post.timestamp,  # type: ignore
        stats=post.stats,  # type: ignore
        likedByCurrentUser=liked,
        equipment_id=post.equipment_id,
        equipment=equipment,
    )


@router.get("", response_model=List[PostResponse], status_code=status.HTTP_200_OK)
def get_posts(
    search: Optional[str] = Query(
        None, description="Search posts by title or content", min_length=1, max_length=100
    ),
    equipment_id: Optional[str] = Query(None, description="Filter by equipment ID"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_optional),
    _: bool = Depends(read_rate_limit),
):
    """
    Get all posts with optional search and equipment filter
    """
    query = db.query(Posts).options(selectinload(Posts.equipment))
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Posts.title.ilike(search_term),
                Posts.content.ilike(search_term),
                Posts.author.ilike(search_term),
            )
        )
    if equipment_id:
        query = query.filter(Posts.equipment_id == equipment_id)
    posts = query.all()
    if not posts:
        return []

    post_ids = [post.id for post in posts]
    user_id = current_user.id if current_user else None

    # Batch-fetch like counts
    like_counts = {
        row.post_id: row.count
        for row in db.query(
            PostLike.post_id, func.count(PostLike.id).label("count")
        ).filter(PostLike.post_id.in_(post_ids)).group_by(PostLike.post_id).all()
    }

    # Batch-fetch liked-by-current-user status
    liked_post_ids = set()
    if user_id:
        liked_post_ids = {
            row.post_id
            for row in db.query(PostLike.post_id)
            .filter(PostLike.post_id.in_(post_ids), PostLike.user_id == user_id)
            .all()
        }

    result = []
    for post in posts:
        liked = post.id in liked_post_ids
        equipment = None
        if post.equipment:
            equipment = {
                "id": str(post.equipment.id),
                "name": str(post.equipment.name),
                "brand": str(post.equipment.brand),
                "category": str(post.equipment.category),
            }
        result.append(PostResponse(
            id=str(post.id),
            title=str(post.title),
            content=str(post.content),
            image_url=str(post.image_url),
            likes=like_counts.get(post.id, 0),
            author=str(post.author),
            timestamp=post.timestamp,
            stats=post.stats,
            likedByCurrentUser=liked,
            equipment_id=post.equipment_id,
            equipment=equipment,
        ))
    return result


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
def get_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_optional),
    _: bool = Depends(read_rate_limit),
):
    post = db.query(Posts).options(selectinload(Posts.equipment)).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
            headers={"X-Error-Code": "POST_001"},
        )
    liked = False
    if current_user:
        liked = (
            db.query(PostLike)
            .filter_by(post_id=post.id, user_id=current_user.id)
            .first()
            is not None
        )
    return build_post_response(post, db, liked)


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
    import json

    try:
        image_url = DEFAULT_IMAGE_URL

        stats_dict = None
        if stats:
            try:
                stats_dict = json.loads(stats)
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid stats JSON format",
                    headers={"X-Error-Code": "POST_003"},
                )

        # Validate equipment_id if provided
        if equipment_id:
            equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
            if not equipment:
                raise HTTPException(
                    status_code=400,
                    detail="Equipment not found",
                    headers={"X-Error-Code": "POST_004"},
                )

        if image and image.filename:
            # Validate file type
            if image.content_type not in ALLOWED_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported file type. Only JPEG, PNG, and WEBP are allowed.",
                    headers={"X-Error-Code": "POST_005"},
                )

            # Validate file size
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

            # Upload using environment-based logic
            try:
                image_url = upload_image(image)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload image. Please try again.",
                    headers={"X-Error-Code": "POST_007"},
                )

        new_post = Posts(
            title=title,
            content=content,
            image_url=image_url,
            likes=0,
            author=current_user.username,
            stats=stats_dict,
            equipment_id=equipment_id,
        )

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        # Load equipment relationship for response
        if new_post.equipment_id:
            db.refresh(new_post, ["equipment"])

        return build_post_response(new_post, db, False)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post with this title already exists",
            headers={"X-Error-Code": "POST_008"},
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating post. Please try again.",
            headers={"X-Error-Code": "POST_008"},
        )


def is_default_image(image_url: str) -> bool:
    return image_url.startswith("/static/default/")


# NOTE: /all must be registered BEFORE /{post_id} so that "all" is not
# treated as a dynamic post_id.
@router.delete("/all", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_all_posts(
    current_user: Users = Depends(get_current_admin),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    try:
        posts = db.query(Posts).all()

        for post in posts:
            if not is_default_image(getattr(post, "image_url", "")):
                # Delete from Cloudinary
                delete_image_from_cloudinary(post.image_url)

        db.query(Posts).delete()
        db.commit()

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting posts. Please try again.",
            headers={"X-Error-Code": "POST_009"},
        )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
    _: bool = Depends(write_rate_limit),
):
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
            headers={"X-Error-Code": "POST_001"},
        )
    if str(post.author) != str(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
            headers={"X-Error-Code": "POST_002"},
        )
    db.delete(post)
    db.commit()
    return


@router.post("/{post_id}/like", response_model=PostResponse, status_code=200)
@router.post("/{post_id}/toggle-like", response_model=PostResponse, status_code=200)
def toggle_like_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
    _: bool = Depends(write_rate_limit),
):
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
            headers={"X-Error-Code": "POST_001"},
        )

    existing_like = db.query(PostLike).filter_by(
        user_id=current_user.id, post_id=post_id
    ).first()

    if existing_like:
        # Unlike the post (dislike)
        db.delete(existing_like)
        # Update post likes count, but don't go below 0
        current_likes = int(post.likes) if post.likes is not None else 0  # type: ignore
        if current_likes > 0:
            setattr(post, "likes", current_likes - 1)
        db.commit()
    else:
        # Like the post
        new_like = PostLike(user_id=current_user.id, post_id=post_id)
        db.add(new_like)
        # Update post likes count
        current_likes = int(post.likes) if post.likes is not None else 0  # type: ignore
        setattr(post, "likes", current_likes + 1)
        db.commit()

    # Get updated like count and liked status
    updated_likes_count = int(post.likes) if post.likes is not None else 0  # type: ignore
    liked_by_current_user = (
        db.query(PostLike)
        .filter_by(post_id=post_id, user_id=current_user.id)
        .first()
        is not None
    )

    return build_post_response(post, db, liked_by_current_user)


@router.get(
    "/{post_id}/likes", response_model=List[PostLikeResponse], status_code=200
)
def get_post_likes(
    post_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    # Check if post exists
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
            headers={"X-Error-Code": "POST_001"},
        )

    likes = db.query(PostLike).filter_by(post_id=post_id).all()
    return [
        {"user_id": like.user_id, "created_at": like.created_at} for like in likes
    ]
