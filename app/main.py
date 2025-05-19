from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers.comments.comments import router as comments_router
from app.routers.posts.posts import router as posts_router
from app.routers.users.users import router as users_router
from fastapi.staticfiles import StaticFiles
from app.routers.users.seeds import seed_default_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_default_admin()
    yield

app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# Routers
app.include_router(comments_router)
app.include_router(posts_router)
app.include_router(users_router)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Server is running"}