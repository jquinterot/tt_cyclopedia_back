from fastapi import status


class TestLogs:
    def test_get_logs_unauthorized(self, client):
        response = client.get("/logs/")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_get_logs_as_admin(self, client, admin_auth_headers):
        response = client.get("/logs/", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_logs_with_filters(self, client, admin_auth_headers):
        response = client.get("/logs/?limit=5&method=GET", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_logs_forbidden_as_user(self, client, auth_headers):
        response = client.get("/logs/", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
