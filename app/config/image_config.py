# config.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

STATIC_DIR = BASE_DIR / "static"
DEFAULT_IMAGE_DIR = STATIC_DIR / "default"
UPLOAD_DIR = STATIC_DIR / "uploads"

# Create directories if they don't exist
DEFAULT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)