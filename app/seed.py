import random
from datetime import datetime
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.crud.users import hash_password
from app.core.database import SessionLocal, Base, engine
from app.models import (
    User, Artwork, Exhibition, Website,
    ViewEvent, LikeEvent, WatchTimeEvent, Review,
    Order, OrderItem, Notification
)

fake = Faker()

DEFAULT_TEST_PASSWORD = "password123"

# ---------------------------
# Configurable parameters
# ---------------------------
NUM_ARTISTS = 3
ARTWORKS_PER_ARTIST = (10, 15)
EXHIBITIONS_PER_ARTIST = 2

# Analytics ranges
VIEWS_RANGE = (50, 120)
LIKES_RANGE = (10, 60)
REVIEWS_RANGE = (3, 20)
WATCH_EVENTS_RANGE = (5, 15)
WATCH_SECONDS_RANGE = (30, 200)

ORDERS_PER_ARTWORK = (1, 3)

# Image dimensions
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600


# ---------------------------
# Helper functions
# ---------------------------
def random_art_category():
    return random.choice([
        "Digital Art", "Photography", "3D Model", "Painting",
        "Illustration", "Mixed Media"
    ])


def random_file_type():
    return random.choice(["image", "video", "model_3d"])


def generate_artwork_title():
    adjectives = ["Ethereal", "Vivid", "Abstract", "Dreamy", "Mystic", "Radiant", "Silent"]
    subjects = ["Sunset", "Forest", "Portrait", "Cityscape", "Ocean", "Galaxy", "Still Life"]
    styles = ["Digital Painting", "Photography", "3D Model", "Illustration", "Mixed Media"]
    return f"{random.choice(adjectives)} {random.choice(subjects)} – {random.choice(styles)}"


def generate_artwork_description(title: str) -> str:
    return (
        f"{title} is a captivating piece that explores {fake.sentence(nb_words=6)}. "
        f"Created with attention to detail, it captures the essence of {fake.word()}."
    )


# ---------------------------
# Database cleanup
# ---------------------------
def clear_database(db: Session):
    print("Clearing all tables...")
    db.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
    db.commit()
    print("Database cleared.")


# ---------------------------
# Seeder functions
# ---------------------------
def seed_users(db: Session):
    print("Seeding users...")
    users = []

    for _ in range(NUM_ARTISTS):
        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            password_hash=hash_password(DEFAULT_TEST_PASSWORD),
            profile_pic=fake.image_url(width=200, height=200),
        )
        db.add(user)
        users.append(user)
        print(f"Created user: {user.email} / {DEFAULT_TEST_PASSWORD}")

    db.commit()
    return users


def seed_websites(db: Session, users):
    print("Seeding websites...")
    websites = []
    for user in users:
        site = Website(
            artist_id=user.user_id,
            domain=f"{fake.unique.domain_word()}.artspace.io",
            title=f"{user.name}'s Portfolio",
            theme=random.choice(["light", "dark", "minimal", "bold"]),
            config={
                "hero": {"title": f"{user.name} – Digital Artist"},
                "social": {"instagram": fake.url(), "x": fake.url()},
            },
            published_url=None,  # can be set by app later
            status="published",
            is_deleted=False,
        )
        websites.append(site)
    db.add_all(websites)
    db.commit()
    return websites


def seed_exhibitions(db: Session, users):
    print("Seeding exhibitions...")
    exhibitions = []
    for user in users:
        for _ in range(EXHIBITIONS_PER_ARTIST):
            ex = Exhibition(
                artist_id=user.user_id,
                title=fake.catch_phrase(),
                description=fake.text(),
                background_music_url=fake.url(),
                config={"scenes": ["room_a", "room_b", "main_hall"]},
                published_url=None,
                thumbnail_url=fake.image_url(width=IMAGE_WIDTH, height=IMAGE_HEIGHT),  # 🔹 NEW
                status="published",
                is_deleted=False,
            )
            exhibitions.append(ex)
    db.add_all(exhibitions)
    db.commit()
    return exhibitions



def seed_artworks(db: Session, users):
    print("Seeding artworks...")
    artworks = []
    for user in users:
        count = random.randint(*ARTWORKS_PER_ARTIST)
        for _ in range(count):
            title = generate_artwork_title()
            art = Artwork(
                artist_id=user.user_id,
                title=title,
                description=generate_artwork_description(title),
                year=random.randint(2015, 2025),
                file_url=fake.image_url(width=IMAGE_WIDTH, height=IMAGE_HEIGHT),
                file_type=random_file_type(),
                price=round(random.uniform(20, 500), 2),
                availability=random.choice(["Available", "Sold", "Reserved"]),
                category=random_art_category(),
                tags=",".join(fake.words(5)),
                edition_current=1,
                edition_total=1,
                status="published",
            )
            artworks.append(art)
    db.add_all(artworks)
    db.commit()
    return artworks


