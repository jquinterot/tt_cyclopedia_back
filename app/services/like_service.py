from typing import TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


def toggle_like(
    db: Session,
    entity_id: str,
    user_id: str,
    entity_model: type[T],
    like_model: type,
    entity_id_column: str,
    user_id_column: str,
    likes_count_column: str = "likes",
) -> tuple[T, bool, int]:
    """Generic toggle like service.
    Returns: (entity, liked_by_user, updated_likes_count)
    """
    entity = db.query(entity_model).filter(entity_model.id == entity_id).first()
    if not entity:
        raise ValueError("Entity not found")

    existing_like = (
        db.query(like_model)
        .filter(
            getattr(like_model, entity_id_column) == entity_id,
            getattr(like_model, user_id_column) == user_id,
        )
        .first()
    )

    if existing_like:
        db.delete(existing_like)
        current_likes = int(getattr(entity, likes_count_column) or 0)
        if current_likes > 0:
            setattr(entity, likes_count_column, current_likes - 1)
        db.commit()
        liked = False
    else:
        new_like = like_model(**{entity_id_column: entity_id, user_id_column: user_id})
        db.add(new_like)
        current_likes = int(getattr(entity, likes_count_column) or 0)
        setattr(entity, likes_count_column, current_likes + 1)
        db.commit()
        liked = True

    updated_likes_count = int(getattr(entity, likes_count_column) or 0)
    return entity, liked, updated_likes_count
