from sqlalchemy.orm import Session
from app.models import Exhibition
from app.schemas import ExhibitionCreate, ExhibitionUpdate
from typing import List, Optional

def get_exhibition(db: Session, exhibition_id: str) -> Optional[Exhibition]:
    return db.query(Exhibition).filter(Exhibition.exhibition_id == exhibition_id).first()

def get_exhibitions_by_artist(db: Session, artist_id: str) -> List[Exhibition]:
    return db.query(Exhibition).filter(Exhibition.artist_id == artist_id).all()

def create_exhibition(db: Session, artist_id: str, exhibition: ExhibitionCreate) -> Exhibition:
    db_exhibition = Exhibition(
        artist_id=artist_id,
        title=exhibition.title,
        description=exhibition.description,
        background_music_url=exhibition.background_music_url,
        config=exhibition.config
    )
    db.add(db_exhibition)
    db.commit()
    db.refresh(db_exhibition)
    return db_exhibition

def update_exhibition(db: Session, db_exhibition: Exhibition, updates: ExhibitionUpdate) -> Exhibition:
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_exhibition, field, value)
    db.commit()
    db.refresh(db_exhibition)
    return db_exhibition

def delete_exhibition(db: Session, db_exhibition: Exhibition):
    db.delete(db_exhibition)
    db.commit()
