import os
from .environment import EnvironmentConfig

# Read all config from environment variables
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
DEFAULT_IMAGE_URL = os.getenv("DEFAULT_IMAGE_URL", "/static/default/default.jpeg")

# Only import cloudinary if not in testing
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT != "testing":
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        
        # Configure Cloudinary if credentials are present
        if CLOUDINARY_URL:
            cloudinary.config(url=CLOUDINARY_URL)
        elif all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
            cloudinary.config(
                cloud_name=CLOUDINARY_CLOUD_NAME,
                api_key=CLOUDINARY_API_KEY,
                api_secret=CLOUDINARY_API_SECRET
            )
    except ImportError:
        print("Warning: Cloudinary not available. Using local storage only.")

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def upload_image(file, folder="cyclopedia_uploads"):
    if ENVIRONMENT in ["development", "testing"]:
        # Save locally
        from pathlib import Path
        uploads_dir = Path("static/uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        file_path = uploads_dir / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        return f"/static/uploads/{file.filename}"
    else:
        # Upload to Cloudinary
        return upload_image_to_cloudinary(file, folder=folder)

def upload_image_to_cloudinary(file, folder="cyclopedia_uploads"):
    if ENVIRONMENT == "testing":
        # In testing, just return local path
        return f"/static/uploads/{file.filename}"
    
    try:
        import cloudinary.uploader
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="image",
            transformation=[
                {"quality": "auto", "fetch_format": "auto"}
            ]
        )
        return result["secure_url"]
    except Exception as e:
        raise Exception(f"Failed to upload image to Cloudinary: {str(e)}")

def delete_image_from_cloudinary(public_id):
    if ENVIRONMENT == "testing":
        # In testing, do nothing
        return
    
    try:
        if public_id and not public_id.startswith("/static/default/"):
            if public_id.startswith("http"):
                parts = public_id.split("/")
                if "cyclopedia_uploads" in parts:
                    upload_index = parts.index("cyclopedia_uploads")
                    public_id = "/".join(parts[upload_index:-1]) + "/" + parts[-1].split(".")[0]
            import cloudinary.uploader
            cloudinary.uploader.destroy(public_id)
    except Exception as e:
        print(f"Failed to delete image from Cloudinary: {str(e)}")

def get_cloudinary_url_from_db_url(db_url):
    """
    Convert database URL to Cloudinary URL if it's a local path
    """
    if db_url and db_url.startswith("/static/uploads/"):
        # This is a legacy local file, return default
        return DEFAULT_IMAGE_URL
    return db_url 