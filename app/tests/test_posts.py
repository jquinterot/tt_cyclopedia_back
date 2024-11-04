from fastapi.testclient import TestClient
from app.routers.posts.posts import router

client = TestClient(router)


def test_read_posts():
    response = client.get("/posts")
    assert response.status_code == 200
    #assert response.json() == {"postName": "post", "postId": "1F3J"}
