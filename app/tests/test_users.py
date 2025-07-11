import pytest
from app.tests.conftest import Users
from fastapi import status

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
        from app.tests.conftest import Users
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



class TestUsersRouter:
    """Test suite for users router endpoints."""

    def test_get_users_success(self, client, auth_headers, test_user):
        """Test successful retrieval of all users"""
        response = client.get("/users", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == test_user.id
        assert data[0]["username"] == test_user.username
        assert data[0]["email"] == test_user.email
        assert "password" not in data[0]  # Password should not be returned

    def test_get_user_by_id_success(self, client, auth_headers, test_user):
        """Test successful retrieval of a specific user by ID"""
        response = client.get(f"/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert "password" not in data  # Password should not be returned

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
        assert "password" not in data  # Password should not be returned
        assert "id" in data

    def test_create_user_duplicate_username(self, client, test_user):
        """Test creating user with duplicate username"""
        user_data = {
            "username": test_user.username,  # Same username as test_user
            "email": "different@example.com",
            "password": "password123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Username already exists"

    def test_create_user_duplicate_email(self, client, test_user):
        """Test creating user with duplicate email"""
        user_data = {
            "username": "differentuser",
            "email": test_user.email,  # Same email as test_user
            "password": "password123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already exists"

    def test_login_success(self, client, test_user):
        """Test successful user login"""
        login_data = {
            "username": test_user.username,
            "password": "testpassword"
        }
        response = client.post("/users/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == test_user.username
        assert data["user"]["email"] == test_user.email

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistentuser",
            "password": "wrongpassword"
        }
        response = client.post("/users/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid username or password"

    def test_delete_user_success(self, client, auth_headers, test_user):
        """Test successful user deletion by owner"""
        response = client.delete(f"/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify user is deleted
        get_response = client.get(f"/users/{test_user.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_not_found(self, client, auth_headers):
        """Test deleting a user that doesn't exist"""
        fake_id = "fake-user-id"
        response = client.delete(f"/users/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "User not found"

    def test_delete_user_not_owner(self, client, auth_headers, test_user2):
        """Test deleting a user by someone who doesn't own it"""
        response = client.delete(f"/users/{test_user2.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Not authorized to delete this user"

    def test_delete_user_unauthorized(self, client, test_user):
        """Test deleting user without authentication"""
        response = client.delete(f"/users/{test_user.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # --- SIMPLE TESTS ---
    def test_users_endpoint_simple(self, client, auth_headers, test_user):
        response = client.get("/users", headers=auth_headers)
        assert response.status_code == 200

    def test_users_list_simple(self, client, auth_headers):
        response = client.get("/users", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)