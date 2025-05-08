# app/routers/posts/schemas.py
from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str
    image_url: str  # Changed from image_id
    likes: int = 0


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: str
