from datetime import datetime
import shortuuid
import os

from sqlalchemy import String, Column, ForeignKey, Integer, DateTime, inspect
from sqlalchemy.orm import relationship
from app.config.postgres_config import Base, engine

# Set schema only if not using SQLite (check environment variable)
if "sqlite" in os.getenv("SQL_DB", ""):
    SCHEMA_KWARGS = {}
    FK_USER = 'users.id'
    FK_POST = 'posts.id'
    FK_FORUM = 'forums.id'
    FK_COMMENT = 'comments.id'
else:
    SCHEMA_KWARGS = {"schema": "cyclopedia_owner"}
    FK_USER = 'cyclopedia_owner.users.id'
    FK_POST = 'cyclopedia_owner.posts.id'
    FK_FORUM = 'cyclopedia_owner.forums.id'
    FK_COMMENT = 'cyclopedia_owner.comments.id'

class Comments(Base):
    __tablename__ = 'comments'
    __table_args__ = SCHEMA_KWARGS if SCHEMA_KWARGS else None
    id = Column(String(255), nullable=False, primary_key=True)
    comment = Column(String(255), nullable=False, unique=False)
    post_id = Column(String(255), ForeignKey(FK_POST, ondelete='CASCADE'), nullable=True)
    forum_id = Column(String(255), ForeignKey(FK_FORUM, ondelete='CASCADE'), nullable=True)
    user_id = Column(String(255), ForeignKey(FK_USER, ondelete='CASCADE'), nullable=False)
    parent_id = Column(String(255), nullable=True)
    likes = Column(Integer, default=0)
    username = Column(String(255), nullable=True)
    post = relationship("Posts", back_populates="comments")
    users = relationship("Users", back_populates="comments")
    timestamp = Column(DateTime, default=datetime.utcnow)
    comment_likes = relationship("CommentLike", backref="comment", cascade="all, delete-orphan")


class CommentLike(Base):
    __tablename__ = 'comment_likes'
    __table_args__ = SCHEMA_KWARGS if SCHEMA_KWARGS else None
    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    comment_id = Column(String(255), ForeignKey(FK_COMMENT, ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey(FK_USER, ondelete='CASCADE'), nullable=False)

