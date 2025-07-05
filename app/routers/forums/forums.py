from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import ForumCreate, ForumResponse, ForumUpdate, ForumComment, ForumCommentCreate, ForumCommentUpdate
from .models import Forums, ForumLike, ForumComment as ForumCommentModel, ForumCommentLike
from typing import List
from app.auth.dependencies import get_current_user
from app.routers.users.models import Users
from app.config.postgres_config import get_db
import shortuuid
from datetime import datetime

router = APIRouter(prefix="/forums")


@router.get("", response_model=List[ForumResponse], status_code=status.HTTP_200_OK)
def get_all_forums(db: Session = Depends(get_db)):
    """
    Get all forums - Public endpoint, no authentication required
    """
    forums = db.query(Forums).all()
    result = []
    for f in forums:
        result.append(ForumResponse(
            id=str(f.id),
            title=str(f.title),
            content=str(f.content),
            author=str(f.author),
            likes=f.likes or 0,  # type: ignore
            timestamp=f.timestamp,  # type: ignore
            updated_timestamp=f.updated_timestamp,  # type: ignore
            liked_by_current_user=False
        ))
    return result


@router.get("/{forum_id}", response_model=ForumResponse, status_code=status.HTTP_200_OK)
def get_forum_by_id(forum_id: str, db: Session = Depends(get_db)):
    """
    Get a specific forum by ID - Public endpoint, no authentication required
    """
    forum = db.query(Forums).filter(Forums.id == forum_id).first()
    
    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Forum not found"
        )
    
    return ForumResponse(
        id=str(forum.id),
        title=str(forum.title),
        content=str(forum.content),
        author=str(forum.author),
        likes=forum.likes or 0,  # type: ignore
        timestamp=forum.timestamp,  # type: ignore
        updated_timestamp=forum.updated_timestamp,  # type: ignore
        liked_by_current_user=False
    )


