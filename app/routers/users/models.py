from app.config.postgres_config import Base
from sqlalchemy import String, Boolean, Integer, Column
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {"schema": "cyclopedia_owner"}
    id = Column(String(255), nullable=False, primary_key=True, unique=True)
    username = Column(String(255), nullable=False, primary_key=True, unique=True)

    comments = relationship("Comments", back_populates="users")

