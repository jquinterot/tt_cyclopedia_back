from typing import Optional

from pydantic import BaseModel


class CommentBase(BaseModel):
    comment: str
    post_id: str
    user_id: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: Optional[str] = None
