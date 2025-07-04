"""
Best Practice: Always use the db_session provided by the client fixture for all test setup and app requests. This ensures the same session is used, preventing foreign key and visibility issues in tests.
"""
import os
os.environ["SQL_DB"] = os.getenv("TEST_SQL_DB", "sqlite:///:memory:")
os.environ["JWT_SECRET_KEY"] = "testsecret"
os.environ["ALGORITHM"] = "HS256"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.main import app
from app.config.postgres_config import get_db, SessionLocal, Base, engine
from app.auth.jwt_handler import jwt_handler
from passlib.context import CryptContext
import shortuuid
import app.auth.dependencies as auth_deps

# Test database configuration - use in-memory SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test-specific base and engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestBase = declarative_base()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables for testing
Base.metadata.create_all(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Import models after setting up test environment
from app.routers.users.models import Users
from app.routers.posts.models import Posts, PostLike
from app.routers.comments.models import Comments, CommentLike
from app.routers.forums.models import Forums, ForumLike, ForumComment, ForumCommentLike

@pytest.fixture(scope="function")
def db_session():
    """Yield a session and clean up all tables after each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Truncate all tables to ensure isolation
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override, always using the same db_session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user2(db_session):
    """Create a second test user using the shared db_session."""
    user = Users(
        id=shortuuid.uuid(),
        username="testuser2",
        email="test2@example.com",
        password=hash_password("testpassword")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for the test user"""
    token = jwt_handler.create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_user2(test_user2):
    """Create authentication headers for the second test user"""
    token = jwt_handler.create_access_token(data={"sub": test_user2.username})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_forum(db_session, test_user):
    """Create a test forum using the shared db_session."""
    forum = Forums(
        id=shortuuid.uuid(),
        title="Test Forum",
        content="Test forum content",
        author=test_user.username,
        likes=0
    )
    db_session.add(forum)
    db_session.commit()
    db_session.refresh(forum)
    return forum

@pytest.fixture
def test_comment(db_session, test_user, test_post):
    """Create a test comment using the shared db_session."""
    comment = Comments(
        id=shortuuid.uuid(),
        comment="Test comment",
        post_id=test_post.id,
        user_id=test_user.id,
        username=test_user.username,
        likes=0
    )
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)
    return comment

@pytest.fixture
def test_forum_comment(db_session, test_user, test_forum):
    """Create a test forum comment using the shared db_session."""
    comment = ForumComment(
        id=shortuuid.uuid(),
        comment="Test forum comment",
        forum_id=test_forum.id,
        user_id=test_user.id,
        username=test_user.username,
        likes=0
    )
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)
    return comment

@pytest.fixture(scope="function")
def override_current_user(test_user):
    """
    Override the get_current_user dependency to always return the test user.
    Use this fixture in tests that want to skip JWT validation and focus on endpoint logic.
    """
    def _override():
        return test_user
    app.dependency_overrides[auth_deps.get_current_user] = _override
    yield test_user
    app.dependency_overrides.pop(auth_deps.get_current_user, None)

@pytest.fixture
def test_user(db_session):
    """Create a test user using the shared db_session with a deterministic ID."""
    user = Users(
        id="test-user-id-123",
        username="testuser",
        email="test@example.com",
        password=hash_password("testpassword")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_post(db_session, test_user):
    """Create a test post using the shared db_session with a deterministic ID."""
    post = Posts(
        id="test-post-id-123",
        title="Test Post",
        content="Test content",
        author=test_user.username,
        image_url="/static/default/default.jpeg",
        likes=0
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post 