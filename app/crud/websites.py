# app/crud/websites.py
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Website
from app.schemas import WebsiteCreate, WebsiteUpdate


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
        config=website.config,
        status=website.status,
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


# SOFT delete (archive)
def delete_website(db: Session, db_website: Website) -> Website:
    db_website.is_deleted = True
    db_website.status = "archived"
    db.commit()
    db.refresh(db_website)
    return db_website


# ------------------------
# Extra helpers for builder
# ------------------------
def get_active_website_by_artist(db: Session, artist_id: str) -> Optional[Website]:
    return (
        db.query(Website)
        .filter(
            Website.artist_id == artist_id,
            Website.is_deleted == False,
        )
        .order_by(Website.created_at.asc())
        .first()
    )

def get_or_create_website_for_artist(
    db: Session,
    artist_id: str,
    default_domain: Optional[str] = None,
    default_title: Optional[str] = None,
    default_theme: str = "default",
) -> Website:
    website = get_active_website_by_artist(db, artist_id)
    if website:
        return website

    db_website = Website(
        artist_id=artist_id,
        domain=default_domain,
        title=default_title,
        theme=default_theme,
        config={},
        status="draft",
        is_deleted=False,
    )
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website


def get_website_by_domain(
    db: Session,
    domain: str,
    only_published: bool = True,
) -> Optional[Website]:
    q = db.query(Website).filter(
        Website.domain == domain,
        Website.is_deleted == False,
    )
    if only_published:
        q = q.filter(Website.status == "published")
    return q.first()
