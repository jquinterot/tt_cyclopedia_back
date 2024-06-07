import uvicorn
from fastapi import FastAPI, Response
from routers.comments.comments import router as comments_router
from routers.posts.posts import router as posts_router
from routers.users.users import router as users_router

app = FastAPI()

app.include_router(comments_router)
app.include_router(posts_router)
app.include_router(users_router)


@app.get("/")
def read_root():
    return {"message": "Server is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
