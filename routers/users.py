from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
import cloudinary.uploader

from auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


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
