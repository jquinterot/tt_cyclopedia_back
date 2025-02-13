from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from .schemas import Comment
from .models import Comments
from typing import Optional, List
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
    return comments


@router.get("/{item_id}", response_model=Comment, status_code=200)
def get_comment(item_id: str, db: Session = Depends(get_db)):
    item_to_get = db.query(Comments).filter(Comments.id == item_id).first()

    if item_to_get is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resourse Not Found")

    return item_to_get


@router.post("", response_model=Comment, status_code=status.HTTP_201_CREATED)
def post_comment(comment: Comment, db: Session = Depends(get_db)):
    new_comment = Comments(
        id=shortuuid.uuid(),
        comment=comment.comment
    )
    db.add(new_comment)
    db.commit()
    return new_comment


@router.put("/{item_id}", response_model=Comment, status_code=status.HTTP_201_CREATED)
def update_comment(item_id: str, updated_comment: Comment, db: Session = Depends(get_db)):
    item_to_update = db.query(Comments).filter(Comments.id == item_id).first()

    if item_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resourse Not Found")

    item_to_update.comment = updated_comment.comment
    db.commit()
    return item_to_update


@router.delete("/{item_id}", status_code=200)
def delete_comment(item_id: str, db: Session = Depends(get_db)):
    item_to_delete = db.query(Comments).filter(Comments.id == item_id).first()

    if item_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resourse Not Found")

    db.delete(item_to_delete)
    db.commit()
    return item_to_delete
