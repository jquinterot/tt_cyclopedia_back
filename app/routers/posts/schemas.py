# app/routers/posts/schemas.py
from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, field_validator, ConfigDict, Field


class EquipmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    brand: str
    category: str


class PostBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=50000)
    image_url: str
    likes: int = 0
    author: str
    timestamp: datetime
    stats: Optional[Dict[str, float]] = None
    equipment_id: Optional[str] = None

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
    id: str
    likedByCurrentUser: bool
    equipment: Optional[EquipmentSummary] = None
