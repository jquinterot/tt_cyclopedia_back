from fastapi.testclient import TestClient
from app.routers.comments.comments import router

client = TestClient(router)


def test_read_comments():
    response = client.get("/comments")
    assert response.status_code == 200
    data = response.json()
    first_comment = data[0]
    assert 'id' in first_comment, f"Missing 'id' attribute in {first_comment}"
    assert 'comment' in first_comment, f"Missing 'comment' attribute in {first_comment}"
