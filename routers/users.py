from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import cloudinary.uploader

from auth import get_current_user, get_password_hash, authenticate_user, create_access_token
from database import get_db
from models import User
from schemas import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.

    Args:
        user (UserCreate): The user data to register.
        db (Session): The database session.

    Returns:
        UserResponse: The registered user.
    """
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


@router.post("/token")
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    Authenticates a user and generates an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The login form data.
        db (Session): The database session.

    Returns:
        dict: The access token and token type.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)  # or ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user.

    Args:
        current_user (User): The authenticated user object.

    Returns:
        UserResponse: The details of the authenticated user.
    """
    return current_user


@router.put("/me/avatar")
def update_avatar(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """
        Update the avatar of the currently authenticated user.

        Args:
            file (UploadFile): The uploaded avatar file.
            current_user (User): The authenticated user object.

        Returns:
            dict: A dictionary containing the URL of the uploaded avatar.
        """
    result = cloudinary.uploader.upload(
        file.file,
        folder="user_avatars",
        public_id=f"user_{current_user.username}_avatar",
        overwrite=True,
        resource_type="image"
    )
    return {"avatar_url": result.get("secure_url")}
