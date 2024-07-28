
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.comments.comments import router as comments_router
from app.routers.posts.posts import router as posts_router
from app.routers.users.users import router as users_router
from app.config.postgres_config import Base, engine, SessionLocal


Base.metadata.create_all(bind=engine)

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(comments_router)
app.include_router(posts_router)
app.include_router(users_router)


@app.get("/")
def read_root():
    return {"message": "Server is running"}

