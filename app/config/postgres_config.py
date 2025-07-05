from sqlalchemy import create_engine, DDL, event
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
# Prioritize TEST_SQL_DB for tests, otherwise use SQL_DB for production
postgres_db = os.getenv("TEST_SQL_DB") or os.getenv("SQL_DB")
if not postgres_db:
    raise ValueError("Either TEST_SQL_DB or SQL_DB environment variable must be set")

engine = create_engine(
    postgres_db,
    echo=True,
    pool_pre_ping=True,  # Check connections before use
    pool_recycle=300  # Recycle connections every 5 minutes
)

Base = declarative_base()

# Only create schema for PostgreSQL, not SQLite (used in tests)
if engine.dialect.name != "sqlite":
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
    """Check if we're using SQLite database (for tests, check both SQL_DB and TEST_SQL_DB)"""
    db_url = os.getenv("TEST_SQL_DB") or os.getenv("SQL_DB", "")
    return "sqlite" in db_url.lower()

def get_schema_kwargs():
    """Get schema kwargs based on database type (never set schema for SQLite or if TEST_SQL_DB is set)"""
    if is_sqlite():
        return {}
    return {"schema": "cyclopedia_owner"}

def get_fk_reference(table_name):
    """Get foreign key reference with proper schema (never set schema for SQLite or if TEST_SQL_DB is set)"""
    if is_sqlite():
        return f"{table_name}.id"
    return f"cyclopedia_owner.{table_name}.id"
