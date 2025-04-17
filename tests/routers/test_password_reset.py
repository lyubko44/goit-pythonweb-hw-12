from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from auth import create_access_token, get_password_hash
from main import app
from models import User

client = TestClient(app)


class MockDBSession:
    def __init__(self):
        self.users = [
            User(username="testuser@example.com", hashed_password=get_password_hash("oldpassword"))
        ]

    def query(self, model):
        return self

    def filter(self, condition):
        username = condition.right.value
        user = next((u for u in self.users if u.username == username), None)
        return [user] if user else []

    def first(self):
        return self.users[0] if self.users else None

    def commit(self):
        pass


@pytest.fixture
def mock_db():
    return MockDBSession()


def test_request_password_reset_valid_email(mock_db, monkeypatch):
    def mock_get_db():
        return mock_db

    monkeypatch.setattr("routers.password_reset.get_db", mock_get_db)

    response = client.post("/password-reset/request", json={"email": "testuser@example.com"})
    assert response.status_code == 200
    assert response.json() == {"message": "Password reset token sent to your email."}


def test_request_password_reset_invalid_email(mock_db, monkeypatch):
    def mock_get_db():
        return mock_db

    monkeypatch.setattr("routers.password_reset.get_db", mock_get_db)

    response = client.post("/password-reset/request", json={"email": "nonexistent@example.com"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User with this email does not exist"}


def test_confirm_password_reset_valid_token(mock_db, monkeypatch):
    def mock_get_db():
        return mock_db

    monkeypatch.setattr("routers.password_reset.get_db", mock_get_db)

    token = create_access_token(data={"sub": "testuser@example.com"}, expires_delta=timedelta(minutes=15))
    response = client.post("/password-reset/confirm", json={"token": token, "new_password": "newpassword"})
    assert response.status_code == 200
    assert response.json() == {"message": "Password has been reset successfully."}


def test_confirm_password_reset_invalid_token(mock_db, monkeypatch):
    def mock_get_db():
        return mock_db

    monkeypatch.setattr("routers.password_reset.get_db", mock_get_db)

    response = client.post("/password-reset/confirm", json={"token": "invalidtoken", "new_password": "newpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid token"}


def test_confirm_password_reset_nonexistent_user(mock_db, monkeypatch):
    def mock_get_db():
        return mock_db

    monkeypatch.setattr("routers.password_reset.get_db", mock_get_db)

    token = create_access_token(data={"sub": "nonexistent@example.com"}, expires_delta=timedelta(minutes=15))
    response = client.post("/password-reset/confirm", json={"token": token, "new_password": "newpassword"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
