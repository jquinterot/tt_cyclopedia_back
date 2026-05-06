from datetime import datetime
from app.config.postgres_config import Base, get_schema_kwargs
from sqlalchemy import String, Column, DateTime, Boolean
from sqlalchemy.orm import relationship

schema_kwargs = get_schema_kwargs()

class Users(Base):
    __tablename__ = 'users'
    id = Column(String(255), nullable=False, primary_key=True, unique=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    comments = relationship("Comments", back_populates="users")
    if schema_kwargs:
        __table_args__ = schema_kwargs

