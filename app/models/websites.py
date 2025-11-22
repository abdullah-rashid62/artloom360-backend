
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Website(Base):
    __tablename__ = "websites"

    website_id = Column(String(36), primary_key=True, default=gen_uuid)
    artist_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    domain = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    theme = Column(String(100), nullable=True)
    config = Column(JSON, nullable=True)  # hero banner, social links, etc.
    published_url = Column(String(2048), nullable=True)
    status = Column(String(50), default="draft", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    artist = relationship("User", backref="websites")

    def __repr__(self):
        return f"<Website {self.website_id} {self.domain or self.title}>"
