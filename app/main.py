import os

from dotenv import load_dotenv
from fastapi import FastAPI
from app.api import users_router, artworks_router, exhibitions_router, websites_router, analytics_router, orders_router, public_exhibitions_router
from app.api import cloudinary as cloudinary_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="ArtLoom360 Backend")






# Include all routers
app.include_router(users_router)
app.include_router(artworks_router)
app.include_router(exhibitions_router)
app.include_router(websites_router)
app.include_router(analytics_router)
app.include_router(orders_router)
app.include_router(cloudinary_router.router)
app.include_router(public_exhibitions_router)

load_dotenv()
origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
if any("*" in origin for origin in origins):
    raise ValueError("CORS_ORIGINS must contain explicit origins; wildcards are not supported")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
