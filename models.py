from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    birthday = Column(Date, nullable=True)
    additional_info = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Associate with a user

    user = relationship("User", back_populates="contacts")