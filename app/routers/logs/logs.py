from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_admin
from app.config.mongo_config import db
from app.middleware.rate_limiter import read_rate_limit
from app.routers.logs.schemas import LogEntry
from app.routers.users.models import Users

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/", response_model=list[LogEntry])
def get_logs(
    limit: int = Query(10, ge=1, le=100),
    method: str | None = None,
    path: str | None = None,
    since: datetime | None = None,
    current_admin: Users = Depends(get_current_admin),
    _: bool = Depends(read_rate_limit),
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
