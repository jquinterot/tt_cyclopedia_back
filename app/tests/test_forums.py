import pytest
from fastapi import status
# Import test models from conftest instead of production models
from app.tests.conftest import Forums, ForumLike, ForumComment, ForumCommentLike

# --- FACTORY HELPERS ---
def make_forum(db_session, user, title="Unit Forum", content="Unit forum content"):
    forum = Forums(
        id=user.id + title,
        title=title,
        content=content,
        author=user.username,
        likes=0
    )
    db_session.add(forum)
    db_session.commit()
    db_session.refresh(forum)
    return forum

class TestSetup:
    def test_imports_work(self):
        from app.main import app
        from app.tests.conftest import Forums
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



class TestForumsRouter:
    """Test suite for forums router endpoints (unit and integration)."""

    def setup_user_and_forum(self, client):
        user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
        client.post("/users", json=user_data)
        login = client.post("/users/login", json={"username": "testuser", "password": "testpassword"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        forum_data = {"title": "Test Forum", "content": "Test forum content"}
        forum_resp = client.post("/forums", json=forum_data, headers=headers)
        forum_id = forum_resp.json()["id"]
        return headers, forum_id

    def test_get_all_forums_success(self, client, auth_headers, test_forum):
        """Test successful retrieval of all forums"""
        response = client.get("/forums", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == test_forum.id
        assert data[0]["title"] == test_forum.title
        assert data[0]["content"] == test_forum.content
        assert data[0]["author"] == test_forum.author
        assert "likes" in data[0]
        assert "liked_by_current_user" in data[0]
        assert "timestamp" in data[0]
        assert "updated_timestamp" in data[0]
    
    def test_get_forum_by_id_success(self, client, auth_headers, test_forum):
        """Test successful retrieval of a specific forum by ID"""
        response = client.get(f"/forums/{test_forum.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_forum.id
        assert data["title"] == test_forum.title
        assert data["content"] == test_forum.content
        assert data["author"] == test_forum.author
        assert "likes" in data
        assert "liked_by_current_user" in data
        assert "timestamp" in data
        assert "updated_timestamp" in data
    
    def test_get_forum_by_id_not_found(self, client, auth_headers):
        """Test getting a forum that doesn't exist"""
        fake_id = "fake-forum-id"
        response = client.get(f"/forums/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Forum not found"
    
    def test_create_forum_unit(self, client, db_session, test_user, override_current_user):
        """Unit test: create forum with dependency override (no JWT)."""
        forum_data = {
            "title": "Unit Test Forum",
            "content": "Unit forum content"
        }
        response = client.post("/forums", json=forum_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == forum_data["title"]
        assert data["content"] == forum_data["content"]
        assert data["author"] == test_user.username

    def test_create_forum_integration(self, client):
        headers, _ = self.setup_user_and_forum(client)
        forum_data = {"title": "Integration Forum", "content": "Integration content"}
        response = client.post("/forums", json=forum_data, headers=headers)
        assert response.status_code == 201
        assert response.json()["title"] == "Integration Forum"
    
    def test_create_forum_unauthorized(self, client):
        """Test creating forum without authentication"""
        forum_data = {
            "title": "Unauthorized Forum",
            "content": "This should fail"
        }
        response = client.post("/forums", json=forum_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_forum_invalid_data(self, client, auth_headers):
        """Test creating forum with invalid data"""
        # Missing required fields
        forum_data = {
            "title": "Missing content"
            # Missing content
        }
        response = client.post("/forums", json=forum_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_forum_success(self, client, auth_headers, test_forum):
        """Test successful forum update by owner"""
        update_data = {
            "title": "Updated Forum Title",
            "content": "Updated forum content"
        }
        response = client.put(f"/forums/{test_forum.id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["id"] == test_forum.id
    
    def test_update_forum_partial(self, client, auth_headers, test_forum):
        """Test updating forum with partial data"""
        update_data = {
            "title": "Only Title Updated"
            # Only updating title
        }
        response = client.put(f"/forums/{test_forum.id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == test_forum.content  # Should remain unchanged
    
    def test_update_forum_not_found(self, client, auth_headers):
        """Test updating a forum that doesn't exist"""
        fake_id = "fake-forum-id"
        update_data = {
            "title": "Updated Title",
            "content": "Updated content"
        }
        response = client.put(f"/forums/{fake_id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Forum not found"
    
    def test_update_forum_not_owner(self, client):
        headers1, forum_id = self.setup_user_and_forum(client)
        user2_data = {"username": "testuser2", "email": "test2@example.com", "password": "testpassword2"}
        client.post("/users", json=user2_data)
        login2 = client.post("/users/login", json={"username": "testuser2", "password": "testpassword2"})
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        update_data = {"title": "Unauthorized update", "content": "Nope"}
        response = client.put(f"/forums/{forum_id}", json=update_data, headers=headers2)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_forum_unauthorized(self, client, test_forum):
        """Test updating forum without authentication"""
        update_data = {
            "title": "Unauthorized Update",
            "content": "Unauthorized content"
        }
        response = client.put(f"/forums/{test_forum.id}", json=update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_forum_success(self, client):
        headers, forum_id = self.setup_user_and_forum(client)
        response = client.delete(f"/forums/{forum_id}", headers=headers)
        assert response.status_code == 204
        
        # Verify forum is deleted
        get_response = client.get(f"/forums/{forum_id}", headers=headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_forum_not_found(self, client, auth_headers):
        """Test deleting a forum that doesn't exist"""
        fake_id = "fake-forum-id"
        response = client.delete(f"/forums/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_forum_unauthorized(self, client, test_forum):
        """Test deleting forum without authentication"""
        response = client.delete(f"/forums/{test_forum.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_like_forum_success(self, client, auth_headers, test_forum):
        """Test successful forum like"""
        response = client.post(f"/forums/{test_forum.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes"] == 1
        assert data["liked_by_current_user"] == True
    
    def test_like_forum_already_liked(self, client, auth_headers, test_forum):
        """Test liking a forum that's already liked (should unlike)"""
        # First like
        response1 = client.post(f"/forums/{test_forum.id}/like", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        assert response1.json()["likes"] == 1
        
        # Second like should unlike
        response2 = client.post(f"/forums/{test_forum.id}/like", headers=auth_headers)
        assert response2.status_code == status.HTTP_200_OK
        assert response2.json()["likes"] == 0
        assert response2.json()["liked_by_current_user"] == False
    
    def test_like_forum_not_found(self, client, auth_headers):
        """Test liking a forum that doesn't exist"""
        fake_id = "fake-forum-id"
        response = client.post(f"/forums/{fake_id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_like_forum_unauthorized(self, client, test_forum):
        """Test liking forum without authentication"""
        response = client.post(f"/forums/{test_forum.id}/like")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_unlike_forum_success(self, client, auth_headers, test_forum):
        """Test successful forum unlike"""
        # First like the forum
        like_response = client.post(f"/forums/{test_forum.id}/like", headers=auth_headers)
        assert like_response.status_code == status.HTTP_200_OK
        assert like_response.json()["likes"] == 1
        
        # Then unlike it
        response = client.delete(f"/forums/{test_forum.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes"] == 0
        assert data["liked_by_current_user"] == False
    
    def test_unlike_forum_not_liked(self, client, auth_headers, test_forum):
        """Test unliking a forum that's not liked"""
        response = client.delete(f"/forums/{test_forum.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes"] == 0
        assert data["liked_by_current_user"] == False
    
    def test_multiple_users_like_forum(self, client, auth_headers, auth_headers_user2, test_forum):
        """Test multiple users liking the same forum"""
        # First user likes
        response1 = client.post(f"/forums/{test_forum.id}/like", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        assert response1.json()["likes"] == 1
        
        # Second user likes
        response2 = client.post(f"/forums/{test_forum.id}/like", headers=auth_headers_user2)
        assert response2.status_code == status.HTTP_200_OK
        assert response2.json()["likes"] == 2
        
        # First user unlikes
        response3 = client.delete(f"/forums/{test_forum.id}/like", headers=auth_headers)
        assert response3.status_code == status.HTTP_200_OK
        assert response3.json()["likes"] == 1
    
    def test_get_forum_comments_success(self, client, auth_headers, test_forum):
        """Test successful retrieval of forum comments"""
        response = client.get(f"/forums/{test_forum.id}/comments", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_main_forum_comments_success(self, client, auth_headers, test_forum):
        """Test successful retrieval of main forum comments"""
        response = client.get(f"/forums/{test_forum.id}/comments/main", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_forum_comment_reply_success(self, client, auth_headers, test_forum, test_forum_comment):
        """Test successful creation of forum comment reply"""
        reply_data = {
            "comment": "Reply to forum comment",
            "parent_id": test_forum_comment.id,
            "forum_id": test_forum.id
        }
        print(f"DEBUG: Sending request to /forums/{test_forum.id}/comments")
        print(f"DEBUG: Request data: {reply_data}")
        response = client.post(f"/forums/{test_forum.id}/comments", json=reply_data, headers=auth_headers)
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response body: {response.text}")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["comment"] == reply_data["comment"]
        assert data["parent_id"] == test_forum_comment.id
        assert data["forum_id"] == test_forum.id
    
    def test_update_forum_comment_success(self, client, auth_headers, test_forum, test_forum_comment):
        """Test successful forum comment update by owner"""
        update_data = {
            "comment": "Updated forum comment"
        }
        response = client.put(f"/forums/{test_forum.id}/comments/{test_forum_comment.id}", 
                             json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["comment"] == update_data["comment"]
        assert data["id"] == test_forum_comment.id
    
    def test_update_forum_comment_not_owner(self, client, auth_headers_user2, test_forum, test_forum_comment):
        """Test updating forum comment by non-owner"""
        update_data = {
            "comment": "Unauthorized update"
        }
        response = client.put(f"/forums/{test_forum.id}/comments/{test_forum_comment.id}", 
                             json=update_data, headers=auth_headers_user2)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_forum_comment_success(self, client, auth_headers, test_forum, test_forum_comment):
        """Test successful forum comment deletion by owner"""
        response = client.delete(f"/forums/{test_forum.id}/comments/{test_forum_comment.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_delete_forum_comment_not_owner(self, client, auth_headers_user2, test_forum, test_forum_comment):
        """Test deleting forum comment by non-owner"""
        response = client.delete(f"/forums/{test_forum.id}/comments/{test_forum_comment.id}", headers=auth_headers_user2)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_like_forum_comment_success(self, client, auth_headers, test_forum, test_forum_comment):
        """Test successful forum comment like"""
        response = client.post(f"/forums/{test_forum.id}/comments/{test_forum_comment.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes"] == 1
        assert data["liked_by_current_user"] == True
    
    def test_unlike_forum_comment_success(self, client, auth_headers, test_forum, test_forum_comment):
        """Test successful forum comment unlike"""
        # First like the comment
        like_response = client.post(f"/forums/{test_forum.id}/comments/{test_forum_comment.id}/like", headers=auth_headers)
        assert like_response.status_code == status.HTTP_200_OK
        assert like_response.json()["likes"] == 1
        
        # Then unlike it
        response = client.delete(f"/forums/{test_forum.id}/comments/{test_forum_comment.id}/like", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes"] == 0
        assert data["liked_by_current_user"] == False
    
    # --- SIMPLE TESTS ---
    def test_forums_endpoint_simple(self, client, auth_headers, test_forum):
        response = client.get("/forums", headers=auth_headers)
        assert response.status_code == 200
    
    def test_forums_list_simple(self, client, auth_headers):
        response = client.get("/forums", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_all_forums_public(self, client):
        """Test getting all forums without authentication (public endpoint)"""
        response = client.get("/forums")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_get_forum_by_id_public(self, client, test_forum):
        """Test getting a specific forum without authentication (public endpoint)"""
        response = client.get(f"/forums/{test_forum.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_forum.id 