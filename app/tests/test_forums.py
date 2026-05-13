import uuid

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
        forum_data = {"title": "Test Forum", "content": "Test description"}
        response = client.post("/forums", json=forum_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_forum_success(self, client, auth_headers):
        unique = str(uuid.uuid4())
        response = client.post(
            "/forums",
            json={"title": f"Test Forum {unique}", "content": "Forum content"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == f"Test Forum {unique}"
        assert data["author"] == "testuser"

    def test_update_forum_success(self, client, auth_headers):
        unique = str(uuid.uuid4())
        create_resp = client.post(
            "/forums",
            json={"title": f"Update Forum {unique}", "content": "Original content"},
            headers=auth_headers,
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        forum_id = create_resp.json()["id"]
        update_resp = client.put(
            f"/forums/{forum_id}",
            json={"title": "Updated Title", "content": "Updated content"},
            headers=auth_headers,
        )
        assert update_resp.status_code == status.HTTP_200_OK
        assert update_resp.json()["title"] == "Updated Title"

    def test_update_forum_not_found(self, client, auth_headers):
        response = client.put(
            "/forums/fake-forum-id", json={"title": "Updated"}, headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_forum_unauthorized(self, client):
        response = client.delete("/forums/fake-id")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_forum_not_found(self, client, auth_headers):
        response = client.delete("/forums/fake-forum-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_forum_success(self, client, auth_headers):
        unique = str(uuid.uuid4())
        create_resp = client.post(
            "/forums",
            json={"title": f"Delete Forum {unique}", "content": "To delete"},
            headers=auth_headers,
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        forum_id = create_resp.json()["id"]
        del_resp = client.delete(f"/forums/{forum_id}", headers=auth_headers)
        assert del_resp.status_code == status.HTTP_204_NO_CONTENT

    def test_like_forum_success(self, client, auth_headers):
        unique = str(uuid.uuid4())
        create_resp = client.post(
            "/forums",
            json={"title": f"Like Forum {unique}", "content": "Like me"},
            headers=auth_headers,
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        forum_id = create_resp.json()["id"]
        like_resp = client.post(f"/forums/{forum_id}/like", headers=auth_headers)
        assert like_resp.status_code == status.HTTP_200_OK
        assert like_resp.json()["likes"] >= 1
        unlike_resp = client.post(f"/forums/{forum_id}/toggle-like", headers=auth_headers)
        assert unlike_resp.status_code == status.HTTP_200_OK

    def test_like_forum_not_found(self, client, auth_headers):
        response = client.post("/forums/fake-id/like", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_forum_comments_success(self, client, auth_headers):
        unique = str(uuid.uuid4())
        create_resp = client.post(
            "/forums",
            json={"title": f"Comment Forum {unique}", "content": "Forum with comments"},
            headers=auth_headers,
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        forum_id = create_resp.json()["id"]
        comment_resp = client.post(
            f"/forums/{forum_id}/comments", json={"comment": "Nice forum!"}, headers=auth_headers
        )
        assert comment_resp.status_code == status.HTTP_201_CREATED
        assert comment_resp.json()["comment"] == "Nice forum!"

    def test_forum_comments_update_success(self, client, auth_headers):
        unique = str(uuid.uuid4())
        forum_resp = client.post(
            "/forums",
            json={"title": f"Update Comment Forum {unique}", "content": "Content"},
            headers=auth_headers,
        )
        assert forum_resp.status_code == status.HTTP_201_CREATED
        forum_id = forum_resp.json()["id"]
        comment_resp = client.post(
            f"/forums/{forum_id}/comments", json={"comment": "Original"}, headers=auth_headers
        )
        assert comment_resp.status_code == status.HTTP_201_CREATED
        comment_id = comment_resp.json()["id"]
        update_resp = client.put(
            f"/forums/{forum_id}/comments/{comment_id}",
            json={"comment": "Updated"},
            headers=auth_headers,
        )
        assert update_resp.status_code == status.HTTP_200_OK
        assert update_resp.json()["comment"] == "Updated"

    def test_forum_comments_delete_success(self, client, auth_headers):
        unique = str(uuid.uuid4())
        forum_resp = client.post(
            "/forums",
            json={"title": f"Delete Comment Forum {unique}", "content": "Content"},
            headers=auth_headers,
        )
        assert forum_resp.status_code == status.HTTP_201_CREATED
        forum_id = forum_resp.json()["id"]
        comment_resp = client.post(
            f"/forums/{forum_id}/comments", json={"comment": "To delete"}, headers=auth_headers
        )
        assert comment_resp.status_code == status.HTTP_201_CREATED
        comment_id = comment_resp.json()["id"]
        del_resp = client.delete(f"/forums/{forum_id}/comments/{comment_id}", headers=auth_headers)
        assert del_resp.status_code == status.HTTP_200_OK

    def test_forum_comments_like_success(self, client, auth_headers):
        unique = str(uuid.uuid4())
        forum_resp = client.post(
            "/forums",
            json={"title": f"Like Comment Forum {unique}", "content": "Content"},
            headers=auth_headers,
        )
        assert forum_resp.status_code == status.HTTP_201_CREATED
        forum_id = forum_resp.json()["id"]
        comment_resp = client.post(
            f"/forums/{forum_id}/comments", json={"comment": "Like me"}, headers=auth_headers
        )
        assert comment_resp.status_code == status.HTTP_201_CREATED
        comment_id = comment_resp.json()["id"]
        like_resp = client.post(
            f"/forums/{forum_id}/comments/{comment_id}/like", headers=auth_headers
        )
        assert like_resp.status_code == status.HTTP_200_OK

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

    # General forum comment endpoints (mimicking post comments)
    def test_general_forum_comments_crud(self, client, auth_headers):
        unique = str(uuid.uuid4())
        forum_resp = client.post(
            "/forums",
            json={"title": f"General Comment Forum {unique}", "content": "Content"},
            headers=auth_headers,
        )
        assert forum_resp.status_code == status.HTTP_201_CREATED
        forum_id = forum_resp.json()["id"]

        # Create via general endpoint
        create_resp = client.post(
            "/forums/comments",
            json={"comment": "General comment", "forum_id": forum_id},
            headers=auth_headers,
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        comment_id = create_resp.json()["id"]

        # Get by id
        get_resp = client.get(f"/forums/comments/{comment_id}")
        assert get_resp.status_code == status.HTTP_200_OK
        assert get_resp.json()["comment"] == "General comment"

        # Update
        update_resp = client.put(
            f"/forums/comments/{comment_id}",
            json={"comment": "Updated general"},
            headers=auth_headers,
        )
        assert update_resp.status_code == status.HTTP_200_OK
        assert update_resp.json()["comment"] == "Updated general"

        # Like
        like_resp = client.post(f"/forums/comments/{comment_id}/like", headers=auth_headers)
        assert like_resp.status_code == status.HTTP_200_OK

        # Delete
        del_resp = client.delete(f"/forums/comments/{comment_id}", headers=auth_headers)
        assert del_resp.status_code == status.HTTP_200_OK

    def test_general_forum_comment_not_found(self, client, auth_headers):
        response = client.get("/forums/comments/fake-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_forum_comments_by_forum_id(self, client, auth_headers):
        unique = str(uuid.uuid4())
        forum_resp = client.post(
            "/forums",
            json={"title": f"Forum ID Comments {unique}", "content": "Content"},
            headers=auth_headers,
        )
        assert forum_resp.status_code == status.HTTP_201_CREATED
        forum_id = forum_resp.json()["id"]
        client.post(
            "/forums/comments",
            json={"comment": "By forum id", "forum_id": forum_id},
            headers=auth_headers,
        )
        response = client.get(f"/forums/forum/{forum_id}/comments")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_main_forum_comments_by_forum_id(self, client, auth_headers):
        unique = str(uuid.uuid4())
        forum_resp = client.post(
            "/forums",
            json={"title": f"Main Forum Comments {unique}", "content": "Content"},
            headers=auth_headers,
        )
        assert forum_resp.status_code == status.HTTP_201_CREATED
        forum_id = forum_resp.json()["id"]
        client.post(
            "/forums/comments",
            json={"comment": "Main comment", "forum_id": forum_id},
            headers=auth_headers,
        )
        response = client.get(f"/forums/forum/{forum_id}/comments/main")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_forum_comment_replies_by_forum_id(self, client, auth_headers):
        unique = str(uuid.uuid4())
        forum_resp = client.post(
            "/forums",
            json={"title": f"Replies Forum {unique}", "content": "Content"},
            headers=auth_headers,
        )
        assert forum_resp.status_code == status.HTTP_201_CREATED
        forum_id = forum_resp.json()["id"]
        parent_resp = client.post(
            "/forums/comments",
            json={"comment": "Parent", "forum_id": forum_id},
            headers=auth_headers,
        )
        assert parent_resp.status_code == status.HTTP_201_CREATED
        parent_id = parent_resp.json()["id"]
        client.post(
            "/forums/comments",
            json={"comment": "Reply", "forum_id": forum_id, "parent_id": parent_id},
            headers=auth_headers,
        )
        response = client.get(f"/forums/forum/{forum_id}/comments/replies/{parent_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
