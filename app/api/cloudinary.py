from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import time, hashlib

from app.api.deps import get_db
from app.models.users import User
from app.utils.auth import get_current_active_user
import os


router = APIRouter(prefix="/cloudinary", tags=["Cloudinary"])



def _generate_signature(params: dict, api_secret: str) -> str:
    """
    Cloudinary signature:
    1. Sort params by key.
    2. Build 'key=value&key2=value2' string.
    3. signature = SHA1( string_to_sign + api_secret )
    """
    to_sign = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if v is not None)
    raw = f"{to_sign}{api_secret}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


@router.get("/sign-upload")
def get_cloudinary_signature(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Returns a signed payload for uploading directly to Cloudinary from the frontend.
    """
    timestamp = int(time.time())

    # Optional: put each user’s files in their own folder
    folder = f"artloom360/{current_user.user_id}"

    params = {
        "timestamp": timestamp,
        "folder": folder,
    }

    signature = _generate_signature(params, os.getenv("CLOUDINARY_API_SECRET"))

    return {
        "timestamp": timestamp,
        "signature": signature,
        "api_key": os.getenv("CLOUDINARY_API_KEY"),
        "cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME"),
        "folder": folder,
    }
