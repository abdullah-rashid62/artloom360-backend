# app/crud/exhibitions.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from decimal import Decimal

from app.models import Exhibition, ViewEvent, LikeEvent, WatchTimeEvent, Review, Order, OrderItem
from app.schemas import ExhibitionCreate, ExhibitionUpdate


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
        config=exhibition.config or {},        
        thumbnail_url=exhibition.thumbnail_url, 
        status=exhibition.status or "draft",     
      
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


# ------------------------------
# Analytics / Dashboard helper
# ------------------------------
def get_exhibitions_with_analytics_by_artist(db: Session, artist_id: str):
    """
    Returns:
      exhibitions: list[Exhibition]
      views_map, likes_map, watch_map, rating_map, orders_map, reviews_map
      (each map keyed by exhibition_id)
    """

    # 1) Get exhibitions for this artist (ignore deleted ones by default)
    exhibitions: List[Exhibition] = (
        db.query(Exhibition)
        .filter(
            Exhibition.artist_id == artist_id,
            Exhibition.is_deleted == False  # noqa: E712
        )
        .all()
    )

    if not exhibitions:
        return [], {}, {}, {}, {}, {}, {}

    exhibition_ids = [e.exhibition_id for e in exhibitions]

    # 2) Views (count + last viewed)
    views_rows = (
        db.query(
            ViewEvent.target_id.label("exhibition_id"),
            func.count().label("total_views"),
            func.max(ViewEvent.created_at).label("last_viewed"),
        )
        .filter(
            ViewEvent.target_type == "exhibition",
            ViewEvent.target_id.in_(exhibition_ids),
        )
        .group_by(ViewEvent.target_id)
        .all()
    )
    views_map: Dict[str, dict] = {
        row.exhibition_id: {
            "total_views": row.total_views,
            "last_viewed": row.last_viewed,
        }
        for row in views_rows
    }

    # 3) Likes (count)
    likes_rows = (
        db.query(
            LikeEvent.target_id.label("exhibition_id"),
            func.count().label("total_likes"),
        )
        .filter(
            LikeEvent.target_type == "exhibition",
            LikeEvent.target_id.in_(exhibition_ids),
        )
        .group_by(LikeEvent.target_id)
        .all()
    )
    likes_map: Dict[str, int] = {
        row.exhibition_id: row.total_likes for row in likes_rows
    }

    # 4) Watch time (sum seconds)
    watch_rows = (
        db.query(
            WatchTimeEvent.target_id.label("exhibition_id"),
            func.sum(WatchTimeEvent.seconds_watched).label("total_seconds"),
        )
        .filter(
            WatchTimeEvent.target_type == "exhibition",
            WatchTimeEvent.target_id.in_(exhibition_ids),
        )
        .group_by(WatchTimeEvent.target_id)
        .all()
    )
    watch_map: Dict[str, int] = {
        row.exhibition_id: (row.total_seconds or 0) for row in watch_rows
    }

    # 5) Reviews (avg rating)
    rating_rows = (
        db.query(
            Review.target_id.label("exhibition_id"),
            func.avg(Review.rating).label("avg_rating"),
        )
        .filter(
            Review.target_type == "exhibition",
            Review.target_id.in_(exhibition_ids),
        )
        .group_by(Review.target_id)
        .all()
    )
    rating_map: Dict[str, float] = {
        row.exhibition_id: float(row.avg_rating) for row in rating_rows
    }

    # 6) Orders (sold + revenue) per exhibition via source_type/source_id
    valid_statuses = ["confirmed", "delivered"]
    order_rows = (
        db.query(
            OrderItem.source_id.label("exhibition_id"),
            func.sum(OrderItem.quantity).label("sold_qty"),
            func.sum(OrderItem.price * OrderItem.quantity).label("revenue"),
        )
        .join(Order, OrderItem.order_id == Order.order_id)
        .filter(
            OrderItem.source_type == "exhibition",
            OrderItem.source_id.in_(exhibition_ids),
            Order.status.in_(valid_statuses),
        )
        .group_by(OrderItem.source_id)
        .all()
    )
    orders_map: Dict[str, dict] = {
        row.exhibition_id: {
            "sold": int(row.sold_qty or 0),
            "revenue": row.revenue or Decimal("0.00"),
        }
        for row in order_rows
    }

    # 7) Reviews list per exhibition
    reviews_q = (
        db.query(Review)
        .filter(
            Review.target_type == "exhibition",
            Review.target_id.in_(exhibition_ids),
        )
        .all()
    )
    reviews_map: Dict[str, List[Review]] = {eid: [] for eid in exhibition_ids}
    for rev in reviews_q:
        reviews_map.setdefault(rev.target_id, []).append(rev)

    return exhibitions, views_map, likes_map, watch_map, rating_map, orders_map, reviews_map
