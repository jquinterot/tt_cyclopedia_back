from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError
from app.routers.comments.comments import router as comments_router
from app.routers.posts.posts import router as posts_router
from app.routers.users.users import router as users_router
from app.routers.forums.forums import router as forums_router
from fastapi.staticfiles import StaticFiles
from app.middleware.log_to_mongo import MongoLoggingMiddleware
from app.routers.logs.logs import router as logs_router
from app.routers.auth import router as auth_router
from app.routers.equipment import router as equipment_router
from app.config.postgres_config import Base, attach_schema_event
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.config.logging_config import setup_logging
from app.utils.api_error import APIError, api_error_handler
import os

# Setup logging with sensitive data filtering
setup_logging()


class RootResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=600,
)

# Security middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(MongoLoggingMiddleware)

# Exception handlers
app.add_exception_handler(APIError, api_error_handler)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    headers = dict(exc.headers) if exc.headers else {}
    code = headers.pop("X-Error-Code", "UNKNOWN")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": code},
        headers=headers if headers else None,
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc: SQLAlchemyError):
    """Catch database errors and return user-friendly messages without leaking internals."""
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred. Please try again later.", "code": "DB_001"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    """Catch all unhandled exceptions to prevent internal error leakage."""
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later.", "code": "INTERNAL_001"},
    )


app.include_router(comments_router)
app.include_router(posts_router)
app.include_router(users_router)
app.include_router(forums_router)
app.include_router(logs_router)
app.include_router(auth_router)
app.include_router(equipment_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_model=RootResponse)
def read_root():
    return {"message": "Server is running"}


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok"}
