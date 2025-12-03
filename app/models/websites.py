import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Boolean, Index, UniqueConstraint
# ...

class Website(Base):
    __tablename__ = "websites"

    website_id = Column(String(36), primary_key=True, default=gen_uuid)
    artist_id = Column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # domain used in /w/{domain}, so we want it unique
    domain = Column(String(255), nullable=True, unique=True, index=True)
    title = Column(String(255), nullable=True)
    theme = Column(String(100), nullable=True)
    config = Column(JSON, nullable=True)  # hero banner, social links, etc.
    published_url = Column(Text, nullable=True)

    status = Column(String(50), default="draft", nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    artist = relationship("User", backref="websites")

    __table_args__ = (
        Index("ix_websites_artist_deleted_status", "artist_id", "is_deleted", "status"),
        UniqueConstraint("artist_id", name="uq_websites_artist_id"),  # <= 1 website per artist
    )
