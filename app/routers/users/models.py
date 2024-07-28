from app.config.postgres_config import Base
from sqlalchemy import String, Boolean, Integer, Column


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {"schema": "cyclopedia_owner"}
    id = Column(String(255), nullable=False, primary_key=True)
    username = Column(String(255), nullable=False, primary_key=True)