from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import OrderCreate, OrderResponse
from app.crud import orders as crud_orders
from app.api.deps import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/{artist_id}", response_model=OrderResponse)
def create_order(artist_id: str, order_data: OrderCreate, db: Session = Depends(get_db)):
    return crud_orders.create_order(db, artist_id, order_data)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    db_order = crud_orders.get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.get("/artist/{artist_id}", response_model=List[OrderResponse])
def get_orders_by_artist(artist_id: str, db: Session = Depends(get_db)):
    return crud_orders.get_orders_by_artist(db, artist_id)
