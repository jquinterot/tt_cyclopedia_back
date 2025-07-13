#!/usr/bin/env python3
"""
Script to delete production MongoDB data
WARNING: This will permanently delete data from your production MongoDB database!
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()

def get_mongo_connection():
    """Get MongoDB connection details"""
    mongo_url = os.getenv("MONGO_DB")
    mongo_db_name = os.getenv("MONGO_DB_NAME", "tt_cyclopedia")
    
    if not mongo_url:
        print("❌ Error: MONGO_DB environment variable not set")
        print("Please set MONGO_DB in your .env file or environment variables")
        return None, None
    
    return mongo_url, mongo_db_name

def connect_to_mongo(mongo_url, db_name):
    """Connect to MongoDB and return client and database"""
    try:
        client = MongoClient(mongo_url)
        # Test connection
        client.admin.command('ping')
        db = client[db_name]
        return client, db
    except Exception as e:
        print(f" Failed to connect to MongoDB: {str(e)}")
        return None, None

def show_database_info(db):
    """Show current database information"""
    print("\n📊 Current Database Information:")
    print("=" * 50)
    
    # List all collections
    collections = db.list_collection_names()
    print(f"Database: {db.name}")
    print(f"Collections found: {len(collections)}")
    
    total_documents = 0
    for collection_name in collections:
        try:
            count = db[collection_name].count_documents({})
            total_documents += count
            print(f"  📁 {collection_name}: {count:,} documents")
        except Exception as e:
            print(f"  📁 {collection_name}: Error counting documents - {str(e)}")
    
    print(f"\nTotal documents across all collections: {total_documents:,}")

def delete_collection_data(db, collection_name, dry_run=True):
    """Delete data from a specific collection"""
    try:
        collection = db[collection_name]
        count = collection.count_documents({})
        
        if dry_run:
            print(f"  🔍 Would delete {count:,} documents from '{collection_name}'")
            return count
        else:
            result = collection.delete_many({})
            print(f"  ✅ Deleted {result.deleted_count:,} documents from '{collection_name}'")
            return result.deleted_count
    except Exception as e:
        print(f"  ❌ Error deleting from '{collection_name}': {str(e)}")
        return 0

def delete_all_data(db, dry_run=True):
    """Delete all data from all collections"""
    collections = db.list_collection_names()
    total_deleted = 0
    
    print(f"\n{'🔍 DRY RUN - ' if dry_run else '🗑️  DELETING - '}All Collections:")
    print("=" * 50)
    
    for collection_name in collections:
        deleted_count = delete_collection_data(db, collection_name, dry_run)
        total_deleted += deleted_count
    
    return total_deleted

def confirm_deletion():
    """Get user confirmation for deletion"""
    print("\n⚠️  WARNING: This will permanently delete ALL data from your MongoDB database!")
    print("This action cannot be undone.")
    
    # Check if this looks like production
    mongo_url = os.getenv("MONGO_DB", "")
    if "mongodb+srv://" in mongo_url or "atlas" in mongo_url.lower():
        print("🔴 This appears to be a PRODUCTION MongoDB Atlas database!")
    else:
        print("🟡 This appears to be a local MongoDB database.")
    
    print("\nTo confirm deletion, type 'DELETE' (case sensitive):")
    confirmation = input("> ").strip()
    
    if confirmation == "DELETE":
        print("✅ Confirmation received. Proceeding with deletion...")
        return True
    else:
        print("❌ Deletion cancelled.")
        return False

def main():
    """Main function"""
    print("🗑️  Production MongoDB Data Deletion Script")
    print("=" * 60)
    
    # Get MongoDB connection details
    mongo_url, db_name = get_mongo_connection()
    if not mongo_url:
        sys.exit(1)
    
    # Connect to MongoDB
    client, db = connect_to_mongo(mongo_url, db_name)
    if client is None or db is None:
        sys.exit(1)
    
    print(f"✅ Connected to MongoDB: {db_name}")
    
    # Show current database info
    show_database_info(db)
    
    # Ask what to delete
    print("\n🗑️  Deletion Options:")
    print("1. Delete ALL data from ALL collections")
    print("2. Delete specific collection")
    print("3. Dry run (show what would be deleted)")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        # Delete all data
        if confirm_deletion():
            total_deleted = delete_all_data(db, dry_run=False)
            print(f"\n✅ Deletion completed! Total documents deleted: {total_deleted:,}")
        else:
            print("❌ Deletion cancelled.")
    
    elif choice == "2":
        # Delete specific collection
        collections = db.list_collection_names()
        print(f"\nAvailable collections: {', '.join(collections)}")
        collection_name = input("Enter collection name to delete: ").strip()
        
        if collection_name in collections:
            if confirm_deletion():
                deleted_count = delete_collection_data(db, collection_name, dry_run=False)
                print(f"\n✅ Deletion completed! Documents deleted: {deleted_count:,}")
            else:
                print("❌ Deletion cancelled.")
        else:
            print(f"❌ Collection '{collection_name}' not found.")
    
    elif choice == "3":
        # Dry run
        print("\n🔍 DRY RUN - No data will be deleted")
        total_would_delete = delete_all_data(db, dry_run=True)
        print(f"\n📊 Would delete {total_would_delete:,} documents total")
    
    elif choice == "4":
        print("👋 Exiting...")
    
    else:
        print("❌ Invalid choice.")
    
    # Close connection
    client.close()
    print("\n🔌 MongoDB connection closed.")

if __name__ == "__main__":
    main() 