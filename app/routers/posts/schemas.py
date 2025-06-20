# app/routers/posts/schemas.py
from datetime import datetime

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str
    image_url: str  # Changed from image_id
    likes: int = 0
    author: str
    timestamp: datetime


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: str
