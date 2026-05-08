import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.jwt_handler import jwt_handler
from app.config.postgres_config import SessionLocal
from app.routers.users.models import Users
from app.middleware.rate_limiter import auth_rate_limit, write_rate_limit, read_rate_limit

# Disable rate limiting for tests
app.dependency_overrides[auth_rate_limit] = lambda: True
app.dependency_overrides[write_rate_limit] = lambda: True
app.dependency_overrides[read_rate_limit] = lambda: True

TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"

ADMIN_USERNAME = "adminuser"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "adminpass123"


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def ensure_test_users(client):
    """Ensure test users exist in the database for authenticated tests."""
    # Create regular test user
    resp = client.post("/users", json={
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    # Create admin test user
    resp_admin = client.post("/users", json={
        "username": ADMIN_USERNAME,
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    # Promote admin user via direct DB access
    db = SessionLocal()
    try:
        admin = db.query(Users).filter(Users.username == ADMIN_USERNAME).first()
        if admin and not admin.is_admin:
            admin.is_admin = True
            db.commit()
    finally:
        db.close()


@pytest.fixture(scope="session")
def auth_headers(ensure_test_users):
    token = jwt_handler.create_access_token(data={"sub": TEST_USERNAME})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def admin_auth_headers(ensure_test_users):
    token = jwt_handler.create_access_token(data={"sub": ADMIN_USERNAME})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def test_user(ensure_test_users):
    db = SessionLocal()
    try:
        user = db.query(Users).filter(Users.username == TEST_USERNAME).first()
        if user:
            return user
    finally:
        db.close()
    # Fallback dummy if DB query fails
    class User:
        id = "dummyid"
        username = TEST_USERNAME
        email = TEST_EMAIL
    return User()


@pytest.fixture(scope="session")
def test_admin(ensure_test_users):
    db = SessionLocal()
    try:
        user = db.query(Users).filter(Users.username == ADMIN_USERNAME).first()
        if user:
            return user
    finally:
        db.close()
    class User:
        id = "adminid"
        username = ADMIN_USERNAME
        email = ADMIN_EMAIL
        is_admin = True
    return User()


@pytest.fixture(scope="session")
def test_post():
    class Post:
        id = "dummypostid"
        title = "Dummy Post"
        content = "Dummy content"
        author = TEST_USERNAME
    return Post()


@pytest.fixture(scope="session")
def test_forum():
    class Forum:
        id = "dummyforumid"
        title = "Dummy Forum"
        content = "Dummy forum content"
        author = TEST_USERNAME
    return Forum()


@pytest.fixture(scope="session")
def test_comment():
    class Comment:
        id = "dummycommentid"
        content = "Test comment"
        post_id = "dummypostid"
        author = TEST_USERNAME
    return Comment()
