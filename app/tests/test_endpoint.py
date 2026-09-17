from fastapi.testclient import TestClient
from httpx import Response
from app.main import app

client = TestClient(app)


def test_webhook() -> None:
    response: Response = client.post(
        url="/inventory_tracker_webhook",
        json={
            "eventName": "TestMessage",
            "title": "New Book",
            "author": "Author 1",
            "description": "Description 1",
        },
    )
    assert response.status_code == 200
    assert response.json()["response"]["message"]

def test_if_not_webhook_request():
    response: Response = client.post(
        url="/inventory_tracker_webhook",
        json={
            "eventName": "",
            "title": "New Book",
            "author": "Author 1",
            "description": "Description 1",
        },
    )
    assert response.status_code == 200
    assert response.json()["response"]["message"]
