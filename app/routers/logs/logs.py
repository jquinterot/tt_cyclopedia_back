from fastapi import APIRouter, Query
from app.config.mongo_config import db
from typing import List, Optional
from datetime import datetime
from app.routers.logs.schemas import LogEntry

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/", response_model=List[LogEntry])
def get_logs(
    limit: int = Query(10, ge=1, le=100),
    method: Optional[str] = None,
    path: Optional[str] = None,
    since: Optional[datetime] = None
):
    query = {}
    if method:
        query["method"] = method.upper()
    if path:
        query["path"] = path
    if since:
        query["timestamp"] = {"$gte": since}
    logs = list(db.api_logs.find(query).sort("timestamp", -1).limit(limit))
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs 