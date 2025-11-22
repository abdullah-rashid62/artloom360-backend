from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import WebsiteCreate, WebsiteUpdate, WebsiteResponse
from app.crud import websites as crud_websites
from app.api.deps import get_db

router = APIRouter(prefix="/websites", tags=["Websites"])

@router.post("/{artist_id}", response_model=WebsiteResponse)
def create_website(artist_id: str, website: WebsiteCreate, db: Session = Depends(get_db)):
    return crud_websites.create_website(db, artist_id, website)

@router.get("/{website_id}", response_model=WebsiteResponse)
def get_website(website_id: str, db: Session = Depends(get_db)):
    db_website = crud_websites.get_website(db, website_id)
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    return db_website

@router.get("/artist/{artist_id}", response_model=List[WebsiteResponse])
def get_websites_by_artist(artist_id: str, db: Session = Depends(get_db)):
    return crud_websites.get_websites_by_artist(db, artist_id)

@router.put("/{website_id}", response_model=WebsiteResponse)
def update_website(website_id: str, updates: WebsiteUpdate, db: Session = Depends(get_db)):
    db_website = crud_websites.get_website(db, website_id)
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    return crud_websites.update_website(db, db_website, updates)

@router.delete("/{website_id}")
def delete_website(website_id: str, db: Session = Depends(get_db)):
    db_website = crud_websites.get_website(db, website_id)
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    crud_websites.delete_website(db, db_website)
    return {"detail": "Website deleted successfully"}
