import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")  # from .env

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def init_db():
    """
    Initializes the database by creating all tables defined in the models.
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[SessionLocal, None, None]:
    """
    Provides a database session generator.

    Yields:
        SessionLocal: A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
