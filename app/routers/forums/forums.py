from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import ForumCreate, ForumResponse, ForumUpdate
from .models import Forums
from typing import List
from app.config.postgres_config import SessionLocal
from app.auth.dependencies import get_current_user, get_db
from app.routers.users.models import Users
import shortuuid
from datetime import datetime

router = APIRouter(prefix="/forums")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[ForumResponse], status_code=status.HTTP_200_OK)
def get_all_forums(db: Session = Depends(get_db)):
    """
    Get all forums - Public endpoint, no authentication required
    """
    forums = db.query(Forums).all()
    return forums


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
    
    print(type(forum))
    
    return forum


@router.post("", response_model=ForumResponse, status_code=status.HTTP_201_CREATED)
def create_forum(
    forum: ForumCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new forum - Requires authentication
    """
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
    
    return new_forum


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
    db.refresh(forum)
    
    return forum


@router.delete("/{forum_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_forum(
    forum_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a forum - Requires authentication and ownership
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
            detail="You can only delete your own forums"
        )
    
    db.delete(forum)
    db.commit()
    
    return None