from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import extract, or_, and_

from models import Contact
from database import get_db
from auth import get_current_user
from schemas import ContactCreate, ContactResponse

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"]
)


@router.post("/", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db),
                   current_user: str = Depends(get_current_user)):
    """
    Creates a new contact for the current user.

    Args:
        contact (ContactCreate): The contact data to create.
        db (Session): The database session.
        current_user (str): The current authenticated user.

    Returns:
        ContactResponse: The created contact.
    """
    db_contact = Contact(**contact.dict(), user_id=current_user)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.get("/", response_model=List[ContactResponse])
def list_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                  current_user: str = Depends(get_current_user)):
    """
    Retrieves a list of contacts for the current user.

    Args:
        skip (int): The number of records to skip.
        limit (int): The maximum number of records to return.
        db (Session): The database session.
        current_user (str): The current authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts.
    """
    return db.query(Contact).filter(Contact.user_id == current_user).offset(skip).limit(limit).all()


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Retrieves a specific contact by ID.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (Session): The database session.
        current_user (str): The current authenticated user.

    Returns:
        ContactResponse: The requested contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact: ContactCreate, db: Session = Depends(get_db),
                   current_user: str = Depends(get_current_user)):
    """
    Updates an existing contact.

    Args:
        contact_id (int): The ID of the contact to update.
        contact (ContactCreate): The updated contact data.
        db (Session): The database session.
        current_user (str): The current authenticated user.

    Returns:
        ContactResponse: The updated contact.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Deletes a contact by ID.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (Session): The database session.
        current_user (str): The current authenticated user.

    Returns:
        dict: A message indicating the contact was deleted.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
    return {"detail": "Contact deleted"}


@router.get("/search/", response_model=List[ContactResponse])
def search_contacts(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    """
    Searches for contacts based on the provided criteria.

    Args:
        first_name (Optional[str]): The first name to search for.
        last_name (Optional[str]): The last name to search for.
        email (Optional[str]): The email to search for.
        db (Session): The database session.
        current_user (str): The current authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts matching the search criteria.
    """
    query = db.query(Contact).filter(Contact.user_id == current_user)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()


@router.get("/upcoming_birthdays/", response_model=List[ContactResponse])
def get_upcoming_birthdays(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Retrieves contacts with upcoming birthdays within the next 7 days.

    Args:
        db (Session): The database session.
        current_user (str): The current authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(Contact).filter(
        Contact.user_id == current_user,
        or_(
            and_(
                extract('month', Contact.birthday) == today.month,
                extract('day', Contact.birthday) >= today.day
            ),
            and_(
                extract('month', Contact.birthday) == next_week.month,
                extract('day', Contact.birthday) <= next_week.day
            )
        )
    ).all()
