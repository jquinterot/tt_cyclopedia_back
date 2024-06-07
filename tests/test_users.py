from fastapi.testclient import TestClient
from routers.users.users import router

client = TestClient(router)


def test_read_posts():
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == {"name": "Johany", "lastname": "Quintero"}