from fastapi import APIRouter, status, HTTPException
from .models import Posts
from .schemas import Post
from typing import Optional, List
from app.config.postgres_config import SessionLocal
import shortuuid

router = APIRouter(prefix="/posts",
                   )


class Config:
    orm_mode = True


db = SessionLocal()


@router.get("", response_model=List[Post], status_code=status.HTTP_200_OK)
def get_posts():
    posts = db.query(Posts).all()
    return posts


@router.get("/{post_id}", response_model=Post, status_code=status.HTTP_200_OK)
def get_posts(post_id):
    post_to_get = db.query(Posts).filter(Posts.id == post_id).first()

    if post_to_get is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resourse Not Found")
    return post_to_get


@router.post("", response_model=Post, status_code=status.HTTP_201_CREATED)
def post_comment(post: Post):
    existing_post: str = db.query(Posts).filter(Posts.title == post.title).first()

    if existing_post is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post already exists")

    new_post = Posts(
        id=shortuuid.uuid(),
        title=post.title,
        content=post.content,
        img=post.img, likes=post.likes)

    db.add(new_post)
    db.commit()
    return new_post
