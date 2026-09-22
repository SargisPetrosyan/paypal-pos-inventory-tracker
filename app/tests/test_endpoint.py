from fastapi.testclient import TestClient
from httpx import Response
from app.main import app
import pytest
from app.tests.mocked_data import mock_invalid_inventory_data
from pydantic import ValidationError

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

def test_inventory_data_validation():

    with pytest.raises(expected_exception=ValidationError):
            client.post(
        url="/inventory_tracker_webhook",
        json=mock_invalid_inventory_data,
            )
