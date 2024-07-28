from app.config.postgres_config import Base
from sqlalchemy import String, Boolean, Integer, Column


class Posts(Base):
    __tablename__ = 'posts'
    __table_args__ = {"schema": "cyclopedia_owner"}
    id = Column(String(255), nullable=False, primary_key=True)
    title = Column(String(255), nullable=False, unique=False)
    content = Column(String(255), nullable=False, unique=False)
    img = Column(String(255), nullable=True, unique=False)
    likes = Column(String(255), nullable=True, unique=False)
