from datetime import datetime
import shortuuid

from sqlalchemy import String, Column, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from app.config.postgres_config import Base


class Comments(Base):
    __tablename__ = 'comments'
    __table_args__ = {"schema": "cyclopedia_owner"}
    id = Column(String(255), nullable=False, primary_key=True)
    comment = Column(String(255), nullable=False, unique=False)
    post_id = Column(String(255), ForeignKey('cyclopedia_owner.posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey('cyclopedia_owner.users.id', ondelete='CASCADE'), nullable=False)
    parent_id = Column(String(255), nullable=True)
    likes = Column(Integer, default=0)
    username = Column(String(255), nullable=True)
    post = relationship("Posts", back_populates="comments")
    users = relationship("Users", back_populates="comments")
    timestamp = Column(DateTime, default=datetime.utcnow)
    comment_likes = relationship("CommentLike", backref="comment", cascade="all, delete-orphan")


class CommentLike(Base):
    __tablename__ = 'comment_likes'
    __table_args__ = {"schema": "cyclopedia_owner"}
    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    comment_id = Column(String(255), ForeignKey('cyclopedia_owner.comments.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey('cyclopedia_owner.users.id', ondelete='CASCADE'), nullable=False)

