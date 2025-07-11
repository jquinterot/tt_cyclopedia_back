#!/usr/bin/env python3
"""
Migration script to move existing local images to Cloudinary
Run this script after setting up Cloudinary credentials
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import cloudinary
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.config.cloudinary_config import upload_image_to_cloudinary
from app.routers.posts.models import Posts

load_dotenv()

def migrate_images():
    """Migrate local images to Cloudinary"""
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")
    )
    
    # Database connection
    database_url = os.getenv("SQL_DB")
    if not database_url:
        print("Error: SQL_DB environment variable not set")
        return
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all posts with local image URLs
        posts = db.query(Posts).filter(
            Posts.image_url.like("/static/uploads/%")
        ).all()
        
        print(f"Found {len(posts)} posts with local images to migrate")
        
        uploads_dir = Path("static/uploads")
        migrated_count = 0
        failed_count = 0
        
        for post in posts:
            try:
                # Extract filename from URL
                filename = post.image_url.split("/")[-1]
                file_path = uploads_dir / filename
                
                if file_path.exists():
                    print(f"Migrating {filename}...")
                    
                    # Upload to Cloudinary
                    with open(file_path, "rb") as f:
                        cloudinary_url = upload_image_to_cloudinary(f)
                    
                    # Update database
                    post.image_url = cloudinary_url
                    db.commit()
                    
                    print(f"✓ Successfully migrated {filename}")
                    migrated_count += 1
                    
                    # Optionally delete local file
                    # file_path.unlink()
                    # print(f"  Deleted local file {filename}")
                    
                else:
                    print(f"⚠ File not found: {filename}")
                    # Update to default image
                    post.image_url = "/static/default/default.jpeg"
                    db.commit()
                    failed_count += 1
                    
            except Exception as e:
                print(f"✗ Failed to migrate {post.image_url}: {str(e)}")
                failed_count += 1
                db.rollback()
        
        print(f"\nMigration completed:")
        print(f"  Successfully migrated: {migrated_count}")
        print(f"  Failed: {failed_count}")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting image migration to Cloudinary...")
    print("Make sure you have set up your Cloudinary credentials in .env file")
    print()
    
    # Check if Cloudinary credentials are set
    if not all([
        os.getenv("CLOUDINARY_CLOUD_NAME"),
        os.getenv("CLOUDINARY_API_KEY"),
        os.getenv("CLOUDINARY_API_SECRET")
    ]):
        print("Error: Cloudinary credentials not found in .env file")
        print("Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET")
        sys.exit(1)
    
    migrate_images() 