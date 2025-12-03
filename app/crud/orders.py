from sqlalchemy.orm import Session
from app.models import Order, OrderItem, Artwork
from app.schemas import OrderCreate, OrderItemCreate, OrderResponse, OrderItemResponse, OrderItemSource, OrderItemProduct
from typing import List
from app.models import Website
from app.models import Exhibition

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
    return (
        db.query(Order)
        .filter(Order.artist_id == artist_id)
        .order_by(Order.created_at.desc())
        .all()
    )


# app/crud/orders.py
from sqlalchemy.orm import Session
from app.models import Order, OrderItem, Artwork
from app.schemas import OrderCreate, OrderItemCreate, PublicOrderCreate  # <-- add this
from typing import List

# existing get_order, create_order, get_orders_by_artist stay as-is


# ------------------------------
# Public order: compute price from artworks
# ------------------------------
def create_public_order(db: Session, order_data: PublicOrderCreate) -> Order:
    """
    Create an order from a public source (website / exhibition).

    - Uses artwork.price from DB
    - Enforces that artworks belong to the given artist_id
    """
    if not order_data.items:
        raise ValueError("Order must contain at least one item")

    total_amount = 0.0
    artworks_cache = {}

    # 1) Validate artworks and compute total
    for item in order_data.items:
        if item.target_type != "artwork":
            raise ValueError("Only 'artwork' target_type is supported")

        artwork = db.query(Artwork).filter(
            Artwork.artwork_id == item.target_id
        ).first()

        if not artwork:
            raise ValueError(f"Artwork not found: {item.target_id}")

        # ensure artwork belongs to this artist
        if artwork.artist_id != order_data.artist_id:
            raise ValueError("Artwork does not belong to specified artist")

        artworks_cache[item.target_id] = artwork

        price = float(artwork.price or 0)
        total_amount += price * item.quantity

    # 2) Create Order
    db_order = Order(
        artist_id=order_data.artist_id,
        buyer_name=order_data.buyer_name,
        buyer_email=order_data.buyer_email,
        buyer_phone=order_data.buyer_phone,
        buyer_address=order_data.buyer_address,
        total_amount=total_amount,
        currency=order_data.currency,
        status="pending",
    )
    db.add(db_order)
    db.flush()  # get db_order.order_id

    # 3) Create OrderItems
    for item in order_data.items:
        artwork = artworks_cache[item.target_id]
        db_item = OrderItem(
            order_id=db_order.order_id,
            target_type=item.target_type,
            target_id=item.target_id,
            source_type=item.source_type,
            source_id=item.source_id,
            price=artwork.price,      # price from DB, not from client
            quantity=item.quantity,
        )
        db.add(db_item)

    # Optional: mark 1/1 artworks as sold
    # for artwork in artworks_cache.values():
    #     if getattr(artwork, "edition_total", 1) == 1:
    #         artwork.availability = "Sold"

    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_status(
    db: Session,
    order_id: str,
    artist_id: str,
    new_status: str,
) -> Order:
    """
    Update status of an order that belongs to the given artist.
    Raises ValueError if not found / not owned.
    """
    order = (
        db.query(Order)
        .filter(
            Order.order_id == order_id,
            Order.artist_id == artist_id,
        )
        .first()
    )

    if not order:
        raise ValueError("Order not found for this artist")

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order





def build_order_response_with_details(db: Session, order) -> OrderResponse:
    # base order data (no items yet)
    base = OrderResponse.model_validate(
        {
            "order_id": order.order_id,
            "artist_id": order.artist_id,
            "buyer_name": order.buyer_name,
            "buyer_email": order.buyer_email,
            "buyer_phone": order.buyer_phone,
            "buyer_address": order.buyer_address,
            "status": order.status,
            "total_amount": float(order.total_amount or 0),
            "currency": order.currency,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": [],
        }
    )

    # load items for this order
    items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.order_id)
        .all()
    )

    # prefetch all artworks, websites, exhibitions referenced by items
    artwork_ids = [i.target_id for i in items if i.target_type == "artwork"]
    website_ids = [i.source_id for i in items if i.source_type == "website"]
    exhibition_ids = [i.source_id for i in items if i.source_type == "exhibition"]

    artworks = (
        db.query(Artwork)
        .filter(Artwork.artwork_id.in_(artwork_ids)) if artwork_ids else []
    )
    artwork_map = {a.artwork_id: a for a in artworks}

    websites = (
        db.query(Website)
        .filter(Website.website_id.in_(website_ids)) if website_ids else []
    )
    website_map = {w.website_id: w for w in websites}

    exhibitions = (
        db.query(Exhibition)
        .filter(Exhibition.exhibition_id.in_(exhibition_ids)) if exhibition_ids else []
    )
    exhibition_map = {e.exhibition_id: e for e in exhibitions}

    enriched_items: List[OrderItemResponse] = []

    for item in items:
        product = None
        if item.target_type == "artwork":
            a = artwork_map.get(item.target_id)
            if a:
                product = OrderItemProduct(
                    artwork_id=a.artwork_id,
                    title=a.title,
                    thumbnail_url=getattr(a, "thumbnail_url", None) or a.file_url,
                    price=a.price,
                    availability=a.availability,
                )

        source = None
        if item.source_type == "website":
            w = website_map.get(item.source_id)
            if w:
                source = OrderItemSource(
                    source_type="website",
                    source_id=w.website_id,
                    label=w.title or w.domain,
                    url=w.published_url,
                )
        elif item.source_type == "exhibition":
            e = exhibition_map.get(item.source_id)
            if e:
                source = OrderItemSource(
                    source_type="exhibition",
                    source_id=e.exhibition_id,
                    label=e.title,
                    url=e.published_url,
                )

        enriched_items.append(
            OrderItemResponse(
                order_item_id=item.order_item_id,
                target_type=item.target_type,
                target_id=item.target_id,
                source_type=item.source_type,
                source_id=item.source_id,
                quantity=item.quantity,
                price=float(item.price or 0),
                product=product,
                source=source,
            )
        )

    base.items = enriched_items
    return base

