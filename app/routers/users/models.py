from datetime import datetime

from app.config.postgres_config import Base
from sqlalchemy import String, Column, DateTime
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {"schema": "cyclopedia_owner"}
    id = Column(String(255), nullable=False, primary_key=True, unique=True)
    username = Column(String(255), nullable=False, primary_key=True, unique=True)
    password = Column(String(255), nullable=False, primary_key=True, unique=True)
    email = Column(String(255), nullable=False, primary_key=True, unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


    comments = relationship("Comments", back_populates="users")

    ## Add password field, add email field, name, last name, birth date,

