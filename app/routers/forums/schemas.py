from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ForumBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=50000)


class ForumCreate(ForumBase):
    pass


class ForumUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class ForumResponse(ForumBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    author: str
    likes: int
    timestamp: datetime
    updated_timestamp: datetime
    liked_by_current_user: Optional[bool] = False


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

