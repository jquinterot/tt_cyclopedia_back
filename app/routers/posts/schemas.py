from typing import Optional

from pydantic import BaseModel


class Post(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    img: Optional[str] = ''
    likes: Optional[int] = 0
