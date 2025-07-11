"""
Test configuration - uses SQL_LITE_DB for tests only
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Use SQL_LITE_DB for tests
test_db = os.getenv("SQL_LITE_DB", "sqlite:///./test.db")
if not test_db:
    raise ValueError("SQL_LITE_DB environment variable must be set for tests")

engine = create_engine(
    test_db,
    echo=True,
    connect_args={"check_same_thread": False} if "sqlite" in test_db else {}
)

# Enable foreign key support for SQLite
if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_test_db():
    """Get test database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 