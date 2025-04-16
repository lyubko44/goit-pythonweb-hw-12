from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_contact():
    login_response = client.post(
        "/users/token",
        data={"username": "testuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_response.json()["access_token"]
    response = client.post(
        "/contacts/",
        json={"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "birthday": "1990-01-01"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "John"


def test_list_contacts():
    login_response = client.post(
        "/users/token",
        data={"username": "testuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_response.json()["access_token"]
    response = client.get(
        "/contacts/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
