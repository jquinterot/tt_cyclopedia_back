from unittest.mock import MagicMock

import pytest

from app.services.like_service import toggle_like


class FakeEntity:
    id = "dummy"
    likes = 0

    def __init__(self, id, likes=0):
        self.id = id
        self.likes = likes


class FakeLikeModel:
    forum_id = "dummy"
    user_id = "dummy"

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def _make_query(result):
    q = MagicMock()
    q.filter.return_value.first.return_value = result
    return q


def test_toggle_like_creates_like():
    db = MagicMock()
    entity = FakeEntity("e1", likes=0)

    def query_side_effect(model):
        if model is FakeEntity:
            return _make_query(entity)
        return _make_query(None)

    db.query.side_effect = query_side_effect

    returned_entity, liked, count = toggle_like(
        db=db,
        entity_id="e1",
        user_id="u1",
        entity_model=FakeEntity,
        like_model=FakeLikeModel,
        entity_id_column="forum_id",
        user_id_column="user_id",
        likes_count_column="likes",
    )

    assert liked is True
    assert count == 1
    assert returned_entity.likes == 1
    db.add.assert_called_once()
    db.commit.assert_called()


def test_toggle_like_deletes_like():
    db = MagicMock()
    entity = FakeEntity("e1", likes=1)
    existing_like = MagicMock()

    def query_side_effect(model):
        if model is FakeEntity:
            return _make_query(entity)
        return _make_query(existing_like)

    db.query.side_effect = query_side_effect

    returned_entity, liked, count = toggle_like(
        db=db,
        entity_id="e1",
        user_id="u1",
        entity_model=FakeEntity,
        like_model=FakeLikeModel,
        entity_id_column="forum_id",
        user_id_column="user_id",
        likes_count_column="likes",
    )

    assert liked is False
    assert count == 0
    assert returned_entity.likes == 0
    db.delete.assert_called_once_with(existing_like)
    db.commit.assert_called()


def test_toggle_like_raises_when_entity_not_found():
    db = MagicMock()
    db.query.return_value = _make_query(None)

    with pytest.raises(ValueError, match="Entity not found"):
        toggle_like(
            db=db,
            entity_id="e1",
            user_id="u1",
            entity_model=FakeEntity,
            like_model=FakeLikeModel,
            entity_id_column="forum_id",
            user_id_column="user_id",
        )
