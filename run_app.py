
import uvicorn


def start():
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    start()
