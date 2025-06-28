from datetime import datetime
import os
from app.config.postgres_config import Base
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, ForeignKey, UniqueConstraint, inspect
import shortuuid
from sqlalchemy.orm import relationship

# Set schema only if not using SQLite (check environment variable)
if "sqlite" in os.getenv("SQL_DB", ""):
    SCHEMA_KWARGS = {}
    FK_USER = 'users.id'
    FK_POST = 'posts.id'
else:
    SCHEMA_KWARGS = {"schema": "cyclopedia_owner"}
    FK_USER = 'cyclopedia_owner.users.id'
    FK_POST = 'cyclopedia_owner.posts.id'

class PostLike(Base):
    __tablename__ = 'post_likes'
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='_user_post_uc'),) if not SCHEMA_KWARGS else (UniqueConstraint('user_id', 'post_id', name='_user_post_uc'), SCHEMA_KWARGS)
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey(FK_USER), nullable=False)
    post_id = Column(String(255), ForeignKey(FK_POST), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Posts(Base):
    __tablename__ = 'posts'
    __table_args__ = SCHEMA_KWARGS if SCHEMA_KWARGS else None

    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(512), nullable=False)
    likes = Column(Integer, default=0)
    author = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    stats = Column(JSON, nullable=True)

    comments = relationship("Comments", back_populates="post", cascade="all, delete-orphan")
    post_likes = relationship("PostLike", backref="post", cascade="all, delete-orphan")
