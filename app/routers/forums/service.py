from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import shortuuid

from .models import Forums, ForumLike, ForumComment as ForumCommentModel, ForumCommentLike
from .schemas import ForumResponse, ForumComment
from .exceptions import ForumNotFound, ForumNotAuthorized, ForumCommentNotFound, ForumCommentNotAuthorized
from app.services.like_service import toggle_like


def _build_forum_response(forum: Forums, liked: bool = False) -> ForumResponse:
    return ForumResponse.from_orm(forum, liked_by_current_user=liked)


def _build_forum_comment_response(comment: ForumCommentModel, liked: bool = False) -> ForumComment:
    return ForumComment.from_orm(comment, liked_by_current_user=liked)


def get_all_forums(db: Session, current_user) -> List[ForumResponse]:
    forums = db.query(Forums).all()
    if not forums:
        return []

    user_id = current_user.id if current_user else None
    forum_ids = [f.id for f in forums]

    liked_forum_ids = set()
    if user_id:
        liked_forum_ids = {
            row.forum_id
            for row in db.query(ForumLike.forum_id)
            .filter(ForumLike.forum_id.in_(forum_ids), ForumLike.user_id == user_id)
            .all()
        }

    result = []
    for f in forums:
        liked = f.id in liked_forum_ids
        result.append(_build_forum_response(f, liked))
    return result


def get_forum_by_id(db: Session, forum_id: str, current_user) -> ForumResponse:
    forum = db.query(Forums).filter(Forums.id == forum_id).first()
    if forum is None:
        raise ForumNotFound()

    liked = False
    if current_user:
        liked = (
            db.query(ForumLike)
            .filter_by(forum_id=forum_id, user_id=current_user.id)
            .first()
            is not None
        )
    return _build_forum_response(forum, liked)


def create_forum(db: Session, forum_data, current_user) -> ForumResponse:
    new_forum = Forums(
        id=shortuuid.uuid(),
        title=forum_data.title,
        content=forum_data.content,
        author=current_user.username,
        likes=0,
        timestamp=datetime.now(timezone.utc),
        updated_timestamp=datetime.now(timezone.utc),
    )
    db.add(new_forum)
    db.commit()
    db.refresh(new_forum)
    return _build_forum_response(new_forum, False)


def update_forum(db: Session, forum_id: str, forum_data, current_user) -> ForumResponse:
    forum = db.query(Forums).filter(Forums.id == forum_id).first()
    if forum is None:
        raise ForumNotFound()

    if getattr(forum, "author", None) != current_user.username:
        raise ForumNotAuthorized(action="edit")

    if forum_data.title is not None:
        setattr(forum, "title", forum_data.title)
    if forum_data.content is not None:
        setattr(forum, "content", forum_data.content)

    setattr(forum, "updated_timestamp", datetime.now(timezone.utc))
    db.commit()

    liked_by_current_user = (
        db.query(ForumLike)
        .filter_by(forum_id=forum_id, user_id=current_user.id)
        .first()
        is not None
    )
    return _build_forum_response(forum, liked_by_current_user)


def delete_forum(db: Session, forum_id: str, current_user) -> None:
    forum = db.query(Forums).filter(Forums.id == forum_id).first()
    if not forum:
        raise ForumNotFound()
    if str(forum.author) != str(current_user.username):
        raise ForumNotAuthorized(action="delete")
    db.delete(forum)
    db.commit()


def toggle_like_forum(db: Session, forum_id: str, current_user) -> ForumResponse:
    try:
        forum, liked, updated_likes_count = toggle_like(
            db=db,
            entity_id=forum_id,
            user_id=current_user.id,
            entity_model=Forums,
            like_model=ForumLike,
            entity_id_column="forum_id",
            user_id_column="user_id",
            likes_count_column="likes",
        )
    except ValueError:
        raise ForumNotFound()
    return _build_forum_response(forum, liked)


# Forum comment helpers

def get_forum_comments(db: Session, forum_id: str) -> List[ForumComment]:
    comments = db.query(ForumCommentModel).filter(ForumCommentModel.forum_id == forum_id).all()
    return [_build_forum_comment_response(c, False) for c in comments]


def get_main_forum_comments(db: Session, forum_id: str) -> List[ForumComment]:
    main_comments = (
        db.query(ForumCommentModel)
        .filter(ForumCommentModel.forum_id == forum_id, ForumCommentModel.parent_id == None)
        .all()
    )
    return [_build_forum_comment_response(c, False) for c in main_comments]


def get_forum_comment_replies(db: Session, comment_id: str, forum_id: str) -> List[ForumComment]:
    replies = (
        db.query(ForumCommentModel)
        .filter(ForumCommentModel.parent_id == comment_id)
        .filter(ForumCommentModel.forum_id == forum_id)
        .all()
    )
    return [_build_forum_comment_response(r, False) for r in replies]


