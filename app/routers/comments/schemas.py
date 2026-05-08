from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    comment: str = Field(..., min_length=1, max_length=5000, description="Comment text content")
    post_id: Optional[str] = Field(None, description="Associated post ID")
    forum_id: Optional[str] = Field(None, description="Associated forum ID")
    parent_id: Optional[str] = Field(None, description="Parent comment ID for nested replies")


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    comment: str = Field(..., min_length=1, max_length=5000, description="Updated comment text")


class Comment(CommentBase):
    id: Optional[str] = Field(None, description="Unique comment ID")
    user_id: Optional[str] = Field(None, description="Author user ID")
    username: Optional[str] = Field(None, description="Author username")
    liked_by_current_user: Optional[bool] = Field(False, description="Whether current user liked this comment")
    likes: Optional[int] = Field(0, ge=0, description="Number of likes")
    timestamp: Optional[datetime] = Field(None, description="Creation timestamp")
