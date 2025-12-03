# app/schemas/website.py
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel


# -------------------------------------------------
# Base Website schemas (used by CRUD + responses)
# -------------------------------------------------

class WebsiteBase(BaseModel):
    
    title: Optional[str] = None
    theme: Optional[str] = "default"
    config: Dict[str, Any] = {}   # hero, about, artworks_section, etc.
    status: str = "draft"         # 'draft', 'published', 'archived'


class WebsiteCreate(WebsiteBase):
    """Used when creating from admin or tests.
       For /websites/me we’ll build payload manually on PUT."""
    pass


class WebsiteUpdate(BaseModel):
    """Partial update for website (used in /websites/{id} and /websites/me)."""
    
    title: Optional[str] = None
    theme: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    published_url: Optional[str] = None  # set by backend when publishing


class WebsiteResponse(WebsiteBase):
    website_id: str
    artist_id: str
    published_url: Optional[str] = None
    # we don’t expose is_deleted here; it’s internal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------
# Extra schemas for builder + public website
# -------------------------------------------------

class ArtworkSummary(BaseModel):
    artwork_id: str
    title: str
    price: Optional[float] = None
    availability: Optional[str] = None
    file_url: Optional[str] = None

    class Config:
        from_attributes = True


class ArtistPublic(BaseModel):
    user_id: str
    name: str
    profile_pic: Optional[str] = None

    class Config:
        from_attributes = True


class WebsiteMeResponse(BaseModel):
    website: WebsiteResponse
    artworks: List[ArtworkSummary]
    artist: ArtistPublic


class PublicWebsiteResponse(BaseModel):
    website: WebsiteResponse
    artist: ArtistPublic
    artworks: List[ArtworkSummary]
