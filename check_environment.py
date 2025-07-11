#!/usr/bin/env python3
"""
Script to check and set the correct environment for production deployment
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check current environment configuration"""
    
    print("🔍 Environment Configuration Check")
    print("=" * 50)
    
    # Check current environment
    current_env = os.getenv("ENVIRONMENT", "development")
    print(f"Current ENVIRONMENT: {current_env}")
    
    # Check Cloudinary credentials
    cloudinary_url = os.getenv("CLOUDINARY_URL")
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    
    print(f"\n📁 Cloudinary Configuration:")
    print(f"  CLOUDINARY_URL: {'✓ Set' if cloudinary_url else '✗ Not set'}")
    print(f"  CLOUDINARY_CLOUD_NAME: {'✓ Set' if cloud_name else '✗ Not set'}")
    print(f"  CLOUDINARY_API_KEY: {'✓ Set' if api_key else '✗ Not set'}")
    print(f"  CLOUDINARY_API_SECRET: {'✓ Set' if api_secret else '✗ Not set'}")
    
    # Determine where images will be saved
    if current_env == "development":
        print(f"\n📸 Image Storage: LOCAL (static/uploads/)")
        print(f"  Reason: ENVIRONMENT is set to 'development'")
    elif current_env == "testing":
        print(f"\n📸 Image Storage: MOCK (static/uploads/ for testing)")
        print(f"  Reason: ENVIRONMENT is set to 'testing'")
    elif current_env == "production":
        if cloudinary_url or all([cloud_name, api_key, api_secret]):
            print(f"\n📸 Image Storage: CLOUDINARY")
            print(f"  Reason: ENVIRONMENT is set to 'production' and Cloudinary credentials are available")
        else:
            print(f"\n❌ ERROR: ENVIRONMENT is 'production' but Cloudinary credentials are missing!")
            print(f"  Images will fail to upload in production")
    else:
        print(f"\n📸 Image Storage: CLOUDINARY")
        print(f"  Reason: ENVIRONMENT is '{current_env}' (not development/testing)")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if current_env == "development":
        print(f"  ✓ Development environment correctly configured for local storage")
    elif current_env == "production":
        if cloudinary_url or all([cloud_name, api_key, api_secret]):
            print(f"  ✓ Production environment correctly configured for Cloudinary")
        else:
            print(f"  ❌ Set Cloudinary credentials for production")
    else:
        print(f"  ℹ️  For production deployment, set ENVIRONMENT=production")
        print(f"  ℹ️  Ensure Cloudinary credentials are configured")

def set_production_environment():
    """Instructions for setting production environment"""
    
    print(f"\n🚀 Setting Up Production Environment")
    print(f"=" * 50)
    
    print(f"To configure production environment:")
    print(f"")
    print(f"1. Set ENVIRONMENT=production in your production deployment")
    print(f"2. Ensure Cloudinary credentials are set:")
    print(f"   - CLOUDINARY_CLOUD_NAME")
    print(f"   - CLOUDINARY_API_KEY") 
    print(f"   - CLOUDINARY_API_SECRET")
    print(f"   - OR CLOUDINARY_URL")
    print(f"")
    print(f"3. For GitHub Actions, update .github/workflows/ci_cd_pipeline.yml:")
    print(f"   Change ENVIRONMENT: 'development' to ENVIRONMENT: 'production'")
    print(f"")
    print(f"4. For Docker deployment, set environment variable:")
    print(f"   -e ENVIRONMENT=production")
    print(f"")
    print(f"5. For .env file, add:")
    print(f"   ENVIRONMENT=production")

if __name__ == "__main__":
    check_environment()
    set_production_environment() 