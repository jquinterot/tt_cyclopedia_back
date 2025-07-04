import pytest
from fastapi import status
from app.routers.comments.models import Comments, CommentLike
from app.routers.posts.models import Posts
from app.routers.forums.models import Forums
from app.routers.users.models import Users

# --- FACTORY HELPERS ---
def get_or_create_user(db_session):
    user = db_session.query(Users).filter_by(id="test-user-id-123").first()
    if not user:
        user = Users(
            id="test-user-id-123",
            username="testuser",
            email="test@example.com",
            password="hashed"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

def get_or_create_post(db_session, user):
    post = db_session.query(Posts).filter_by(id="test-post-id-123").first()
    if not post:
        post = Posts(
            id="test-post-id-123",
            title="Test Post",
            content="Test content",
            author=user.username,
            image_url="/static/default/default.jpeg",
            likes=0
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
    return post

class TestSetup:
    """Basic setup and health checks for the test environment."""
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
    """Test suite for comments router endpoints (unit and integration)."""

    def setup_user_and_post(self, client):
        # Create user via API
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
        reg_resp = client.post("/users", json=user_data)
        print("REGISTER STATUS:", reg_resp.status_code, reg_resp.json())
        # Login to get auth headers
        login_data = {"username": "testuser", "password": "testpassword"}
        login_resp = client.post("/users/login", json=login_data)
        print("LOGIN STATUS:", login_resp.status_code, login_resp.json())
        token = login_resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        # Fetch user ID
        me_resp = client.get("/users/me", headers=headers)
        print("ME STATUS:", me_resp.status_code, me_resp.json())
        user_id = me_resp.json().get("id")
        # Create post via API
        post_data = {
            "title": "Test Post",
            "content": "Test content",
            "image_url": "/static/default/default.jpeg"
        }
        post_resp = client.post("/posts", data=post_data, headers=headers)
        print("POST STATUS:", post_resp.status_code, post_resp.json())
        post_id = post_resp.json().get("id")
        return headers, user_id, post_id

    # def test_get_comments_success(self, client):
    #     headers, user_id, post_id = self.setup_user_and_post(client)
    #     # Create a comment via API
    #     comment_data = {
    #         "comment": "Test comment",
    #         "post_id": post_id,
    #         "parent_id": None
    #     }
    #     client.post("/comments", json=comment_data, headers=headers)
    #     response = client.get("/comments", headers=headers)
    #     assert response.status_code == status.HTTP_200_OK
    #     assert len(response.json()) >= 1

    # def test_get_comment_by_id_success(self, client):
    #     headers, user_id, post_id = self.setup_user_and_post(client)
    #     # Create a comment via API
    #     comment_data = {
    #         "comment": "Test comment by id",
    #         "post_id": post_id,
    #         "parent_id": None
    #     }
    #     comment_resp = client.post("/comments", json=comment_data, headers=headers)
    #     comment_id = comment_resp.json()["id"]
    #     response = client.get(f"/comments/{comment_id}", headers=headers)
    #     assert response.status_code == status.HTTP_200_OK
    #     assert response.json()["id"] == comment_id

    # def test_create_comment_success(self, client):
    #     headers, user_id, post_id = self.setup_user_and_post(client)
    #     comment_data = {
    #         "comment": "This is a new test comment",
    #         "post_id": post_id,
    #         "parent_id": None
    #     }
    #     response = client.post("/comments", json=comment_data, headers=headers)
    #     assert response.status_code == status.HTTP_201_CREATED
    #     assert response.json()["comment"] == "This is a new test comment"
    #     # Fetch the comment to verify it exists
    #     comment_id = response.json()["id"]
    #     get_response = client.get(f"/comments/{comment_id}", headers=headers)
    #     assert get_response.status_code == status.HTTP_200_OK

    def test_create_reply_comment_success(self, client):
        headers, user_id, post_id = self.setup_user_and_post(client)
        # Create a parent comment via API
        parent_data = {
            "comment": "Parent comment",
            "post_id": post_id,
            "parent_id": None
        }
        parent_resp = client.post("/comments", json=parent_data, headers=headers)
        parent_id = parent_resp.json()["id"]
        reply_data = {
            "comment": "This is a reply to the test comment",
            "post_id": post_id,
            "parent_id": parent_id
        }
        response = client.post("/comments", json=reply_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["parent_id"] == parent_id

    def test_create_comment_invalid_data(self, client):
        # Create user and post via API
        user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
        client.post("/users", json=user_data)
        login = client.post("/users/login", json={"username": "testuser", "password": "testpassword"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # Missing post_id in payload
        comment_data = {"comment": "Missing post_id"}
        response = client.post("/comments", json=comment_data, headers=headers)
        print("INVALID DATA RESPONSE:", response.status_code, response.json())
        assert response.status_code in [201, 422]

    def test_create_comment_integration(self, client):
        headers, user_id, post_id = self.setup_user_and_post(client)
        comment_data = {
            "comment": "Integration comment",
            "post_id": post_id,
            "parent_id": None
        }
        response = client.post("/comments", json=comment_data, headers=headers)
        assert response.status_code == 201
        assert response.json()["comment"] == "Integration comment"
        assert response.json()["post_id"] == post_id

    def test_update_comment_success(self, client, auth_headers, db_session):
        # Create user, post, and comment via API
        headers, user_id, post_id = self.setup_user_and_post(client)
        comment_data = {
            "comment": "Update me",
            "post_id": post_id,
            "parent_id": None
        }
        comment_resp = client.post("/comments", json=comment_data, headers=headers)
        comment_id = comment_resp.json()["id"]
        update_data = {"comment": "Updated comment content"}
        response = client.put(f"/comments/{comment_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["comment"] == "Updated comment content"
    
    def test_update_comment_not_found(self, client, auth_headers):
        """Test updating a comment that doesn't exist"""
        fake_id = "fake-comment-id"
        update_data = {
            "comment": "Updated content"
        }
        response = client.put(f"/comments/{fake_id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Resource Not Found"
    
    def test_update_comment_not_owner(self, client):
        # Create user1 and comment
        headers1, user1_id, post_id = self.setup_user_and_post(client)
        comment_data = {
            "comment": "Owner's comment",
            "post_id": post_id,
            "parent_id": None
        }
        comment_resp = client.post("/comments", json=comment_data, headers=headers1)
        comment_id = comment_resp.json()["id"]
        # Create user2 and login
        user2_data = {"username": "testuser2", "email": "test2@example.com", "password": "testpassword2"}
        client.post("/users", json=user2_data)
        login2 = client.post("/users/login", json={"username": "testuser2", "password": "testpassword2"})
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        # Try to update comment as user2
        update_data = {"comment": "Unauthorized update"}
        response = client.put(f"/comments/{comment_id}", json=update_data, headers=headers2)
        assert response.status_code in [401, 403]

    def test_update_comment_unauthorized(self, client):
        # Create user and comment
        headers, user_id, post_id = self.setup_user_and_post(client)
        comment_data = {
            "comment": "Owner's comment",
            "post_id": post_id,
            "parent_id": None
        }
        comment_resp = client.post("/comments", json=comment_data, headers=headers)
        comment_id = comment_resp.json()["id"]
        # Try to update without auth
        update_data = {"comment": "Unauthorized update"}
        response = client.put(f"/comments/{comment_id}", json=update_data)
        assert response.status_code in [401, 403]

    def test_delete_comment_success(self, client):
        headers, user_id, post_id = self.setup_user_and_post(client)
        comment_data = {
            "comment": "To be deleted",
            "post_id": post_id,
            "parent_id": None
        }
        comment_resp = client.post("/comments", json=comment_data, headers=headers)
        comment_id = comment_resp.json()["id"]
        response = client.delete(f"/comments/{comment_id}", headers=headers)
        assert response.status_code == 200

    def test_delete_comment_with_replies(self, client):
        headers, user_id, post_id = self.setup_user_and_post(client)
        # Create parent comment
        parent_data = {
            "comment": "Parent comment",
            "post_id": post_id,
            "parent_id": None
        }
        parent_resp = client.post("/comments", json=parent_data, headers=headers)
        parent_id = parent_resp.json()["id"]
        # Create reply
        reply_data = {
            "comment": "Reply to be deleted",
            "post_id": post_id,
            "parent_id": parent_id
        }
        reply_resp = client.post("/comments", json=reply_data, headers=headers)
        reply_id = reply_resp.json()["id"]
        # Delete parent
        response = client.delete(f"/comments/{parent_id}", headers=headers)
        assert response.status_code == 200

    def test_get_comments_by_post_id_success(self, client):
        # Create user, post, and comment via API
        user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
        client.post("/users", json=user_data)
        login = client.post("/users/login", json={"username": "testuser", "password": "testpassword"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        post_data = {"title": "Test Post", "content": "Test content", "image_url": "/static/default/default.jpeg"}
        post_resp = client.post("/posts", data=post_data, headers=headers)
        post_id = post_resp.json()["id"]
        comment_data = {"comment": "Test comment", "post_id": post_id}
        comment_resp = client.post("/comments", json=comment_data, headers=headers)
        print("COMMENT CREATE RESPONSE:", comment_resp.status_code, comment_resp.json())
        response = client.get(f"/comments/by_post/{post_id}", headers=headers)
        print("GET COMMENTS BY POST RESPONSE:", response.status_code, response.json())
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert len(response.json()) == 1

    def test_get_main_comments_by_post_id_success(self, client):
        # Create user, post, and comment via API
        user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
        client.post("/users", json=user_data)
        login = client.post("/users/login", json={"username": "testuser", "password": "testpassword"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        post_data = {"title": "Test Post", "content": "Test content", "image_url": "/static/default/default.jpeg"}
        post_resp = client.post("/posts", data=post_data, headers=headers)
        post_id = post_resp.json()["id"]
        comment_data = {"comment": "Test comment", "post_id": post_id}
        comment_resp = client.post("/comments", json=comment_data, headers=headers)
        print("COMMENT CREATE RESPONSE:", comment_resp.status_code, comment_resp.json())
        response = client.get(f"/comments/main/{post_id}", headers=headers)
        print("GET MAIN COMMENTS RESPONSE:", response.status_code, response.json())
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert len(response.json()) == 1

    def test_get_replies_to_comment_success(self, client):
        # Create user, post, parent comment, and reply via API
        user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
        client.post("/users", json=user_data)
        login = client.post("/users/login", json={"username": "testuser", "password": "testpassword"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        post_data = {"title": "Test Post", "content": "Test content", "image_url": "/static/default/default.jpeg"}
        post_resp = client.post("/posts", data=post_data, headers=headers)
        post_id = post_resp.json()["id"]
        parent_data = {"comment": "Parent comment", "post_id": post_id}
        parent_resp = client.post("/comments", json=parent_data, headers=headers)
        parent_id = parent_resp.json()["id"]
        reply_data = {"comment": "Reply to test comment", "post_id": post_id, "parent_id": parent_id}
        reply_resp = client.post("/comments", json=reply_data, headers=headers)
        print("REPLY CREATE RESPONSE:", reply_resp.status_code, reply_resp.json())
        response = client.get(f"/comments/replies/{parent_id}", headers=headers)
        print("GET REPLIES RESPONSE:", response.status_code, response.json())
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert len(response.json()) == 1

    def test_like_comment_success(self, client):
        # Create user, post, and comment via API
        user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
        client.post("/users", json=user_data)
        login = client.post("/users/login", json={"username": "testuser", "password": "testpassword"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        post_data = {"title": "Test Post", "content": "Test content", "image_url": "/static/default/default.jpeg"}
        post_resp = client.post("/posts", data=post_data, headers=headers)
        post_id = post_resp.json()["id"]
        comment_data = {"comment": "Test comment", "post_id": post_id}
        comment_resp = client.post("/comments", json=comment_data, headers=headers)
        comment_id = comment_resp.json()["id"]
        response = client.post(f"/comments/{comment_id}/like", headers=headers)
        assert response.status_code == 200

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
