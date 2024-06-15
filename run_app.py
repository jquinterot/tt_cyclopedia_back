from app.main import app
import uvicorn


def start():
    uvicorn.run(app, host="localhost", port=8000)
