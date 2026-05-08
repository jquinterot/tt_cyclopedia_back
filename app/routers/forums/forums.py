from fastapi import APIRouter, status, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from .schemas import (
    ForumCreate,
    ForumResponse,
    ForumUpdate,
    ForumComment,
    ForumCommentCreate,
    ForumCommentCreateNested,
    ForumCommentUpdate,
)
from .models import Forums, ForumLike, ForumComment as ForumCommentModel, ForumCommentLike
from typing import List
from app.auth.dependencies import get_current_user, get_current_user_optional
from app.routers.users.models import Users
from app.config.postgres_config import get_db
import shortuuid
from datetime import datetime, timezone
from app.middleware.rate_limiter import read_rate_limit, write_rate_limit

router = APIRouter(prefix="/forums")


class MessageResponse(BaseModel):
    detail: str


@router.get("", response_model=List[ForumResponse], status_code=status.HTTP_200_OK)
def get_all_forums(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_optional),
    _: bool = Depends(read_rate_limit),
):
    """
    Get all forums - Public endpoint, no authentication required
    """
    forums = db.query(Forums).all()
    if not forums:
        return []

    user_id = current_user.id if current_user else None
    forum_ids = [f.id for f in forums]

    # Batch-fetch liked-by-current-user status to avoid N+1
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
        result.append(
            ForumResponse(
                id=str(f.id),
                title=str(f.title),
                content=str(f.content),
                author=str(f.author),
                likes=f.likes or 0,  # type: ignore
                timestamp=f.timestamp,  # type: ignore
                updated_timestamp=f.updated_timestamp,  # type: ignore
                liked_by_current_user=liked,
            )
        )
    return result


@router.get("/{forum_id}", response_model=ForumResponse, status_code=status.HTTP_200_OK)
def get_forum_by_id(
    forum_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_optional),
    _: bool = Depends(read_rate_limit),
):
    """
    Get a specific forum by ID - Public endpoint, no authentication required
    """
    forum = db.query(Forums).filter(Forums.id == forum_id).first()

    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum not found",
            headers={"X-Error-Code": "FORUM_001"},
        )

    liked = False
    if current_user:
        liked = (
            db.query(ForumLike)
            .filter_by(forum_id=forum_id, user_id=current_user.id)
            .first()
            is not None
        )

    return ForumResponse(
        id=str(forum.id),
        title=str(forum.title),
        content=str(forum.content),
        author=str(forum.author),
        likes=forum.likes or 0,  # type: ignore
        timestamp=forum.timestamp,  # type: ignore
        updated_timestamp=forum.updated_timestamp,  # type: ignore
        liked_by_current_user=liked,
    )


@router.post("", response_model=ForumResponse, status_code=status.HTTP_201_CREATED)
def create_forum(
    forum: ForumCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    new_forum = Forums(
        id=shortuuid.uuid(),
        title=forum.title,
        content=forum.content,
        author=current_user.username,
        likes=0,
        timestamp=datetime.now(timezone.utc),
        updated_timestamp=datetime.now(timezone.utc),
    )

    db.add(new_forum)
    db.commit()
    db.refresh(new_forum)

    return ForumResponse(
        id=str(new_forum.id),
        title=str(new_forum.title),
        content=str(new_forum.content),
        author=str(new_forum.author),
        likes=new_forum.likes or 0,  # type: ignore
        timestamp=new_forum.timestamp,  # type: ignore
        updated_timestamp=new_forum.updated_timestamp,  # type: ignore
        liked_by_current_user=False,
    )


@router.put("/{forum_id}", response_model=ForumResponse, status_code=status.HTTP_200_OK)
def update_forum(
    forum_id: str,
    forum_update: ForumUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    """
    Update a forum - Requires authentication and ownership
    """
    forum = db.query(Forums).filter(Forums.id == forum_id).first()

    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum not found",
            headers={"X-Error-Code": "FORUM_001"},
        )

    # Check if the user owns this forum
    if getattr(forum, "author", None) != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own forums",
            headers={"X-Error-Code": "FORUM_002"},
        )

    # Use setattr to avoid linter errors
    if forum_update.title is not None:
        setattr(forum, "title", forum_update.title)
    if forum_update.content is not None:
        setattr(forum, "content", forum_update.content)

    setattr(forum, "updated_timestamp", datetime.now(timezone.utc))

    db.commit()

    liked_by_current_user = (
        db.query(ForumLike)
        .filter_by(forum_id=forum_id, user_id=current_user.id)
        .first()
        is not None
    )

    return ForumResponse(
        id=str(forum.id),
        title=str(forum.title),
        content=str(forum.content),
        author=str(forum.author),
        likes=forum.likes or 0,  # type: ignore
        timestamp=forum.timestamp,  # type: ignore
        updated_timestamp=forum.updated_timestamp,  # type: ignore
        liked_by_current_user=liked_by_current_user,
    )


