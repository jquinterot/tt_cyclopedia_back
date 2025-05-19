# app/routers/users/seeds.py
from sqlalchemy.exc import IntegrityError
from app.config.postgres_config import Base, engine, SessionLocal
from .models import Users


async def seed_default_admin():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = db.query(Users).filter(Users.username == "admin").first()
        if not admin:
            db.add(Users(id="default_admin_id", username="admin"))
            db.commit()
            print("✔ Admin user seeded")
    except IntegrityError as e:
        db.rollback()
        print(f" Seed failed: {e}")
    finally:
        db.close()