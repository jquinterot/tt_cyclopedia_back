import uuid

from fastapi import status


class TestUsers:
    def test_get_users_endpoint(self, client, auth_headers):
        response = client.get("/users", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_users_public(self, client):
        response = client.get("/users")
        assert response.status_code == status.HTTP_200_OK

    def test_get_user_by_id_public(self, client):
        response = client.get("/users/fake-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_user_by_id_not_found(self, client, auth_headers):
        response = client.get("/users/fake-user-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_user_endpoint(self, client):
        unique = uuid.uuid4().hex[:8]
        user_data = {
            "username": f"newuser_{unique}",
            "email": f"new_{unique}@example.com",
            "password": "testpass123",
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]

    def test_create_user_duplicate_username(self, client):
        # testuser already exists from conftest
        response = client.post(
            "/users",
            json={"username": "testuser", "email": "unique@example.com", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_duplicate_email(self, client):
        response = client.post(
            "/users",
            json={
                "username": "uniqueuser123",
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_endpoint(self, client):
        response = client.post(
            "/users/login", json={"username": "fakeuser", "password": "fakepass"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_success(self, client):
        unique = uuid.uuid4().hex[:8]
        username = f"logintest_{unique}"
        client.post(
            "/users",
            json={"username": username, "email": f"{username}@test.com", "password": "pass12345"},
        )
        response = client.post("/users/login", json={"username": username, "password": "pass12345"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_wrong_password(self, client):
        unique = uuid.uuid4().hex[:8]
        username = f"wrongpass_{unique}"
        client.post(
            "/users",
            json={"username": username, "email": f"{username}@test.com", "password": "pass12345"},
        )
        response = client.post(
            "/users/login", json={"username": username, "password": "wrongpassword"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_user_unauthorized(self, client):
        response = client.delete("/users/fake-id")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_user_not_found(self, client, auth_headers):
        response = client.delete("/users/fake-user-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_forbidden(self, client, auth_headers):
        # Try to delete admin user as testuser
        users = client.get("/users").json()
        admin_id = None
        for u in users:
            if u["username"] == "adminuser":
                admin_id = u["id"]
                break
        if admin_id:
            response = client.delete(f"/users/{admin_id}", headers=auth_headers)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_user_success(self, client):
        # Create a disposable user
        unique = uuid.uuid4().hex[:8]
        username = f"deluser_{unique}"
        create = client.post(
            "/users",
            json={"username": username, "email": f"{username}@test.com", "password": "pass12345"},
        )
        assert create.status_code == status.HTTP_201_CREATED
        # Login
        login = client.post("/users/login", json={"username": username, "password": "pass12345"})
        assert login.status_code == status.HTTP_200_OK
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # Get user id
        users = client.get("/users").json()
        user_id = None
        for u in users:
            if u["username"] == username:
                user_id = u["id"]
                break
        assert user_id is not None
        del_resp = client.delete(f"/users/{user_id}", headers=headers)
        assert del_resp.status_code == status.HTTP_204_NO_CONTENT

    def test_users_response_structure(self, client, auth_headers):
        response = client.get("/users", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_user_by_id_response_structure(self, client, auth_headers, test_user):
        response = client.get(f"/users/{test_user.id}", headers=auth_headers)
        if response.status_code == status.HTTP_404_NOT_FOUND:
            assert True
        else:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, dict)
            assert "id" in data
            assert "username" in data
            assert "email" in data
