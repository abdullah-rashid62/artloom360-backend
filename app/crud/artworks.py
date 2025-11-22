from sqlalchemy.orm import Session
from app.models import Artwork
from app.schemas import ArtworkCreate, ArtworkUpdate
from typing import List, Optional

# ------------------------------
# Get Artwork by ID
# ------------------------------
def get_artwork(db: Session, artwork_id: str) -> Optional[Artwork]:
    return db.query(Artwork).filter(Artwork.artwork_id == artwork_id).first()

# ------------------------------
# Get all artworks by artist
# ------------------------------
def get_artworks_by_artist(db: Session, artist_id: str) -> List[Artwork]:
    return db.query(Artwork).filter(Artwork.artist_id == artist_id).all()

# ------------------------------
# Create Artwork
# ------------------------------
def create_artwork(db: Session, artist_id: str, artwork: ArtworkCreate) -> Artwork:
    db_artwork = Artwork(
        artist_id=artist_id,
        title=artwork.title,
        description=artwork.description,
        file_url=artwork.file_url,
        thumbnail_url=artwork.thumbnail_url,
        file_type=artwork.file_type,
        price=artwork.price,
        is_for_sale=artwork.is_for_sale
    )
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork

# ------------------------------
# Update Artwork
# ------------------------------
def update_artwork(db: Session, db_artwork: Artwork, updates: ArtworkUpdate) -> Artwork:
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_artwork, field, value)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork

# ------------------------------
# Delete Artwork
# ------------------------------
def delete_artwork(db: Session, db_artwork: Artwork):
    db.delete(db_artwork)
    db.commit()
