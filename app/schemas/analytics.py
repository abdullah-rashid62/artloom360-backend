# app/schemas/analytics.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# ---------- Views ----------
class ViewEventBase(BaseModel):
    view_id: str
    target_type: str
    target_id: str
    session_id: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class ViewEventCreate(BaseModel):
    target_type: str
    target_id: str
    session_id: Optional[str]

# ---------- Likes ----------
class LikeEventBase(BaseModel):
    like_id: str
    target_type: str
    target_id: str
    session_id: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class LikeEventCreate(BaseModel):
    target_type: str
    target_id: str
    session_id: Optional[str]

# ---------- Watch Time ----------
class WatchTimeBase(BaseModel):
    watch_id: str
    target_type: str
    target_id: str
    session_id: Optional[str]
    seconds_watched: int
    created_at: datetime

    class Config:
        orm_mode = True

class WatchTimeCreate(BaseModel):
    target_type: str
    target_id: str
    session_id: Optional[str]
    seconds_watched: int

# ---------- Reviews ----------
class ReviewBase(BaseModel):
    review_id: str
    target_type: str
    target_id: str
    session_id: Optional[str]
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class ReviewCreate(BaseModel):
    target_type: str
    target_id: str
    rating: int
    comment: Optional[str]
    session_id: Optional[str]
