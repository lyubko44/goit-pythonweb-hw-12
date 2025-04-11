from datetime import date, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, Request
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from sqlalchemy.sql import extract, or_, and_

from auth import decode_access_token, oauth2_scheme
from database import SessionLocal, init_db
from models import Contact

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )


@app.get("/users/me")
@limiter.limit("5/minute")  # Limit to 5 requests per minute
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: Optional[date] = None
    additional_info: Optional[str] = None


class ContactResponse(ContactCreate):
    id: int

    class Config:
        orm_mode = True


@app.on_event("startup")
async def startup_event():
    init_db()


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


@app.post("/contacts/", response_model=ContactResponse)
def create_contact(
        contact: ContactCreate,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    db_contact = Contact(**contact.dict(), user_id=current_user)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@app.get("/contacts/", response_model=List[ContactResponse])
def read_contacts(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    contacts = db.query(Contact).filter(Contact.user_id == current_user).offset(skip).limit(limit).all()
    return contacts


@app.get("/contacts/{contact_id}", response_model=ContactResponse)
def read_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
        contact_id: int,
        contact: ContactCreate,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@app.delete("/contacts/{contact_id}")
def delete_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
    return {"detail": "Contact deleted"}


@app.get("/contacts/search/", response_model=List[ContactResponse])
def search_contacts(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    query = db.query(Contact)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    contacts = query.all()
    return contacts


@app.get("/contacts/upcoming_birthdays/", response_model=List[ContactResponse])
def get_upcoming_birthdays(
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = db.query(Contact).filter(
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
    return contacts
