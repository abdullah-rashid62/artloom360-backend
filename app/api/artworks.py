from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import ArtworkCreate, ArtworkUpdate, ArtworkResponse
from app.crud import artworks as crud_artworks
from app.api.deps import get_db

router = APIRouter(prefix="/artworks", tags=["Artworks"])

@router.post("/{artist_id}", response_model=ArtworkResponse)
def create_artwork(artist_id: str, artwork: ArtworkCreate, db: Session = Depends(get_db)):
    return crud_artworks.create_artwork(db, artist_id, artwork)

@router.get("/{artwork_id}", response_model=ArtworkResponse)
def get_artwork(artwork_id: str, db: Session = Depends(get_db)):
    db_artwork = crud_artworks.get_artwork(db, artwork_id)
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return db_artwork

@router.get("/artist/{artist_id}", response_model=List[ArtworkResponse])
def get_artworks_by_artist(artist_id: str, db: Session = Depends(get_db)):
    return crud_artworks.get_artworks_by_artist(db, artist_id)

@router.put("/{artwork_id}", response_model=ArtworkResponse)
def update_artwork(artwork_id: str, updates: ArtworkUpdate, db: Session = Depends(get_db)):
    db_artwork = crud_artworks.get_artwork(db, artwork_id)
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return crud_artworks.update_artwork(db, db_artwork, updates)

@router.delete("/{artwork_id}")
def delete_artwork(artwork_id: str, db: Session = Depends(get_db)):
    db_artwork = crud_artworks.get_artwork(db, artwork_id)
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    crud_artworks.delete_artwork(db, db_artwork)
    return {"detail": "Artwork deleted successfully"}
