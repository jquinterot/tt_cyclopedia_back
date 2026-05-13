from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config.postgres_config import get_db
from app.routers.users.models import Users

from .exceptions import CommentNotAuthorized, CommentNotFound
from .models import Comments


def valid_comment_id(comment_id: str, db: Session = Depends(get_db)) -> Comments:
    comment = db.query(Comments).filter(Comments.id == comment_id).first()
    if not comment:
        raise CommentNotFound()
    return comment


def valid_owned_comment(
    comment: Comments = Depends(valid_comment_id),
    current_user: Users = Depends(get_current_user),
) -> Comments:
    if comment.user_id != current_user.id:
        raise CommentNotAuthorized(action="edit")
    return comment
