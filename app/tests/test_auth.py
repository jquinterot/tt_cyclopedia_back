from fastapi import status


class TestAuth:
    def test_validate_token(self, client, auth_headers):
        response = client.get("/auth/validate", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True
        assert "user" in data
        assert "username" in data["user"]

    def test_validate_token_unauthorized(self, client):
        response = client.get("/auth/validate")
        assert response.status_code == status.HTTP_403_FORBIDDEN
