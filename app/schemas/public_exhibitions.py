# app/schemas/public_exhibitions.py
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class PublicArtistSummary(BaseModel):
    user_id: str
    name: str
    avatar_url: Optional[str] = None


class PublicExhibitionAnalytics(BaseModel):
    total_views: int = 0
    total_likes: int = 0
    avg_rating: Optional[float] = None


class PublicExhibitionResponse(BaseModel):
    exhibition_id: str
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    artist: PublicArtistSummary
    analytics: PublicExhibitionAnalytics
    config: Optional[Dict[str, Any]] = None  # enriched config


# --- Reviews ---

class ReviewResponse(BaseModel):
    review_id: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # pydantic v2 style to load directly from SQLAlchemy model


class PublicReviewCreate(BaseModel):
    # frontend sends name but backend doesn't store it;
    # we just ignore it and show "Visitor" on UI.
    name: Optional[str] = None
    rating: int
    comment: str


class PublicReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
