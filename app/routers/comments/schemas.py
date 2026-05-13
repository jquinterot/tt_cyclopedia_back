from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    comment: str = Field(..., min_length=1, max_length=5000, description="Comment text content")
    post_id: str | None = Field(None, description="Associated post ID")
    forum_id: str | None = Field(None, description="Associated forum ID")
    parent_id: str | None = Field(None, description="Parent comment ID for nested replies")


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    comment: str = Field(..., min_length=1, max_length=5000, description="Updated comment text")


class Comment(CommentBase):
    id: str | None = Field(None, description="Unique comment ID")
    user_id: str | None = Field(None, description="Author user ID")
    username: str | None = Field(None, description="Author username")
    liked_by_current_user: bool | None = Field(
        False, description="Whether current user liked this comment"
    )
    likes: int | None = Field(0, ge=0, description="Number of likes")
    timestamp: datetime | None = Field(None, description="Creation timestamp")

    @classmethod
    def from_orm(cls, obj, liked_by_current_user: bool = False):
        return cls(
            id=str(obj.id),
            comment=str(obj.comment),
            post_id=str(obj.post_id) if obj.post_id else None,
            forum_id=str(obj.forum_id) if obj.forum_id else None,
            parent_id=obj.parent_id,
            user_id=obj.user_id,
            username=obj.username,
            liked_by_current_user=liked_by_current_user,
            likes=obj.likes or 0,
            timestamp=obj.timestamp,
        )
