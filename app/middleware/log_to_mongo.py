from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.config.mongo_config import db
import datetime

class MongoLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        log_entry = {
            "method": request.method,
            "path": request.url.path,
            "timestamp": datetime.datetime.utcnow(),
            "client": request.client.host,
        }
        try:
            db.api_logs.insert_one(log_entry)
        except Exception as e:
            pass  # Optionally log to file if Mongo is down
        response = await call_next(request)
        return response