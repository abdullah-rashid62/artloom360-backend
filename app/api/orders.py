from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from app.crud import orders as crud_orders
from app.schemas import PublicOrderCreate, PublicOrderOut
from app.api.deps import get_db
from app.utils.auth import get_current_active_user
from app.models.users import User

router = APIRouter(prefix="/orders", tags=["Orders"])

# @router.post("/{artist_id}", response_model=OrderResponse)
# def create_order(artist_id: str, order_data: OrderCreate, db: Session = Depends(get_db)):
#     return crud_orders.create_order(db, artist_id, order_data)

# @router.get("/{order_id}", response_model=OrderResponse)
# def get_order(order_id: str, db: Session = Depends(get_db)):
#     db_order = crud_orders.get_order(db, order_id)
#     if not db_order:
#         raise HTTPException(status_code=404, detail="Order not found")
#     return db_order

# @router.get("/artist/{artist_id}", response_model=List[OrderResponse])
# def get_orders_by_artist(artist_id: str, db: Session = Depends(get_db)):
#     return crud_orders.get_orders_by_artist(db, artist_id)


@router.post("/", response_model=PublicOrderOut)
def create_public_order(
    payload: PublicOrderCreate,
    db: Session = Depends(get_db),
):
    """
    Guest checkout endpoint for website/exhibition orders.

    - No auth (public)
    - Uses artwork.price from DB
    - Associates items with website/exhibition via source_type/source_id
    """
    try:
        order = crud_orders.create_public_order(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return PublicOrderOut.model_validate(order)




@router.get("/", response_model=List[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    orders = crud_orders.get_orders_by_artist(db, current_user.user_id)
    return [crud_orders.build_order_response_with_details(db, o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = crud_orders.get_order(db, order_id)
    if not order or order.artist_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud_orders.build_order_response_with_details(db, order)



@router.put("/{order_id}", response_model=OrderResponse)
@router.patch("/{order_id}", response_model=OrderResponse)
def change_order_status(
    order_id: str,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Update an order's status (only for the artist who owns the order).
    """
    try:
        updated = crud_orders.update_order_status(
            db=db,
            order_id=order_id,
            artist_id=current_user.user_id,
            new_status=payload.status,
        )
        return updated

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status",
        )