@router.delete("/{forum_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_forum(
    forum_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
    _: bool = Depends(write_rate_limit),
):
    forum = db.query(Forums).filter(Forums.id == forum_id).first()
    if not forum:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum not found",
            headers={"X-Error-Code": "FORUM_001"},
        )
    if str(forum.author) != str(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this forum",
            headers={"X-Error-Code": "FORUM_003"},
        )
    db.delete(forum)
    db.commit()
    return


# Forum Like Endpoints
@router.post("/{forum_id}/like", response_model=ForumResponse, status_code=200)
@router.post("/{forum_id}/toggle-like", response_model=ForumResponse, status_code=200)
def toggle_like_forum(
    forum_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    forum = db.query(Forums).filter_by(id=forum_id).first()
    if not forum:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum not found",
            headers={"X-Error-Code": "FORUM_001"},
        )

    existing_like = db.query(ForumLike).filter_by(
        forum_id=forum_id, user_id=current_user.id
    ).first()

    if existing_like:
        # Unlike the forum (dislike)
        db.delete(existing_like)
        # Update forum likes count, but don't go below 0
        current_likes = int(forum.likes) if forum.likes is not None else 0  # type: ignore
        if current_likes > 0:
            setattr(forum, "likes", current_likes - 1)
        db.commit()
    else:
        # Like the forum
        new_like = ForumLike(forum_id=forum_id, user_id=current_user.id)
        db.add(new_like)
        # Update forum likes count
        current_likes = int(forum.likes) if forum.likes is not None else 0  # type: ignore
        setattr(forum, "likes", current_likes + 1)
        db.commit()

    # Get updated like count and liked status
    updated_likes_count = int(forum.likes) if forum.likes is not None else 0  # type: ignore
    liked_by_current_user = (
        db.query(ForumLike)
        .filter_by(forum_id=forum_id, user_id=current_user.id)
        .first()
        is not None
    )

    return ForumResponse(
        id=str(forum.id),
        title=str(forum.title),
        content=str(forum.content),
        author=str(forum.author),
        likes=updated_likes_count,
        timestamp=forum.timestamp,  # type: ignore
        updated_timestamp=forum.updated_timestamp,  # type: ignore
        liked_by_current_user=liked_by_current_user,
    )


