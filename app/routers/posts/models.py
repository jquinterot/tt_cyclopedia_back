from datetime import UTC, datetime

import shortuuid
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.config.postgres_config import Base, get_fk_reference, get_schema_kwargs

schema_kwargs = get_schema_kwargs()


class PostLike(Base):
    __tablename__ = "post_likes"
    if schema_kwargs:
        __table_args__ = (
            UniqueConstraint("user_id", "post_id", name="_user_post_uc"),
            schema_kwargs,
        )
    else:
        __table_args__ = (UniqueConstraint("user_id", "post_id", name="_user_post_uc"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey(get_fk_reference("users")), nullable=False)
    post_id = Column(String(255), ForeignKey(get_fk_reference("posts")), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))


class Posts(Base):
    __tablename__ = "posts"
    if schema_kwargs:
        __table_args__ = schema_kwargs
    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(512), nullable=False)
    likes = Column(Integer, default=0)
    author = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    stats = Column(JSON, nullable=True)
    equipment_id = Column(String(255), ForeignKey(get_fk_reference("equipment")), nullable=True)
    equipment = relationship("Equipment", foreign_keys=[equipment_id])
    comments = relationship("Comments", back_populates="post", cascade="all, delete-orphan")
    post_likes = relationship("PostLike", backref="post", cascade="all, delete-orphan")
