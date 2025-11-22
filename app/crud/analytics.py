from sqlalchemy.orm import Session
from app.models import ViewEvent, LikeEvent, WatchTimeEvent, Review
from app.schemas import ViewEventCreate, LikeEventCreate, WatchTimeCreate, ReviewCreate
from typing import List

# ------------------------------
# Views
# ------------------------------
def record_view(db: Session, data: ViewEventCreate) -> ViewEvent:
    db_view = ViewEvent(**data.dict())
    db.add(db_view)
    db.commit()
    db.refresh(db_view)
    return db_view

# ------------------------------
# Likes
# ------------------------------
def record_like(db: Session, data: LikeEventCreate) -> LikeEvent:
    db_like = LikeEvent(**data.dict())
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like

# ------------------------------
# Watch Time
# ------------------------------
def record_watch_time(db: Session, data: WatchTimeCreate) -> WatchTimeEvent:
    db_watch = WatchTimeEvent(**data.dict())
    db.add(db_watch)
    db.commit()
    db.refresh(db_watch)
    return db_watch

# ------------------------------
# Reviews
# ------------------------------
def record_review(db: Session, data: ReviewCreate) -> Review:
    db_review = Review(**data.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review
