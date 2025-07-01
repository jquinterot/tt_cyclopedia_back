from datetime import datetime
from app.config.postgres_config import Base, get_schema_kwargs, get_fk_reference
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
import shortuuid
from sqlalchemy.orm import relationship

schema_kwargs = get_schema_kwargs()

class Forums(Base):
    __tablename__ = 'forums'
    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    author = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    updated_timestamp = Column(DateTime, default=datetime.utcnow)
    forum_likes = relationship("ForumLike", backref="forum", cascade="all, delete-orphan")
    forum_comments = relationship("ForumComment", backref="forum", cascade="all, delete-orphan")
    if schema_kwargs:
        __table_args__ = schema_kwargs  # type: ignore


class ForumLike(Base):
    __tablename__ = 'forum_likes'
    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    forum_id = Column(String(255), ForeignKey(get_fk_reference('forums'), ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey(get_fk_reference('users'), ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    if schema_kwargs:
        __table_args__ = schema_kwargs  # type: ignore


class ForumComment(Base):
    __tablename__ = 'forum_comments'
    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    comment = Column(String(255), nullable=False)
    forum_id = Column(String(255), ForeignKey(get_fk_reference('forums'), ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey(get_fk_reference('users'), ondelete='CASCADE'), nullable=False)
    parent_id = Column(String(255), nullable=True)
    likes = Column(Integer, default=0)
    username = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    comment_likes = relationship("ForumCommentLike", backref="comment", cascade="all, delete-orphan")
    if schema_kwargs:
        __table_args__ = schema_kwargs  # type: ignore


class ForumCommentLike(Base):
    __tablename__ = 'forum_comment_likes'
    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    comment_id = Column(String(255), ForeignKey(get_fk_reference('forum_comments'), ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey(get_fk_reference('users'), ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    if schema_kwargs:
        __table_args__ = schema_kwargs  # type: ignore