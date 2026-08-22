import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

@pytest.fixture
def admin_token(client):
    response = client.post("/login", json={
        "username": "admin1",
        "password": "adminpass123"
    })
    return response.get_json()["access_token"]

@pytest.fixture
def staff_token(client):
    response = client.post("/login", json={
        "username": "staff1",
        "password": "staffpass123"
    })
    return response.get_json()["access_token"]