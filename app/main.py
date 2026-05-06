from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
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
from app.middleware.rate_limiter import WriteRateLimiterMiddleware
from app.config.logging_config import setup_logging
import os

# Setup logging with sensitive data filtering
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(MongoLoggingMiddleware)

# Rate limiting - only in production
if os.getenv("PRODUCTION", "false").lower() == "true":
    app.add_middleware(WriteRateLimiterMiddleware)

app.include_router(comments_router)
app.include_router(posts_router)
app.include_router(users_router)
app.include_router(forums_router)
app.include_router(logs_router)
app.include_router(auth_router)
app.include_router(equipment_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Server is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}