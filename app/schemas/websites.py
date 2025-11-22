# app/schemas/websites.py
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

class WebsiteBase(BaseModel):
    website_id: str
    artist_id: str
    domain: Optional[str]
    title: Optional[str]
    theme: Optional[str]
    config: Optional[Any]
    published_url: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class WebsiteCreate(BaseModel):
    domain: Optional[str]
    title: Optional[str]
    theme: Optional[str]
    config: Optional[Any]

class WebsiteUpdate(BaseModel):
    domain: Optional[str]
    title: Optional[str]
    theme: Optional[str]
    config: Optional[Any]
    status: Optional[str]

class WebsiteResponse(WebsiteBase):
    pass
