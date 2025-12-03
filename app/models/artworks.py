import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Artwork(Base):
    __tablename__ = "artworks"

    artwork_id = Column(String(36), primary_key=True, default=gen_uuid)
    artist_id = Column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    year = Column(Integer, nullable=True)
    file_url = Column(Text, nullable=True)
    file_type = Column(String(50), nullable=False)  # 'image', 'video', 'model_3d'

    price = Column(Numeric(10, 2), nullable=True)
    availability = Column(String(100), nullable=True)  # 'Available', 'Sold', etc.
    category = Column(String(255), nullable=True)      # "Digital Art", "Photography", etc.
    tags = Column(Text, nullable=True)                 # comma-separated

    edition_current = Column(Integer, nullable=True)
    edition_total = Column(Integer, nullable=True)

    height = Column(Numeric(10, 2), nullable=True)
    width  = Column(Numeric(10, 2), nullable=True)
    length = Column(Numeric(10, 2), nullable=True)

 
    status = Column(String(50), default="published", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    artist = relationship("User", backref="artworks")

    __table_args__ = (
        Index("ix_artworks_artist_status", "artist_id", "status"),
    )

    def __repr__(self):
        return f"<Artwork {self.artwork_id} {self.title}>"
