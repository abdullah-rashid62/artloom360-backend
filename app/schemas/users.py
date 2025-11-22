# app/schemas/users.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# --------------------
# Shared (returned fields)
# --------------------
class UserBase(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    profile_pic: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

# --------------------
# Create
# --------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# --------------------
# Update
# --------------------
class UserUpdate(BaseModel):
    name: Optional[str]
    profile_pic: Optional[str]
    password: Optional[str]

# --------------------
# Response
# --------------------
class UserResponse(UserBase):
    pass
