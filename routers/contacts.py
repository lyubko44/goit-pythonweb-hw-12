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
    db_contact = Contact(**contact.dict(), user_id=current_user)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.get("/", response_model=List[ContactResponse])
def list_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                  current_user: str = Depends(get_current_user)):
    return db.query(Contact).filter(Contact.user_id == current_user).offset(skip).limit(limit).all()


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact: ContactCreate, db: Session = Depends(get_db),
                   current_user: str = Depends(get_current_user)):
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
