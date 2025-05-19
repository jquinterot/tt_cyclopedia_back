from app.config.postgres_config import Base
from sqlalchemy import String, Boolean, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship


class Comments(Base):
    __tablename__ = 'comments'
    __table_args__ = {"schema": "cyclopedia_owner"}
    id = Column(String(255), nullable=False, primary_key=True)
    comment = Column(String(255), nullable=False, unique=False)
    post_id = Column(String(255), ForeignKey('cyclopedia_owner.posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), ForeignKey('cyclopedia_owner.users.id', ondelete='CASCADE'), nullable=False)
    post = relationship("Posts", back_populates="comments")
    users = relationship("Users", back_populates="comments")
