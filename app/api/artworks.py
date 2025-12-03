# app/api/artworks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.users import User
from app.schemas import ArtworkCreate, ArtworkUpdate, ArtworkResponse
from app.schemas import ArtworkWithAnalyticsResponse, ArtworkAnalytics, ReviewResponse 

from app.crud import artworks as crud_artworks
from app.api.deps import get_db
from app.utils.auth import get_current_active_user
from decimal import Decimal

router = APIRouter(prefix="/artworks", tags=["Artworks"])


@router.post("/", response_model=ArtworkResponse)
def create_artwork(
    artwork: ArtworkCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud_artworks.create_artwork(db, current_user.user_id, artwork)




# 🔹 Get single artwork by ID, but only if it belongs to the current user
@router.get("/{artwork_id}", response_model=ArtworkResponse)
def get_artwork(
    artwork_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_artwork = crud_artworks.get_artwork(db, artwork_id)
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # lock by user
    if db_artwork.artist_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this artwork",
        )

    return db_artwork



@router.put("/{artwork_id}", response_model=ArtworkResponse)
@router.patch("/{artwork_id}", response_model=ArtworkResponse)
def update_artwork(
    artwork_id: str,
    updates: ArtworkUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_artwork = crud_artworks.get_artwork(db, artwork_id)
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Only the owner can update
    if db_artwork.artist_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this artwork",
        )

    return crud_artworks.update_artwork(db, db_artwork, updates)


@router.delete("/{artwork_id}")
def delete_artwork(
    artwork_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_artwork = crud_artworks.get_artwork(db, artwork_id)
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Only the owner can delete
    if db_artwork.artist_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this artwork",
        )

    crud_artworks.delete_artwork(db, db_artwork)
    return {"detail": "Artwork deleted successfully"}


# ---------- NEW: dashboard style endpoint ----------

@router.get("/me/all", response_model=List[ArtworkWithAnalyticsResponse])
def get_my_artworks_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    (
        artworks,
        views_map,
        likes_map,
        watch_map,
        rating_map,
        orders_map,
        reviews_map,
    ) = crud_artworks.get_artworks_with_analytics_by_artist(db, current_user.user_id)

    result: List[ArtworkWithAnalyticsResponse] = []

    for art in artworks:
        aid = art.artwork_id

        total_views = views_map.get(aid, {}).get("total_views", 0)
        last_viewed = views_map.get(aid, {}).get("last_viewed")
        total_likes = likes_map.get(aid, 0)
        total_watch_seconds = watch_map.get(aid, 0)
        avg_rating = rating_map.get(aid)
        sold = orders_map.get(aid, {}).get("sold", 0)
        revenue = orders_map.get(aid, {}).get("revenue")

        # conversion = sold / views (fraction)
        conversion_rate = float(sold) / total_views if total_views > 0 else 0.0

        # avg view duration in seconds
        avg_view_duration = (
            float(total_watch_seconds) / total_views
            if total_views > 0 else None
        )

        analytics = ArtworkAnalytics(
            total_views=total_views,
            total_likes=total_likes,
            total_watch_seconds=total_watch_seconds,
            sold=sold,
            revenue=revenue or Decimal("0.00"),
            avg_rating=avg_rating,
            last_viewed=last_viewed,
            conversion_rate=conversion_rate,
            avg_view_duration_seconds=avg_view_duration,
            created_at=art.created_at,
        )

        reviews = [
            ReviewResponse(
                review_id=r.review_id,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at,
            )
            for r in reviews_map.get(aid, [])
        ]

        result.append(
            ArtworkWithAnalyticsResponse(
                id=aid,
                artwork=ArtworkResponse.model_validate(art),
                analytics=analytics,
                reviews=reviews,
            )
        )

    return result


@router.get("/me/list", response_model=List[ArtworkResponse])
def get_my_artworks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_artworks = crud_artworks.get_artworks_by_artist(db, current_user.user_id)
    return db_artworks


