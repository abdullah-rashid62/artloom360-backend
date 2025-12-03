# app/schemas/exhibitions.py
from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel, ConfigDict
from decimal import Decimal


# ------------------------------------------------------------------------------
# Review Schema (shared with artworks dashboard)
# ------------------------------------------------------------------------------
class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime


# ------------------------------------------------------------------------------
# Core Exhibition Schemas
# ------------------------------------------------------------------------------

class ExhibitionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exhibition_id: str
    artist_id: str
    title: str
    description: Optional[str] = None
    config: Optional[Any] = None
    thumbnail_url: Optional[str] = None
    status: str                                            
    created_at: datetime
    updated_at: datetime


class ExhibitionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    background_music_url: Optional[str] = None
    config: Optional[Any] = None         
    thumbnail_url: Optional[str] = None
    status: Optional[str] = "draft"      


class ExhibitionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    background_music_url: Optional[str] = None
    config: Optional[Any] = None
    status: Optional[str] = None
    is_deleted: Optional[bool] = None

    # 🔹 Optional on update
    thumbnail_url: Optional[str] = None


class ExhibitionResponse(ExhibitionBase):
    pass


# ------------------------------------------------------------------------------
# Dashboard Analytics Schemas for Exhibitions
# ------------------------------------------------------------------------------

class ExhibitionAnalytics(BaseModel):
    total_views: int
    total_likes: int
    total_watch_seconds: int

    sold: int
    revenue: Decimal                    # defaulted to 0.00 in code

    avg_rating: Optional[float] = None
    last_viewed: Optional[datetime] = None

    conversion_rate: float              # 0.023 → "2.3%"
    avg_view_duration_seconds: Optional[float] = None

    created_at: datetime                # for FE → createdDate


class ExhibitionWithAnalyticsResponse(BaseModel):
    id: str
    exhibition: ExhibitionResponse
    analytics: ExhibitionAnalytics
    reviews: List[ReviewResponse]
