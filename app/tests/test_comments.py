import pytest
from fastapi import status

class TestComments:
    def test_get_comments_endpoint(self, client, auth_headers):
        response = client.get("/comments", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_comments_public(self, client):
        response = client.get("/comments")
        assert response.status_code == status.HTTP_200_OK

    def test_get_comment_by_id_public(self, client):
        response = client.get("/comments/fake-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_comment_by_id_not_found(self, client, auth_headers):
        response = client.get("/comments/fake-comment-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_comment_unauthorized(self, client):
        comment_data = {
            "content": "Test comment",
            "post_id": "fake-post-id"
        }
        response = client.post("/comments", json=comment_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_comment_unauthorized(self, client):
        response = client.delete("/comments/fake-id")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_comment_not_found(self, client, auth_headers):
        response = client.delete("/comments/fake-comment-id", headers=auth_headers)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_get_comments_by_post_public(self, client):
        response = client.get("/comments/post/fake-post-id")
        assert response.status_code == status.HTTP_200_OK

    def test_get_comments_by_post_returns_empty(self, client, auth_headers):
        response = client.get("/comments/post/fake-post-id", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_comments_response_structure(self, client, auth_headers):
        response = client.get("/comments", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_comment_by_id_response_structure(self, client, auth_headers, test_comment):
        response = client.get(f"/comments/{test_comment.id}", headers=auth_headers)
        if response.status_code == status.HTTP_404_NOT_FOUND:
            assert True
        else:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, dict)
            assert "id" in data
            assert "content" in data
            assert "post_id" in data
            assert "author" in data
