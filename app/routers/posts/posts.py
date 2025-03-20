from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import Posts
from .schemas import PostCreate, PostResponse
from typing import List
from app.config.postgres_config import SessionLocal
import shortuuid
from pathlib import Path
from app.config.image_config import DEFAULT_IMAGE_DIR, UPLOAD_DIR
import shutil

router = APIRouter(prefix="/posts")

# Configuration
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_IMAGE_URL = "/static/default/default.jpeg"  # Ensure this path is correct
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[PostResponse], status_code=status.HTTP_200_OK)
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Posts).all()
    return posts


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
def get_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
        title: str = Form(...),
        content: str = Form(...),
        image: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    try:
        image_url = DEFAULT_IMAGE_URL

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

            # Generate unique filename
            file_ext = image.filename.split(".")[-1]
            filename = f"{shortuuid.uuid()}.{file_ext}"
            file_path = UPLOAD_DIR / filename

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            image_url = f"/static/uploads/{filename}"

        # Create post
        new_post = Posts(
            title=title,
            content=content,
            image_url=image_url,
            likes=0
        )

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return new_post

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
def delete_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Posts).filter(Posts.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        # Delete associated image only if it's user-uploaded
        if not is_default_image(post.image_url):
            filename = post.image_url.split("/")[-1]
            file_path = UPLOAD_DIR / filename
            if file_path.exists():
                file_path.unlink()

        db.delete(post)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error deleting post: {str(e)}")


@router.delete("/all", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_posts(db: Session = Depends(get_db)):
    try:
        posts = db.query(Posts).all()

        for post in posts:
            if not is_default_image(post.image_url):
                filename = post.image_url.split("/")[-1]
                file_path = UPLOAD_DIR / filename
                if file_path.exists():
                    file_path.unlink()

        db.query(Posts).delete()
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error deleting posts: {str(e)}")
