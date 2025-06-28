from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ForumBase(BaseModel):
    title: str
    content: str


class ForumCreate(ForumBase):
    pass


class ForumUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class ForumResponse(ForumBase):
    id: str
    author: str
    likes: int
    timestamp: datetime
    updated_timestamp: datetime
    liked_by_current_user: Optional[bool] = False

    class Config:
        orm_mode = True


# Forum Comment Schemas
class ForumCommentBase(BaseModel):
    comment: str
    forum_id: str
    parent_id: Optional[str] = None


class ForumCommentCreate(ForumCommentBase):
    pass


class ForumCommentUpdate(BaseModel):
    comment: str


class ForumComment(ForumCommentBase):
    id: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    liked_by_current_user: Optional[bool] = False
    likes: Optional[int] = 0
    timestamp: Optional[datetime] = None

