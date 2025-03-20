# app/routers/posts/models.py
from app.config.postgres_config import Base
from sqlalchemy import Column, String, Text, Integer
import shortuuid


class Posts(Base):
    __tablename__ = 'posts'
    __table_args__ = {"schema": "cyclopedia_owner"}

    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(512), nullable=False)  # Changed from image_id
    likes = Column(Integer, default=0)

