# app/schemas/artworks.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ArtworkBase(BaseModel):
    artwork_id: str
    artist_id: str
    title: str
    description: Optional[str]
    file_url: Optional[str]
    thumbnail_url: Optional[str]
    file_type: str
    price: Optional[float]
    is_for_sale: bool
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ArtworkCreate(BaseModel):
    title: str
    description: Optional[str]
    file_url: Optional[str]
    thumbnail_url: Optional[str]
    file_type: str
    price: Optional[float]
    is_for_sale: bool = False

class ArtworkUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    file_url: Optional[str]
    thumbnail_url: Optional[str]
    file_type: Optional[str]
    price: Optional[float]
    is_for_sale: Optional[bool]
    status: Optional[str]

class ArtworkResponse(ArtworkBase):
    pass
