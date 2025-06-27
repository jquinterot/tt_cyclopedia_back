from datetime import datetime

from app.config.postgres_config import Base
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, ForeignKey, UniqueConstraint
import shortuuid
from sqlalchemy.orm import relationship


class PostLike(Base):
    __tablename__ = 'post_likes'
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='_user_post_uc'), {"schema": "cyclopedia_owner"})
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey('cyclopedia_owner.users.id'), nullable=False)
    post_id = Column(String(255), ForeignKey('cyclopedia_owner.posts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Posts(Base):
    __tablename__ = 'posts'
    __table_args__ = {"schema": "cyclopedia_owner"}

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
