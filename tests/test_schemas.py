import pytest
from pydantic import ValidationError

from schemas import ContactCreate, UserCreate, ContactResponse


def test_contact_create_schema():
    # Valid data
    valid_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "1234567890",
        "birthday": "1990-01-01",
        "additional_info": "Some info"
    }
    contact = ContactCreate(**valid_data)
    assert contact.first_name == "John"
    assert contact.email == "john.doe@example.com"

    # Invalid data
    invalid_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "invalid-email",
        "phone_number": "1234567890"
    }
    with pytest.raises(ValidationError):
        ContactCreate(**invalid_data)


def test_user_create_schema():
    # Valid data
    valid_data = {
        "username": "user@example.com",
        "password": "securepassword"
    }
    user = UserCreate(**valid_data)
    assert user.username == "user@example.com"
    assert user.password == "securepassword"

    # Invalid data
    invalid_data = {
        "username": "invalid-email",
        "password": "securepassword"
    }
    with pytest.raises(ValidationError):
        UserCreate(**invalid_data)


def test_contact_response_schema():
    # Valid data
    valid_data = {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "1234567890",
        "birthday": "1990-01-01",
        "additional_info": "Some info"
    }
    contact_response = ContactResponse(**valid_data)
    assert contact_response.id == 1
    assert contact_response.first_name == "John"
    assert contact_response.email == "john.doe@example.com"
