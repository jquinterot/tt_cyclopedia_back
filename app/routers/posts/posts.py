from datetime import datetime

from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File, Form, Response, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from .models import Posts, PostLike
from .schemas import PostResponse
from typing import List, Optional
from app.auth.dependencies import get_current_user
from app.routers.users.models import Users
from app.config.postgres_config import get_db
from app.config.cloudinary_config import upload_image, delete_image_from_cloudinary, ALLOWED_TYPES, MAX_FILE_SIZE, DEFAULT_IMAGE_URL
import shortuuid
import json

router = APIRouter(prefix="/posts")

# Configuration - Using Cloudinary for image storage


class Config:
    orm_mode = True


@router.get("", response_model=List[PostResponse], status_code=status.HTTP_200_OK)
def get_posts(
    search: Optional[str] = Query(None, description="Search posts by title or content"),
    db: Session = Depends(get_db)
):
    """
    Get all posts with optional search functionality
    """
    query = db.query(Posts)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Posts.title.ilike(search_term),
                Posts.content.ilike(search_term),
                Posts.author.ilike(search_term)
            )
        )
    posts = query.all()
    result = []
    for post in posts:
        likes_count = db.query(PostLike).filter_by(post_id=post.id).count()
        # likedByCurrentUser is always False for unauthenticated
        result.append(PostResponse(
            id=str(post.id),
            title=str(post.title),
            content=str(post.content),
            image_url=str(post.image_url),
            likes=likes_count,
            author=str(post.author),
            timestamp=post.timestamp,  # type: ignore
            stats=post.stats,  # type: ignore
            likedByCurrentUser=False
        ))
    return result


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
def get_post(post_id: str, request: Request, db: Session = Depends(get_db)):
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    likes_count = db.query(PostLike).filter_by(post_id=post.id).count()
    liked = False
    user = None
    if hasattr(request, 'state') and hasattr(request.state, 'user'):
        user = request.state.user
    if user and hasattr(user, 'id'):
        liked = db.query(PostLike).filter_by(post_id=post.id, user_id=user.id).first() is not None
    return PostResponse(
        id=str(post.id),
        title=str(post.title),
        content=str(post.content),
        image_url=str(post.image_url),
        likes=likes_count,
        author=str(post.author),
        timestamp=post.timestamp,  # type: ignore
        stats=post.stats,  # type: ignore
        likedByCurrentUser=liked
    )


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
        title: str = Form(...),
        content: str = Form(...),
        stats: str = Form(None),  # Accept as string
        image: UploadFile = File(None),
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    import json
    try:
        image_url = DEFAULT_IMAGE_URL

        stats_dict = None
        if stats:
            try:
                stats_dict = json.loads(stats)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid stats JSON format")

        if image and image.filename:
            # Validate file type
            if image.content_type not in ALLOWED_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported file type. Only JPEG, PNG, and WEBP are allowed."
                )

            # Validate file size
            file_size = 0
            for chunk in image.file:
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="File size exceeds 5MB limit"
                    )
            image.file.seek(0)

            # Upload using environment-based logic
            try:
                image_url = upload_image(image)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload image: {str(e)}"
                )

        new_post = Posts(
            title=title,
            content=content,
            image_url=image_url,
            likes=0,
            author=current_user.username,  # Use authenticated user's username
            stats=stats_dict,  # Store as dict/JSON
        )

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        # Calculate likes and likedByCurrentUser
        likes_count = db.query(PostLike).filter_by(post_id=new_post.id).count()
        liked = False
        if current_user:
            liked = db.query(PostLike).filter_by(post_id=new_post.id, user_id=current_user.id).first() is not None

        return PostResponse(
            id=str(new_post.id),
            title=str(new_post.title),
            content=str(new_post.content),
            image_url=str(new_post.image_url),
            likes=likes_count,
            author=str(new_post.author),
            timestamp=new_post.timestamp,  # type: ignore
            stats=new_post.stats,  # type: ignore
            likedByCurrentUser=liked
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post with this title already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating post: {str(e)}"
        )


def is_default_image(image_url: str) -> bool:
    return image_url.startswith("/static/default/")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if str(post.author) != str(current_user.username):
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    db.delete(post)
    db.commit()
    return


@router.delete("/all", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_posts(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only allow admin users to delete all posts (you might want to add an admin field to users)
    try:
        posts = db.query(Posts).all()

        for post in posts:
            if not is_default_image(getattr(post, 'image_url', '')):
                # Delete from Cloudinary
                delete_image_from_cloudinary(post.image_url)

        db.query(Posts).delete()
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error deleting posts: {str(e)}")


@router.post("/{post_id}/like", status_code=204)
def like_post(post_id: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    # Check if post exists
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    like = db.query(PostLike).filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        raise HTTPException(status_code=400, detail="Already liked")
    db.add(PostLike(user_id=current_user.id, post_id=post_id))
    db.commit()
    return Response(status_code=204)


@router.delete("/{post_id}/like", status_code=204)
def unlike_post(post_id: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    # Check if post exists
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    like = db.query(PostLike).filter_by(user_id=current_user.id, post_id=post_id).first()
    if not like:
        raise HTTPException(status_code=400, detail="Not liked yet")
    db.delete(like)
    db.commit()
    return Response(status_code=204)


@router.get("/{post_id}/likes", status_code=200)
def get_post_likes(post_id: str, db: Session = Depends(get_db)):
    # Check if post exists
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    likes = db.query(PostLike).filter_by(post_id=post_id).all()
    return [{"user_id": like.user_id, "created_at": like.created_at} for like in likes]
