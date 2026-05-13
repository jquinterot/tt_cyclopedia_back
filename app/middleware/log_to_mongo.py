import datetime
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config.mongo_config import db

logger = logging.getLogger(__name__)


class MongoLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        log_entry = {
            "method": request.method,
            "path": request.url.path,
            "timestamp": datetime.datetime.now(datetime.UTC),
            "client": request.client.host,  # type: ignore
        }
        try:
            db.api_logs.insert_one(log_entry)
        except Exception as e:
            logger.warning(f"Failed to log to MongoDB: {e}")
        response = await call_next(request)
        return response
