##Pydantic schema here
from pydantic import BaseModel


class Comment(BaseModel):
    id: int
    comment: str
