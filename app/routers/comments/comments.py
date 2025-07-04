from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import null
from sqlalchemy.orm import Session
from .schemas import Comment, CommentCreate, CommentUpdate
from .models import Comments, CommentLike
from typing import List
from app.auth.dependencies import get_current_user
from app.routers.users.models import Users
from app.config.postgres_config import get_db
import shortuuid

router = APIRouter(prefix="/comments",
                   )


class Config:
    orm_mode = True


@router.get("", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_comments(db: Session = Depends(get_db)):
    comments = db.query(Comments).all()
    result = []
    for c in comments:
        result.append(Comment(
            id=str(c.id),
            comment=str(c.comment),
            post_id=str(c.post_id),
            parent_id=c.parent_id,  # type: ignore
            user_id=c.user_id,  # type: ignore
            username=c.username,  # type: ignore
            liked_by_current_user=False,
            likes=c.likes or 0,  # type: ignore
            timestamp=c.timestamp  # type: ignore
        ))
    return result


@router.get("/{item_id}", response_model=Comment, status_code=200)
def get_comment(item_id: str, db: Session = Depends(get_db)):
    item_to_get = db.query(Comments).filter(Comments.id == item_id).first()

    if item_to_get is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource Not Found")

    return Comment(
        id=str(item_to_get.id),
        comment=str(item_to_get.comment),
        post_id=str(item_to_get.post_id),
        parent_id=item_to_get.parent_id,  # type: ignore
        user_id=item_to_get.user_id,  # type: ignore
        username=item_to_get.username,  # type: ignore
        liked_by_current_user=False,  # Will be set by frontend if needed
        likes=item_to_get.likes or 0,  # type: ignore
        timestamp=item_to_get.timestamp  # type: ignore
    )


@router.post("", response_model=Comment, status_code=status.HTTP_201_CREATED)
def post_comment(
    comment: CommentCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use the authenticated user's information
    new_comment = Comments(
        id=shortuuid.uuid(),
        comment=comment.comment,
        post_id=comment.post_id,
        user_id=current_user.id,  # Use authenticated user's ID
        username=current_user.username,  # Use authenticated user's username
        parent_id=comment.parent_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return Comment(
        id=str(new_comment.id),
        comment=str(new_comment.comment),
        post_id=str(new_comment.post_id),
        parent_id=new_comment.parent_id,  # type: ignore
        user_id=new_comment.user_id,  # type: ignore
        username=new_comment.username,  # type: ignore
        liked_by_current_user=False,
        likes=new_comment.likes or 0,  # type: ignore
        timestamp=new_comment.timestamp  # type: ignore
    )


@router.put("/{item_id}", response_model=Comment, status_code=status.HTTP_200_OK)
def update_comment(
    item_id: str, 
    updated_comment: CommentUpdate, 
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item_to_update = db.query(Comments).filter(Comments.id == item_id).first()
    if item_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource Not Found")
    if item_to_update.user_id != current_user.id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments")
    item_to_update.comment = updated_comment.comment  # type: ignore
    db.commit()
    liked_by_current_user = db.query(CommentLike).filter_by(
        comment_id=item_to_update.id, user_id=current_user.id
    ).first() is not None
    return Comment(
        id=str(item_to_update.id),
        comment=str(item_to_update.comment),
        post_id=str(item_to_update.post_id),
        parent_id=item_to_update.parent_id,  # type: ignore
        user_id=item_to_update.user_id,  # type: ignore
        username=item_to_update.username,  # type: ignore
        likes=item_to_update.likes or 0,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        timestamp=item_to_update.timestamp  # type: ignore
    )


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_comment_with_replies(
    item_id: str, 
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Query the comment to delete
    comment_to_delete = db.query(Comments).filter(Comments.id == item_id).first()

    if not comment_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Check if the user owns this comment
    if comment_to_delete.user_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You can only delete your own comments"
        )

    # Delete all child comments where parent_id matches the given item ID
    if comment_to_delete.parent_id is None:
        child_comments = db.query(Comments).filter(Comments.parent_id == item_id).all()
        for child in child_comments:
         db.delete(child)

    # Delete the main comment
    db.delete(comment_to_delete)
    db.commit()

    return {"detail": f"Comment with id {item_id} and its replies have been deleted"}


@router.get("/post/{post_id}", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_comments_by_post_id(post_id: str, db: Session = Depends(get_db)):
    comments = db.query(Comments).filter(Comments.post_id == post_id).all()
    result = []
    for comment in comments:
        result.append(Comment(
            id=str(comment.id),
            comment=str(comment.comment),
            post_id=str(comment.post_id),
            parent_id=comment.parent_id,  # type: ignore
            user_id=comment.user_id,  # type: ignore
            username=comment.username,  # type: ignore
            liked_by_current_user=False,
            likes=comment.likes or 0,  # type: ignore
            timestamp=comment.timestamp  # type: ignore
        ))
    return result

@router.get("/post/{post_id}/replies/{comment_id}", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_comments_replied_to(comment_id: str, post_id:str,  db: Session = Depends(get_db)):
    replies = db.query(Comments).filter(Comments.parent_id == comment_id).filter(Comments.post_id == post_id).all()
    result = []
    for reply in replies:
        result.append(Comment(
            id=str(reply.id),
            comment=str(reply.comment),
            post_id=str(reply.post_id),
            parent_id=reply.parent_id,  # type: ignore
            user_id=reply.user_id,  # type: ignore
            username=reply.username,  # type: ignore
            liked_by_current_user=False,
            likes=reply.likes or 0,  # type: ignore
            timestamp=reply.timestamp  # type: ignore
        ))
    return result

@router.get("/post/{post_id}/main", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_main_comments_by_post_id(post_id: str, db: Session = Depends(get_db)):
    main_comments = (
        db.query(Comments)
        .filter(Comments.post_id == post_id, Comments.parent_id == None)
        .all()
    )
    if not main_comments:
        return []
    result = []
    for comment in main_comments:
        result.append(Comment(
            id=str(comment.id),
            comment=str(comment.comment),
            post_id=str(comment.post_id),
            parent_id=comment.parent_id,  # type: ignore
            user_id=comment.user_id,  # type: ignore
            username=comment.username,  # type: ignore
            liked_by_current_user=False,
            likes=comment.likes or 0,  # type: ignore
            timestamp=comment.timestamp  # type: ignore
        ))
    return result

@router.post("/{comment_id}/like", response_model=Comment, status_code=200)
def toggle_like_comment(
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(CommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first()
    comment = db.query(Comments).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if existing:
        db.delete(existing)
        if comment.likes and comment.likes > 0:  # type: ignore
            comment.likes -= 1  # type: ignore
        db.commit()
    else:
        like = CommentLike(
            id=shortuuid.uuid(),
            comment_id=comment_id, 
            user_id=current_user.id
        )
        db.add(like)
        comment.likes = (comment.likes or 0) + 1  # type: ignore
        db.commit()

    # Return the updated comment object
    liked_by_current_user = db.query(CommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first() is not None
    return Comment(
        id=str(comment.id),
        comment=str(comment.comment),
        post_id=str(comment.post_id),
        parent_id=comment.parent_id,  # type: ignore
        user_id=comment.user_id,  # type: ignore
        username=comment.username,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        likes=comment.likes or 0,  # type: ignore
        timestamp=comment.timestamp  # type: ignore
    )

@router.delete("/{comment_id}/like", response_model=Comment, status_code=200)
def delete_like_comment(
    comment_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(CommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first()
    comment = db.query(Comments).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if existing:
        db.delete(existing)
        if comment.likes and comment.likes > 0:  # type: ignore
            comment.likes -= 1  # type: ignore
        db.commit()
    # After unlike (or if not previously liked), return the updated comment object
    liked_by_current_user = db.query(CommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first() is not None
    return Comment(
        id=str(comment.id),
        comment=str(comment.comment),
        post_id=str(comment.post_id),
        parent_id=comment.parent_id,  # type: ignore
        user_id=comment.user_id,  # type: ignore
        username=comment.username,  # type: ignore
        liked_by_current_user=liked_by_current_user,
        likes=comment.likes or 0,  # type: ignore
        timestamp=comment.timestamp  # type: ignore
    )

# Forum Comment Endpoints (using the same Comments table)
@router.get("/forum/{forum_id}", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_forum_comments(forum_id: str, db: Session = Depends(get_db)):
    comments = db.query(Comments).filter(Comments.forum_id == forum_id).all()
    result = []
    for comment in comments:
        result.append(Comment(
            id=str(comment.id),
            comment=str(comment.comment),
            forum_id=str(comment.forum_id),
            post_id=str(comment.post_id),
            parent_id=comment.parent_id,  # type: ignore
            user_id=comment.user_id,  # type: ignore
            username=comment.username,  # type: ignore
            liked_by_current_user=False,
            likes=comment.likes or 0,  # type: ignore
            timestamp=comment.timestamp  # type: ignore
        ))
    return result


@router.get("/forum/{forum_id}/main", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_main_forum_comments(forum_id: str, db: Session = Depends(get_db)):
    main_comments = (
        db.query(Comments)
        .filter(Comments.forum_id == forum_id, Comments.parent_id == None)
        .all()
    )
    result = []
    for comment in main_comments:
        result.append(Comment(
            id=str(comment.id),
            comment=str(comment.comment),
            forum_id=str(comment.forum_id),
            post_id=str(comment.post_id),
            parent_id=comment.parent_id,  # type: ignore
            user_id=comment.user_id,  # type: ignore
            username=comment.username,  # type: ignore
            liked_by_current_user=False,
            likes=comment.likes or 0,  # type: ignore
            timestamp=comment.timestamp  # type: ignore
        ))
    return result


@router.get("/forum/{forum_id}/replies/{comment_id}", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_forum_comments_replied_to(comment_id: str, forum_id: str, db: Session = Depends(get_db)):
    replies = db.query(Comments).filter(Comments.parent_id == comment_id).filter(Comments.forum_id == forum_id).all()
    result = []
    for reply in replies:
        result.append(Comment(
            id=str(reply.id),
            comment=str(reply.comment),
            forum_id=str(reply.forum_id),
            post_id=str(reply.post_id),
            parent_id=reply.parent_id,  # type: ignore
            user_id=reply.user_id,  # type: ignore
            username=reply.username,  # type: ignore
            liked_by_current_user=False,
            likes=reply.likes or 0,  # type: ignore
            timestamp=reply.timestamp  # type: ignore
        ))
    return result


@router.post("/forum/{forum_id}", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_forum_comment(
    forum_id: str,
    comment: CommentCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new comment on a forum
    """
    new_comment = Comments(
        id=shortuuid.uuid(),
        comment=comment.comment,
        forum_id=forum_id,
        post_id=comment.post_id,  # Will be None for forum comments
        user_id=current_user.id,
        username=current_user.username,
        parent_id=comment.parent_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return Comment(
        id=str(new_comment.id),
        comment=str(new_comment.comment),
        forum_id=str(new_comment.forum_id),
        post_id=str(new_comment.post_id),
        parent_id=new_comment.parent_id,  # type: ignore
        user_id=new_comment.user_id,  # type: ignore
        username=new_comment.username,  # type: ignore
        liked_by_current_user=False,
        likes=new_comment.likes or 0,  # type: ignore
        timestamp=new_comment.timestamp  # type: ignore
    )