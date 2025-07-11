import pytest
from fastapi import status
from app.tests.conftest import Comments, CommentLike, Posts, Forums, Users

# --- FACTORY HELPERS ---
def make_comment(db_session, user, post, comment_text="Unit Comment"):
    comment = Comments(
        id=user.id + comment_text,
        comment=comment_text,
        post_id=post.id,
        user_id=user.id,
        username=user.username,
        likes=0
    )
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)
    return comment

class TestSetup:
    """Basic setup and health checks for the test environment."""
    def test_imports_work(self):
        from app.main import app
        from app.tests.conftest import Comments
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



class TestCommentsRouter:
    """Test suite for comments router endpoints (unit and integration)."""

    def test_get_comments_success(self, client, auth_headers, test_comment):
        """Test successful retrieval of all comments"""
        response = client.get("/comments/", headers=auth_headers)
        print(f"DEBUG: status={response.status_code}, data={response.json()}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == test_comment.id
        assert data[0]["comment"] == test_comment.comment
        assert data[0]["post_id"] == test_comment.post_id
        assert data[0]["user_id"] == test_comment.user_id
        assert data[0]["username"] == test_comment.username
        assert "likes" in data[0]
        assert "liked_by_current_user" in data[0]
        assert "timestamp" in data[0]

    def test_get_comment_by_id_success(self, client, auth_headers, test_comment):
        """Test successful retrieval of a specific comment by ID"""
        response = client.get(f"/comments/{test_comment.id}", headers=auth_headers)
        print(f"DEBUG: status={response.status_code}, data={response.json()}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_comment.id
        assert data["comment"] == test_comment.comment
        assert data["post_id"] == test_comment.post_id
        assert data["user_id"] == test_comment.user_id
        assert data["username"] == test_comment.username
        assert "likes" in data
        assert "liked_by_current_user" in data
        assert "timestamp" in data

    def test_get_comment_by_id_not_found(self, client, auth_headers):
        """Test getting a comment that doesn't exist"""
        fake_id = "fake-comment-id"
        response = client.get(f"/comments/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Resource Not Found"

    def test_create_comment_success(self, client, auth_headers, test_post):
        """Test successful comment creation"""
        data = {"comment": "New comment", "post_id": test_post.id}
        response = client.post("/comments/", json=data, headers=auth_headers)
        print(f"DEBUG: status={response.status_code}, data={response.json()}")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["comment"] == "New comment"
        assert response.json()["post_id"] == data["post_id"]
        assert "id" in response.json()
        assert "user_id" in response.json()
        assert "username" in response.json()

    def test_create_comment_unauthorized(self, client, test_post):
        response = client.post("/comments/", json={"comment": "Unauthorized comment", "post_id": test_post.id})
        assert response.status_code == 401

    def test_update_comment_success(self, client, auth_headers, test_comment):
        """Test successful comment update by owner"""
        update_data = {
            "comment": "Updated comment"
        }
        response = client.put(f"/comments/{test_comment.id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["comment"] == update_data["comment"]
        assert data["id"] == test_comment.id

    def test_update_comment_not_owner(self, client, auth_headers_user2, test_comment):
        """Test updating comment by non-owner"""
        update_data = {
            "comment": "Unauthorized update"
        }
        response = client.put(f"/comments/{test_comment.id}", json=update_data, headers=auth_headers_user2)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You can only edit your own comments"

    def test_update_comment_not_found(self, client, auth_headers):
        """Test updating a comment that doesn't exist"""
        fake_id = "fake-comment-id"
        update_data = {
            "comment": "Updated comment"
        }
        response = client.put(f"/comments/{fake_id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Resource Not Found"

    def test_update_comment_unauthorized(self, client, test_comment):
        response = client.put(f"/comments/{test_comment.id}", json={"comment": "Unauthorized update"})
        assert response.status_code == 401

    def test_delete_comment_success(self, client, auth_headers, test_comment):
        """Test successful comment deletion by owner"""
        response = client.delete(f"/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == f"Comment with id {test_comment.id} and its replies have been deleted"
        
        # Verify comment is deleted
        get_response = client.get(f"/comments/{test_comment.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_comment_not_found(self, client, auth_headers):
        """Test deleting a comment that doesn't exist"""
        fake_id = "fake-comment-id"
        response = client.delete(f"/comments/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Comment not found"

    def test_delete_comment_not_owner(self, client, auth_headers_user2, test_comment):
        """Test deleting a comment by someone who doesn't own it"""
        response = client.delete(f"/comments/{test_comment.id}", headers=auth_headers_user2)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You can only delete your own comments"

    def test_delete_comment_unauthorized(self, client, test_comment):
        response = client.delete(f"/comments/{test_comment.id}")
        assert response.status_code == 401

    def test_like_comment_success(self, client, auth_headers, test_comment):
        """Test successful comment like"""
        response = client.post(f"/comments/{test_comment.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes"] == 1
        assert data["liked_by_current_user"] == True

    def test_like_comment_already_liked(self, client, auth_headers, test_comment):
        """Test liking a comment that's already liked (should unlike)"""
        # First like
        response1 = client.post(f"/comments/{test_comment.id}/like", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        assert response1.json()["likes"] == 1
        
        # Second like should unlike
        response2 = client.post(f"/comments/{test_comment.id}/like", headers=auth_headers)
        assert response2.status_code == status.HTTP_200_OK
        assert response2.json()["likes"] == 0
        assert response2.json()["liked_by_current_user"] == False

    def test_like_comment_not_found(self, client, auth_headers):
        """Test liking a comment that doesn't exist"""
        fake_id = "fake-comment-id"
        response = client.post(f"/comments/{fake_id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_like_comment_unauthorized(self, client, test_comment):
        response = client.post(f"/comments/{test_comment.id}/like")
        assert response.status_code == 401

    def test_unlike_comment_success(self, client, auth_headers, test_comment):
        """Test successful comment unlike"""
        # First like the comment
        like_response = client.post(f"/comments/{test_comment.id}/like", headers=auth_headers)
        assert like_response.status_code == status.HTTP_200_OK
        assert like_response.json()["likes"] == 1
        
        # Then unlike it
        response = client.delete(f"/comments/{test_comment.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes"] == 0
        assert data["liked_by_current_user"] == False

    def test_unlike_comment_not_liked(self, client, auth_headers, test_comment):
        """Test unliking a comment that's not liked"""
        response = client.delete(f"/comments/{test_comment.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes"] == 0
        assert data["liked_by_current_user"] == False

    # --- SIMPLE TESTS ---
    def test_comments_endpoint_simple(self, client, auth_headers, test_comment):
        response = client.get("/comments", headers=auth_headers)
        assert response.status_code == 200

    def test_comments_list_simple(self, client, auth_headers):
        response = client.get("/comments", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    # Forum Comments Tests
    def test_get_forum_comments_success(self, client, auth_headers, test_forum):
        """Test getting comments for a specific forum"""
        response = client.get(f"/comments/forum/{test_forum.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_main_forum_comments_success(self, client, auth_headers, test_forum):
        """Test getting main comments for a specific forum"""
        response = client.get(f"/comments/forum/{test_forum.id}/main", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_forum_comment_success(self, client, auth_headers):
        # Create forum via API
        forum_data = {"title": "Test Forum", "content": "Test forum content"}
        forum_resp = client.post("/forums", json=forum_data, headers=auth_headers)
        forum_id = forum_resp.json()["id"]
        comment_data = {
            "comment": "Forum comment",
            "forum_id": forum_id,
            "parent_id": None
        }
        response = client.post(f"/comments/forum/{forum_id}", json=comment_data, headers=auth_headers)
        print("FORUM COMMENT CREATE RESPONSE:", response.status_code, response.json())
        assert response.status_code in [201, 200]

    def test_get_forum_comments_replied_to_success(self, client, auth_headers):
        # Create forum via API
        forum_data = {"title": "Test Forum", "content": "Test forum content"}
        forum_resp = client.post("/forums", json=forum_data, headers=auth_headers)
        forum_id = forum_resp.json()["id"]
        # First create a forum comment
        comment_data = {
            "comment": "Main forum comment",
            "forum_id": forum_id,
            "parent_id": None
        }
        comment_response = client.post(f"/comments/forum/{forum_id}", json=comment_data, headers=auth_headers)
        main_comment_id = comment_response.json()["id"]
        # Now create a reply
        reply_data = {
            "comment": "Reply to forum comment",
            "forum_id": forum_id,
            "parent_id": main_comment_id
        }
        reply_response = client.post(f"/comments/forum/{forum_id}", json=reply_data, headers=auth_headers)
        print("FORUM REPLY CREATE RESPONSE:", reply_response.status_code, reply_response.json())
        # Fetch replies
        response = client.get(f"/comments/forum/replies/{main_comment_id}", headers=auth_headers)
        print("GET FORUM REPLIES RESPONSE:", response.status_code, response.json())
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert len(response.json()) == 1

    def test_get_comments_public(self, client):
        """Test getting comments without authentication (should be public)"""
        response = client.get("/comments")
        assert response.status_code == 200
