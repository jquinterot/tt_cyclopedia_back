from PIL import Image, ImageDraw, ImageFont
import os


def create_placeholder(path, name, brand, category):
    """Create a placeholder image for equipment"""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Brand colors
    colors = {
        "Butterfly": "#3b82f6",
        "Donic": "#ef4444",
        "DHS": "#dc2626",
        "Nittaku": "#f59e0b",
        "Xiom": "#8b5cf6",
        "Tibhar": "#10b981",
        "Andro": "#06b6d4",
        "Stiga": "#f97316",
    }
    bg_color = colors.get(brand, "#6b7280")

    img = Image.new("RGB", (400, 400), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load a font, fallback to default
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        font_brand = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_brand = ImageFont.load_default()

    # Draw text centered
    draw.text((200, 150), name, fill="white", font=font_large, anchor="mm")
    draw.text((200, 200), brand, fill="white", font=font_brand, anchor="mm")
    draw.text((200, 250), category.upper(), fill="white", font=font_small, anchor="mm")

    img.save(path, "JPEG", quality=85)
    print(f"Created: {path}")


# Create placeholders for all equipment
import sys

sys.path.insert(0, "/Users/johany/Documents/projects/python/fastapi/tt_cyclopedia_back")
from app.seeds.equipment_seed import BLADES, RUBBERS

base_path = "/Users/johany/Documents/projects/python/fastapi/tt_cyclopedia_back/static/equipment"


def safe_slug(name):
    return name.lower().replace(" ", "-").replace(".", "").replace("/", "-").replace("+", "-plus")


print("Creating blade images...")
for blade in BLADES:
    slug = f"{blade['brand'].lower()}-{safe_slug(blade['name'])}.jpg"
    path = os.path.join(base_path, "blades", slug)
    create_placeholder(path, blade["name"], blade["brand"], "Blade")

print("Creating rubber images...")
for rubber in RUBBERS:
    slug = f"{rubber['brand'].lower()}-{safe_slug(rubber['name'])}.jpg"
    path = os.path.join(base_path, "rubbers", slug)
    create_placeholder(path, rubber["name"], rubber["brand"], "Rubber")

print("Done! Created all placeholder images.")
