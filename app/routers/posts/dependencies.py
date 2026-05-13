from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config.postgres_config import get_db
from app.routers.users.models import Users

from .exceptions import PostNotAuthorized, PostNotFound
from .models import Posts


def valid_post_id(post_id: str, db: Session = Depends(get_db)) -> Posts:
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise PostNotFound()
    return post


def valid_owned_post(
    post: Posts = Depends(valid_post_id),
    current_user: Users = Depends(get_current_user),
) -> Posts:
    if str(post.author) != str(current_user.username):
        raise PostNotAuthorized()
    return post
