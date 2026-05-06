import sys
sys.path.insert(0, '/Users/johany/Documents/projects/python/fastapi/tt_cyclopedia_back')

# Import ALL models first to resolve relationships
from app.routers.users.models import Users
from app.routers.posts.models import Posts, PostLike
from app.routers.forums.models import Forums, ForumLike, ForumComment, ForumCommentLike
from app.routers.comments.models import Comments, CommentLike
from app.routers.equipment.models import Equipment, BladeSpecs, RubberSpecs

from app.config.postgres_config import SessionLocal
from app.routers.equipment.seed_data import SEED_POSTS
import shortuuid

db = SessionLocal()

# Delete post likes first, then posts
db.query(PostLike).delete()
db.query(Posts).delete()
db.commit()

# Get some equipment IDs
equipment = db.query(Equipment).all()
blades = [e for e in equipment if e.category == 'blade']

# Seed posts with equipment links
for i, post_data in enumerate(SEED_POSTS):
    post = Posts(
        id=shortuuid.uuid(),
        title=post_data['title'],
        content=post_data['content'],
        image_url=post_data.get('image_url', '/static/default/default.jpeg'),
        likes=0,
        author=post_data['author'],
        stats=post_data.get('stats'),
        equipment_id=blades[i % len(blades)].id if blades else None,
    )
    db.add(post)

db.commit()
print(f'Created {len(SEED_POSTS)} posts linked to equipment')

# Verify
posts = db.query(Posts).all()
for p in posts:
    eq_name = p.equipment.name if p.equipment else 'None'
    print(f"  - {p.title[:50]}... -> Equipment: {eq_name}")

db.close()
