from pydantic import BaseModel


class Comment(BaseModel):
    id: str
    comment: str


class PlainComment(BaseModel):
    comment: str
