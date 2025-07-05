# Set environment variables BEFORE any imports
import os
if os.path.exists("test.db"):
    os.remove("test.db")
os.environ["TEST_SQL_DB"] = "sqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "testsecret"
os.environ["ALGORITHM"] = "HS256"

"""
Best Practice: Always use the db_session provided by the client fixture for all test setup and app requests. This ensures the same session is used, preventing foreign key and visibility issues in tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.main import app
from app.config.postgres_config import get_db, SessionLocal, Base
from app.auth.jwt_handler import jwt_handler
from app.auth.dependencies import get_current_user
from passlib.context import CryptContext
import shortuuid
import app.auth.dependencies as auth_deps

# Test database configuration - use in-memory SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test-specific engine using production Base
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
# Create a single connection for all sessions
connection = engine.connect()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)

# Patch BEFORE importing anything else from the app
import app.config.postgres_config as postgres_config
postgres_config.engine = engine
postgres_config.SessionLocal = TestingSessionLocal

# Now import Base and models, then create tables using the single connection
from app.config.postgres_config import Base
from app.routers.users.models import Users
from app.routers.posts.models import Posts, PostLike
from app.routers.comments.models import Comments, CommentLike
from app.routers.forums.models import Forums, ForumLike, ForumComment, ForumCommentLike

Base.metadata.create_all(bind=connection)

# Now import the app and the rest
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.postgres_config import get_db
from app.auth.jwt_handler import jwt_handler
from passlib.context import CryptContext
import shortuuid
import app.auth.dependencies as auth_deps

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@pytest.fixture(scope="session", autouse=True)
def ensure_tables_exist():
    """Ensure all tables are created before any test runs"""
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after all tests
    if os.path.exists("test.db"):
        os.remove("test.db")

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
    
    def override_get_current_user():
        """Override get_current_user to use the test database session"""
        from app.auth.dependencies import get_current_user
        from app.routers.users.models import Users
        from app.auth.jwt_handler import jwt_handler
        from fastapi import HTTPException, status
        from fastapi.security import HTTPBearer
        from fastapi import Depends
        
        security = HTTPBearer()
        
        async def _get_current_user(credentials=Depends(security)):
            try:
                username = jwt_handler.verify_token(credentials.credentials)
                user = db_session.query(Users).filter(Users.username == username).first()
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return user
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        return _get_current_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user()
    
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
    """Override the get_current_user dependency to return the test user."""
    def _override():
        return test_user
    app.dependency_overrides[auth_deps.get_current_user] = _override
    yield
    app.dependency_overrides.pop(auth_deps.get_current_user, None)

@pytest.fixture
def test_user(db_session):
    """Create a test user using the shared db_session."""
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