from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LogEntry(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    method: str
    path: str
    timestamp: datetime
    client: str

    class Config:
        allow_population_by_field_name = True
        orm_mode = True 