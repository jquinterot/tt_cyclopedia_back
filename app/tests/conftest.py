# Set environment variables BEFORE any imports
import os
if os.path.exists("test.db"):
    os.remove("test.db")

# Use SQLite in-memory for faster tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
os.environ["SQL_LITE_DB"] = SQLALCHEMY_DATABASE_URL
os.environ["JWT_SECRET_KEY"] = "testsecret"
os.environ["ALGORITHM"] = "HS256"
os.environ["ENVIRONMENT"] = "testing"  # Use testing to avoid Cloudinary imports

"""
Optimized test configuration for speed:
- Uses SQLite in-memory database
- Pre-hashed passwords to avoid bcrypt overhead
- Simplified transaction management
- Cached fixtures where possible
- Testing environment to avoid Cloudinary imports
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.main import app
from app.auth.jwt_handler import jwt_handler
from app.auth.dependencies import get_current_user
from passlib.context import CryptContext
import shortuuid
import app.auth.dependencies as auth_deps
from fastapi import HTTPException, status

# Create fast in-memory SQLite engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # Disable SQL logging for speed
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Patch BEFORE importing anything else from the app
import app.config.postgres_config as postgres_config
postgres_config.engine = engine
postgres_config.SessionLocal = TestingSessionLocal

# Import Base for table creation
from app.config.postgres_config import Base

# Remove schema event listener for SQLite tests
if hasattr(Base.metadata, '_event_dispatch'):
    # Clear any schema-related events
    Base.metadata._event_dispatch.clear()

# Import models - they will use the patched postgres_config
from app.routers.users.models import Users
from app.routers.posts.models import Posts, PostLike
from app.routers.comments.models import Comments, CommentLike
from app.routers.forums.models import Forums, ForumLike, ForumComment, ForumCommentLike

# Now import the app and the rest
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.postgres_config import get_db
from app.auth.jwt_handler import jwt_handler
from passlib.context import CryptContext
import shortuuid
import app.auth.dependencies as auth_deps

# Password hashing - pre-hash common passwords for speed
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pre-hashed passwords to avoid bcrypt overhead in tests
HASHED_TEST_PASSWORD = pwd_context.hash("testpassword")
HASHED_TEST_PASSWORD2 = pwd_context.hash("testpassword2")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@pytest.fixture(scope="session")
def connection():
    """Create a single connection for the whole test session (needed for SQLite in-memory)."""
    conn = engine.connect()
    Base.metadata.create_all(bind=conn)
    yield conn
    conn.close()

@pytest.fixture(scope="function")
def db_session(connection):
    """Use the session-scoped connection for each test, with SAVEPOINT."""
    transaction = connection.begin_nested()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()

@pytest.fixture(scope="function")
def client(db_session):
    """Fast client fixture with minimal overhead. Only override get_current_user if Authorization header is present."""
    from fastapi import Request
    import app.auth.dependencies as auth_deps
    real_get_current_user = auth_deps.get_current_user

    async def override_get_current_user(request: Request, db=None):
        # If Authorization header is present, extract username from token and return corresponding user
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # Decode token to get username
                username = jwt_handler.verify_token(token)
                if username:
                    user = db_session.query(Users).filter(Users.username == username).first()
                    if user:
                        return user
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        # Otherwise, raise 401 Unauthorized
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[auth_deps.get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user using pre-hashed password for speed"""
    # Check if user already exists
    existing_user = db_session.query(Users).filter(Users.username == "testuser").first()
    if existing_user:
        return existing_user
    
    user = Users(
        id=shortuuid.uuid(),
        username="testuser",
        email="test@example.com",
        password=HASHED_TEST_PASSWORD  # Use pre-hashed password
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_user2(db_session):
    """Create a second test user using pre-hashed password for speed"""
    # Check if user already exists
    existing_user = db_session.query(Users).filter(Users.username == "testuser2").first()
    if existing_user:
        return existing_user
    
    user = Users(
        id=shortuuid.uuid(),
        username="testuser2",
        email="test2@example.com",
        password=HASHED_TEST_PASSWORD2  # Use pre-hashed password
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
    """Override the get_current_user dependency to return the test user."""
    def _override():
        return test_user
    app.dependency_overrides[auth_deps.get_current_user] = _override
    yield
    app.dependency_overrides.pop(auth_deps.get_current_user, None)

@pytest.fixture
def test_post(db_session, test_user):
    """Create a test post using the shared db_session."""
    post = Posts(
        id=shortuuid.uuid(),
        title="Test Post",
        content="Test post content",
        image_url="/static/default/default.jpeg",
        likes=0,
        author=test_user.username
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post 