from sqlalchemy.orm import Session
from app.models import Website
from app.schemas import WebsiteCreate, WebsiteUpdate
from typing import List, Optional

def get_website(db: Session, website_id: str) -> Optional[Website]:
    return db.query(Website).filter(Website.website_id == website_id).first()

def get_websites_by_artist(db: Session, artist_id: str) -> List[Website]:
    return db.query(Website).filter(Website.artist_id == artist_id).all()

def create_website(db: Session, artist_id: str, website: WebsiteCreate) -> Website:
    db_website = Website(
        artist_id=artist_id,
        domain=website.domain,
        title=website.title,
        theme=website.theme,
        config=website.config
    )
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website

def update_website(db: Session, db_website: Website, updates: WebsiteUpdate) -> Website:
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_website, field, value)
    db.commit()
    db.refresh(db_website)
    return db_website

def delete_website(db: Session, db_website: Website):
    db.delete(db_website)
    db.commit()
