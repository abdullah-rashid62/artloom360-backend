from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas import ViewEventCreate, LikeEventCreate, WatchTimeCreate, ReviewCreate
from app.schemas import ViewEventBase, LikeEventBase, WatchTimeBase, ReviewBase
from app.crud import analytics as crud_analytics
from app.api.deps import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Views
@router.post("/views", response_model=ViewEventBase)
def record_view(data: ViewEventCreate, db: Session = Depends(get_db)):
    return crud_analytics.record_view(db, data)

# Likes
@router.post("/likes", response_model=LikeEventBase)
def record_like(data: LikeEventCreate, db: Session = Depends(get_db)):
    return crud_analytics.record_like(db, data)

# Watch Time
@router.post("/watch-time", response_model=WatchTimeBase)
def record_watch_time(data: WatchTimeCreate, db: Session = Depends(get_db)):
    return crud_analytics.record_watch_time(db, data)

# Reviews
@router.post("/reviews", response_model=ReviewBase)
def record_review(data: ReviewCreate, db: Session = Depends(get_db)):
    return crud_analytics.record_review(db, data)
