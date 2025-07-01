# app/routers/posts/schemas.py
from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, field_validator


class PostBase(BaseModel):
    title: str
    content: str
    image_url: str
    likes: int = 0
    author: str
    timestamp: datetime
    stats: Optional[Dict[str, float]] = None

    @field_validator('stats')
    @classmethod
    def validate_stats(cls, v):
        if v is not None:
            for key, value in v.items():
                if not (5 <= value <= 10):
                    raise ValueError(f"Stat '{key}' must be between 5 and 10 (got {value})")
        return v

    class Config:
        orm_mode = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: str
    likedByCurrentUser: bool
