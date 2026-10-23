from fastapi.testclient import TestClient
from httpx import Response
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import pytest

from app.core.config import get_db_session
from app.main import app
from app.tests.mocked_data import mock_valid_inventory_data

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")  
def client_fixture(session: Session):
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_db_session] = get_session_override

    client = TestClient(app)  
    yield client  
    app.dependency_overrides.clear()  


def test_create_inventory_record(client: TestClient):
    response: Response = client.post(
        url="/inventory_tracker_webhook", json=mock_valid_inventory_data
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"message": "Data registered in db"}


def test_duplicate_inventory_record(client: TestClient):
    client.post(
        url="/inventory_tracker_webhook", json=mock_valid_inventory_data
    )
    response_2: Response = client.post(
        url="/inventory_tracker_webhook", json=mock_valid_inventory_data
    )
    app.dependency_overrides.clear()

    assert response_2.status_code == 200
    assert response_2.json()[0] == {"message": "Data already exist in db"}
