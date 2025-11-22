import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Exhibition(Base):
    __tablename__ = "exhibitions"

    exhibition_id = Column(String(36), primary_key=True, default=gen_uuid)
    artist_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    background_music_url = Column(String(2048), nullable=True)
    config = Column(JSON, nullable=True)  # Three.js scene configuration
    published_url = Column(String(2048), nullable=True)
    status = Column(String(50), default="draft", nullable=False)  # 'draft','published','archived','deleted'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    artist = relationship("User", backref="exhibitions")

    def __repr__(self):
        return f"<Exhibition {self.exhibition_id} {self.title}>"
