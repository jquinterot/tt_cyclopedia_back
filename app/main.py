from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.comments.comments import router as comments_router
from app.routers.posts.posts import router as posts_router
from app.routers.users.users import router as users_router
from app.config.postgres_config import Base, engine, SessionLocal
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(comments_router)
app.include_router(posts_router)
app.include_router(users_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return {"message": "Server is running"}
