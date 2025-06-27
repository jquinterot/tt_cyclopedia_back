from datetime import datetime

from app.config.postgres_config import Base
from sqlalchemy import Column, String, Text, Integer,DateTime
import shortuuid
from sqlalchemy.orm import relationship


class Forums(Base):
    __tablename__ = 'forums'
    __table_args__ = {"schema": "cyclopedia_owner"}

    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    author = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    updated_timestamp = Column(DateTime, default=datetime.utcnow)