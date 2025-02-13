from sqlalchemy import create_engine, DDL, event
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
postgres_db = os.getenv("SQL_DB")

engine = create_engine(postgres_db, echo=True)
Base = declarative_base()

event.listen(
    Base.metadata,
    'before_create',
    DDL("CREATE SCHEMA IF NOT EXISTS cyclopedia_owner")
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
