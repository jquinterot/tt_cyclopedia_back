from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config.postgres_config import get_db
from app.routers.users.models import Users

from .exceptions import ForumNotAuthorized, ForumNotFound
from .models import Forums


def valid_forum_id(forum_id: str, db: Session = Depends(get_db)) -> Forums:
    forum = db.query(Forums).filter(Forums.id == forum_id).first()
    if not forum:
        raise ForumNotFound()
    return forum


def valid_owned_forum(
    forum: Forums = Depends(valid_forum_id),
    current_user: Users = Depends(get_current_user),
) -> Forums:
    if forum.author != current_user.username:
        raise ForumNotAuthorized(action="edit")
    return forum
