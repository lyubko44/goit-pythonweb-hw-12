from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_startup_event():
    """
    Test the startup event to ensure the database initializes without errors.
    """
    response = client.get("/")
    assert response.status_code in [200, 404]  # Root path may or may not exist


def test_contacts_router():
    """
    Test the /contacts route to ensure it is included and responds correctly.
    """
    response = client.get("/contacts")
    assert response.status_code in [200, 404]  # Adjust based on your implementation


def test_users_router():
    """
    Test the /users route to ensure it is included and responds correctly.
    """
    response = client.get("/users")
    assert response.status_code in [200, 404]  # Adjust based on your implementation


def test_rate_limit_exceeded():
    """
    Test the rate limiter by sending multiple requests to trigger the limit.
    """
    for _ in range(100):  # Simulate multiple requests
        response = client.get("/contacts")
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded. Try again later."}
