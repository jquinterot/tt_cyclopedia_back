from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="forbid")
    id: str | None = Field(None, alias="_id", description="MongoDB document ID")
    method: str = Field(..., description="HTTP method", examples=["GET", "POST"])
    path: str = Field(..., description="Request path", examples=["/users"])
    timestamp: datetime = Field(..., description="Request timestamp")
    client: str = Field(..., description="Client identifier or IP")
