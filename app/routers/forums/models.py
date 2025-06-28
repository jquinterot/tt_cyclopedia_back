from datetime import datetime
import os
from app.config.postgres_config import Base
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
import shortuuid
from sqlalchemy.orm import relationship

# Set schema only if not using SQLite (check environment variable)
if "sqlite" in os.getenv("SQL_DB", ""):
    SCHEMA_KWARGS = {}
    FK_USER = 'users.id'
    FK_FORUM = 'forums.id'
    FK_FORUM_COMMENT = 'forum_comments.id'
else:
    SCHEMA_KWARGS = {"schema": "cyclopedia_owner"}
    FK_USER = 'cyclopedia_owner.users.id'
    FK_FORUM = 'cyclopedia_owner.forums.id'
    FK_FORUM_COMMENT = 'cyclopedia_owner.forum_comments.id'

class Forums(Base):
    __tablename__ = 'forums'
    __table_args__ = SCHEMA_KWARGS if SCHEMA_KWARGS else None
    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    author = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    updated_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    forum_likes = relationship("ForumLike", backref="forum", cascade="all, delete-orphan")
    forum_comments = relationship("ForumComment", backref="forum", cascade="all, delete-orphan")


class ForumLike(Base):
    __tablename__ = 'forum_likes'
    __table_args__ = SCHEMA_KWARGS if SCHEMA_KWARGS else None
    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    forum_id = Column(String(255), ForeignKey(FK_FORUM, ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey(FK_USER, ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ForumComment(Base):
    __tablename__ = 'forum_comments'
    __table_args__ = SCHEMA_KWARGS if SCHEMA_KWARGS else None
    id = Column(String(255), nullable=False, primary_key=True)
    comment = Column(String(255), nullable=False, unique=False)
    forum_id = Column(String(255), ForeignKey(FK_FORUM, ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey(FK_USER, ondelete='CASCADE'), nullable=False)
    parent_id = Column(String(255), nullable=True)
    likes = Column(Integer, default=0)
    username = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    comment_likes = relationship("ForumCommentLike", backref="comment", cascade="all, delete-orphan")


class ForumCommentLike(Base):
    __tablename__ = 'forum_comment_likes'
    __table_args__ = SCHEMA_KWARGS if SCHEMA_KWARGS else None
    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    comment_id = Column(String(255), ForeignKey(FK_FORUM_COMMENT, ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey(FK_USER, ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)