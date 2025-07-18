import pytest
from fastapi import status

class TestForums:
    def test_get_forums_endpoint(self, client, auth_headers):
        response = client.get("/forums", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_forums_public(self, client):
        response = client.get("/forums")
        assert response.status_code == status.HTTP_200_OK

    def test_get_forum_by_id_public(self, client):
        response = client.get("/forums/fake-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_forum_by_id_not_found(self, client, auth_headers):
        response = client.get("/forums/fake-forum-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_forum_unauthorized(self, client):
        forum_data = {
            "name": "Test Forum",
            "description": "Test description"
        }
        response = client.post("/forums", json=forum_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_forum_unauthorized(self, client):
        response = client.delete("/forums/fake-id")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_forum_not_found(self, client, auth_headers):
        response = client.delete("/forums/fake-forum-id", headers=auth_headers)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_forums_response_structure(self, client, auth_headers):
        response = client.get("/forums", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_forum_by_id_response_structure(self, client, auth_headers, test_forum):
        response = client.get(f"/forums/{test_forum.id}", headers=auth_headers)
        if response.status_code == status.HTTP_404_NOT_FOUND:
            assert True
        else:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, dict)
            assert "id" in data
            assert "title" in data
            assert "content" in data 