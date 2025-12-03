from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# --------------------
# Token Data (for JWT decoding)
# --------------------
class TokenData(BaseModel):
    user_id: Optional[str] = None


# --------------------
# Shared fields (returned for any user)
# --------------------
class UserBase(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    profile_pic: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


# --------------------
# Create User (Signup)
# --------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# --------------------
# Update User
# --------------------
class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_pic: Optional[str] = None
    password: Optional[str] = None


# --------------------
# Response Schema (Used in API responses)
# --------------------
class UserResponse(UserBase):
    pass


# --------------------
# Login Schema
# --------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# --------------------
# Token Response Schema
# --------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
