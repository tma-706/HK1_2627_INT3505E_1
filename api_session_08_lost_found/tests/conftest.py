import pytest

from app import create_app
from models import db


@pytest.fixture()
def app():
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        }
    )
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def _login(client, email, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.get_json()['token']}"}


@pytest.fixture()
def seeker_headers(client):
    return _login(client, "seeker@example.com", "seeker123")


@pytest.fixture()
def finder_headers(client):
    return _login(client, "finder@example.com", "finder123")


@pytest.fixture()
def lost_payload():
    return {
        "title": "Lost black backpack",
        "description": "Black backpack with a blue keychain",
        "category": "BAG",
        "location": "Main Library",
        "event_time": "2026-11-16T09:00:00+07:00",
        "image_urls": [],
    }


@pytest.fixture()
def found_payload():
    return {
        "title": "Black backpack found",
        "description": "Found a black backpack with a blue keychain",
        "category": "BAG",
        "location": "Main Library",
        "event_time": "2026-11-16T10:00:00+07:00",
        "image_urls": ["https://example.test/images/backpack.jpg"],
    }
