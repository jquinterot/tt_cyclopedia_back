import pytest
from fastapi import status
from app.tests.conftest import Posts, PostLike, Users
import json
import os
from app.config.postgres_config import Base

if "sqlite" in os.getenv("SQL_DB", ""):
    SCHEMA_KWARGS = {}
else:
    SCHEMA_KWARGS = {"schema": "cyclopedia_owner"}

# --- FACTORY HELPERS ---
def make_post(db_session, user, title="Unit Post", content="Unit post content"):
    post = Posts(
        id=user.id + title,
        title=title,
        content=content,
        author=user.username,
        image_url="/static/default/default.jpeg",
        likes=0
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post

class TestSetup:
    def test_imports_work(self):
        from app.main import app
        from app.tests.conftest import Posts
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



class TestPostsRouter:
    """Test suite for posts router endpoints."""

    def test_get_posts_success(self, client, auth_headers, test_post):
        """Test successful retrieval of all posts"""
        response = client.get("/posts", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == test_post.id
        assert data[0]["title"] == test_post.title
        assert data[0]["content"] == test_post.content
        assert data[0]["author"] == test_post.author
        assert "likes" in data[0]
        assert "likedByCurrentUser" in data[0]
        assert "timestamp" in data[0]

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
        assert "timestamp" in data

    def test_get_post_by_id_not_found(self, client, auth_headers):
        """Test getting a post that doesn't exist"""
        fake_id = "fake-post-id"
        response = client.get(f"/posts/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Post not found"

    def test_create_post_success(self, client, auth_headers):
        """Test successful post creation"""
        post_data = {
            "title": "Test Post",
            "content": "Test post content"
        }
        response = client.post("/posts", data=post_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == post_data["title"]
        assert data["content"] == post_data["content"]
        assert "id" in data
        assert "author" in data

    def test_create_post_unauthorized(self, client):
        """Test creating post without authentication"""
        post_data = {
            "title": "Unauthorized Post",
            "content": "This should fail"
        }
        response = client.post("/posts", data=post_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

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

    def test_delete_post_not_owner(self, client, auth_headers_user2, test_post):
        """Test deleting a post by someone who doesn't own it"""
        response = client.delete(f"/posts/{test_post.id}", headers=auth_headers_user2)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Not authorized to delete this post"

    def test_delete_post_unauthorized(self, client, test_post):
        """Test deleting post without authentication"""
        response = client.delete(f"/posts/{test_post.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_like_post_success(self, client, auth_headers, test_post):
        """Test successful post like"""
        response = client.post(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_like_post_already_liked(self, client, auth_headers, test_post):
        """Test liking a post that's already liked"""
        # First like
        response1 = client.post(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response1.status_code == status.HTTP_204_NO_CONTENT
        
        # Second like should fail
        response2 = client.post(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert response2.json()["detail"] == "Already liked"

    def test_like_post_not_found(self, client, auth_headers):
        """Test liking a post that doesn't exist"""
        fake_id = "fake-post-id"
        response = client.post(f"/posts/{fake_id}/like", headers=auth_headers)
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response body: {response.text}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_like_post_unauthorized(self, client, test_post):
        """Test liking post without authentication"""
        response = client.post(f"/posts/{test_post.id}/like")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unlike_post_success(self, client, auth_headers, test_post):
        """Test successful post unlike"""
        # First like the post
        like_response = client.post(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert like_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Then unlike it
        response = client.delete(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_unlike_post_not_liked(self, client, auth_headers, test_post):
        """Test unliking a post that's not liked"""
        response = client.delete(f"/posts/{test_post.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Not liked yet"

    def test_get_post_likes_success(self, client, auth_headers, test_post):
        """Test successful retrieval of post likes"""
        response = client.get(f"/posts/{test_post.id}/likes", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    # --- SIMPLE TESTS ---
    def test_posts_endpoint_simple(self, client, auth_headers, test_post):
        response = client.get("/posts", headers=auth_headers)
        assert response.status_code == 200

    def test_posts_list_simple(self, client, auth_headers):
        response = client.get("/posts", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
