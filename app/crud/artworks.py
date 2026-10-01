# app/crud/artworks.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from decimal import Decimal

from app.models import Artwork, ViewEvent, LikeEvent, WatchTimeEvent, Review, Order, OrderItem
from app.schemas import ArtworkCreate, ArtworkUpdate


# ------------------------------
# Basic CRUD
# ------------------------------
def get_artwork(db: Session, artwork_id: str) -> Optional[Artwork]:
    return db.query(Artwork).filter(Artwork.artwork_id == artwork_id).first()


def get_artworks_by_artist(db: Session, artist_id: str) -> List[Artwork]:
    return (
        db.query(Artwork)
        .filter(
            Artwork.artist_id == artist_id,
            Artwork.status != "archived",
            Artwork.status != "draft",
        )
        .order_by(Artwork.created_at.desc())
        .all()
    )

def create_artwork(db: Session, artist_id: str, artwork: ArtworkCreate) -> Artwork:
    data = artwork.dict(exclude_unset=True)
    db_artwork = Artwork(
        artist_id=artist_id,
        **data
    )
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork


def update_artwork(db: Session, db_artwork: Artwork, updates: ArtworkUpdate) -> Artwork:
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_artwork, field, value)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork


def delete_artwork(db: Session, db_artwork: Artwork):
    db.delete(db_artwork)
    db.commit()


# ------------------------------
# Analytics / Dashboard helper
# ------------------------------
def get_artworks_with_analytics_by_artist(db: Session, artist_id: str):
    """
    Returns:
      artworks: list[Artwork]
      views_map, likes_map, watch_map, rating_map, orders_map, reviews_map
      (each map keyed by artwork_id)
    """
    # 1) Get all artworks for this artist
    artworks: List[Artwork] = (
        db.query(Artwork)
        .filter(Artwork.artist_id == artist_id)
        .order_by(Artwork.created_at.desc())  
        .all()
    )

    if not artworks:
        return [], {}, {}, {}, {}, {}, {}

    artwork_ids = [a.artwork_id for a in artworks]

    # 2) Views (count + last viewed)
    views_rows = (
        db.query(
            ViewEvent.target_id.label("artwork_id"),
            func.count().label("total_views"),
            func.max(ViewEvent.created_at).label("last_viewed"),
        )
        .filter(
            ViewEvent.target_type == "artwork",
            ViewEvent.target_id.in_(artwork_ids),
        )
        .group_by(ViewEvent.target_id)
        .all()
    )
    views_map: Dict[str, dict] = {
        row.artwork_id: {
            "total_views": row.total_views,
            "last_viewed": row.last_viewed,
        }
        for row in views_rows
    }

    # 3) Likes (count)
    likes_rows = (
        db.query(
            LikeEvent.target_id.label("artwork_id"),
            func.count().label("total_likes"),
        )
        .filter(
            LikeEvent.target_type == "artwork",
            LikeEvent.target_id.in_(artwork_ids),
        )
        .group_by(LikeEvent.target_id)
        .all()
    )
    likes_map: Dict[str, int] = {
        row.artwork_id: row.total_likes for row in likes_rows
    }

    # 4) Watch time (sum seconds)
    watch_rows = (
        db.query(
            WatchTimeEvent.target_id.label("artwork_id"),
            func.sum(WatchTimeEvent.seconds_watched).label("total_seconds"),
        )
        .filter(
            WatchTimeEvent.target_type == "artwork",
            WatchTimeEvent.target_id.in_(artwork_ids),
        )
        .group_by(WatchTimeEvent.target_id)
        .all()
    )
    watch_map: Dict[str, int] = {
        row.artwork_id: (row.total_seconds or 0) for row in watch_rows
    }

    # 5) Reviews (avg rating)
    rating_rows = (
        db.query(
            Review.target_id.label("artwork_id"),
            func.avg(Review.rating).label("avg_rating"),
        )
        .filter(
            Review.target_type == "artwork",
            Review.target_id.in_(artwork_ids),
        )
        .group_by(Review.target_id)
        .all()
    )
    rating_map: Dict[str, float] = {
        row.artwork_id: float(row.avg_rating) for row in rating_rows
    }

    # 6) Orders (sold quantity + revenue) for artwork
    valid_statuses = ["confirmed", "delivered"]
    order_rows = (
        db.query(
            OrderItem.target_id.label("artwork_id"),
            func.sum(OrderItem.quantity).label("sold_qty"),
            func.sum(OrderItem.price * OrderItem.quantity).label("revenue"),
        )
        .join(Order, OrderItem.order_id == Order.order_id)
        .filter(
            OrderItem.target_type == "artwork",
            OrderItem.target_id.in_(artwork_ids),
            Order.status.in_(valid_statuses),
        )
        .group_by(OrderItem.target_id)
        .all()
    )
    orders_map: Dict[str, dict] = {
        row.artwork_id: {
            "sold": int(row.sold_qty or 0),
            "revenue": row.revenue or Decimal("0.00"),
        }
        for row in order_rows
    }

    # 7) List of reviews per artwork
    reviews_q = (
        db.query(Review)
        .filter(
            Review.target_type == "artwork",
            Review.target_id.in_(artwork_ids),
        )
        .all()
    )
    reviews_map: Dict[str, List[Review]] = {aid: [] for aid in artwork_ids}
    for rev in reviews_q:
        reviews_map.setdefault(rev.target_id, []).append(rev)

    return artworks, views_map, likes_map, watch_map, rating_map, orders_map, reviews_map
