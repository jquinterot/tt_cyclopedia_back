from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: Optional[str] = None
    username: str
    password: str
    email: str