@router.post("", response_model=ForumResponse, status_code=status.HTTP_201_CREATED)
def create_forum(
    forum: ForumCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_forum = Forums(
        id=shortuuid.uuid(),
        title=forum.title,
        content=forum.content,
        author=current_user.username,
        likes=0,
        timestamp=datetime.utcnow(),
        updated_timestamp=datetime.utcnow()
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
        liked_by_current_user=False
    )


@router.put("/{forum_id}", response_model=ForumResponse, status_code=status.HTTP_200_OK)
def update_forum(
    forum_id: str,
    forum_update: ForumUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a forum - Requires authentication and ownership
    """
    forum = db.query(Forums).filter(Forums.id == forum_id).first()
    
    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Forum not found"
        )
    
    # Check if the user owns this forum
    if getattr(forum, 'author', None) != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You can only edit your own forums"
        )
    
    # Use setattr to avoid linter errors
    if forum_update.title is not None:
        setattr(forum, 'title', forum_update.title)
    if forum_update.content is not None:
        setattr(forum, 'content', forum_update.content)
    
    setattr(forum, 'updated_timestamp', datetime.utcnow())
    
    db.commit()
    
    liked_by_current_user = db.query(ForumLike).filter_by(forum_id=forum_id, user_id=current_user.id).first() is not None
    
    return ForumResponse(
        id=str(forum.id),
        title=str(forum.title),
        content=str(forum.content),
        author=str(forum.author),
        likes=forum.likes or 0,  # type: ignore
        timestamp=forum.timestamp,  # type: ignore
        updated_timestamp=forum.updated_timestamp,  # type: ignore
        liked_by_current_user=liked_by_current_user
    )


@router.delete("/{forum_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_forum(forum_id: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    forum = db.query(Forums).filter(Forums.id == forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Forum not found")
    if str(forum.author) != str(current_user.username):
        raise HTTPException(status_code=403, detail="Not authorized to delete this forum")
    db.delete(forum)
    db.commit()
    return


# Forum Like Endpoints
@router.post("/{forum_id}/like", response_model=ForumResponse, status_code=200)
def toggle_like_forum(
    forum_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(ForumLike).filter_by(forum_id=forum_id, user_id=current_user.id).first()
    forum = db.query(Forums).filter_by(id=forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Forum not found")

    if existing:
        db.delete(existing)
        current_likes = forum.likes or 0
        if current_likes > 0:  # type: ignore
            setattr(forum, 'likes', current_likes - 1)
        db.commit()
    else:
        like = ForumLike(forum_id=forum_id, user_id=current_user.id)
        db.add(like)
        current_likes = forum.likes or 0
        setattr(forum, 'likes', current_likes + 1)
        db.commit()

    # Return the updated forum object
    liked_by_current_user = db.query(ForumLike).filter_by(forum_id=forum_id, user_id=current_user.id).first() is not None
    return ForumResponse(
        id=str(forum.id),
        title=str(forum.title),
        content=str(forum.content),
        author=str(forum.author),
        likes=forum.likes or 0,  # type: ignore
        timestamp=forum.timestamp,  # type: ignore
        updated_timestamp=forum.updated_timestamp,  # type: ignore
        liked_by_current_user=liked_by_current_user
    )


@router.delete("/{forum_id}/like", response_model=ForumResponse, status_code=200)
def delete_like_forum(
    forum_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(ForumLike).filter_by(forum_id=forum_id, user_id=current_user.id).first()
    forum = db.query(Forums).filter_by(id=forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Forum not found")

    if existing:
        db.delete(existing)
        if (forum.likes or 0) > 0:  # type: ignore
            setattr(forum, 'likes', (forum.likes or 0) - 1)
        db.commit()
    
    # After unlike (or if not previously liked), return the updated forum object
    liked_by_current_user = db.query(ForumLike).filter_by(forum_id=forum_id, user_id=current_user.id).first() is not None
    return ForumResponse(
        id=str(forum.id),
        title=str(forum.title),
        content=str(forum.content),
        author=str(forum.author),
        likes=forum.likes or 0,  # type: ignore
        timestamp=forum.timestamp,  # type: ignore
        updated_timestamp=forum.updated_timestamp,  # type: ignore
        liked_by_current_user=liked_by_current_user
    )


# Forum Comments Endpoints
@router.get("/{forum_id}/comments", response_model=List[ForumComment], status_code=status.HTTP_200_OK)
def get_forum_comments(forum_id: str, db: Session = Depends(get_db)):
    comments = db.query(ForumCommentModel).filter(ForumCommentModel.forum_id == forum_id).all()
    result = []
    for c in comments:
        result.append(ForumComment(
            id=str(c.id),
            comment=str(c.comment),
            forum_id=str(c.forum_id),
            parent_id=c.parent_id,  # type: ignore
            user_id=c.user_id,  # type: ignore
            username=c.username,  # type: ignore
            liked_by_current_user=False,
            likes=c.likes or 0,  # type: ignore
            timestamp=c.timestamp  # type: ignore
        ))
    return result


@router.get("/{forum_id}/comments/main", response_model=List[ForumComment], status_code=status.HTTP_200_OK)
def get_main_forum_comments(forum_id: str, db: Session = Depends(get_db)):
    main_comments = (
        db.query(ForumCommentModel)
        .filter(ForumCommentModel.forum_id == forum_id, ForumCommentModel.parent_id == None)
        .all()
    )
    
    result = []
    for comment in main_comments:
        result.append(ForumComment(
            id=str(comment.id),
            comment=str(comment.comment),
            forum_id=str(comment.forum_id),
            parent_id=comment.parent_id,  # type: ignore
            user_id=comment.user_id,  # type: ignore
            username=comment.username,  # type: ignore
            liked_by_current_user=False,
            likes=comment.likes or 0,  # type: ignore
            timestamp=comment.timestamp  # type: ignore
        ))
    
    return result


@router.get("/{forum_id}/comments/replies/{comment_id}", response_model=List[ForumComment], status_code=status.HTTP_200_OK)
def get_forum_comments_replied_to(comment_id: str, forum_id: str, db: Session = Depends(get_db)):
    replies = db.query(ForumCommentModel).filter(ForumCommentModel.parent_id == comment_id).filter(ForumCommentModel.forum_id == forum_id).all()
    
    result = []
    for reply in replies:
        result.append(ForumComment(
            id=str(reply.id),
            comment=str(reply.comment),
            forum_id=str(reply.forum_id),
            parent_id=reply.parent_id,  # type: ignore
            user_id=reply.user_id,  # type: ignore
            username=reply.username,  # type: ignore
            liked_by_current_user=False,
            likes=reply.likes or 0,  # type: ignore
            timestamp=reply.timestamp  # type: ignore
        ))
    
    return result


@router.post("/{forum_id}/comments", response_model=ForumComment, status_code=status.HTTP_201_CREATED)
def post_forum_comment(
    forum_id: str,
    comment: ForumCommentCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_comment = ForumCommentModel(
        id=shortuuid.uuid(),
        comment=comment.comment,
        forum_id=forum_id,
        user_id=current_user.id,
        username=current_user.username,
        parent_id=comment.parent_id
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
        timestamp=new_comment.timestamp  # type: ignore
    )


@router.put("/{forum_id}/comments/{comment_id}", response_model=ForumComment, status_code=status.HTTP_200_OK)
def update_forum_comment(
    forum_id: str,
    comment_id: str,
    updated_comment: ForumCommentUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item_to_update = db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    if item_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource Not Found")
    if item_to_update.user_id != current_user.id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments")
    
    item_to_update.comment = updated_comment.comment  # type: ignore
    db.commit()
    
    liked_by_current_user = db.query(ForumCommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first() is not None
    return ForumComment(
        id=str(item_to_update.id),
        comment=str(item_to_update.comment),
        forum_id=str(item_to_update.forum_id),
        parent_id=item_to_update.parent_id,  # type: ignore
        user_id=item_to_update.user_id,  # type: ignore
        username=item_to_update.username,  # type: ignore
        likes=item_to_update.likes or 0,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        timestamp=item_to_update.timestamp  # type: ignore
    )


@router.delete("/{forum_id}/comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_forum_comment_with_replies(
    forum_id: str,
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment_to_delete = db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    if not comment_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment_to_delete.user_id != current_user.id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own comments")
    
    if comment_to_delete.parent_id is None:
        child_comments = db.query(ForumCommentModel).filter(ForumCommentModel.parent_id == comment_id).all()
        for child in child_comments:
            db.delete(child)
    
    db.delete(comment_to_delete)
    db.commit()
    return {"detail": f"Comment with id {comment_id} and its replies have been deleted"}


@router.post("/{forum_id}/comments/{comment_id}/like", response_model=ForumComment, status_code=200)
def toggle_like_forum_comment(
    forum_id: str,
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(ForumCommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first()
    comment = db.query(ForumCommentModel).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if existing:
        db.delete(existing)
        if comment.likes and comment.likes > 0:  # type: ignore
            comment.likes -= 1  # type: ignore
        db.commit()
    else:
        like = ForumCommentLike(comment_id=comment_id, user_id=current_user.id)
        db.add(like)
        comment.likes = (comment.likes or 0) + 1  # type: ignore
        db.commit()

    liked_by_current_user = db.query(ForumCommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first() is not None
    return ForumComment(
        id=str(comment.id),
        comment=str(comment.comment),
        forum_id=str(comment.forum_id),
        parent_id=comment.parent_id,  # type: ignore
        user_id=comment.user_id,  # type: ignore
        username=comment.username,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        likes=comment.likes or 0,  # type: ignore
        timestamp=comment.timestamp  # type: ignore
    )


@router.delete("/{forum_id}/comments/{comment_id}/like", response_model=ForumComment, status_code=200)
def delete_like_forum_comment(
    forum_id: str,
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(ForumCommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first()
    comment = db.query(ForumCommentModel).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if existing:
        db.delete(existing)
        if comment.likes and comment.likes > 0:  # type: ignore
            comment.likes -= 1  # type: ignore
        db.commit()
    
    liked_by_current_user = db.query(ForumCommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first() is not None
    return ForumComment(
        id=str(comment.id),
        comment=str(comment.comment),
        forum_id=str(comment.forum_id),
        parent_id=comment.parent_id,  # type: ignore
        user_id=comment.user_id,  # type: ignore
        username=comment.username,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        likes=comment.likes or 0,  # type: ignore
        timestamp=comment.timestamp  # type: ignore
    )


# General forum comment endpoints (mimicking post comments behavior)
@router.get("/comments", response_model=List[ForumComment], status_code=status.HTTP_200_OK)
def get_all_forum_comments(db: Session = Depends(get_db)):
    """
    Get all forum comments - mimics post comments behavior
    """
    comments = db.query(ForumCommentModel).all()
    result = []
    for c in comments:
        result.append(ForumComment(
            id=str(c.id),
            comment=str(c.comment),
            forum_id=str(c.forum_id),
            parent_id=c.parent_id,  # type: ignore
            user_id=c.user_id,  # type: ignore
            username=c.username,  # type: ignore
            liked_by_current_user=False,
            likes=c.likes or 0,  # type: ignore
            timestamp=c.timestamp  # type: ignore
        ))
    return result


@router.get("/comments/{comment_id}", response_model=ForumComment, status_code=200)
def get_forum_comment(comment_id: str, db: Session = Depends(get_db)):
    """
    Get a specific forum comment by ID - mimics post comments behavior
    """
    comment = db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forum comment not found")
    
    return ForumComment(
        id=str(comment.id),
        comment=str(comment.comment),
        forum_id=str(comment.forum_id),
        parent_id=comment.parent_id,  # type: ignore
        user_id=comment.user_id,  # type: ignore
        username=comment.username,  # type: ignore
        liked_by_current_user=False,  # Will be set by frontend if needed
        likes=comment.likes or 0,  # type: ignore
        timestamp=comment.timestamp  # type: ignore
    )


@router.post("/comments", response_model=ForumComment, status_code=status.HTTP_201_CREATED)
def create_forum_comment(
    comment: ForumCommentCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
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
        parent_id=comment.parent_id
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
        timestamp=new_comment.timestamp  # type: ignore
    )


@router.put("/comments/{comment_id}", response_model=ForumComment, status_code=status.HTTP_200_OK)
def update_forum_comment_general(
    comment_id: str,
    updated_comment: ForumCommentUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a forum comment - mimics post comments behavior
    """
    item_to_update = db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    if item_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forum comment not found")
    if item_to_update.user_id != current_user.id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments")
    
    item_to_update.comment = updated_comment.comment  # type: ignore
    db.commit()
    
    liked_by_current_user = db.query(ForumCommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first() is not None
    return ForumComment(
        id=str(item_to_update.id),
        comment=str(item_to_update.comment),
        forum_id=str(item_to_update.forum_id),
        parent_id=item_to_update.parent_id,  # type: ignore
        user_id=item_to_update.user_id,  # type: ignore
        username=item_to_update.username,  # type: ignore
        likes=item_to_update.likes or 0,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        timestamp=item_to_update.timestamp  # type: ignore
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_forum_comment_general(
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a forum comment with replies - mimics post comments behavior
    """
    comment_to_delete = db.query(ForumCommentModel).filter(ForumCommentModel.id == comment_id).first()
    if not comment_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forum comment not found")
    if comment_to_delete.user_id != current_user.id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own comments")
    
    if comment_to_delete.parent_id is None:
        child_comments = db.query(ForumCommentModel).filter(ForumCommentModel.parent_id == comment_id).all()
        for child in child_comments:
            db.delete(child)
    
    db.delete(comment_to_delete)
    db.commit()
    return {"detail": f"Forum comment with id {comment_id} and its replies have been deleted"}


@router.post("/comments/{comment_id}/like", response_model=ForumComment, status_code=200)
def toggle_like_forum_comment_general(
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle like on a forum comment - mimics post comments behavior
    """
    existing = db.query(ForumCommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first()
    comment = db.query(ForumCommentModel).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Forum comment not found")

    if existing:
        db.delete(existing)
        if comment.likes and comment.likes > 0:  # type: ignore
            comment.likes -= 1  # type: ignore
        db.commit()
    else:
        like = ForumCommentLike(comment_id=comment_id, user_id=current_user.id)
        db.add(like)
        comment.likes = (comment.likes or 0) + 1  # type: ignore
        db.commit()

    liked_by_current_user = db.query(ForumCommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first() is not None
    return ForumComment(
        id=str(comment.id),
        comment=str(comment.comment),
        forum_id=str(comment.forum_id),
        parent_id=comment.parent_id,  # type: ignore
        user_id=comment.user_id,  # type: ignore
        username=comment.username,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        likes=comment.likes or 0,  # type: ignore
        timestamp=comment.timestamp  # type: ignore
    )


@router.delete("/comments/{comment_id}/like", response_model=ForumComment, status_code=200)
def delete_like_forum_comment_general(
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove like from a forum comment - mimics post comments behavior
    """
    existing = db.query(ForumCommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first()
    comment = db.query(ForumCommentModel).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Forum comment not found")

    if existing:
        db.delete(existing)
        if comment.likes and comment.likes > 0:  # type: ignore
            comment.likes -= 1  # type: ignore
        db.commit()
    
    liked_by_current_user = db.query(ForumCommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first() is not None
    return ForumComment(
        id=str(comment.id),
        comment=str(comment.comment),
        forum_id=str(comment.forum_id),
        parent_id=comment.parent_id,  # type: ignore
        user_id=comment.user_id,  # type: ignore
        username=comment.username,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        likes=comment.likes or 0,  # type: ignore
        timestamp=comment.timestamp  # type: ignore
    )


# Forum-specific comment endpoints (mimicking post comments behavior)
@router.get("/forum/{forum_id}/comments", response_model=List[ForumComment], status_code=status.HTTP_200_OK)
def get_forum_comments_by_forum_id(forum_id: str, db: Session = Depends(get_db)):
    """
    Get all comments for a specific forum - mimics post comments behavior
    """
    comments = db.query(ForumCommentModel).filter(ForumCommentModel.forum_id == forum_id).all()
    
    result = []
    for comment in comments:
        result.append(ForumComment(
            id=str(comment.id),
            comment=str(comment.comment),
            forum_id=str(comment.forum_id),
            parent_id=comment.parent_id,  # type: ignore
            user_id=comment.user_id,  # type: ignore
            username=comment.username,  # type: ignore
            liked_by_current_user=False,
            likes=comment.likes or 0,  # type: ignore
            timestamp=comment.timestamp  # type: ignore
        ))
    
    return result


@router.get("/forum/{forum_id}/comments/main", response_model=List[ForumComment], status_code=status.HTTP_200_OK)
def get_main_forum_comments_by_forum_id(forum_id: str, db: Session = Depends(get_db)):
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
        result.append(ForumComment(
            id=str(comment.id),
            comment=str(comment.comment),
            forum_id=str(comment.forum_id),
            parent_id=comment.parent_id,  # type: ignore
            user_id=comment.user_id,  # type: ignore
            username=comment.username,  # type: ignore
            liked_by_current_user=False,
            likes=comment.likes or 0,  # type: ignore
            timestamp=comment.timestamp  # type: ignore
        ))
    
    return result


@router.get("/forum/{forum_id}/comments/replies/{comment_id}", response_model=List[ForumComment], status_code=status.HTTP_200_OK)
def get_forum_comments_replied_to_by_forum_id(comment_id: str, forum_id: str, db: Session = Depends(get_db)):
    """
    Get replies to a specific comment in a forum - mimics post comments behavior
    """
    replies = db.query(ForumCommentModel).filter(ForumCommentModel.parent_id == comment_id).filter(ForumCommentModel.forum_id == forum_id).all()
    
    result = []
    for reply in replies:
        result.append(ForumComment(
            id=str(reply.id),
            comment=str(reply.comment),
            forum_id=str(reply.forum_id),
            parent_id=reply.parent_id,  # type: ignore
            user_id=reply.user_id,  # type: ignore
            username=reply.username,  # type: ignore
            liked_by_current_user=False,
            likes=reply.likes or 0,  # type: ignore
            timestamp=reply.timestamp  # type: ignore
        ))
    
    return result