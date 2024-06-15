from app.config.postgres_config import Base
from sqlalchemy import String, Boolean, Integer, Column


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    comment = Column(String(255), nullable=False, unique=False)
