from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB configuration with environment variable support
MONGO_URL = os.getenv("MONGO_DB")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "tt_cyclopedia")

if not MONGO_URL:
    raise ValueError("MONGO_DB environment variable must be set")

# Create MongoDB client
client = MongoClient(MONGO_URL)

# Get database instance
db = client[MONGO_DB_NAME]

def get_mongo_client():
    """Get MongoDB client instance"""
    return client

def get_mongo_db():
    """Get MongoDB database instance"""
    return db

def is_mongo_atlas():
    """Check if we're using MongoDB Atlas (cloud) vs local MongoDB"""
    mongo_url = os.getenv("MONGO_DB", "")
    return "mongodb+srv://" in mongo_url or "atlas" in mongo_url.lower() 