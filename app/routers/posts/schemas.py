from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, field_validator, ConfigDict, Field


class EquipmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    id: str = Field(..., description="Equipment ID")
    name: str = Field(..., description="Equipment name")
    brand: str = Field(..., description="Equipment brand")
    category: str = Field(..., description="Equipment category")


class PostBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    content: str = Field(..., min_length=1, max_length=50000, description="Post content")
    image_url: str = Field(..., description="URL to post image")
    likes: int = Field(0, ge=0, description="Number of likes")
    author: str = Field(..., description="Author username")
    timestamp: datetime = Field(..., description="Creation timestamp")
    stats: Optional[Dict[str, float]] = Field(None, description="Optional stats dictionary")
    equipment_id: Optional[str] = Field(None, description="Linked equipment ID")

    @field_validator('stats')
    @classmethod
    def validate_stats(cls, v):
        if v is not None:
            for key, value in v.items():
                if not (5 <= value <= 10):
                    raise ValueError(f"Stat '{key}' must be between 5 and 10 (got {value})")
        return v


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: str = Field(..., description="Post ID")
    likedByCurrentUser: bool = Field(..., description="Whether current user liked this post")
    equipment: Optional[EquipmentSummary] = Field(None, description="Linked equipment summary")

    @classmethod
    def from_orm(cls, obj, liked_by_current_user: bool = False, equipment: Optional[EquipmentSummary] = None, likes_count: int = 0):
        return cls(
            id=str(obj.id),
            title=str(obj.title),
            content=str(obj.content),
            image_url=str(obj.image_url),
            likes=likes_count,
            author=str(obj.author),
            timestamp=obj.timestamp,
            stats=obj.stats,
            likedByCurrentUser=liked_by_current_user,
            equipment_id=obj.equipment_id,
            equipment=equipment,
        )


class PostLikeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    user_id: str = Field(..., description="User ID who liked")
    created_at: datetime = Field(..., description="Like timestamp")
