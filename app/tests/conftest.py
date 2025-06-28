import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.main import app
from app.config.postgres_config import get_db
from app.auth.jwt_handler import jwt_handler
from passlib.context import CryptContext
import shortuuid
import os

# Set environment variable for SQLite testing
os.environ["SQL_DB"] = "sqlite:///:memory:"

# Test database configuration - use in-memory SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test-specific base and engine
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestBase = declarative_base()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

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
    """Create a fresh database session for each test"""
    # Create tables
    Users.__table__.create(bind=test_engine, checkfirst=True)
    Posts.__table__.create(bind=test_engine, checkfirst=True)
    PostLike.__table__.create(bind=test_engine, checkfirst=True)
    Comments.__table__.create(bind=test_engine, checkfirst=True)
    CommentLike.__table__.create(bind=test_engine, checkfirst=True)
    Forums.__table__.create(bind=test_engine, checkfirst=True)
    ForumLike.__table__.create(bind=test_engine, checkfirst=True)
    ForumComment.__table__.create(bind=test_engine, checkfirst=True)
    ForumCommentLike.__table__.create(bind=test_engine, checkfirst=True)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up tables
        Users.__table__.drop(bind=test_engine, checkfirst=True)
        Posts.__table__.drop(bind=test_engine, checkfirst=True)
        PostLike.__table__.drop(bind=test_engine, checkfirst=True)
        Comments.__table__.drop(bind=test_engine, checkfirst=True)
        CommentLike.__table__.drop(bind=test_engine, checkfirst=True)
        Forums.__table__.drop(bind=test_engine, checkfirst=True)
        ForumLike.__table__.drop(bind=test_engine, checkfirst=True)
        ForumComment.__table__.drop(bind=test_engine, checkfirst=True)
        ForumCommentLike.__table__.drop(bind=test_engine, checkfirst=True)

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override"""
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
def test_user(db_session):
    """Create a test user"""
    user = Users(
        id=shortuuid.uuid(),
        username="testuser",
        email="test@example.com",
        password=hash_password("testpassword")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_user2(db_session):
    """Create a second test user"""
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
def test_post(db_session, test_user):
    """Create a test post"""
    post = Posts(
        id=shortuuid.uuid(),
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

@pytest.fixture
def test_forum(db_session, test_user):
    """Create a test forum"""
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
    """Create a test comment"""
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
    """Create a test forum comment"""
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