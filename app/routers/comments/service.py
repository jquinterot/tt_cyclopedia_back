from sqlalchemy.orm import Session
from typing import List
import shortuuid

from .models import Comments, CommentLike
from .schemas import Comment
from .exceptions import CommentNotFound, CommentNotAuthorized
from app.services.like_service import toggle_like


def _build_comment_response(comment: Comments, liked: bool = False) -> Comment:
    return Comment.from_orm(comment, liked_by_current_user=liked)


def get_comments(db: Session) -> List[Comment]:
    comments = db.query(Comments).all()
    return [_build_comment_response(c, False) for c in comments]


def get_comment_by_id(db: Session, comment_id: str) -> Comment:
    item_to_get = db.query(Comments).filter(Comments.id == comment_id).first()
    if item_to_get is None:
        raise CommentNotFound()
    return _build_comment_response(item_to_get, False)


def create_comment(db: Session, comment_data, current_user) -> Comment:
    new_comment = Comments(
        id=shortuuid.uuid(),
        comment=comment_data.comment,
        post_id=comment_data.post_id,
        forum_id=comment_data.forum_id,
        user_id=current_user.id,
        username=current_user.username,
        parent_id=comment_data.parent_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return _build_comment_response(new_comment, False)


def update_comment(db: Session, comment_id: str, comment_data, current_user) -> Comment:
    item_to_update = db.query(Comments).filter(Comments.id == comment_id).first()
    if item_to_update is None:
        raise CommentNotFound()
    if item_to_update.user_id != current_user.id:
        raise CommentNotAuthorized(action="edit")
    item_to_update.comment = comment_data.comment
    db.commit()
    liked_by_current_user = (
        db.query(CommentLike)
        .filter_by(comment_id=item_to_update.id, user_id=current_user.id)
        .first()
        is not None
    )
    return _build_comment_response(item_to_update, liked_by_current_user)


def delete_comment(db: Session, comment_id: str, current_user) -> str:
    comment_to_delete = db.query(Comments).filter(Comments.id == comment_id).first()
    if not comment_to_delete:
        raise CommentNotFound()
    if comment_to_delete.user_id != current_user.id:
        raise CommentNotAuthorized(action="delete")

    if comment_to_delete.parent_id is None:
        child_comments = db.query(Comments).filter(Comments.parent_id == comment_id).all()
        for child in child_comments:
            db.delete(child)

    db.delete(comment_to_delete)
    db.commit()
    return f"Comment with id {comment_id} and its replies have been deleted"


def get_comments_by_post(db: Session, post_id: str) -> List[Comment]:
    comments = db.query(Comments).filter(Comments.post_id == post_id).all()
    return [_build_comment_response(c, False) for c in comments]


def get_main_comments(db: Session, post_id: str) -> List[Comment]:
    main_comments = (
        db.query(Comments)
        .filter(Comments.post_id == post_id, Comments.parent_id == None)
        .all()
    )
    return [_build_comment_response(c, False) for c in main_comments]


def get_replies(db: Session, comment_id: str, post_id: str) -> List[Comment]:
    replies = (
        db.query(Comments)
        .filter(Comments.parent_id == comment_id)
        .filter(Comments.post_id == post_id)
        .all()
    )
    return [_build_comment_response(r, False) for r in replies]


def toggle_like_comment(db: Session, comment_id: str, current_user) -> Comment:
    try:
        comment, liked, updated_likes_count = toggle_like(
            db=db,
            entity_id=comment_id,
            user_id=current_user.id,
            entity_model=Comments,
            like_model=CommentLike,
            entity_id_column="comment_id",
            user_id_column="user_id",
            likes_count_column="likes",
        )
    except ValueError:
        raise CommentNotFound()
    return _build_comment_response(comment, liked)


# Forum comment variants within the comments router

def get_forum_comments(db: Session, forum_id: str) -> List[Comment]:
    comments = db.query(Comments).filter(Comments.forum_id == forum_id).all()
    return [_build_comment_response(c, False) for c in comments]


def get_main_forum_comments(db: Session, forum_id: str) -> List[Comment]:
    main_comments = (
        db.query(Comments)
        .filter(Comments.forum_id == forum_id, Comments.parent_id == None)
        .all()
    )
    return [_build_comment_response(c, False) for c in main_comments]


def get_forum_replies(db: Session, comment_id: str, forum_id: str) -> List[Comment]:
    replies = (
        db.query(Comments)
        .filter(Comments.parent_id == comment_id)
        .filter(Comments.forum_id == forum_id)
        .all()
    )
    return [_build_comment_response(r, False) for r in replies]


def create_forum_comment(db: Session, forum_id: str, comment_data, current_user) -> Comment:
    new_comment = Comments(
        id=shortuuid.uuid(),
        comment=comment_data.comment,
        forum_id=forum_id,
        post_id=comment_data.post_id,
        user_id=current_user.id,
        username=current_user.username,
        parent_id=comment_data.parent_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return _build_comment_response(new_comment, False)
