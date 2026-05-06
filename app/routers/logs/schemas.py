from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class LogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: Optional[str] = Field(None, alias="_id")
    method: str
    path: str
    timestamp: datetime
    client: str