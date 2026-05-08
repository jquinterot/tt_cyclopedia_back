"""
Seeder script for TT Cyclopedia.
Run with: python3 seed_database.py
Or import and call seed_all()
"""
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.postgres_config import Base, engine, SessionLocal
# Import ALL models to ensure SQLAlchemy relationship mapping works
from app.routers.users.models import Users
from app.routers.posts.models import Posts, PostLike
from app.routers.forums.models import Forums, ForumLike, ForumComment, ForumCommentLike
from app.routers.comments.models import Comments, CommentLike
from app.routers.equipment.models import Equipment, BladeSpecs, RubberSpecs, EquipmentReview
from app.seeds.equipment_seed import BLADES, RUBBERS, SEED_POSTS, SEED_FORUMS
from datetime import datetime, timezone

def seed_equipment():
    """Seed equipment catalog with blades and rubbers"""
    db = SessionLocal()
    try:
        print("Checking existing equipment...")
        existing = db.query(Equipment).count()
        if existing > 0:
            print(f"Found {existing} equipment items already seeded. Skipping equipment seed.")
            return
        
        print("Seeding blades...")
        for blade_data in BLADES:
            equipment = Equipment(
                id=shortuuid.uuid(),
                name=blade_data["name"],
                brand=blade_data["brand"],
                category="blade",
                subcategory=blade_data.get("subcategory"),
                description=blade_data.get("description"),
                image_url=f"/static/equipment/blades/{blade_data['brand'].lower()}-{blade_data['name'].lower().replace(' ', '-').replace('.', '')}.jpg",
                price_usd=blade_data.get("price_usd"),
                release_year=blade_data.get("release_year"),
            )
            db.add(equipment)
            db.flush()  # Get the ID
            
            specs = blade_data.get("specs", {})
            blade_spec = BladeSpecs(
                id=shortuuid.uuid(),
                equipment_id=equipment.id,
                speed=specs.get("speed"),
                control=specs.get("control"),
                stiffness=specs.get("stiffness"),
                hardness=specs.get("hardness"),
                weight_min=specs.get("weight_min"),
                weight_max=specs.get("weight_max"),
                plies=specs.get("plies"),
                material=specs.get("material"),
                thickness=specs.get("thickness"),
                head_size=specs.get("head_size"),
                handle_types=specs.get("handle_types"),
            )
            db.add(blade_spec)
        
        print("Seeding rubbers...")
        for rubber_data in RUBBERS:
            equipment = Equipment(
                id=shortuuid.uuid(),
                name=rubber_data["name"],
                brand=rubber_data["brand"],
                category="rubber",
                subcategory=rubber_data.get("subcategory"),
                description=rubber_data.get("description"),
                image_url=f"/static/equipment/rubbers/{rubber_data['brand'].lower()}-{rubber_data['name'].lower().replace(' ', '-').replace('.', '')}.jpg",
                price_usd=rubber_data.get("price_usd"),
                release_year=rubber_data.get("release_year"),
            )
            db.add(equipment)
            db.flush()
            
            specs = rubber_data.get("specs", {})
            rubber_spec = RubberSpecs(
                id=shortuuid.uuid(),
                equipment_id=equipment.id,
                speed=specs.get("speed"),
                spin=specs.get("spin"),
                control=specs.get("control"),
                tackiness=specs.get("tackiness"),
                grip=specs.get("grip"),
                sponge_thickness=specs.get("sponge_thickness"),
                sponge_hardness=specs.get("sponge_hardness"),
                top_sheet=specs.get("top_sheet"),
                weight=specs.get("weight"),
                durability=specs.get("durability"),
            )
            db.add(rubber_spec)
        
        db.commit()
        print(f"Seeded {len(BLADES)} blades and {len(RUBBERS)} rubbers successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding equipment: {e}")
        raise
    finally:
        db.close()


def seed_posts_and_forums():
    """Seed initial posts and forums"""
    db = SessionLocal()
    try:
        print("Checking existing posts...")
        existing_posts = db.query(Posts).count()
        if existing_posts > 0:
            print(f"Found {existing_posts} posts already. Skipping post seed.")
        else:
            print("Seeding posts...")
            for post_data in SEED_POSTS:
                post = Posts(
                    id=shortuuid.uuid(),
                    title=post_data["title"],
                    content=post_data["content"],
                    image_url=post_data.get("image_url", "/static/default/default.jpeg"),
                    likes=0,
                    author=post_data["author"],
                    stats=post_data.get("stats"),
                )
                db.add(post)
            db.commit()
            print(f"Seeded {len(SEED_POSTS)} posts successfully!")
        
        print("Checking existing forums...")
        existing_forums = db.query(Forums).count()
        if existing_forums > 0:
            print(f"Found {existing_forums} forums already. Skipping forum seed.")
        else:
            print("Seeding forums...")
            for forum_data in SEED_FORUMS:
                forum = Forums(
                    id=shortuuid.uuid(),
                    title=forum_data["title"],
                    content=forum_data["content"],
                    likes=0,
                    author=forum_data["author"],
                    timestamp=datetime.now(timezone.utc),
                    updated_timestamp=datetime.now(timezone.utc),
                )
                db.add(forum)
            db.commit()
            print(f"Seeded {len(SEED_FORUMS)} forums successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding posts/forums: {e}")
        raise
    finally:
        db.close()


def seed_all():
    """Run all seeders"""
    print("="*60)
    print("TT CYCLOPEDIA DATABASE SEEDER")
    print("="*60)
    
    # Create tables if not exist
    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Tables ready.")
    
    seed_equipment()
    seed_posts_and_forums()
    
    print("="*60)
    print("SEEDING COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    import shortuuid
    seed_all()
