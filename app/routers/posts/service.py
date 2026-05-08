import json
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timezone
import shortuuid

from .models import Posts, PostLike
from .schemas import PostResponse, PostLikeResponse
from .exceptions import PostNotFound, PostNotAuthorized, PostInvalidStats, PostEquipmentNotFound, PostCreationFailed, PostDeleteFailed
from app.routers.equipment.models import Equipment
from app.services.like_service import toggle_like


def _build_post_response(post: Posts, db: Session, liked: bool) -> PostResponse:
    equipment = None
    if post.equipment:
        equipment = {
            "id": str(post.equipment.id),
            "name": str(post.equipment.name),
            "brand": str(post.equipment.brand),
            "category": str(post.equipment.category),
        }
    likes_count = db.query(PostLike).filter_by(post_id=post.id).count()
    return PostResponse.from_orm(post, liked_by_current_user=liked, equipment=equipment, likes_count=likes_count)


def get_posts(db: Session, search: Optional[str], equipment_id: Optional[str], current_user) -> List[PostResponse]:
    query = db.query(Posts).options(selectinload(Posts.equipment))
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Posts.title.ilike(search_term),
                Posts.content.ilike(search_term),
                Posts.author.ilike(search_term),
            )
        )
    if equipment_id:
        query = query.filter(Posts.equipment_id == equipment_id)
    posts = query.all()
    if not posts:
        return []

    post_ids = [post.id for post in posts]
    user_id = current_user.id if current_user else None

    like_counts = {
        row.post_id: row.count
        for row in db.query(
            PostLike.post_id, func.count(PostLike.id).label("count")
        ).filter(PostLike.post_id.in_(post_ids)).group_by(PostLike.post_id).all()
    }

    liked_post_ids = set()
    if user_id:
        liked_post_ids = {
            row.post_id
            for row in db.query(PostLike.post_id)
            .filter(PostLike.post_id.in_(post_ids), PostLike.user_id == user_id)
            .all()
        }

    result = []
    for post in posts:
        liked = post.id in liked_post_ids
        equipment = None
        if post.equipment:
            equipment = {
                "id": str(post.equipment.id),
                "name": str(post.equipment.name),
                "brand": str(post.equipment.brand),
                "category": str(post.equipment.category),
            }
        result.append(PostResponse.from_orm(
            post,
            liked_by_current_user=liked,
            equipment=equipment,
            likes_count=like_counts.get(post.id, 0),
        ))
    return result


def get_post_by_id(db: Session, post_id: str, current_user) -> PostResponse:
    post = db.query(Posts).options(selectinload(Posts.equipment)).filter(Posts.id == post_id).first()
    if not post:
        raise PostNotFound()
    liked = False
    if current_user:
        liked = (
            db.query(PostLike)
            .filter_by(post_id=post.id, user_id=current_user.id)
            .first()
            is not None
        )
    return _build_post_response(post, db, liked)


def create_post(
    db: Session,
    title: str,
    content: str,
    image_url: str,
    stats_str: Optional[str],
    equipment_id: Optional[str],
    current_user,
) -> PostResponse:
    stats_dict = None
    if stats_str:
        try:
            stats_dict = json.loads(stats_str)
        except Exception:
            raise PostInvalidStats()

    if equipment_id:
        equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
        if not equipment:
            raise PostEquipmentNotFound()

    new_post = Posts(
        title=title,
        content=content,
        image_url=image_url,
        likes=0,
        author=current_user.username,
        stats=stats_dict,
        equipment_id=equipment_id,
    )

    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        if new_post.equipment_id:
            db.refresh(new_post, ["equipment"])
        return _build_post_response(new_post, db, False)
    except IntegrityError:
        db.rollback()
        raise PostCreationFailed()
    except Exception:
        db.rollback()
        raise PostCreationFailed()


def delete_all_posts(db: Session, current_admin) -> None:
    try:
        posts = db.query(Posts).all()
        for post in posts:
            if not _is_default_image(getattr(post, "image_url", "")):
                from app.config.cloudinary_config import delete_image_from_cloudinary
                delete_image_from_cloudinary(post.image_url)
        db.query(Posts).delete()
        db.commit()
    except Exception:
        db.rollback()
        raise PostDeleteFailed()


def _is_default_image(image_url: str) -> bool:
    return image_url.startswith("/static/default/")


def delete_post(db: Session, post_id: str, current_user) -> None:
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise PostNotFound()
    if str(post.author) != str(current_user.username):
        raise PostNotAuthorized()
    db.delete(post)
    db.commit()


def toggle_like_post(db: Session, post_id: str, current_user) -> PostResponse:
    try:
        post, liked, updated_likes_count = toggle_like(
            db=db,
            entity_id=post_id,
            user_id=current_user.id,
            entity_model=Posts,
            like_model=PostLike,
            entity_id_column="post_id",
            user_id_column="user_id",
            likes_count_column="likes",
        )
    except ValueError:
        raise PostNotFound()
    return _build_post_response(post, db, liked)


def get_post_likes(db: Session, post_id: str) -> List[PostLikeResponse]:
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise PostNotFound()
    likes = db.query(PostLike).filter_by(post_id=post_id).all()
    return [
        {"user_id": like.user_id, "created_at": like.created_at} for like in likes
    ]
