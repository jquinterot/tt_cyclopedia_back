#!/usr/bin/env python3
"""
Test script to verify Cloudinary setup
Run this to check if your credentials are working
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

load_dotenv()

def test_cloudinary_setup():
    """Test Cloudinary configuration"""
    
    print("Testing Cloudinary Setup...")
    print("=" * 40)
    
    # Check environment variables
    cloudinary_url = os.getenv("CLOUDINARY_URL")
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    
    print(f"CLOUDINARY_URL: {'✓ Set' if cloudinary_url else '✗ Not set'}")
    print(f"CLOUDINARY_CLOUD_NAME: {'✓ Set' if cloud_name else '✗ Not set'}")
    print(f"CLOUDINARY_API_KEY: {'✓ Set' if api_key else '✗ Not set'}")
    print(f"CLOUDINARY_API_SECRET: {'✓ Set' if api_secret else '✗ Not set'}")
    print()
    
    # Check if we have either URL or individual credentials
    if not cloudinary_url and not all([cloud_name, api_key, api_secret]):
        print("❌ Error: Missing Cloudinary credentials!")
        print("Please set either CLOUDINARY_URL or all three individual credentials:")
        print("  CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")
        return False
    
    print("✓ Credentials found!")
    
    # Try to import and configure cloudinary
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Configure cloudinary
        if cloudinary_url:
            print("Using CLOUDINARY_URL format...")
            cloudinary.config(url=cloudinary_url)
        else:
            print("Using individual credentials format...")
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
        
        print("✓ Cloudinary configured successfully!")
        
        # Test connection by getting account info
        try:
            import cloudinary.api
            account_info = cloudinary.api.ping()
            print("✓ Cloudinary connection test successful!")
            print(f"  Response: {account_info}")
            return True
        except Exception as e:
            print(f"❌ Cloudinary connection test failed: {str(e)}")
            return False
            
    except ImportError:
        print("❌ Error: cloudinary package not installed!")
        print("Please install it with: pip install cloudinary")
        return False
    except Exception as e:
        print(f"❌ Error configuring Cloudinary: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_cloudinary_setup()
    if success:
        print("\n🎉 Cloudinary setup is working correctly!")
        print("You can now use image uploads in your application.")
    else:
        print("\n❌ Cloudinary setup needs attention.")
        print("Please check the errors above and fix them.")
        sys.exit(1) 