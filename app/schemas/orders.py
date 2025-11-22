
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# ---------------------
# Order Item
# ---------------------
class OrderItemBase(BaseModel):
    order_item_id: str
    target_type: str
    target_id: str
    source_type: Optional[str]
    source_id: Optional[str]
    price: float
    quantity: int

    class Config:
        orm_mode = True

class OrderItemCreate(BaseModel):
    target_type: str = "artwork"
    target_id: str
    source_type: Optional[str]  # exhibition / website
    source_id: Optional[str]
    price: float
    quantity: int = 1

# ---------------------
# Order
# ---------------------
class OrderBase(BaseModel):
    order_id: str
    artist_id: Optional[str]
    buyer_name: str
    buyer_email: Optional[str]
    buyer_phone: Optional[str]
    buyer_address: Optional[str]
    total_amount: float
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    buyer_name: str
    buyer_email: Optional[str]
    buyer_phone: Optional[str]
    buyer_address: Optional[str]
    items: List[OrderItemCreate]

class OrderResponse(OrderBase):
    items: List[OrderItemBase]
