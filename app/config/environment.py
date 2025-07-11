import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EnvironmentConfig:
    """Environment configuration for different deployment scenarios"""
    
    @staticmethod
    def get_environment() -> str:
        """Get current environment"""
        return os.getenv("ENVIRONMENT", "development")
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production"""
        return EnvironmentConfig.get_environment() == "production"
    
    @staticmethod
    def is_development() -> bool:
        """Check if running in development"""
        return EnvironmentConfig.get_environment() == "development"
    
    @staticmethod
    def is_testing() -> bool:
        """Check if running in testing"""
        return EnvironmentConfig.get_environment() == "testing"
    
    @staticmethod
    def get_cloudinary_config() -> dict:
        """Get Cloudinary configuration based on environment"""
        config = {
            "cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME"),
            "api_key": os.getenv("CLOUDINARY_API_KEY"),
            "api_secret": os.getenv("CLOUDINARY_API_SECRET"),
            "url": os.getenv("CLOUDINARY_URL")
        }
        
        # Validate configuration
        if not config["url"] and not all([config["cloud_name"], config["api_key"], config["api_secret"]]):
            if EnvironmentConfig.is_production():
                raise ValueError("Cloudinary credentials are required in production")
            else:
                print("Warning: Cloudinary credentials not found. Image uploads will fail.")
        
        return config
    
    @staticmethod
    def is_docker() -> bool:
        """Check if running in Docker environment"""
        # Check for Docker-specific environment variables or files
        return (
            os.path.exists("/.dockerenv") or  # Docker creates this file
            os.getenv("DOCKER_ENV") == "true" or  # Custom Docker env var
            os.getenv("KUBERNETES_SERVICE_HOST") is not None  # Kubernetes (often in Docker)
        )
    
    @staticmethod
    def get_database_url() -> str:
        """Get database URL based on environment"""
        if EnvironmentConfig.is_testing():
            return os.getenv("SQL_LITE_DB", "sqlite:///./test.db")
        else:
            # Use "db" for Docker, "localhost" for local development
            host = "db" if EnvironmentConfig.is_docker() else "localhost"
            return os.getenv("SQL_DB", f"postgresql://postgres:postgres@{host}:5432/tt_cyclopedia")
    
    @staticmethod
    def get_mongo_config() -> dict:
        """Get MongoDB configuration"""
        return {
            "url": os.getenv("MONGO_DB", "mongodb://localhost:27017"),
            "database": os.getenv("MONGO_DB_NAME", "tt_cyclopedia")
        } 