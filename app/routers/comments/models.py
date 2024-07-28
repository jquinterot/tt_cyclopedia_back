from app.config.postgres_config import Base
from sqlalchemy import String, Boolean, Integer, Column


class Comments(Base):
    __tablename__ = 'comments'
    __table_args__ = {"schema": "cyclopedia_owner"}
    id = Column(String(255), nullable=False, primary_key=True)
    comment = Column(String(255), nullable=False, unique=False)