def seed_analytics(db: Session, artworks, exhibitions):
    print("Seeding analytics...")
    events = []

    for item in artworks + exhibitions:
        if isinstance(item, Artwork):
            target_type = "artwork"
            target_id = item.artwork_id
        else:
            target_type = "exhibition"
            target_id = item.exhibition_id

        # Views
        for _ in range(random.randint(*VIEWS_RANGE)):
            events.append(ViewEvent(
                target_type=target_type,
                target_id=target_id,
                session_id=fake.uuid4(),
                ip_hash=fake.sha256(),
                user_agent=fake.user_agent(),
            ))

        # Likes
        for _ in range(random.randint(*LIKES_RANGE)):
            events.append(LikeEvent(
                target_type=target_type,
                target_id=target_id,
                session_id=fake.uuid4(),
                ip_hash=fake.sha256(),
            ))

        # Watch Time
        for _ in range(random.randint(*WATCH_EVENTS_RANGE)):
            events.append(WatchTimeEvent(
                target_type=target_type,
                target_id=target_id,
                session_id=fake.uuid4(),
                seconds_watched=random.randint(*WATCH_SECONDS_RANGE),
            ))

        # Reviews
        for _ in range(random.randint(*REVIEWS_RANGE)):
            events.append(Review(
                target_type=target_type,
                target_id=target_id,
                session_id=fake.uuid4(),
                ip_hash=fake.sha256(),
                rating=random.randint(1, 5),
                comment=fake.sentence(),
            ))

    db.add_all(events)
    db.commit()


def seed_orders(db: Session, artworks, users, exhibitions, websites):
    print("Seeding orders (channel-aware)...")
    orders = []

    # Build quick lookup maps for channels per artist
    artist_exhibitions = {}
    for ex in exhibitions:
        artist_exhibitions.setdefault(ex.artist_id, []).append(ex)

    artist_websites = {}
    for site in websites:
        artist_websites.setdefault(site.artist_id, []).append(site)

    for art in artworks:
        num_orders = random.randint(*ORDERS_PER_ARTWORK)
        for _ in range(num_orders):
            artist = next(u for u in users if u.user_id == art.artist_id)

            # Decide channel: 'exhibition' or 'website'
            channel = random.choice(["exhibition", "website"])
            source_type = None
            source_id = None

            ex_list = artist_exhibitions.get(artist.user_id, [])
            site_list = artist_websites.get(artist.user_id, [])

            if channel == "exhibition" and ex_list:
                chosen = random.choice(ex_list)
                source_type = "exhibition"
                source_id = chosen.exhibition_id
            elif channel == "website" and site_list:
                chosen = random.choice(site_list)
                source_type = "website"
                source_id = chosen.website_id
            else:
                # Fallback: if chosen channel missing for some reason, use whatever exists
                if ex_list:
                    chosen = random.choice(ex_list)
                    source_type = "exhibition"
                    source_id = chosen.exhibition_id
                elif site_list:
                    chosen = random.choice(site_list)
                    source_type = "website"
                    source_id = chosen.website_id
                # else both None -> direct artwork (no channel), still valid

            order = Order(
                artist_id=artist.user_id,
                buyer_name=fake.name(),
                buyer_email=fake.email(),
                buyer_phone=fake.phone_number(),
                buyer_address=fake.address(),
                total_amount=art.price,
                currency="USD",
                status=random.choice(["pending", "confirmed", "delivered"]),
            )

            item = OrderItem(
                target_type="artwork",
                target_id=art.artwork_id,
                source_type=source_type,
                source_id=source_id,
                price=art.price,
                quantity=1,
            )

            order.items.append(item)
            orders.append(order)

    db.add_all(orders)
    db.commit()
    return orders



def seed_notifications(db: Session, users, artworks, exhibitions, orders):
    """
    Simple notification seeding:
    - One notification per order for the artist.
    - Some notifications for reviews on artworks/exhibitions.
    """
    print("Seeding notifications...")
    notifications = []

    # Order notifications
    for order in orders:
        notifications.append(Notification(
            user_id=order.artist_id,
            type="order",
            target_type="order",
            target_id=order.order_id,
            link_url=f"/dashboard/orders/{order.order_id}",
            title="New order received",
            message=f"You received a new order from {order.buyer_name}.",
            is_read=False,
        ))

    # Review notifications (pick a subset so it doesn't explode)
    all_reviews = db.query(Review).all()
    random.shuffle(all_reviews)
    sample_reviews = all_reviews[: min(len(all_reviews), 50)]

    # Map target -> artist id for artworks and exhibitions
    artwork_artist_map = {a.artwork_id: a.artist_id for a in artworks}
    exhibition_artist_map = {e.exhibition_id: e.artist_id for e in exhibitions}

    for review in sample_reviews:
        if review.target_type == "artwork":
            artist_id = artwork_artist_map.get(review.target_id)
        elif review.target_type == "exhibition":
            artist_id = exhibition_artist_map.get(review.target_id)
        else:
            artist_id = None

        if not artist_id:
            continue

        notifications.append(Notification(
            user_id=artist_id,
            type="review",
            target_type=review.target_type,
            target_id=review.review_id,
            link_url=f"/dashboard/reviews/{review.review_id}",
            title="New review received",
            message=f"Someone left a {review.rating}-star review.",
            is_read=False,
        ))

    db.add_all(notifications)
    db.commit()


# ---------------------------
# Run Seeder
# ---------------------------
def run_seed():
    db = SessionLocal()

    clear_database(db)
    users = seed_users(db)
    websites = seed_websites(db, users)
    exhibitions = seed_exhibitions(db, users)
    artworks = seed_artworks(db, users)
    seed_analytics(db, artworks, exhibitions)
    orders = seed_orders(db, artworks, users, exhibitions, websites)
    seed_notifications(db, users, artworks, exhibitions, orders)

    db.close()
    print("🎉 Database seeding complete!")


if __name__ == "__main__":
    run_seed()

