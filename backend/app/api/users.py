from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DbSession
from app.core.security import verify_password, hash_password
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import PasswordChangeRequest, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users"])
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_PROFILE_IMAGE_BYTES = 5 * 1024 * 1024


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: CurrentUser) -> User:
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(payload: UserUpdateRequest, current_user: CurrentUser, db: DbSession) -> User:
    updates = payload.model_dump(exclude_unset=True)
    if "email" in updates:
        email = str(updates["email"]).lower()
        existing = db.scalar(select(User).where(User.email == email, User.id != current_user.id))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")
        updates["email"] = email
    for field, value in updates.items():
        setattr(current_user, field, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(payload: PasswordChangeRequest, current_user: CurrentUser, db: DbSession) -> None:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")
    current_user.password_hash = hash_password(payload.new_password)
    db.commit()


@router.post("/me/profile-image", response_model=UserResponse)
def upload_profile_image(
    current_user: CurrentUser,
    db: DbSession,
    image: UploadFile = File(...),
) -> User:
    """Store a small profile image with a generated filename, never the client filename."""
    extension = ALLOWED_IMAGE_TYPES.get(image.content_type or "")
    if extension is None:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Use a JPG, PNG, or WebP image.")
    content = image.file.read(MAX_PROFILE_IMAGE_BYTES + 1)
    if len(content) > MAX_PROFILE_IMAGE_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Profile image must be 5 MB or smaller.")
    destination_dir = Path(settings.upload_dir) / "profiles" / str(current_user.id)
    destination_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    (destination_dir / filename).write_bytes(content)
    current_user.profile_image = f"/uploads/profiles/{current_user.id}/{filename}"
    db.commit()
    db.refresh(current_user)
    return current_user
