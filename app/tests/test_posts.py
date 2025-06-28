import pytest
from fastapi import status
from app.routers.posts.models import Posts, PostLike
import json
import os
from app.config.postgres_config import Base

if "sqlite" in os.getenv("SQL_DB", ""):
    SCHEMA_KWARGS = {}
else:
    SCHEMA_KWARGS = {"schema": "cyclopedia_owner"}

class TestSetup:
    def test_imports_work(self):
        from app.main import app
        from app.routers.posts.models import Posts
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

class TestPostsRouter:
    """Test suite for posts router endpoints"""
    
    def test_get_posts_success(self, client, auth_headers, test_post):
        """Test successful retrieval of all posts"""
        response = client.get("/posts", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == test_post.id
        assert data[0]["title"] == test_post.title
        assert data[0]["content"] == test_post.content
        assert data[0]["author"] == test_post.author
        assert "likes" in data[0]
        assert "likedByCurrentUser" in data[0]
    
    def test_get_posts_unauthorized(self, client):
        """Test getting posts without authentication"""
        response = client.get("/posts")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_post_by_id_success(self, client, auth_headers, test_post):
        """Test successful retrieval of a specific post by ID"""
        response = client.get(f"/posts/{test_post.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_post.id
        assert data["title"] == test_post.title
        assert data["content"] == test_post.content
        assert data["author"] == test_post.author
        assert "likes" in data
        assert "likedByCurrentUser" in data
    
    def test_get_post_by_id_not_found(self, client, auth_headers):
        """Test getting a post that doesn't exist"""
        fake_id = "fake-post-id"
        response = client.get(f"/posts/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Post not found"
    
    def test_get_post_by_id_unauthorized(self, client, test_post):
        """Test getting post by ID without authentication"""
        response = client.get(f"/posts/{test_post.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_post_success(self, client, auth_headers):
        """Test successful post creation"""
        post_data = {
            "title": "New Test Post",
            "content": "This is a new test post content",
            "stats": json.dumps({"views": 0, "shares": 0})
        }
        response = client.post("/posts", data=post_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == post_data["title"]
        assert data["content"] == post_data["content"]
        assert "id" in data
        assert "author" in data
        assert "timestamp" in data
        assert "likes" in data
        assert "likedByCurrentUser" in data
    
    def test_create_post_without_stats(self, client, auth_headers):
        """Test creating post without stats"""
        post_data = {
            "title": "Post Without Stats",
            "content": "This post has no stats"
        }
        response = client.post("/posts", data=post_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == post_data["title"]
        assert data["content"] == post_data["content"]
    
    def test_create_post_invalid_stats(self, client, auth_headers):
        """Test creating post with invalid stats JSON"""
        post_data = {
            "title": "Post With Invalid Stats",
            "content": "This post has invalid stats",
            "stats": "invalid json string"
        }
        response = client.post("/posts", data=post_data, headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid stats JSON format" in response.json()["detail"]
    
    def test_create_post_unauthorized(self, client):
        """Test creating post without authentication"""
        post_data = {
            "title": "Unauthorized Post",
            "content": "This should fail"
        }
        response = client.post("/posts", data=post_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_post_missing_required_fields(self, client, auth_headers):
        """Test creating post with missing required fields"""
        # Missing title
        post_data = {
            "content": "Only content provided"
        }
        response = client.post("/posts", data=post_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_delete_post_success(self, client, auth_headers, test_post):
        """Test successful post deletion by owner"""
        response = client.delete(f"/posts/{test_post.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify post is deleted
        get_response = client.get(f"/posts/{test_post.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_post_not_found(self, client, auth_headers):
        """Test deleting a post that doesn't exist"""
        fake_id = "fake-post-id"
        response = client.delete(f"/posts/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Post not found"
    
    def test_delete_post_unauthorized(self, client, test_post):
        """Test deleting post without authentication"""
        response = client.delete(f"/posts/{test_post.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_post_not_owner(self, client, auth_headers_user2, test_post):
        """Test deleting a post by someone who doesn't own it"""
        response = client.delete(f"/posts/{test_post.id}", headers=auth_headers_user2)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You can only delete your own posts"
    
    def test_like_post_success(self, client, auth_headers, test_post):
        """Test successfully liking a post"""
        response = client.post(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify post is now liked
        get_response = client.get(f"/posts/{test_post.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["likedByCurrentUser"] == True
        assert data["likes"] == 1
    
    def test_like_post_already_liked(self, client, auth_headers, test_post):
        """Test liking a post that's already liked (should toggle)"""
        # First like
        response1 = client.post(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response1.status_code == status.HTTP_204_NO_CONTENT
        
        # Second like (should unlike)
        response2 = client.post(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response2.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify post is now unliked
        get_response = client.get(f"/posts/{test_post.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["likedByCurrentUser"] == False
        assert data["likes"] == 0
    
    def test_like_post_not_found(self, client, auth_headers):
        """Test liking a post that doesn't exist"""
        fake_id = "fake-post-id"
        response = client.post(f"/posts/{fake_id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_like_post_unauthorized(self, client, test_post):
        """Test liking post without authentication"""
        response = client.post(f"/posts/{test_post.id}/like")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unlike_post_success(self, client, auth_headers, test_post):
        """Test successfully unliking a post"""
        # First like the post
        client.post(f"/posts/{test_post.id}/like", headers=auth_headers)
        
        # Then unlike it
        response = client.delete(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify post is now unliked
        get_response = client.get(f"/posts/{test_post.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["likedByCurrentUser"] == False
        assert data["likes"] == 0
    
    def test_unlike_post_not_liked(self, client, auth_headers, test_post):
        """Test unliking a post that's not liked"""
        response = client.delete(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify post is still unliked
        get_response = client.get(f"/posts/{test_post.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["likedByCurrentUser"] == False
        assert data["likes"] == 0
    
    def test_get_post_likes_success(self, client, auth_headers, test_post):
        """Test getting post likes count"""
        response = client.get(f"/posts/{test_post.id}/likes", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "likes" in data
        assert isinstance(data["likes"], int)
    
    def test_get_post_likes_not_found(self, client, auth_headers):
        """Test getting likes for a post that doesn't exist"""
        fake_id = "fake-post-id"
        response = client.get(f"/posts/{fake_id}/likes", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_multiple_users_like_post(self, client, auth_headers, auth_headers_user2, test_post):
        """Test multiple users liking the same post"""
        # First user likes
        response1 = client.post(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response1.status_code == status.HTTP_204_NO_CONTENT
        
        # Second user likes
        response2 = client.post(f"/posts/{test_post.id}/like", headers=auth_headers_user2)
        assert response2.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify total likes count
        get_response = client.get(f"/posts/{test_post.id}/likes", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["likes"] == 2
    
    def test_delete_all_posts_success(self, client, auth_headers, test_post):
        """Test deleting all posts (admin functionality)"""
        response = client.delete("/posts/all", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify all posts are deleted
        get_response = client.get("/posts", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert len(data) == 0
