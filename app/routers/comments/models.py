from datetime import datetime
import shortuuid
from sqlalchemy import String, Column, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from app.config.postgres_config import Base, get_schema_kwargs, get_fk_reference

schema_kwargs = get_schema_kwargs()

class Comments(Base):
    __tablename__ = 'comments'
    id = Column(String(255), nullable=False, primary_key=True)
    comment = Column(String(255), nullable=False, unique=False)
    post_id = Column(String(255), ForeignKey(get_fk_reference('posts'), ondelete='CASCADE'), nullable=True)
    forum_id = Column(String(255), ForeignKey(get_fk_reference('forums'), ondelete='CASCADE'), nullable=True)
    user_id = Column(String(255), ForeignKey(get_fk_reference('users'), ondelete='CASCADE'), nullable=False)
    parent_id = Column(String(255), nullable=True)
    likes = Column(Integer, default=0)
    username = Column(String(255), nullable=True)
    post = relationship("Posts", back_populates="comments")
    users = relationship("Users", back_populates="comments")
    timestamp = Column(DateTime, default=datetime.utcnow)
    if schema_kwargs:
        __table_args__ = schema_kwargs  # type: ignore
    comment_likes = relationship("CommentLike", backref="comment", cascade="all, delete-orphan")


class CommentLike(Base):
    __tablename__ = 'comment_likes'
    id = Column(String(255), nullable=False, primary_key=True)
    comment_id = Column(String(255), ForeignKey(get_fk_reference('comments'), ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey(get_fk_reference('users'), ondelete='CASCADE'), nullable=False)
    if schema_kwargs:
        __table_args__ = schema_kwargs  # type: ignore

