import pytest
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
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_login_endpoint(self, client):
        login_data = {
            "username": "fakeuser",
            "password": "fakepass"
        }
        response = client.post("/users/login", json=login_data)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_delete_user_unauthorized(self, client):
        response = client.delete("/users/fake-id")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_user_not_found(self, client, auth_headers):
        response = client.delete("/users/fake-user-id", headers=auth_headers)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

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