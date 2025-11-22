import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Artwork(Base):
    __tablename__ = "artworks"

    artwork_id = Column(String(36), primary_key=True, default=gen_uuid)
    artist_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String(2048), nullable=True)
    thumbnail_url = Column(String(2048), nullable=True)
    file_type = Column(String(50), nullable=False)  # 'image', 'video', 'model_3d'
    price = Column(Numeric(10, 2), nullable=True)
    is_for_sale = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="draft", nullable=False)  # 'draft','published','archived','deleted'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    artist = relationship("User", backref="artworks")

    def __repr__(self):
        return f"<Artwork {self.artwork_id} {self.title}>"
