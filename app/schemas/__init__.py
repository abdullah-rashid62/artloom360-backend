from .users import *
# app/schemas/__init__.py
from .artworks import (
    ArtworkBase,
    ArtworkCreate,
    ArtworkUpdate,
    ArtworkResponse,
    ArtworkAnalytics,
    ArtworkWithAnalyticsResponse,
)

from .exhibitions import (
    ExhibitionBase,
    ExhibitionCreate,
    ExhibitionUpdate,
    ExhibitionResponse,
    ExhibitionAnalytics,
    ExhibitionWithAnalyticsResponse,
    ReviewResponse,  # ✅ shared review schema
)
from .websites import *
from .analytics import *
from .orders import *
