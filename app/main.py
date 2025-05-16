from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.comments.comments import router as comments_router
from app.routers.posts.posts import router as posts_router
from app.routers.users.users import router as users_router, Users  # Import Users model
from app.config.postgres_config import Base, engine, SessionLocal
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError

app = FastAPI()


@app.on_event("startup")
def startup_event():
    # Create all database tables

    Base.metadata.create_all(bind=engine)

    # Create default admin user if not exists
    db = SessionLocal()
    try:
        admin_id: str = "default_admin_id"  # default_admin_idConsistent ID across environments
        admin_username: str = "admin"

        # Check if admin user with the specific ID exists
        admin_user = db.query(Users).filter(Users.id == admin_id).first()

        if not admin_user:
            # Attempt to create the admin user
            new_admin = Users(id=admin_id, username=admin_username)
            db.add(new_admin)
            db.commit()
            print("Default admin user created successfully.")
        else:
            print("Default admin user already exists.")
    except IntegrityError as e:
        db.rollback()
        # Handle case where username is already taken
        if 'unique constraint' in str(e).lower() and 'username' in str(e).lower():
            print(f"Username '{admin_username}' is already taken. Admin user not created.")
        else:
            print(f"Database integrity error: {e}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error creating admin user: {e}")
    finally:
        db.close()


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
