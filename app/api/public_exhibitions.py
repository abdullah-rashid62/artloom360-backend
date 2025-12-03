# app/api/public_exhibitions.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db
from app.models.exhibitions import Exhibition
from app.models.users import User
from app.models.artworks import Artwork
from app.models.analytics import ViewEvent, LikeEvent, WatchTimeEvent, Review
from app.schemas.public_exhibitions import (
    PublicExhibitionResponse,
    PublicArtistSummary,
    PublicExhibitionAnalytics,
    PublicReviewCreate,
    PublicReviewListResponse,
    ReviewResponse,
)
from app.crud import exhibitions as crud_exhibitions
from app.crud.public_exhibitions import enrich_exhibition_config_for_public


router = APIRouter(prefix="/public", tags=["Public Exhibitions"])


# ---------- Public exhibition details ----------
@router.get("/exhibitions/{exhibition_id}", response_model=PublicExhibitionResponse)
def get_public_exhibition(exhibition_id: str, db: Session = Depends(get_db)):
    db_ex: Exhibition | None = crud_exhibitions.get_exhibition(db, exhibition_id)
    if not db_ex or db_ex.is_deleted or db_ex.status != "published":
        raise HTTPException(status_code=404, detail="Exhibition not found")

    # Exhibition-level analytics (views/watch/likes/rating) –
    # this likely already exists in your crud_exhibitions file.
    (
        exhibitions,
        views_map,
        likes_map,
        watch_map,
        rating_map,
        orders_map,
        reviews_map,
    ) = crud_exhibitions.get_exhibitions_with_analytics_by_artist(db, db_ex.artist_id)

    eid = db_ex.exhibition_id
    analytics = PublicExhibitionAnalytics(
        total_views=views_map.get(eid, {}).get("total_views", 0),
        total_likes=likes_map.get(eid, 0),
        avg_rating=rating_map.get(eid),
    )

    artist: User = db_ex.artist
    artist_summary = PublicArtistSummary(
        user_id=str(artist.user_id),
        name=artist.name,
        avatar_url=getattr(artist, "profile_pic", None),
    )

    # Enrich config with artwork snapshot + likes
    enriched_config = enrich_exhibition_config_for_public(db, db_ex.config or {})

    return PublicExhibitionResponse(
        exhibition_id=db_ex.exhibition_id,
        title=db_ex.title,
        description=db_ex.description,
        thumbnail_url=db_ex.thumbnail_url,
        artist=artist_summary,
        analytics=analytics,
        config=enriched_config,
    )


# ---------- Track exhibition view ----------
@router.post("/exhibitions/{exhibition_id}/events/view", status_code=201)
def track_public_exhibition_view(
    exhibition_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    db_ex: Exhibition | None = crud_exhibitions.get_exhibition(db, exhibition_id)
    if not db_ex or db_ex.is_deleted or db_ex.status != "published":
        raise HTTPException(status_code=404, detail="Exhibition not found")

    # Minimal example: store view event
    user_agent = request.headers.get("user-agent")
    # If you want ip_hash, you can hash request.client.host here.
    view_event = ViewEvent(
        target_type="exhibition",
        target_id=exhibition_id,
        user_agent=user_agent,
    )
    db.add(view_event)
    db.commit()

    return {"detail": "view recorded"}


# ---------- Artwork reviews ----------
@router.get(
    "/artworks/{artwork_id}/reviews",
    response_model=PublicReviewListResponse,
)
def get_public_artwork_reviews(artwork_id: str, db: Session = Depends(get_db)):
    reviews = (
        db.query(Review)
        .filter(
            Review.target_type == "artwork",
            Review.target_id == artwork_id,
        )
        .order_by(Review.created_at.desc())
        .all()
    )
    return PublicReviewListResponse(
        reviews=[ReviewResponse.model_validate(r) for r in reviews]
    )


@router.post(
    "/artworks/{artwork_id}/reviews",
    response_model=ReviewResponse,
    status_code=201,
)
def create_public_artwork_review(
    artwork_id: str,
    payload: PublicReviewCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    # optional: validate artwork exists
    db_art = db.query(Artwork).filter(Artwork.artwork_id == artwork_id).first()
    if not db_art:
        raise HTTPException(status_code=404, detail="Artwork not found")

    user_agent = request.headers.get("user-agent")

    review = Review(
        target_type="artwork",
        target_id=artwork_id,
        rating=payload.rating,
        comment=payload.comment,
        user_agent=user_agent if hasattr(Review, "user_agent") else None,  # only if you add field
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return ReviewResponse.model_validate(review)


# ---------- Artwork like event ----------
@router.post("/artworks/{artwork_id}/events/like", status_code=201)
def like_public_artwork(
    artwork_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    db_art = db.query(Artwork).filter(Artwork.artwork_id == artwork_id).first()
    if not db_art:
        raise HTTPException(status_code=404, detail="Artwork not found")

    user_agent = request.headers.get("user-agent")

    like_event = LikeEvent(
        target_type="artwork",
        target_id=artwork_id,
        user_agent=user_agent if hasattr(LikeEvent, "user_agent") else None,
    )
    db.add(like_event)
    db.commit()

    # Return updated likes count for convenience
    likes_count = (
        db.query(func.count(LikeEvent.like_id))
        .filter(
            LikeEvent.target_type == "artwork",
            LikeEvent.target_id == artwork_id,
        )
        .scalar()
    )

    return {"artwork_id": artwork_id, "likes": likes_count}
