import pytest
from fastapi import status
from app.routers.comments.models import Comments, CommentLike
from app.routers.posts.models import Posts
from app.routers.forums.models import Forums

class TestSetup:
    def test_imports_work(self):
        from app.main import app
        from app.routers.comments.models import Comments
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

    def test_basic_health_check(self, client):
        response = client.get("/docs")
        assert response.status_code in [200, 404]

class TestCommentsRouter:
    """Test suite for comments router endpoints"""
    
    def test_get_comments_success(self, client, auth_headers, test_comment):
        """Test successful retrieval of all comments"""
        response = client.get("/comments", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == test_comment.id
        assert data[0]["comment"] == test_comment.comment
        assert data[0]["post_id"] == test_comment.post_id
        assert data[0]["username"] == test_comment.username
        assert "liked_by_current_user" in data[0]
        assert "likes" in data[0]
        assert "timestamp" in data[0]
    
    def test_get_comments_unauthorized(self, client):
        """Test getting comments without authentication"""
        response = client.get("/comments")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_comment_by_id_success(self, client, auth_headers, test_comment):
        """Test successful retrieval of a specific comment by ID"""
        response = client.get(f"/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_comment.id
        assert data["comment"] == test_comment.comment
        assert data["post_id"] == test_comment.post_id
        assert data["username"] == test_comment.username
        assert "liked_by_current_user" in data
        assert "likes" in data
        assert "timestamp" in data
    
    def test_get_comment_by_id_not_found(self, client, auth_headers):
        """Test getting a comment that doesn't exist"""
        fake_id = "fake-comment-id"
        response = client.get(f"/comments/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Resource Not Found"
    
    def test_create_comment_success(self, client, auth_headers, test_post):
        """Test successful comment creation"""
        comment_data = {
            "comment": "This is a new test comment",
            "post_id": test_post.id,
            "parent_id": None
        }
        response = client.post("/comments", json=comment_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["comment"] == comment_data["comment"]
        assert data["post_id"] == comment_data["post_id"]
        assert data["parent_id"] == comment_data["parent_id"]
        assert "id" in data
        assert "user_id" in data
        assert "username" in data
        assert "timestamp" in data
        assert "liked_by_current_user" in data
        assert "likes" in data
    
    def test_create_reply_comment_success(self, client, auth_headers, test_post, test_comment):
        """Test successful reply comment creation"""
        reply_data = {
            "comment": "This is a reply to the test comment",
            "post_id": test_post.id,
            "parent_id": test_comment.id
        }
        response = client.post("/comments", json=reply_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["comment"] == reply_data["comment"]
        assert data["post_id"] == reply_data["post_id"]
        assert data["parent_id"] == reply_data["parent_id"]
    
    def test_create_comment_unauthorized(self, client, test_post):
        """Test creating comment without authentication"""
        comment_data = {
            "comment": "Unauthorized comment",
            "post_id": test_post.id,
            "parent_id": None
        }
        response = client.post("/comments", json=comment_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_comment_invalid_data(self, client, auth_headers):
        """Test creating comment with invalid data"""
        # Missing required fields
        comment_data = {
            "comment": "Missing post_id"
            # Missing post_id
        }
        response = client.post("/comments", json=comment_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_comment_success(self, client, auth_headers, test_comment):
        """Test successful comment update by owner"""
        update_data = {
            "comment": "Updated comment content"
        }
        response = client.put(f"/comments/{test_comment.id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["comment"] == update_data["comment"]
        assert data["id"] == test_comment.id
    
    def test_update_comment_not_found(self, client, auth_headers):
        """Test updating a comment that doesn't exist"""
        fake_id = "fake-comment-id"
        update_data = {
            "comment": "Updated content"
        }
        response = client.put(f"/comments/{fake_id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Resource Not Found"
    
    def test_update_comment_not_owner(self, client, auth_headers_user2, test_comment):
        """Test updating a comment by someone who doesn't own it"""
        update_data = {
            "comment": "Unauthorized update"
        }
        response = client.put(f"/comments/{test_comment.id}", json=update_data, headers=auth_headers_user2)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You can only edit your own comments"
    
    def test_update_comment_unauthorized(self, client, test_comment):
        """Test updating comment without authentication"""
        update_data = {
            "comment": "Unauthorized update"
        }
        response = client.put(f"/comments/{test_comment.id}", json=update_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_comment_success(self, client, auth_headers, test_comment):
        """Test successful comment deletion by owner"""
        response = client.delete(f"/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == f"Comment with id {test_comment.id} and its replies have been deleted"
        
        # Verify comment is deleted
        get_response = client.get(f"/comments/{test_comment.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_comment_with_replies(self, client, auth_headers, test_post, test_comment):
        """Test deleting a comment that has replies"""
        # Create a reply first
        reply_data = {
            "comment": "Reply to be deleted",
            "post_id": test_post.id,
            "parent_id": test_comment.id
        }
        client.post("/comments", json=reply_data, headers=auth_headers)
        
        # Delete the parent comment
        response = client.delete(f"/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify both comment and reply are deleted
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
    
    def test_get_comments_by_post_id_success(self, client, auth_headers, test_post, test_comment):
        """Test getting comments for a specific post"""
        response = client.get(f"/comments/post/{test_post.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["post_id"] == test_post.id
        assert data[0]["id"] == test_comment.id
    
    def test_get_comments_by_post_id_empty(self, client, auth_headers, test_post):
        """Test getting comments for a post with no comments"""
        # Create a new post without comments
        new_post = Posts(
            id="new-post-id",
            title="New Post",
            content="New content",
            author="testuser",
            image_url="/static/default/default.jpeg",
            likes=0
        )
        response = client.get(f"/comments/post/{new_post.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_main_comments_by_post_id_success(self, client, auth_headers, test_post, test_comment):
        """Test getting main comments (no parent) for a specific post"""
        response = client.get(f"/comments/post/{test_post.id}/main", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["post_id"] == test_post.id
        assert data[0]["parent_id"] is None
    
    def test_get_replies_to_comment_success(self, client, auth_headers, test_post, test_comment):
        """Test getting replies to a specific comment"""
        # Create a reply first
        reply_data = {
            "comment": "Reply to test comment",
            "post_id": test_post.id,
            "parent_id": test_comment.id
        }
        client.post("/comments", json=reply_data, headers=auth_headers)
        
        # Get replies
        response = client.get(f"/comments/post/{test_post.id}/replies/{test_comment.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["parent_id"] == test_comment.id
    
    def test_like_comment_success(self, client, auth_headers, test_comment):
        """Test successfully liking a comment"""
        response = client.post(f"/comments/{test_comment.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["liked_by_current_user"] == True
        assert data["likes"] == 1
    
    def test_like_comment_already_liked(self, client, auth_headers, test_comment):
        """Test liking a comment that's already liked (should toggle)"""
        # First like
        response1 = client.post(f"/comments/{test_comment.id}/like", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        
        # Second like (should unlike)
        response2 = client.post(f"/comments/{test_comment.id}/like", headers=auth_headers)
        assert response2.status_code == status.HTTP_200_OK
        data = response2.json()
        assert data["liked_by_current_user"] == False
        assert data["likes"] == 0
    
    def test_unlike_comment_success(self, client, auth_headers, test_comment):
        """Test successfully unliking a comment"""
        # First like the comment
        client.post(f"/comments/{test_comment.id}/like", headers=auth_headers)
        
        # Then unlike it
        response = client.delete(f"/comments/{test_comment.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["liked_by_current_user"] == False
        assert data["likes"] == 0
    
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
    
    def test_create_forum_comment_success(self, client, auth_headers, test_forum):
        """Test creating a comment for a forum"""
        comment_data = {
            "comment": "Forum comment",
            "post_id": test_forum.id,  # Using forum_id as post_id for forum comments
            "parent_id": None
        }
        response = client.post(f"/comments/forum/{test_forum.id}", json=comment_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["comment"] == comment_data["comment"]
        assert data["post_id"] == comment_data["post_id"]
    
    def test_get_forum_comments_replied_to_success(self, client, auth_headers, test_forum):
        """Test getting replies to a forum comment"""
        # First create a forum comment
        comment_data = {
            "comment": "Main forum comment",
            "post_id": test_forum.id,
            "parent_id": None
        }
        comment_response = client.post(f"/comments/forum/{test_forum.id}", json=comment_data, headers=auth_headers)
        comment_id = comment_response.json()["id"]
        
        # Create a reply
        reply_data = {
            "comment": "Reply to forum comment",
            "post_id": test_forum.id,
            "parent_id": comment_id
        }
        client.post(f"/comments/forum/{test_forum.id}", json=reply_data, headers=auth_headers)
        
        # Get replies
        response = client.get(f"/comments/forum/{test_forum.id}/replies/{comment_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["parent_id"] == comment_id
