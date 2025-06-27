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

    class Config:
        orm_mode = True

