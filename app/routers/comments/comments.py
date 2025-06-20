from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import null
from sqlalchemy.orm import Session
from .schemas import Comment, CommentCreate
from .models import Comments
from typing import List
from app.config.postgres_config import SessionLocal
import shortuuid

router = APIRouter(prefix="/comments",
                   )


class Config:
    orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_comments(db: Session = Depends(get_db)):
    comments = db.query(Comments).all()
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resourse Not Found")

    return comments


@router.get("/{item_id}", response_model=Comment, status_code=200)
def get_comment(item_id: str, db: Session = Depends(get_db)):
    item_to_get = db.query(Comments).filter(Comments.id == item_id).first()

    if item_to_get is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource Not Found")

    return item_to_get


@router.post("", response_model=Comment, status_code=status.HTTP_201_CREATED)
def post_comment(comment: CommentCreate
, db: Session = Depends(get_db)):
    new_comment = Comments(
        id=shortuuid.uuid(),
        comment=comment.comment,
        post_id=comment.post_id,
        user_id=comment.user_id,
        username=comment.username,
        parent_id=comment.parent_id

    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.put("/{item_id}", response_model=Comment, status_code=status.HTTP_201_CREATED)
def update_comment(item_id: str, updated_comment: Comment, db: Session = Depends(get_db)):
    item_to_update = db.query(Comments).filter(Comments.id == item_id).first()

    if item_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resourse Not Found")

    item_to_update.comment = updated_comment.comment
    db.commit()
    return item_to_update


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_comment_with_replies(item_id: str, db: Session = Depends(get_db)):
    # Query the comment to delete
    comment_to_delete = db.query(Comments).filter(Comments.id == item_id).first()

    if not comment_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

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

    return comments

@router.get("/post/{post_id}/replies/{comment_id}", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_comments_replied_to(comment_id: str, post_id:str,  db: Session = Depends(get_db)):
    replies = db.query(Comments).filter(Comments.parent_id == comment_id).filter(Comments.post_id == post_id).all()
    if not replies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No replies found for this comment")

    return replies

@router.get("/post/{post_id}/main", response_model=List[Comment], status_code=status.HTTP_200_OK)
def get_main_comments_by_post_id(post_id: str, db: Session = Depends(get_db)):
    # Query comments by post_id and where parent_id is None
    main_comments = (
        db.query(Comments)
        .filter(Comments.post_id == post_id, Comments.parent_id == None)
        .all()
    )

    if not main_comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No main comments found for this post")

    return main_comments


