from app.config.postgres_config import Base, attach_schema_event

# Attach schema event for production
attach_schema_event(Base)

import uvicorn


def start():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()