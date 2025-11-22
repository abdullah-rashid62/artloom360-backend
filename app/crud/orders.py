from sqlalchemy.orm import Session
from app.models import Order, OrderItem, Artwork
from app.schemas import OrderCreate, OrderItemCreate
from typing import List

# ------------------------------
# Get Order
# ------------------------------
def get_order(db: Session, order_id: str) -> Order:
    return db.query(Order).filter(Order.order_id == order_id).first()

# ------------------------------
# Create Order + Items
# ------------------------------
def create_order(db: Session, artist_id: str, order_data: OrderCreate) -> Order:
    total_amount = sum(item.price * item.quantity for item in order_data.items)
    db_order = Order(
        artist_id=artist_id,
        buyer_name=order_data.buyer_name,
        buyer_email=order_data.buyer_email,
        buyer_phone=order_data.buyer_phone,
        buyer_address=order_data.buyer_address,
        total_amount=total_amount
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Add order items
    for item in order_data.items:
        db_item = OrderItem(
            order_id=db_order.order_id,
            target_type=item.target_type,
            target_id=item.target_id,
            source_type=item.source_type,
            source_id=item.source_id,
            price=item.price,
            quantity=item.quantity
        )
        db.add(db_item)
    db.commit()
    return db_order

# ------------------------------
# List Orders by Artist
# ------------------------------
def get_orders_by_artist(db: Session, artist_id: str) -> List[Order]:
    return db.query(Order).filter(Order.artist_id == artist_id).all()
