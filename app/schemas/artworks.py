# app/schemas/artworks.py
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.exhibitions import ReviewResponse 


# ---------- Core Artwork Schemas ----------

class ArtworkBase(BaseModel):
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    file_url: Optional[str] = None
    file_type: str  # 'image', 'video', 'model_3d'
    price: Optional[Decimal] = None
    availability: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    edition_current: Optional[int] = None
    edition_total: Optional[int] = None

    height: Optional[Decimal] = None
    width: Optional[Decimal] = None
    length: Optional[Decimal] = None

    status: Optional[str] = "draft"


class ArtworkCreate(ArtworkBase):
    # if you want any required fields for creation beyond ArtworkBase, add here
    pass


class ArtworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    price: Optional[Decimal] = None
    availability: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    edition_current: Optional[int] = None
    edition_total: Optional[int] = None

    height: Optional[Decimal] = None
    width: Optional[Decimal] = None
    length: Optional[Decimal] = None

    status: Optional[str] = None


class ArtworkResponse(ArtworkBase):
    model_config = ConfigDict(from_attributes=True)
    artwork_id: str
    artist_id: str
    created_at: datetime
    updated_at: datetime


# ---------- Analytics block ----------

class ArtworkAnalytics(BaseModel):
    total_views: int
    total_likes: int
    total_watch_seconds: int
    sold: int
    revenue: Optional[Decimal] = Decimal("0.00")
    avg_rating: Optional[float]
    last_viewed: Optional[datetime]
    conversion_rate: float                 
    avg_view_duration_seconds: Optional[float]
    created_at: datetime                  


# ---------- Combined node ----------

class ArtworkWithAnalyticsResponse(BaseModel):
    id: str                              
    artwork: ArtworkResponse
    analytics: ArtworkAnalytics
    reviews: List[ReviewResponse]
