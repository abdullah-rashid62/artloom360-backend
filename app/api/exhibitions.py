from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import ExhibitionCreate, ExhibitionUpdate, ExhibitionResponse
from app.crud import exhibitions as crud_exhibitions
from app.api.deps import get_db

router = APIRouter(prefix="/exhibitions", tags=["Exhibitions"])

@router.post("/{artist_id}", response_model=ExhibitionResponse)
def create_exhibition(artist_id: str, exhibition: ExhibitionCreate, db: Session = Depends(get_db)):
    return crud_exhibitions.create_exhibition(db, artist_id, exhibition)

@router.get("/{exhibition_id}", response_model=ExhibitionResponse)
def get_exhibition(exhibition_id: str, db: Session = Depends(get_db)):
    db_exhibition = crud_exhibitions.get_exhibition(db, exhibition_id)
    if not db_exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    return db_exhibition

@router.get("/artist/{artist_id}", response_model=List[ExhibitionResponse])
def get_exhibitions_by_artist(artist_id: str, db: Session = Depends(get_db)):
    return crud_exhibitions.get_exhibitions_by_artist(db, artist_id)

@router.put("/{exhibition_id}", response_model=ExhibitionResponse)
def update_exhibition(exhibition_id: str, updates: ExhibitionUpdate, db: Session = Depends(get_db)):
    db_exhibition = crud_exhibitions.get_exhibition(db, exhibition_id)
    if not db_exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    return crud_exhibitions.update_exhibition(db, db_exhibition, updates)

@router.delete("/{exhibition_id}")
def delete_exhibition(exhibition_id: str, db: Session = Depends(get_db)):
    db_exhibition = crud_exhibitions.get_exhibition(db, exhibition_id)
    if not db_exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    crud_exhibitions.delete_exhibition(db, db_exhibition)
    return {"detail": "Exhibition deleted successfully"}
