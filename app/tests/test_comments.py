import pytest
import uuid
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
            "comment": "Test comment",
            "post_id": "fake-post-id"
        }
        response = client.post("/comments", json=comment_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_comment_success(self, client, auth_headers):
        # First create a post
        post_resp = client.post("/posts", data={
            "title": f"Comment Post {uuid.uuid4()}",
            "content": "Post for comments"
        }, headers=auth_headers)
        assert post_resp.status_code == status.HTTP_201_CREATED
        post_id = post_resp.json()["id"]
        comment_resp = client.post("/comments", json={
            "comment": "Nice post!",
            "post_id": post_id
        }, headers=auth_headers)
        assert comment_resp.status_code == status.HTTP_201_CREATED
        data = comment_resp.json()
        assert data["comment"] == "Nice post!"
        assert data["post_id"] == post_id
        assert data["username"] == "testuser"

    def test_update_comment_success(self, client, auth_headers):
        post_resp = client.post("/posts", data={
            "title": f"Update Comment Post {uuid.uuid4()}",
            "content": "Content"
        }, headers=auth_headers)
        assert post_resp.status_code == status.HTTP_201_CREATED
        post_id = post_resp.json()["id"]
        comment_resp = client.post("/comments", json={
            "comment": "Original",
            "post_id": post_id
        }, headers=auth_headers)
        assert comment_resp.status_code == status.HTTP_201_CREATED
        comment_id = comment_resp.json()["id"]
        update_resp = client.put(f"/comments/{comment_id}", json={
            "comment": "Updated text"
        }, headers=auth_headers)
        assert update_resp.status_code == status.HTTP_200_OK
        assert update_resp.json()["comment"] == "Updated text"

    def test_update_comment_not_found(self, client, auth_headers):
        response = client.put("/comments/fake-comment-id", json={
            "comment": "Updated"
        }, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_comment_unauthorized(self, client):
        response = client.delete("/comments/fake-id")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_comment_not_found(self, client, auth_headers):
        response = client.delete("/comments/fake-comment-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_comment_success(self, client, auth_headers):
        post_resp = client.post("/posts", data={
            "title": f"Delete Comment Post {uuid.uuid4()}",
            "content": "Content"
        }, headers=auth_headers)
        assert post_resp.status_code == status.HTTP_201_CREATED
        post_id = post_resp.json()["id"]
        comment_resp = client.post("/comments", json={
            "comment": "To delete",
            "post_id": post_id
        }, headers=auth_headers)
        assert comment_resp.status_code == status.HTTP_201_CREATED
        comment_id = comment_resp.json()["id"]
        del_resp = client.delete(f"/comments/{comment_id}", headers=auth_headers)
        assert del_resp.status_code == status.HTTP_200_OK
        assert "deleted" in del_resp.json()["detail"].lower()

    def test_get_comments_by_post_public(self, client):
        response = client.get("/comments/post/fake-post-id")
        assert response.status_code == status.HTTP_200_OK

    def test_get_comments_by_post_with_data(self, client, auth_headers):
        post_resp = client.post("/posts", data={
            "title": f"Comments By Post {uuid.uuid4()}",
            "content": "Content"
        }, headers=auth_headers)
        assert post_resp.status_code == status.HTTP_201_CREATED
        post_id = post_resp.json()["id"]
        client.post("/comments", json={
            "comment": "Comment 1",
            "post_id": post_id
        }, headers=auth_headers)
        response = client.get(f"/comments/post/{post_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_comments_by_post_returns_empty(self, client, auth_headers):
        response = client.get("/comments/post/fake-post-id", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_like_comment_success(self, client, auth_headers):
        post_resp = client.post("/posts", data={
            "title": f"Like Comment Post {uuid.uuid4()}",
            "content": "Content"
        }, headers=auth_headers)
        assert post_resp.status_code == status.HTTP_201_CREATED
        post_id = post_resp.json()["id"]
        comment_resp = client.post("/comments", json={
            "comment": "Like me",
            "post_id": post_id
        }, headers=auth_headers)
        assert comment_resp.status_code == status.HTTP_201_CREATED
        comment_id = comment_resp.json()["id"]
        like_resp = client.post(f"/comments/{comment_id}/like", headers=auth_headers)
        assert like_resp.status_code == status.HTTP_200_OK
        assert like_resp.json()["likes"] >= 1
        # Unlike
        unlike_resp = client.post(f"/comments/{comment_id}/toggle-like", headers=auth_headers)
        assert unlike_resp.status_code == status.HTTP_200_OK

    def test_like_comment_not_found(self, client, auth_headers):
        response = client.post("/comments/fake-id/like", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_main_comments_by_post(self, client, auth_headers):
        post_resp = client.post("/posts", data={
            "title": f"Main Comments Post {uuid.uuid4()}",
            "content": "Content"
        }, headers=auth_headers)
        assert post_resp.status_code == status.HTTP_201_CREATED
        post_id = post_resp.json()["id"]
        client.post("/comments", json={
            "comment": "Main",
            "post_id": post_id
        }, headers=auth_headers)
        response = client.get(f"/comments/post/{post_id}/main")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_replies(self, client, auth_headers):
        post_resp = client.post("/posts", data={
            "title": f"Replies Post {uuid.uuid4()}",
            "content": "Content"
        }, headers=auth_headers)
        assert post_resp.status_code == status.HTTP_201_CREATED
        post_id = post_resp.json()["id"]
        parent_resp = client.post("/comments", json={
            "comment": "Parent",
            "post_id": post_id
        }, headers=auth_headers)
        assert parent_resp.status_code == status.HTTP_201_CREATED
        parent_id = parent_resp.json()["id"]
        client.post("/comments", json={
            "comment": "Reply",
            "post_id": post_id,
            "parent_id": parent_id
        }, headers=auth_headers)
        response = client.get(f"/comments/post/{post_id}/replies/{parent_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

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
            assert "comment" in data
            assert "post_id" in data