# Forum Comments Endpoints
@router.get(
    "/{forum_id}/comments", response_model=List[ForumComment], status_code=status.HTTP_200_OK
)
def get_forum_comments(
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    comments = db.query(ForumCommentModel).filter(ForumCommentModel.forum_id == forum_id).all()
    result = []
    for c in comments:
        result.append(
            ForumComment(
                id=str(c.id),
                comment=str(c.comment),
                forum_id=str(c.forum_id),
                parent_id=c.parent_id,  # type: ignore
                user_id=c.user_id,  # type: ignore
                username=c.username,  # type: ignore
                liked_by_current_user=False,
                likes=c.likes or 0,  # type: ignore
                timestamp=c.timestamp,  # type: ignore
            )
        )
    return result


@router.get(
    "/{forum_id}/comments/main",
    response_model=List[ForumComment],
    status_code=status.HTTP_200_OK,
)
def get_main_forum_comments(
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    main_comments = (
        db.query(ForumCommentModel)
        .filter(ForumCommentModel.forum_id == forum_id, ForumCommentModel.parent_id == None)
        .all()
    )

    result = []
    for comment in main_comments:
        result.append(
            ForumComment(
                id=str(comment.id),
                comment=str(comment.comment),
                forum_id=str(comment.forum_id),
                parent_id=comment.parent_id,  # type: ignore
                user_id=comment.user_id,  # type: ignore
                username=comment.username,  # type: ignore
                liked_by_current_user=False,
                likes=comment.likes or 0,  # type: ignore
                timestamp=comment.timestamp,  # type: ignore
            )
        )

    return result


@router.get(
    "/{forum_id}/comments/replies/{comment_id}",
    response_model=List[ForumComment],
    status_code=status.HTTP_200_OK,
)
def get_forum_comments_replied_to(
    comment_id: str,
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    replies = (
        db.query(ForumCommentModel)
        .filter(ForumCommentModel.parent_id == comment_id)
        .filter(ForumCommentModel.forum_id == forum_id)
        .all()
    )

    result = []
    for reply in replies:
        result.append(
            ForumComment(
                id=str(reply.id),
                comment=str(reply.comment),
                forum_id=str(reply.forum_id),
                parent_id=reply.parent_id,  # type: ignore
                user_id=reply.user_id,  # type: ignore
                username=reply.username,  # type: ignore
                liked_by_current_user=False,
                likes=reply.likes or 0,  # type: ignore
                timestamp=reply.timestamp,  # type: ignore
            )
        )

    return result


@router.post(
    "/{forum_id}/comments", response_model=ForumComment, status_code=status.HTTP_201_CREATED
)
def post_forum_comment(
    forum_id: str,
    comment: ForumCommentCreateNested,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    new_comment = ForumCommentModel(
        id=shortuuid.uuid(),
        comment=comment.comment,
        forum_id=forum_id,
        user_id=current_user.id,
        username=current_user.username,
        parent_id=comment.parent_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return ForumComment(
        id=str(new_comment.id),
        comment=str(new_comment.comment),
        forum_id=str(new_comment.forum_id),
        parent_id=new_comment.parent_id,  # type: ignore
        user_id=new_comment.user_id,  # type: ignore
        username=new_comment.username,  # type: ignore
        liked_by_current_user=False,
        likes=new_comment.likes or 0,  # type: ignore
        timestamp=new_comment.timestamp,  # type: ignore
    )


@router.put(
    "/{forum_id}/comments/{comment_id}",
    response_model=ForumComment,
    status_code=status.HTTP_200_OK,
)
def update_forum_comment(
    forum_id: str,
    comment_id: str,
    updated_comment: ForumCommentUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    item_to_update = (
        db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    )
    if item_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
            headers={"X-Error-Code": "FORUM_004"},
        )
    if item_to_update.user_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
            headers={"X-Error-Code": "FORUM_005"},
        )

    item_to_update.comment = updated_comment.comment  # type: ignore
    db.commit()

    liked_by_current_user = (
        db.query(ForumCommentLike)
        .filter_by(comment_id=comment_id, user_id=current_user.id)
        .first()
        is not None
    )
    return ForumComment(
        id=str(item_to_update.id),
        comment=str(item_to_update.comment),
        forum_id=str(item_to_update.forum_id),
        parent_id=item_to_update.parent_id,  # type: ignore
        user_id=item_to_update.user_id,  # type: ignore
        username=item_to_update.username,  # type: ignore
        likes=item_to_update.likes or 0,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        timestamp=item_to_update.timestamp,  # type: ignore
    )


@router.delete(
    "/{forum_id}/comments/{comment_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def delete_forum_comment_with_replies(
    forum_id: str,
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    comment_to_delete = (
        db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    )
    if not comment_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
            headers={"X-Error-Code": "FORUM_004"},
        )
    if comment_to_delete.user_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
            headers={"X-Error-Code": "FORUM_006"},
        )

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
    return {"detail": f"Comment with id {comment_id} and its replies have been deleted"}


@router.post(
    "/{forum_id}/comments/{comment_id}/like",
    response_model=ForumComment,
    status_code=200,
)
@router.post(
    "/{forum_id}/comments/{comment_id}/toggle-like",
    response_model=ForumComment,
    status_code=200,
)
def toggle_like_forum_comment(
    forum_id: str,
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    comment = db.query(ForumCommentModel).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
            headers={"X-Error-Code": "FORUM_004"},
        )

    existing_like = db.query(ForumCommentLike).filter_by(
        comment_id=comment_id, user_id=current_user.id
    ).first()

    if existing_like:
        # Unlike the comment (dislike)
        db.delete(existing_like)
        # Update comment likes count, but don't go below 0
        current_likes = int(comment.likes) if comment.likes is not None else 0  # type: ignore
        if current_likes > 0:
            setattr(comment, "likes", current_likes - 1)
        db.commit()
    else:
        # Like the comment
        new_like = ForumCommentLike(comment_id=comment_id, user_id=current_user.id)
        db.add(new_like)
        # Update comment likes count
        current_likes = int(comment.likes) if comment.likes is not None else 0  # type: ignore
        setattr(comment, "likes", current_likes + 1)
        db.commit()

    # Get updated like count and liked status
    updated_likes_count = int(comment.likes) if comment.likes is not None else 0  # type: ignore
    liked_by_current_user = (
        db.query(ForumCommentLike)
        .filter_by(comment_id=comment_id, user_id=current_user.id)
        .first()
        is not None
    )

    return ForumComment(
        id=str(comment.id),
        comment=str(comment.comment),
        forum_id=str(comment.forum_id),
        parent_id=comment.parent_id,  # type: ignore
        user_id=comment.user_id,  # type: ignore
        username=comment.username,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        likes=updated_likes_count,
        timestamp=comment.timestamp,  # type: ignore
    )


# General forum comment endpoints (mimicking post comments behavior)
@router.get("/comments", response_model=List[ForumComment], status_code=status.HTTP_200_OK)
def get_all_forum_comments(
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    """
    Get all forum comments - mimics post comments behavior
    """
    comments = db.query(ForumCommentModel).all()
    result = []
    for c in comments:
        result.append(
            ForumComment(
                id=str(c.id),
                comment=str(c.comment),
                forum_id=str(c.forum_id),
                parent_id=c.parent_id,  # type: ignore
                user_id=c.user_id,  # type: ignore
                username=c.username,  # type: ignore
                liked_by_current_user=False,
                likes=c.likes or 0,  # type: ignore
                timestamp=c.timestamp,  # type: ignore
            )
        )
    return result


@router.get("/comments/{comment_id}", response_model=ForumComment, status_code=200)
def get_forum_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    """
    Get a specific forum comment by ID - mimics post comments behavior
    """
    comment = db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum comment not found",
            headers={"X-Error-Code": "FORUM_004"},
        )

    return ForumComment(
        id=str(comment.id),
        comment=str(comment.comment),
        forum_id=str(comment.forum_id),
        parent_id=comment.parent_id,  # type: ignore
        user_id=comment.user_id,  # type: ignore
        username=comment.username,  # type: ignore
        liked_by_current_user=False,  # Will be set by frontend if needed
        likes=comment.likes or 0,  # type: ignore
        timestamp=comment.timestamp,  # type: ignore
    )


@router.post("/comments", response_model=ForumComment, status_code=status.HTTP_201_CREATED)
def create_forum_comment(
    comment: ForumCommentCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    """
    Create a new forum comment - mimics post comments behavior
    """
    new_comment = ForumCommentModel(
        id=shortuuid.uuid(),
        comment=comment.comment,
        forum_id=comment.forum_id,
        user_id=current_user.id,
        username=current_user.username,
        parent_id=comment.parent_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return ForumComment(
        id=str(new_comment.id),
        comment=str(new_comment.comment),
        forum_id=str(new_comment.forum_id),
        parent_id=new_comment.parent_id,  # type: ignore
        user_id=new_comment.user_id,  # type: ignore
        username=new_comment.username,  # type: ignore
        liked_by_current_user=False,
        likes=new_comment.likes or 0,  # type: ignore
        timestamp=new_comment.timestamp,  # type: ignore
    )


@router.put(
    "/comments/{comment_id}", response_model=ForumComment, status_code=status.HTTP_200_OK
)
def update_forum_comment_general(
    comment_id: str,
    updated_comment: ForumCommentUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    """
    Update a forum comment - mimics post comments behavior
    """
    item_to_update = (
        db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    )
    if item_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum comment not found",
            headers={"X-Error-Code": "FORUM_004"},
        )
    if item_to_update.user_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
            headers={"X-Error-Code": "FORUM_005"},
        )

    item_to_update.comment = updated_comment.comment  # type: ignore
    db.commit()

    liked_by_current_user = (
        db.query(ForumCommentLike)
        .filter_by(comment_id=comment_id, user_id=current_user.id)
        .first()
        is not None
    )
    return ForumComment(
        id=str(item_to_update.id),
        comment=str(item_to_update.comment),
        forum_id=str(item_to_update.forum_id),
        parent_id=item_to_update.parent_id,  # type: ignore
        user_id=item_to_update.user_id,  # type: ignore
        username=item_to_update.username,  # type: ignore
        likes=item_to_update.likes or 0,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        timestamp=item_to_update.timestamp,  # type: ignore
    )


@router.delete(
    "/comments/{comment_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def delete_forum_comment_general(
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    """
    Delete a forum comment with replies - mimics post comments behavior
    """
    comment_to_delete = (
        db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    )
    if not comment_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum comment not found",
            headers={"X-Error-Code": "FORUM_004"},
        )
    if comment_to_delete.user_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
            headers={"X-Error-Code": "FORUM_006"},
        )

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
    return {"detail": f"Forum comment with id {comment_id} and its replies have been deleted"}


@router.post(
    "/comments/{comment_id}/like", response_model=ForumComment, status_code=200
)
@router.post(
    "/comments/{comment_id}/toggle-like", response_model=ForumComment, status_code=200
)
def toggle_like_forum_comment_general(
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    """
    Toggle like on a forum comment - mimics post comments behavior
    """
    comment = db.query(ForumCommentModel).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum comment not found",
            headers={"X-Error-Code": "FORUM_004"},
        )

    existing_like = db.query(ForumCommentLike).filter_by(
        comment_id=comment_id, user_id=current_user.id
    ).first()

    if existing_like:
        # Unlike the comment (dislike)
        db.delete(existing_like)
        # Update comment likes count, but don't go below 0
        current_likes = int(comment.likes) if comment.likes is not None else 0  # type: ignore
        if current_likes > 0:
            setattr(comment, "likes", current_likes - 1)
        db.commit()
    else:
        # Like the comment
        new_like = ForumCommentLike(comment_id=comment_id, user_id=current_user.id)
        db.add(new_like)
        # Update comment likes count
        current_likes = int(comment.likes) if comment.likes is not None else 0  # type: ignore
        setattr(comment, "likes", current_likes + 1)
        db.commit()

    # Get updated like count and liked status
    updated_likes_count = int(comment.likes) if comment.likes is not None else 0  # type: ignore
    liked_by_current_user = (
        db.query(ForumCommentLike)
        .filter_by(comment_id=comment_id, user_id=current_user.id)
        .first()
        is not None
    )

    return ForumComment(
        id=str(comment.id),
        comment=str(comment.comment),
        forum_id=str(comment.forum_id),
        parent_id=comment.parent_id,  # type: ignore
        user_id=comment.user_id,  # type: ignore
        username=comment.username,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        likes=updated_likes_count,
        timestamp=comment.timestamp,  # type: ignore
    )


# Forum-specific comment endpoints (mimicking post comments behavior)
@router.get(
    "/forum/{forum_id}/comments",
    response_model=List[ForumComment],
    status_code=status.HTTP_200_OK,
)
def get_forum_comments_by_forum_id(
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    """
    Get all comments for a specific forum - mimics post comments behavior
    """
    comments = db.query(ForumCommentModel).filter(ForumCommentModel.forum_id == forum_id).all()

    result = []
    for comment in comments:
        result.append(
            ForumComment(
                id=str(comment.id),
                comment=str(comment.comment),
                forum_id=str(comment.forum_id),
                parent_id=comment.parent_id,  # type: ignore
                user_id=comment.user_id,  # type: ignore
                username=comment.username,  # type: ignore
                liked_by_current_user=False,
                likes=comment.likes or 0,  # type: ignore
                timestamp=comment.timestamp,  # type: ignore
            )
        )

    return result


@router.get(
    "/forum/{forum_id}/comments/main",
    response_model=List[ForumComment],
    status_code=status.HTTP_200_OK,
)
def get_main_forum_comments_by_forum_id(
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    """
    Get main comments for a specific forum - mimics post comments behavior
    """
    main_comments = (
        db.query(ForumCommentModel)
        .filter(ForumCommentModel.forum_id == forum_id, ForumCommentModel.parent_id == None)
        .all()
    )

    result = []
    for comment in main_comments:
        result.append(
            ForumComment(
                id=str(comment.id),
                comment=str(comment.comment),
                forum_id=str(comment.forum_id),
                parent_id=comment.parent_id,  # type: ignore
                user_id=comment.user_id,  # type: ignore
                username=comment.username,  # type: ignore
                liked_by_current_user=False,
                likes=comment.likes or 0,  # type: ignore
                timestamp=comment.timestamp,  # type: ignore
            )
        )

    return result


@router.get(
    "/forum/{forum_id}/comments/replies/{comment_id}",
    response_model=List[ForumComment],
    status_code=status.HTTP_200_OK,
)
def get_forum_comments_replied_to_by_forum_id(
    comment_id: str,
    forum_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    """
    Get replies to a specific comment in a forum - mimics post comments behavior
    """
    replies = (
        db.query(ForumCommentModel)
        .filter(ForumCommentModel.parent_id == comment_id)
        .filter(ForumCommentModel.forum_id == forum_id)
        .all()
    )

    result = []
    for reply in replies:
        result.append(
            ForumComment(
                id=str(reply.id),
                comment=str(reply.comment),
                forum_id=str(reply.forum_id),
                parent_id=reply.parent_id,  # type: ignore
                user_id=reply.user_id,  # type: ignore
                username=reply.username,  # type: ignore
                liked_by_current_user=False,
                likes=reply.likes or 0,  # type: ignore
                timestamp=reply.timestamp,  # type: ignore
            )
        )

    return result
