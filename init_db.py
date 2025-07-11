#!/usr/bin/env python3
"""
Initialize SQLite database with all tables
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy import create_engine
from app.routers.users.models import Users
from app.routers.posts.models import Posts
from app.routers.comments.models import Comments
from app.routers.forums.models import Forums
from app.config.postgres_config import Base

def init_database():
    """Initialize the database with all tables"""
    
    # Use SQLite for local development
    database_url = "sqlite:///./test.db"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✓ Database tables created successfully!")
    print(f"Database file: {Path('./test.db').absolute()}")

if __name__ == "__main__":
    init_database() 