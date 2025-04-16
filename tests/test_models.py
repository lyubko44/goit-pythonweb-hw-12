import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import User, Contact

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)  # Create tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Drop tables after test


def test_create_user(test_db):
    user = User(username="testuser", hashed_password="hashedpassword")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.hashed_password == "hashedpassword"


def test_create_contact(test_db):
    user = User(username="testuser", hashed_password="hashedpassword")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        user_id=user.id,
    )
    test_db.add(contact)
    test_db.commit()
    test_db.refresh(contact)

    assert contact.id is not None
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john.doe@example.com"
    assert contact.user_id == user.id


def test_user_contact_relationship(test_db):
    user = User(username="testuser", hashed_password="hashedpassword")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        user_id=user.id,
    )
    test_db.add(contact)
    test_db.commit()
    test_db.refresh(contact)

    assert len(user.contacts) == 1
    assert user.contacts[0].first_name == "John"
    assert user.contacts[0].email == "john.doe@example.com"
