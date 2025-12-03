from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.schemas import ExhibitionCreate, ExhibitionUpdate, ExhibitionResponse
from app.schemas import ExhibitionWithAnalyticsResponse, ExhibitionAnalytics, ReviewResponse
from app.models.users import User
from app.crud import exhibitions as crud_exhibitions
from app.api.deps import get_db
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/exhibitions", tags=["Exhibitions"])

# @router.post("/{artist_id}", response_model=ExhibitionResponse)
# def create_exhibition(artist_id: str, exhibition: ExhibitionCreate, db: Session = Depends(get_db)):
#     return crud_exhibitions.create_exhibition(db, artist_id, exhibition)

# @router.get("/{exhibition_id}", response_model=ExhibitionResponse)
# def get_exhibition(exhibition_id: str, db: Session = Depends(get_db)):
#     db_exhibition = crud_exhibitions.get_exhibition(db, exhibition_id)
#     if not db_exhibition:
#         raise HTTPException(status_code=404, detail="Exhibition not found")
#     return db_exhibition

# @router.get("/artist/{artist_id}", response_model=List[ExhibitionResponse])
# def get_exhibitions_by_artist(artist_id: str, db: Session = Depends(get_db)):
#     return crud_exhibitions.get_exhibitions_by_artist(db, artist_id)

# @router.put("/{exhibition_id}", response_model=ExhibitionResponse)
# def update_exhibition(exhibition_id: str, updates: ExhibitionUpdate, db: Session = Depends(get_db)):
#     db_exhibition = crud_exhibitions.get_exhibition(db, exhibition_id)
#     if not db_exhibition:
#         raise HTTPException(status_code=404, detail="Exhibition not found")
#     return crud_exhibitions.update_exhibition(db, db_exhibition, updates)

# @router.delete("/{exhibition_id}")
# def delete_exhibition(exhibition_id: str, db: Session = Depends(get_db)):
#     db_exhibition = crud_exhibitions.get_exhibition(db, exhibition_id)
#     if not db_exhibition:
#         raise HTTPException(status_code=404, detail="Exhibition not found")
#     crud_exhibitions.delete_exhibition(db, db_exhibition)
#     return {"detail": "Exhibition deleted successfully"}

@router.post("/", response_model=ExhibitionResponse)
def create_exhibition_endpoint(
    payload: ExhibitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new exhibition for the logged-in artist.
    """
    exhibition = crud_exhibitions.create_exhibition(
        db=db,
        artist_id=current_user.user_id,
        exhibition=payload,
    )
    return exhibition



@router.get("/me/dashboard", response_model=List[ExhibitionWithAnalyticsResponse])
def get_my_exhibitions_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    (
        exhibitions,
        views_map,
        likes_map,
        watch_map,
        rating_map,
        orders_map,
        reviews_map,
    ) = crud_exhibitions.get_exhibitions_with_analytics_by_artist(db, current_user.user_id)

    result: List[ExhibitionWithAnalyticsResponse] = []

    for ex in exhibitions:
        eid = ex.exhibition_id

        total_views = views_map.get(eid, {}).get("total_views", 0)
        last_viewed = views_map.get(eid, {}).get("last_viewed")
        total_likes = likes_map.get(eid, 0)
        total_watch_seconds = watch_map.get(eid, 0)
        avg_rating = rating_map.get(eid)

        # Orders info: sold + revenue, with safe defaults
        order_info = orders_map.get(eid, {"sold": 0, "revenue": Decimal("0.00")})
        sold = order_info["sold"]
        revenue = order_info["revenue"]

        conversion_rate = float(sold) / total_views if total_views > 0 else 0.0
        avg_view_duration = (
            float(total_watch_seconds) / total_views
            if total_views > 0 else None
        )

        analytics = ExhibitionAnalytics(
            total_views=total_views,
            total_likes=total_likes,
            total_watch_seconds=total_watch_seconds,
            sold=sold,
            revenue=revenue,
            avg_rating=avg_rating,
            last_viewed=last_viewed,
            conversion_rate=conversion_rate,
            avg_view_duration_seconds=avg_view_duration,
            created_at=ex.created_at,
        )

        reviews = [
            ReviewResponse.model_validate(r)
            for r in reviews_map.get(eid, [])
        ]

        result.append(
            ExhibitionWithAnalyticsResponse(
                id=eid,
                exhibition=ExhibitionResponse.model_validate(ex),
                analytics=analytics,
                reviews=reviews,
            )
        )

    return result

@router.get("/me/e/{exhibition_id}", response_model=ExhibitionResponse)
def get_my_exhibition(
    exhibition_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_ex = crud_exhibitions.get_exhibition(db, exhibition_id)
    if not db_ex:
        raise HTTPException(status_code=404, detail="Exhibition not found")

    if db_ex.artist_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this exhibition")

    return db_ex

@router.put("/me/e/{exhibition_id}", response_model=ExhibitionResponse)
@router.patch("/me/e/{exhibition_id}", response_model=ExhibitionResponse)
def update_my_exhibition(
    exhibition_id: str,
    updates: ExhibitionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_ex = crud_exhibitions.get_exhibition(db, exhibition_id)
    if not db_ex:
        raise HTTPException(status_code=404, detail="Exhibition not found")

    if db_ex.artist_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this exhibition")

    return crud_exhibitions.update_exhibition(db, db_ex, updates)


