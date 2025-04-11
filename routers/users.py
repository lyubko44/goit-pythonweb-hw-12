from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
import cloudinary.uploader

from auth import get_current_user, get_password_hash
from database import get_db
from models import User
from schemas import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/me")
def read_current_user(current_user: str = Depends(get_current_user)):
    return {"username": current_user}


@router.put("/me/avatar")
def update_avatar(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="user_avatars",
            public_id=f"user_{current_user}_avatar",
            overwrite=True,
            resource_type="image"
        )
        return {"avatar_url": result.get("secure_url")}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to upload avatar")