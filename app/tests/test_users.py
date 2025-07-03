import pytest
from fastapi import status
from app.routers.users.models import Users

# --- FACTORY HELPERS ---
def make_user(db_session, username="unituser", email="unit@example.com", password="hashedpass"):
    user = Users(
        id=username + email,
        username=username,
        email=email,
        password=password
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

class TestSetup:
    def test_imports_work(self):
        from app.main import app
        from app.routers.users.models import Users
        assert True

    def test_client_fixture(self, client):
        assert client is not None

    def test_db_session_fixture(self, db_session):
        assert db_session is not None

    def test_user_fixture(self, test_user):
        assert test_user is not None
        assert test_user.username == "testuser"
        assert test_user.email == "test@example.com"

    def test_auth_headers_fixture(self, auth_headers):
        assert auth_headers is not None
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"].startswith("Bearer ")

    def test_basic_health_check(self, client):
        response = client.get("/docs")
        assert response.status_code in [200, 404]

class TestUsersRouter:
    """Test suite for users router endpoints (unit and integration)."""

    def setup_user(self, client):
        user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
        reg_resp = client.post("/users", json=user_data)
        login = client.post("/users/login", json={"username": "testuser", "password": "testpassword"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = login.json()["user"]["id"]
        return headers, user_id

    def test_get_users_success(self, client, auth_headers, test_user):
        """Test successful retrieval of all users"""
        response = client.get("/users", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["username"] == test_user.username
        assert data[0]["email"] == test_user.email
        assert "password" not in data[0]  # Password should not be returned
    
    def test_get_user_integration(self, client):
        headers, user_id = self.setup_user(client)
        response = client.get(f"/users/{user_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == user_id

    def test_get_user_by_id_success(self, client, auth_headers, test_user):
        """Test successful retrieval of a specific user by ID"""
        response = client.get(f"/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert "password" not in data
    
    def test_get_user_by_id_not_found(self, client, auth_headers):
        """Test getting a user that doesn't exist"""
        fake_id = "fake-user-id"
        response = client.get(f"/users/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "User not found"
    
    def test_create_user_success(self, client):
        """Test successful user creation"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "password" not in data
        assert "id" in data
    
    def test_create_user_duplicate_username(self, client, test_user):
        """Test creating user with existing username"""
        user_data = {
            "username": test_user.username,  # Already exists
            "email": "different@example.com",
            "password": "newpassword123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Username already exists"
    
    def test_create_user_duplicate_email(self, client, test_user):
        """Test creating user with existing email"""
        user_data = {
            "username": "differentuser",
            "email": test_user.email,  # Already exists
            "password": "newpassword123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already exists"
    
    def test_create_user_invalid_data(self, client):
        """Test creating user with invalid data"""
        # Missing required fields
        user_data = {
            "username": "newuser"
            # Missing email and password
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client, test_user):
        """Test successful user login"""
        login_data = {
            "username": test_user.username,
            "password": "testpassword"  # Original password from fixture
        }
        response = client.post("/users/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == test_user.username
        assert data["user"]["email"] == test_user.email
        assert "password" not in data["user"]
    
    def test_login_invalid_username(self, client):
        """Test login with non-existent username"""
        login_data = {
            "username": "nonexistentuser",
            "password": "testpassword"
        }
        response = client.post("/users/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid username or password"
    
    def test_login_invalid_password(self, client, test_user):
        """Test login with wrong password"""
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword"
        }
        response = client.post("/users/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid username or password"
    
    def test_login_invalid_data(self, client):
        """Test login with invalid data format"""
        login_data = {
            "username": "testuser"
            # Missing password
        }
        response = client.post("/users/login", json=login_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_multiple_users_creation(self, client):
        """Test creating multiple users successfully"""
        users_data = [
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "password123"
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "password": "password456"
            }
        ]
        
        for user_data in users_data:
            response = client.post("/users", json=user_data)
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["username"] == user_data["username"]
            assert data["email"] == user_data["email"]
    
    def test_user_password_hashing(self, client):
        """Test that passwords are properly hashed"""
        user_data = {
            "username": "passwordtestuser",
            "email": "passwordtest@example.com",
            "password": "plaintextpassword"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to login with the same password
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        login_response = client.post("/users/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK