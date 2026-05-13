from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ForumBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    title: str = Field(..., min_length=1, max_length=200, description="Forum title")
    content: str = Field(..., min_length=1, max_length=50000, description="Forum content/body")


class ForumCreate(ForumBase):
    pass


class ForumUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(None, min_length=1, max_length=200, description="Updated forum title")
    content: str | None = Field(
        None, min_length=1, max_length=50000, description="Updated forum content"
    )


class ForumResponse(ForumBase):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: str = Field(..., description="Unique forum ID")
    author: str = Field(..., description="Forum author username")
    likes: int = Field(..., ge=0, description="Number of likes")
    timestamp: datetime = Field(..., description="Creation timestamp")
    updated_timestamp: datetime = Field(..., description="Last update timestamp")
    liked_by_current_user: bool | None = Field(
        False, description="Whether current user liked this forum"
    )

    @classmethod
    def from_orm(cls, obj, liked_by_current_user: bool = False):
        return cls(
            id=str(obj.id),
            title=str(obj.title),
            content=str(obj.content),
            author=str(obj.author),
            likes=obj.likes or 0,
            timestamp=obj.timestamp,
            updated_timestamp=obj.updated_timestamp,
            liked_by_current_user=liked_by_current_user,
        )


# Forum Comment Schemas
class ForumCommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    comment: str = Field(..., min_length=1, max_length=5000, description="Comment text")


class ForumCommentCreate(ForumCommentBase):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    forum_id: str = Field(..., min_length=1, max_length=50, description="Associated forum ID")
    parent_id: str | None = Field(None, description="Parent comment ID for replies")


class ForumCommentCreateNested(ForumCommentBase):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    parent_id: str | None = Field(None, description="Parent comment ID for replies")


class ForumCommentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    comment: str = Field(..., min_length=1, max_length=5000, description="Updated comment text")


class ForumComment(ForumCommentBase):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: str | None = Field(None, description="Unique comment ID")
    forum_id: str | None = Field(None, description="Associated forum ID")
    user_id: str | None = Field(None, description="Author user ID")
    username: str | None = Field(None, description="Author username")
    liked_by_current_user: bool | None = Field(
        False, description="Whether current user liked this comment"
    )
    likes: int | None = Field(0, ge=0, description="Number of likes")
    timestamp: datetime | None = Field(None, description="Creation timestamp")
    parent_id: str | None = Field(None, description="Parent comment ID for replies")

    @classmethod
    def from_orm(cls, obj, liked_by_current_user: bool = False):
        return cls(
            id=str(obj.id),
            comment=str(obj.comment),
            forum_id=str(obj.forum_id) if obj.forum_id else None,
            user_id=obj.user_id,
            username=obj.username,
            liked_by_current_user=liked_by_current_user,
            likes=obj.likes or 0,
            timestamp=obj.timestamp,
            parent_id=obj.parent_id,
        )
