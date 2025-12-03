# app/crud/public_exhibitions.py
from typing import Dict, Any, List
from copy import deepcopy
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.artworks import Artwork
from app.models.analytics import LikeEvent  # <-- path based on your snippet


def enrich_exhibition_config_for_public(db: Session, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a copy of config where each placement in layout.placements
    is enriched with artwork snapshot fields + likes (from LikeEvent).
    Does NOT modify the DB-stored config.
    """
    if not config:
        return config

    cfg = deepcopy(config)
    layout = cfg.get("layout") or {}
    placements: List[Dict[str, Any]] = layout.get("placements") or []

    if not placements:
        return cfg

    # Unique artwork_ids from placements
    artwork_ids = {p.get("artwork_id") for p in placements if p.get("artwork_id")}
    artwork_ids = {aid for aid in artwork_ids if aid}
    if not artwork_ids:
        return cfg

    # 1) Load artworks for snapshot data
    artworks = (
        db.query(Artwork)
        .filter(Artwork.artwork_id.in_(artwork_ids))
        .all()
    )
    artwork_map = {a.artwork_id: a for a in artworks}

    # 2) Aggregate likes from LikeEvent
    like_rows = (
        db.query(LikeEvent.target_id, func.count(LikeEvent.like_id))
        .filter(
            LikeEvent.target_type == "artwork",
            LikeEvent.target_id.in_(artwork_ids),
        )
        .group_by(LikeEvent.target_id)
        .all()
    )
    likes_map = {target_id: count for (target_id, count) in like_rows}

    def snapshot(a: Artwork, likes: int) -> Dict[str, Any]:
        return {
            "artwork_description": a.description,
            "artwork_price": a.price,
            "artwork_currency": getattr(a, "currency", None) or "PKR",
            "artwork_availability": a.availability,
            "artwork_year": a.year,
            "artwork_category": a.category,
            "artwork_tags": a.tags,
            "artwork_likes": likes,
        }

    enriched: List[Dict[str, Any]] = []
    for p in placements:
        art_id = p.get("artwork_id")
        art = artwork_map.get(art_id)
        likes = likes_map.get(art_id, 0)

        if art:
            enriched.append({**p, **snapshot(art, likes)})
        else:
            enriched.append(p)

    layout["placements"] = enriched
    cfg["layout"] = layout

    return cfg
