import pytest
from app import app as flask_app, db, User

@pytest.fixture(autouse=True)
def setup_database():
    with flask_app.app_context():
        db.create_all()

        if not User.query.filter_by(username="admin1").first():
            admin = User(username="admin1", role="admin")
            admin.set_password("adminpass123")
            db.session.add(admin)

        if not User.query.filter_by(username="staff1").first():
            staff = User(username="staff1", role="staff")
            staff.set_password("staffpass123")
            db.session.add(staff)

        db.session.commit()

    yield


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