def create_forum_comment(db: Session, forum_id: str, comment_data, current_user) -> ForumComment:
    new_comment = ForumCommentModel(
        id=shortuuid.uuid(),
        comment=comment_data.comment,
        forum_id=forum_id,
        user_id=current_user.id,
        username=current_user.username,
        parent_id=comment_data.parent_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return _build_forum_comment_response(new_comment, False)


def update_forum_comment(db: Session, comment_id: str, comment_data, current_user) -> ForumComment:
    item_to_update = (
        db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    )
    if item_to_update is None:
        raise ForumCommentNotFound()
    if item_to_update.user_id != current_user.id:
        raise ForumCommentNotAuthorized(action="edit")

    item_to_update.comment = comment_data.comment
    db.commit()

    liked_by_current_user = (
        db.query(ForumCommentLike)
        .filter_by(comment_id=comment_id, user_id=current_user.id)
        .first()
        is not None
    )
    return _build_forum_comment_response(item_to_update, liked_by_current_user)


def delete_forum_comment(db: Session, comment_id: str, current_user) -> str:
    comment_to_delete = (
        db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    )
    if not comment_to_delete:
        raise ForumCommentNotFound()
    if comment_to_delete.user_id != current_user.id:
        raise ForumCommentNotAuthorized(action="delete")

    if comment_to_delete.parent_id is None:
        child_comments = (
            db.query(ForumCommentModel)
            .filter(ForumCommentModel.parent_id == comment_id)
            .all()
        )
        for child in child_comments:
            db.delete(child)

    db.delete(comment_to_delete)
    db.commit()
    return f"Comment with id {comment_id} and its replies have been deleted"


def toggle_like_forum_comment(db: Session, comment_id: str, current_user) -> ForumComment:
    try:
        comment, liked, updated_likes_count = toggle_like(
            db=db,
            entity_id=comment_id,
            user_id=current_user.id,
            entity_model=ForumCommentModel,
            like_model=ForumCommentLike,
            entity_id_column="comment_id",
            user_id_column="user_id",
            likes_count_column="likes",
        )
    except ValueError:
        raise ForumCommentNotFound()
    return _build_forum_comment_response(comment, liked)


# General forum comment endpoints (mimicking post comments behavior)

def get_all_forum_comments(db: Session) -> List[ForumComment]:
    comments = db.query(ForumCommentModel).all()
    return [_build_forum_comment_response(c, False) for c in comments]


def get_forum_comment(db: Session, comment_id: str) -> ForumComment:
    comment = db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    if comment is None:
        raise ForumCommentNotFound()
    return _build_forum_comment_response(comment, False)


def create_general_forum_comment(db: Session, comment_data, current_user) -> ForumComment:
    new_comment = ForumCommentModel(
        id=shortuuid.uuid(),
        comment=comment_data.comment,
        forum_id=comment_data.forum_id,
        user_id=current_user.id,
        username=current_user.username,
        parent_id=comment_data.parent_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return _build_forum_comment_response(new_comment, False)


def update_general_forum_comment(db: Session, comment_id: str, comment_data, current_user) -> ForumComment:
    item_to_update = (
        db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    )
    if item_to_update is None:
        raise ForumCommentNotFound()
    if item_to_update.user_id != current_user.id:
        raise ForumCommentNotAuthorized(action="edit")

    item_to_update.comment = comment_data.comment
    db.commit()

    liked_by_current_user = (
        db.query(ForumCommentLike)
        .filter_by(comment_id=comment_id, user_id=current_user.id)
        .first()
        is not None
    )
    return _build_forum_comment_response(item_to_update, liked_by_current_user)


def delete_general_forum_comment(db: Session, comment_id: str, current_user) -> str:
    comment_to_delete = (
        db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    )
    if not comment_to_delete:
        raise ForumCommentNotFound()
    if comment_to_delete.user_id != current_user.id:
        raise ForumCommentNotAuthorized(action="delete")

    if comment_to_delete.parent_id is None:
        child_comments = (
            db.query(ForumCommentModel)
            .filter(ForumCommentModel.parent_id == comment_id)
            .all()
        )
        for child in child_comments:
            db.delete(child)

    db.delete(comment_to_delete)
    db.commit()
    return f"Forum comment with id {comment_id} and its replies have been deleted"


def toggle_like_general_forum_comment(db: Session, comment_id: str, current_user) -> ForumComment:
    try:
        comment, liked, updated_likes_count = toggle_like(
            db=db,
            entity_id=comment_id,
            user_id=current_user.id,
            entity_model=ForumCommentModel,
            like_model=ForumCommentLike,
            entity_id_column="comment_id",
            user_id_column="user_id",
            likes_count_column="likes",
        )
    except ValueError:
        raise ForumCommentNotFound()
    return _build_forum_comment_response(comment, liked)


# Forum-specific comment endpoints (mimicking post comments behavior)

def get_forum_comments_by_forum_id(db: Session, forum_id: str) -> List[ForumComment]:
    comments = db.query(ForumCommentModel).filter(ForumCommentModel.forum_id == forum_id).all()
    return [_build_forum_comment_response(c, False) for c in comments]


def get_main_forum_comments_by_forum_id(db: Session, forum_id: str) -> List[ForumComment]:
    main_comments = (
        db.query(ForumCommentModel)
        .filter(ForumCommentModel.forum_id == forum_id, ForumCommentModel.parent_id == None)
        .all()
    )
    return [_build_forum_comment_response(c, False) for c in main_comments]


def get_forum_comment_replies_by_forum_id(db: Session, comment_id: str, forum_id: str) -> List[ForumComment]:
    replies = (
        db.query(ForumCommentModel)
        .filter(ForumCommentModel.parent_id == comment_id)
        .filter(ForumCommentModel.forum_id == forum_id)
        .all()
    )
    return [_build_forum_comment_response(r, False) for r in replies]
