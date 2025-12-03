# app/api/auth.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.utils.auth import get_current_active_user
from app.models import User  # your SQLAlchemy user model

router = APIRouter(prefix="/auth", tags=["auth"])


class UserResponse(BaseModel):
    user_id: str
    name: str | None = None
    email: str

    class Config:
        from_attributes = True  # pydantic v2

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
