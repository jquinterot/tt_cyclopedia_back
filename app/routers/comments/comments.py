from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import null
from sqlalchemy.orm import Session
from .schemas import Comment, CommentCreate, CommentUpdate
from .models import Comments, CommentLike
from typing import List
from app.config.postgres_config import SessionLocal
from app.auth.dependencies import get_current_user, get_db
from app.routers.users.models import Users
import shortuuid

router = APIRouter(prefix="/comments",
                   )


class Config:
    orm_mode = True


@router.get("", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_comments(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    comments = db.query(Comments).all()
    liked_ids = set(
        r.comment_id for r in db.query(CommentLike).filter_by(user_id=current_user.id).all()
    )
    result = []
    for c in comments:
        result.append(Comment(
            id=c.id,
            comment=c.comment,
            post_id=c.post_id,
            parent_id=c.parent_id,
            user_id=c.user_id,
            username=c.username,
            liked_by_current_user=c.id in liked_ids,
            likes=c.likes or 0,
            timestamp=c.timestamp
        ))
    return result


@router.get("/{item_id}", response_model=Comment, status_code=200)
def get_comment(item_id: str, db: Session = Depends(get_db)):
    item_to_get = db.query(Comments).filter(Comments.id == item_id).first()

    if item_to_get is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource Not Found")

    return Comment(
        id=item_to_get.id,
        comment=item_to_get.comment,
        post_id=item_to_get.post_id,
        parent_id=item_to_get.parent_id,
        user_id=item_to_get.user_id,
        username=item_to_get.username,
        liked_by_current_user=False,  # Will be set by frontend if needed
        likes=item_to_get.likes or 0,
        timestamp=item_to_get.timestamp
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
        id=new_comment.id,
        comment=new_comment.comment,
        post_id=new_comment.post_id,
        parent_id=new_comment.parent_id,
        user_id=new_comment.user_id,
        username=new_comment.username,
        liked_by_current_user=False,
        likes=new_comment.likes or 0,
        timestamp=new_comment.timestamp
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
    if item_to_update.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments")
    item_to_update.comment = updated_comment.comment
    db.commit()
    liked_by_current_user = db.query(CommentLike).filter_by(
        comment_id=item_to_update.id, user_id=current_user.id
    ).first() is not None
    return Comment(
        id=item_to_update.id,
        comment=item_to_update.comment,
        post_id=item_to_update.post_id,
        parent_id=item_to_update.parent_id,
        user_id=item_to_update.user_id,
        username=item_to_update.username,
        likes=item_to_update.likes or 0,
        liked_by_current_user=liked_by_current_user,
        timestamp=item_to_update.timestamp
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
    if comment_to_delete.user_id != current_user.id:
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
def get_comments_by_post_id(post_id: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    comments = db.query(Comments).filter(Comments.post_id == post_id).all()
    
    # Get liked comment IDs for current user
    liked_ids = set(
        r.comment_id for r in db.query(CommentLike).filter_by(user_id=current_user.id).all()
    )
    
    result = []
    for comment in comments:
        result.append(Comment(
            id=comment.id,
            comment=comment.comment,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            user_id=comment.user_id,
            username=comment.username,
            liked_by_current_user=comment.id in liked_ids,
            likes=comment.likes or 0,
            timestamp=comment.timestamp
        ))
    
    return result

@router.get("/post/{post_id}/replies/{comment_id}", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_comments_replied_to(comment_id: str, post_id:str,  db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    replies = db.query(Comments).filter(Comments.parent_id == comment_id).filter(Comments.post_id == post_id).all()
    
    # Get liked comment IDs for current user
    liked_ids = set(
        r.comment_id for r in db.query(CommentLike).filter_by(user_id=current_user.id).all()
    )
    
    result = []
    for reply in replies:
        result.append(Comment(
            id=reply.id,
            comment=reply.comment,
            post_id=reply.post_id,
            parent_id=reply.parent_id,
            user_id=reply.user_id,
            username=reply.username,
            liked_by_current_user=reply.id in liked_ids,
            likes=reply.likes or 0,
            timestamp=reply.timestamp
        ))
    
    return result

@router.get("/post/{post_id}/main", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_main_comments_by_post_id(post_id: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    # Query comments by post_id and where parent_id is None
    main_comments = (
        db.query(Comments)
        .filter(Comments.post_id == post_id, Comments.parent_id == None)
        .all()
    )

    if not main_comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No main comments found for this post")

    # Get liked comment IDs for current user
    liked_ids = set(
        r.comment_id for r in db.query(CommentLike).filter_by(user_id=current_user.id).all()
    )
    
    result = []
    for comment in main_comments:
        result.append(Comment(
            id=comment.id,
            comment=comment.comment,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            user_id=comment.user_id,
            username=comment.username,
            liked_by_current_user=comment.id in liked_ids,
            likes=comment.likes or 0,
            timestamp=comment.timestamp
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
        if comment.likes and comment.likes > 0:
            comment.likes -= 1
        db.commit()
    else:
        like = CommentLike(comment_id=comment_id, user_id=current_user.id)
        db.add(like)
        comment.likes = (comment.likes or 0) + 1
        db.commit()

    # Return the updated comment object
    liked_by_current_user = db.query(CommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first() is not None
    return Comment(
        id=comment.id,
        comment=comment.comment,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        user_id=comment.user_id,
        username=comment.username,
        liked_by_current_user=liked_by_current_user,
        likes=comment.likes or 0,
        timestamp=comment.timestamp
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
        if comment.likes and comment.likes > 0:
            comment.likes -= 1
        db.commit()
    # After unlike (or if not previously liked), return the updated comment object
    liked_by_current_user = db.query(CommentLike).filter_by(comment_id=comment_id, user_id=current_user.id).first() is not None
    return Comment(
        id=comment.id,
        comment=comment.comment,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        user_id=comment.user_id,
        username=comment.username,
        liked_by_current_user=liked_by_current_user,
        likes=comment.likes or 0,
        timestamp=comment.timestamp
    )

# Forum Comment Endpoints (using the same Comments table)
@router.get("/forum/{forum_id}", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_forum_comments(forum_id: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """
    Get all comments for a specific forum
    """
    comments = db.query(Comments).filter(Comments.forum_id == forum_id).all()
    
    # Get liked comment IDs for current user
    liked_ids = set(
        r.comment_id for r in db.query(CommentLike).filter_by(user_id=current_user.id).all()
    )
    
    result = []
    for comment in comments:
        result.append(Comment(
            id=comment.id,
            comment=comment.comment,
            forum_id=comment.forum_id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            user_id=comment.user_id,
            username=comment.username,
            liked_by_current_user=comment.id in liked_ids,
            likes=comment.likes or 0,
            timestamp=comment.timestamp
        ))
    
    return result


@router.get("/forum/{forum_id}/main", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_main_forum_comments(forum_id: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """
    Get main comments for a specific forum
    """
    main_comments = (
        db.query(Comments)
        .filter(Comments.forum_id == forum_id, Comments.parent_id == None)
        .all()
    )
    
    # Get liked comment IDs for current user
    liked_ids = set(
        r.comment_id for r in db.query(CommentLike).filter_by(user_id=current_user.id).all()
    )
    
    result = []
    for comment in main_comments:
        result.append(Comment(
            id=comment.id,
            comment=comment.comment,
            forum_id=comment.forum_id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            user_id=comment.user_id,
            username=comment.username,
            liked_by_current_user=comment.id in liked_ids,
            likes=comment.likes or 0,
            timestamp=comment.timestamp
        ))
    
    return result


@router.get("/forum/{forum_id}/replies/{comment_id}", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_forum_comments_replied_to(comment_id: str, forum_id: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """
    Get replies to a specific comment in a forum
    """
    replies = db.query(Comments).filter(Comments.parent_id == comment_id).filter(Comments.forum_id == forum_id).all()
    
    # Get liked comment IDs for current user
    liked_ids = set(
        r.comment_id for r in db.query(CommentLike).filter_by(user_id=current_user.id).all()
    )
    
    result = []
    for reply in replies:
        result.append(Comment(
            id=reply.id,
            comment=reply.comment,
            forum_id=reply.forum_id,
            post_id=reply.post_id,
            parent_id=reply.parent_id,
            user_id=reply.user_id,
            username=reply.username,
            liked_by_current_user=reply.id in liked_ids,
            likes=reply.likes or 0,
            timestamp=reply.timestamp
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
        id=new_comment.id,
        comment=new_comment.comment,
        forum_id=new_comment.forum_id,
        post_id=new_comment.post_id,
        parent_id=new_comment.parent_id,
        user_id=new_comment.user_id,
        username=new_comment.username,
        liked_by_current_user=False,
        likes=new_comment.likes or 0,
        timestamp=new_comment.timestamp
    )