# app/models/__init__.py
# import all models here so Alembic/autogenerate can detect them by importing app.models

from .users import User
from .artworks import Artwork
from .exhibitions import Exhibition
from .websites import Website
from .analytics import ViewEvent, LikeEvent, WatchTimeEvent, Review
from .orders import Order, OrderItem

# Now Base.metadata will include all models when app.models is imported
