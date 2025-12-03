
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

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


# app/schemas/order_public.py
from typing import List, Literal
from datetime import datetime
from pydantic import BaseModel, Field

class PublicOrderItemCreate(BaseModel):
    target_type: Literal["artwork"] = "artwork"
    target_id: str = Field(..., description="artwork_id being purchased")
    source_type: Literal["website", "exhibition"] = "website"
    source_id: str = Field(..., description="website_id or exhibition_id")
    quantity: int = Field(1, ge=1)

class PublicOrderCreate(BaseModel):
    artist_id: str
    buyer_name: str
    buyer_email: str
    buyer_phone: str
    buyer_address: str
    currency: str = "PKR"
    items: List[PublicOrderItemCreate]

class PublicOrderOut(BaseModel):
    order_id: str
    status: str
    total_amount: float
    currency: str
    created_at: datetime
    class Config:
        from_attributes = True 
        
        
class OrderStatusUpdate(BaseModel):
    status: Literal["pending", "confirmed","shipped", "delivered", "cancelled"]




class OrderItemProduct(BaseModel):
    artwork_id: str
    title: str
    thumbnail_url: Optional[str] = None
    price: Optional[float] = None
    availability: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrderItemSource(BaseModel):
    source_type: str          # 'website' | 'exhibition'
    source_id: str
    label: Optional[str] = None   # website / exhibition title
    url: Optional[str] = None     # published_url

    model_config = ConfigDict(from_attributes=True)


class OrderItemResponse(BaseModel):
    order_item_id: str
    target_type: str
    target_id: str
    source_type: str
    source_id: str
    quantity: int
    price: float

    # enriched fields
    product: Optional[OrderItemProduct] = None
    source: Optional[OrderItemSource] = None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    order_id: str
    artist_id: str
    buyer_name: str
    buyer_email: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_address: Optional[str] = None
    status: str
    total_amount: float
    currency: str
    created_at: datetime
    updated_at: datetime

    items: List[OrderItemResponse] = []   

    model_config = ConfigDict(from_attributes=True)