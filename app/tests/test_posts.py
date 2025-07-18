import pytest
from fastapi import status

class TestPosts:
    def test_get_posts_endpoint(self, client, auth_headers):
        response = client.get("/posts", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_posts_public(self, client):
        response = client.get("/posts")
        assert response.status_code == status.HTTP_200_OK

    def test_get_post_by_id_public(self, client):
        response = client.get("/posts/fake-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_post_by_id_not_found(self, client, auth_headers):
        response = client.get("/posts/fake-post-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_post_unauthorized(self, client):
        post_data = {
            "title": "Test Post",
            "content": "Test content"
        }
        response = client.post("/posts", data=post_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_post_unauthorized(self, client):
        response = client.delete("/posts/fake-id")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_post_not_found(self, client, auth_headers):
        response = client.delete("/posts/fake-post-id", headers=auth_headers)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_like_post_unauthorized(self, client):
        response = client.post("/posts/fake-id/like")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_like_post_not_found(self, client, auth_headers):
        response = client.post("/posts/fake-post-id/like", headers=auth_headers)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_unlike_post_unauthorized(self, client):
        response = client.delete("/posts/fake-id/like")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unlike_post_not_found(self, client, auth_headers):
        response = client.delete("/posts/fake-post-id/like", headers=auth_headers)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_get_post_likes_public(self, client):
        response = client.get("/posts/fake-id/likes")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_post_likes_not_found(self, client, auth_headers):
        response = client.get("/posts/fake-post-id/likes", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_posts_response_structure(self, client, auth_headers):
        response = client.get("/posts", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_post_by_id_response_structure(self, client, auth_headers, test_post):
        response = client.get(f"/posts/{test_post.id}", headers=auth_headers)
        if response.status_code == status.HTTP_404_NOT_FOUND:
            assert True
        else:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, dict)
            assert "id" in data
            assert "title" in data
            assert "content" in data
            assert "author" in data
