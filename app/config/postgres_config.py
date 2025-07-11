from sqlalchemy import create_engine, DDL, event
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
# Use SQL_DB for app, SQL_LITE_DB for tests
postgres_db = os.getenv("SQL_DB")
if not postgres_db:
    raise ValueError("SQL_DB environment variable must be set")

engine = create_engine(
    postgres_db,
    echo=True,
    pool_pre_ping=True,  # Check connections before use
    pool_recycle=300  # Recycle connections every 5 minutes
)

# Enable foreign key support for SQLite
if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

Base = declarative_base()

# Refactored: Only attach schema event when explicitly called

def attach_schema_event(Base):
    if "sqlite" not in str(engine.url):
        event.listen(
            Base.metadata,
            'before_create',
            DDL("CREATE SCHEMA IF NOT EXISTS cyclopedia_owner")
        )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_sqlite():
    """Check if we're using SQLite database (for tests)"""
    # Check both environment variables and engine URL
    db_url = os.getenv("SQL_LITE_DB", "")
    engine_url = str(engine.url) if engine else ""
    return "sqlite" in db_url.lower() or "sqlite" in engine_url.lower()

def get_schema_kwargs():
    """Get schema kwargs based on database type (never set schema for SQLite)"""
    if is_sqlite():
        return {}
    return {"schema": "cyclopedia_owner"}

def get_fk_reference(table_name):
    """Get foreign key reference with proper schema (never set schema for SQLite)"""
    if is_sqlite():
        return f"{table_name}.id"
    return f"cyclopedia_owner.{table_name}.id"
