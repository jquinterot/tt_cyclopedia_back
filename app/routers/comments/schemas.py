from typing import Optional

from pydantic import BaseModel


class Comment(BaseModel):
    id: Optional[str] = None
    comment: str

