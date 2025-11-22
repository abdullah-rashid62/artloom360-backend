# app/schemas/exhibitions.py
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

class ExhibitionBase(BaseModel):
    exhibition_id: str
    artist_id: str
    title: str
    description: Optional[str]
    background_music_url: Optional[str]
    config: Optional[Any]
    published_url: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ExhibitionCreate(BaseModel):
    title: str
    description: Optional[str]
    background_music_url: Optional[str]
    config: Optional[Any]

class ExhibitionUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    background_music_url: Optional[str]
    config: Optional[Any]
    status: Optional[str]

class ExhibitionResponse(ExhibitionBase):
    pass
