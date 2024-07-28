from fastapi import APIRouter, status
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

@router.post("", response_model=Post, status_code=status.HTTP_201_CREATED)
def post_comment(post: Post):
    new_post = Posts(
        id=shortuuid.uuid(),
        title=post.title,
        content=post.content
    , img=post.img, likes=post.likes)
    db.add(new_post)
    db.commit()
    return new_post
