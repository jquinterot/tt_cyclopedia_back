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
from app.config.postgres_config import Base, attach_schema_event

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:3001",  # Alternative React port
        "http://localhost:5173",  # Vite default
        "http://localhost:8080",  # Vue default
        "http://localhost:4200",  # Angular default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:4200",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MongoLoggingMiddleware)

# Routers
app.include_router(comments_router)
app.include_router(posts_router)
app.include_router(users_router)
app.include_router(forums_router)
app.include_router(logs_router)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Server is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}