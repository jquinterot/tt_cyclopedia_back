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

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
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