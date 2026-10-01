# app/api/websites.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import (
    WebsiteCreate,
    WebsiteUpdate,
    WebsiteResponse,
    WebsiteMeResponse,
    PublicWebsiteResponse,
    ArtworkSummary,
    ArtistPublic,
)
from app.crud import websites as crud_websites
from app.api.deps import get_db
from app.utils.auth import get_current_active_user
from app.models import Artwork, User

router = APIRouter(prefix="/websites", tags=["Websites"])


# -------------------------------------------------
# EXISTING CRUD ENDPOINTS (keep for admin/testing)
# -------------------------------------------------

@router.post("/{artist_id}", response_model=WebsiteResponse)
def create_website(
    artist_id: str,
    website: WebsiteCreate,
    db: Session = Depends(get_db),
):
    return crud_websites.create_website(db, artist_id, website)


# @router.get("/{website_id}", response_model=WebsiteResponse)
# def get_website(website_id: str, db: Session = Depends(get_db)):
#     db_website = crud_websites.get_website(db, website_id)
#     if not db_website:
#         raise HTTPException(status_code=404, detail="Website not found")
#     return WebsiteResponse.model_validate(db_website)


# @router.get("/artist/{artist_id}", response_model=List[WebsiteResponse])
# def get_websites_by_artist(artist_id: str, db: Session = Depends(get_db)):
#     db_websites = crud_websites.get_websites_by_artist(db, artist_id)
#     return [WebsiteResponse.model_validate(w) for w in db_websites]


# @router.put("/{website_id}", response_model=WebsiteResponse)
# def update_website(
#     website_id: str,
#     updates: WebsiteUpdate,
#     db: Session = Depends(get_db),
# ):
#     db_website = crud_websites.get_website(db, website_id)
#     if not db_website:
#         raise HTTPException(status_code=404, detail="Website not found")
#     db_website = crud_websites.update_website(db, db_website, updates)
#     return WebsiteResponse.model_validate(db_website)


# @router.delete("/{website_id}")
# def delete_website(website_id: str, db: Session = Depends(get_db)):
#     db_website = crud_websites.get_website(db, website_id)
#     if not db_website:
#         raise HTTPException(status_code=404, detail="Website not found")
#     crud_websites.delete_website(db, db_website)
#     return {"detail": "Website archived successfully"}


# -------------------------------------------------
# NEW: AUTHENTICATED BUILDER ENDPOINTS
# -------------------------------------------------

@router.get("/me", response_model=WebsiteMeResponse)
def get_my_website(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    default_domain = current_user.name.lower().replace(" ", "-")
    default_title = f"{current_user.name} — Portfolio"

    website = crud_websites.get_or_create_website_for_artist(
        db,
        artist_id=current_user.user_id,
        default_domain=default_domain,
        default_title=default_title,
    )

    artworks = (
        db.query(Artwork)
        .filter(
            Artwork.artist_id == current_user.user_id,
            Artwork.status != "archived",
            Artwork.status != "draft",
        )
        .all()
    )

    website_resp = WebsiteResponse.model_validate(website)
    artist_resp = ArtistPublic(
        user_id=current_user.user_id,
        name=current_user.name,
        profile_pic=getattr(current_user, "profile_pic", None),
    )
    artworks_resp = [
        ArtworkSummary(
            artwork_id=a.artwork_id,
            title=a.title,
            price=getattr(a, "price", None),
            availability=getattr(a, "availability", None),
            file_url=getattr(a, "file_url", None),
        )
        for a in artworks
    ]

    return WebsiteMeResponse(
        website=website_resp,
        artworks=artworks_resp,
        artist=artist_resp,
    )


# PUT /websites/me  -> update my single website (status, domain, config...)
@router.put("/me", response_model=WebsiteResponse)
@router.patch("/me", response_model=WebsiteResponse)
def update_my_website(
    updates: WebsiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    website = crud_websites.get_active_website_by_artist(db, current_user.user_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    if website.artist_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # handle domain uniqueness, publishing URL, etc.
    # (we already wrote that logic earlier – you can plug it in here)
    update_data = updates.dict(exclude_unset=True)

    new_status = update_data.get("status", website.status)
    new_domain = update_data.get("domain", website.domain)

    # If user is publishing, set published_url
    if new_status == "published" and new_domain:
        public_base = "https://artloom360.com"
        update_data["published_url"] = f"{public_base}/w/{new_domain}"

    for field, value in update_data.items():
        setattr(website, field, value)

    db.commit()
    db.refresh(website)

    return WebsiteResponse.model_validate(website)

# -------------------------------------------------
# NEW: PUBLIC PORTFOLIO ENDPOINT
# -------------------------------------------------

@router.get("/public/{domain}", response_model=PublicWebsiteResponse)
def get_public_website(domain: str, db: Session = Depends(get_db)):
    website = crud_websites.get_website_by_domain(db, domain, only_published=True)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    artist = website.artist
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    cfg = website.config or {}
    artworks_section = cfg.get("artworks_section") or {}
    artwork_ids = artworks_section.get("artwork_ids", [])

    artworks = []
    if artwork_ids:
        artworks = (
            db.query(Artwork)
            .filter(
                Artwork.artwork_id.in_(artwork_ids),
                Artwork.status == "published",
            )
            .all()
        )

    website_resp = WebsiteResponse.model_validate(website)
    artist_resp = ArtistPublic(
        user_id=artist.user_id,
        name=artist.name,
        profile_pic=getattr(artist, "profile_pic", None),
    )
    artworks_resp = [
        ArtworkSummary(
            artwork_id=a.artwork_id,
            title=a.title,
            price=getattr(a, "price", None),
            availability=getattr(a, "availability", None),
            file_url=getattr(a, "file_url", None),
        )
        for a in artworks
    ]

    return PublicWebsiteResponse(
        website=website_resp,
        artist=artist_resp,
        artworks=artworks_resp,
    )
