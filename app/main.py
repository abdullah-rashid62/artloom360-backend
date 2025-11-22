from fastapi import FastAPI
from app.api import users_router, artworks_router, exhibitions_router, websites_router, analytics_router, orders_router

app = FastAPI(title="ArtLoom360 Backend")

# Include all routers
app.include_router(users_router)
app.include_router(artworks_router)
app.include_router(exhibitions_router)
app.include_router(websites_router)
app.include_router(analytics_router)
app.include_router(orders_router)
