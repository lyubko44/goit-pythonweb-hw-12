from datetime import timedelta

from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    authenticate_user,
)
from models import User


# Mock database session
class MockDBSession:
    def __init__(self):
        self.users = [
            User(username="testuser", hashed_password=get_password_hash("testpassword"))
        ]

    def query(self, model):
        return self

    def filter(self, condition):
        username = condition.right.value
        user = next((u for u in self.users if u.username == username), None)
        return [user] if user else []

    def first(self):
        return self.users[0] if self.users else None


def test_get_password_hash():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert len(hashed_password) > 0


def test_verify_password():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password) is True
    assert verify_password("wrongpassword", hashed_password) is False


def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    decoded_data = decode_access_token(token)
    assert decoded_data["sub"] == "testuser"


def test_expired_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))  # Expired token
    try:
        decode_access_token(token)
        assert False, "Expired token should raise an exception"
    except Exception as e:
        assert "Invalid token" in str(e)


def test_invalid_access_token():
    invalid_token = "invalid.token.value"
    try:
        decode_access_token(invalid_token)
        assert False, "Invalid token should raise an exception"
    except Exception as e:
        assert "Invalid token" in str(e)


def test_authenticate_user():
    db = MockDBSession()
    user = authenticate_user("testuser", "testpassword", db)
    assert user is not None
    assert user.username == "testuser"

    invalid_user = authenticate_user("testuser", "wrongpassword", db)
    assert invalid_user is None


def test_missing_token():
    try:
        decode_access_token(None)
        assert False, "Missing token should raise an exception"
    except Exception as e:
        assert "Invalid token" in str(e)
