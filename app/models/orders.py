import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Numeric, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(36), primary_key=True, default=gen_uuid)
    artist_id = Column(
        String(36),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    buyer_name = Column(String(255), nullable=False)
    buyer_email = Column(String(255), nullable=True)
    buyer_phone = Column(String(50), nullable=True)
    buyer_address = Column(Text, nullable=True)
    total_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(16), default="USD", nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    artist = relationship("User", backref="orders")

    __table_args__ = (
        Index("ix_orders_artist_status", "artist_id", "status"),
        Index("ix_orders_status_created", "status", "created_at"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(String(36), primary_key=True, default=gen_uuid)
    order_id = Column(
        String(36),
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    target_type = Column(String(50), nullable=False, default="artwork")
    target_id = Column(String(36), nullable=False, index=True)  # artwork_id being purchased

    source_type = Column(String(50), nullable=True)  # 'exhibition' or 'website'
    source_id = Column(String(36), nullable=True)    # exhibition_id or website_id

    price = Column(Numeric(12, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    order = relationship("Order", back_populates="items")

    __table_args__ = (
        Index("ix_order_items_target_type_id", "target_type", "target_id"),
        Index("ix_order_items_source_type_id", "source_type", "source_id"),
    )

