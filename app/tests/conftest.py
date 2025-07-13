import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def auth_headers():
    # Dummy JWT for endpoints that require Authorization header
    return {"Authorization": "Bearer testtoken"}

@pytest.fixture(scope="session")
def test_user():
    # Dummy user object for response structure tests
    class User:
        id = "dummyid"
        username = "dummyuser"
        email = "dummy@example.com"
    return User()

@pytest.fixture(scope="session")
def test_post():
    class Post:
        id = "dummypostid"
        title = "Dummy Post"
        content = "Dummy content"
        author = "dummyuser"
    return Post()

@pytest.fixture(scope="session")
def test_forum():
    class Forum:
        id = "dummyforumid"
        title = "Dummy Forum"
        content = "Dummy forum content"
        author = "dummyuser"
    return Forum()

@pytest.fixture(scope="session")
def test_comment():
    class Comment:
        id = "dummycommentid"
        content = "Test comment"
        post_id = "dummypostid"
        author = "dummyuser"
    return Comment() 