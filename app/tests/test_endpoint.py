from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from app.main import app

client = TestClient(app)

def test_event_checking():
        response: Response = client.post(
                url="/inventory_tracker_webhook", 
                json={
                    "eventName" :"TestMessage",
                    "title": "New Book", 
                    "author": "Author 1", 
                    "description": "Description 1"
                    })
        assert response.status_code == 200
