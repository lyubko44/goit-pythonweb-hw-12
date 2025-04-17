from jose import jwt, JWTError

from utils.email_utils import send_email
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from auth import create_access_token, get_password_hash
from database import get_db
from models import User
from schemas import PasswordResetRequest, PasswordResetConfirm

router = APIRouter(
    prefix="/password-reset",
    tags=["password-reset"]
)


@router.post("/request")
def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Requests a password reset by sending a token to the user's email.
    """
    user = db.query(User).filter(User.username == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )

    reset_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=15))

    send_email(
        to=user.username,
        subject="Password Reset Request",
        body=f"Use this token to reset your password: {reset_token}"
    )
    return {"message": "Password reset token sent to your email."}


@router.post("/confirm")
def confirm_password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Confirms the password reset using the token.
    """
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password has been reset successfully."}
