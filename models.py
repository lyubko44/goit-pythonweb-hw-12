from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    Represents a user in the database.

    Attributes:
        id (int): The primary key of the user.
        username (str): The username of the user.
        hashed_password (str): The hashed password of the user.
        contacts (list): A list of contacts associated with the user.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    contacts = relationship("Contact", back_populates="user")


class Contact(Base):
    """
    Represents a contact in the database.

    Attributes:
        id (int): The primary key of the contact.
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact.
        phone_number (str): The phone number of the contact.
        birthday (Date): The birthday of the contact.
        additional_info (str): Additional information about the contact.
        user_id (int): The ID of the user who owns the contact.
        user (User): The user associated with the contact.
    """
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    birthday = Column(Date, nullable=True)
    additional_info = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="contacts")
