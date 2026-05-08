import pytest
from unittest.mock import MagicMock
from app.routers.forums.service import (
    get_all_forums,
    get_forum_by_id,
    create_forum,
    update_forum,
    delete_forum,
)
from app.routers.forums.exceptions import ForumNotFound, ForumNotAuthorized


class FakeUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username


class FakeForum:
    def __init__(self, id, title, content, author, likes=0, timestamp=None, updated_timestamp=None):
        self.id = id
        self.title = title
        self.content = content
        self.author = author
        self.likes = likes
        self.timestamp = timestamp or "2024-01-01T00:00:00"
        self.updated_timestamp = updated_timestamp or "2024-01-01T00:00:00"


def test_get_all_forums_empty():
    db = MagicMock()
    db.query.return_value.all.return_value = []
    result = get_all_forums(db, None)
    assert result == []


def test_get_all_forums_returns_list():
    db = MagicMock()
    forum = FakeForum("f1", "Title", "Content", "alice")
    db.query.return_value.all.return_value = [forum]
    db.query.return_value.filter.return_value.all.return_value = []
    result = get_all_forums(db, None)
    assert len(result) == 1
    assert result[0].id == "f1"
    assert result[0].title == "Title"


def test_get_forum_by_id_found():
    db = MagicMock()
    forum = FakeForum("f1", "Title", "Content", "alice")
    db.query.return_value.filter.return_value.first.return_value = forum
    db.query.return_value.filter_by.return_value.first.return_value = None
    result = get_forum_by_id(db, "f1", None)
    assert result.id == "f1"


def test_get_forum_by_id_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ForumNotFound):
        get_forum_by_id(db, "missing", None)


def test_create_forum():
    db = MagicMock()
    user = FakeUser("u1", "alice")
    forum_data = MagicMock()
    forum_data.title = "New Forum"
    forum_data.content = "Some content"
    result = create_forum(db, forum_data, user)
    assert result.title == "New Forum"
    assert result.author == "alice"
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_update_forum_success():
    db = MagicMock()
    forum = FakeForum("f1", "Old", "Content", "alice")
    db.query.return_value.filter.return_value.first.return_value = forum
    db.query.return_value.filter_by.return_value.first.return_value = None
    user = FakeUser("u1", "alice")
    forum_data = MagicMock()
    forum_data.title = "Updated"
    forum_data.content = None
    result = update_forum(db, "f1", forum_data, user)
    assert result.title == "Updated"


def test_update_forum_not_authorized():
    db = MagicMock()
    forum = FakeForum("f1", "Old", "Content", "alice")
    db.query.return_value.filter.return_value.first.return_value = forum
    user = FakeUser("u2", "bob")
    forum_data = MagicMock()
    forum_data.title = "Updated"
    forum_data.content = None
    with pytest.raises(ForumNotAuthorized):
        update_forum(db, "f1", forum_data, user)


def test_delete_forum_success():
    db = MagicMock()
    forum = FakeForum("f1", "Title", "Content", "alice")
    db.query.return_value.filter.return_value.first.return_value = forum
    user = FakeUser("u1", "alice")
    delete_forum(db, "f1", user)
    db.delete.assert_called_once_with(forum)
    db.commit.assert_called_once()


def test_delete_forum_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    user = FakeUser("u1", "alice")
    with pytest.raises(ForumNotFound):
        delete_forum(db, "missing", user)
