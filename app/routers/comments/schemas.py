from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CommentBase(BaseModel):
    comment: str
    post_id: Optional[str] = None  # Optional for forum comments
    forum_id: Optional[str] = None  # Optional for post comments
    parent_id: Optional[str] = None


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    comment: str


class Comment(CommentBase):
    id: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    liked_by_current_user: Optional[bool] = False
    likes: Optional[int] = 0
    timestamp: Optional[datetime] = None

