from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    comment: str = Field(..., min_length=1, max_length=5000)
    post_id: Optional[str] = None
    forum_id: Optional[str] = None
    parent_id: Optional[str] = None


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    comment: str = Field(..., min_length=1, max_length=5000)


class Comment(CommentBase):
    id: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    liked_by_current_user: Optional[bool] = False
    likes: Optional[int] = 0
    timestamp: Optional[datetime] = None

