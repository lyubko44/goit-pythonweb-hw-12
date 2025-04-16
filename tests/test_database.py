import pytest
from sqlalchemy.orm import Session
from database import init_db, get_db, engine, Base


def test_init_db():
    """
    Test that the database tables are created successfully.
    """
    try:
        init_db()
    except Exception as e:
        pytest.fail(f"init_db() raised an exception: {e}")


def test_get_db():
    """
    Test that the get_db function provides a valid database session.
    """
    session_generator = get_db()
    session = next(session_generator)
    assert isinstance(session, Session)
    session.close()
