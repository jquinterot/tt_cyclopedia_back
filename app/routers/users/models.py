from datetime import datetime
import os
from app.config.postgres_config import Base
from sqlalchemy import String, Column, DateTime
from sqlalchemy.orm import relationship

# Set schema only if not using SQLite (check environment variable)
if "sqlite" in os.getenv("SQL_DB", ""):
    SCHEMA_KWARGS = {}
else:
    SCHEMA_KWARGS = {"schema": "cyclopedia_owner"}

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = SCHEMA_KWARGS if SCHEMA_KWARGS else None
    id = Column(String(255), nullable=False, primary_key=True, unique=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    comments = relationship("Comments", back_populates="users")

    ## Add password field, add email field, name, last name, birth date,

